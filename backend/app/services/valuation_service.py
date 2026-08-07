"""Simple two-stage DCF valuation."""

from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.schemas.valuation import ValuationRequest, ValuationResult


class ValuationService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def value(self, req: ValuationRequest) -> ValuationResult:
        result = await self._session.execute(
            select(Company).where(Company.id == req.company_id)
        )
        company = result.scalar_one_or_none()
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

        if req.discount_rate <= req.terminal_growth:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="discount_rate must be greater than terminal_growth",
            )

        # Explicit period cash flows
        total_pv = Decimal("0")
        fcf = req.current_earnings_or_fcf
        for year in range(1, req.years + 1):
            fcf = fcf * (Decimal("1") + req.growth_rate)
            discount_factor = (Decimal("1") + req.discount_rate) ** year
            total_pv += fcf / discount_factor

        # Terminal value (Gordon growth)
        terminal_fcf = fcf * (Decimal("1") + req.terminal_growth)
        terminal_value = terminal_fcf / (req.discount_rate - req.terminal_growth)
        terminal_pv = terminal_value / ((Decimal("1") + req.discount_rate) ** req.years)
        intrinsic_total = (total_pv + terminal_pv).quantize(Decimal("0.01"))

        per_share: Decimal | None = None
        buy_below: Decimal | None = None
        if req.shares_outstanding:
            per_share = (intrinsic_total / req.shares_outstanding).quantize(Decimal("0.01"))
            buy_below = (per_share * (Decimal("1") - req.margin_of_safety)).quantize(
                Decimal("0.01")
            )

        upside: Decimal | None = None
        if req.current_price and per_share and req.current_price > 0:
            upside = ((per_share - req.current_price) / req.current_price * 100).quantize(
                Decimal("0.01")
            )

        return ValuationResult(
            company_id=req.company_id,
            intrinsic_value_total=intrinsic_total,
            intrinsic_value_per_share=per_share,
            buy_below=buy_below,
            current_price=req.current_price,
            margin_of_safety_pct=req.margin_of_safety * 100,
            upside_pct=upside,
            assumptions={
                "growth_rate": req.growth_rate,
                "discount_rate": req.discount_rate,
                "terminal_growth": req.terminal_growth,
                "years": req.years,
                "margin_of_safety": req.margin_of_safety,
            },
        )
