"""Simple fundamental screening service."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.schemas.company import CompanyRead
from app.schemas.screening import ScreenCriteria, ScreenResponse, ScreenResultItem


class ScreeningService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def screen(self, criteria: ScreenCriteria) -> ScreenResponse:
        query = select(Company).where(Company.is_active.is_(True))

        if criteria.sector:
            query = query.where(Company.sector == criteria.sector)
        if criteria.exchange:
            query = query.where(Company.exchange == criteria.exchange.upper())
        if criteria.min_roce is not None:
            query = query.where(Company.roce >= criteria.min_roce)
        if criteria.max_debt_to_equity is not None:
            query = query.where(Company.debt_to_equity <= criteria.max_debt_to_equity)
        if criteria.min_pe is not None:
            query = query.where(Company.pe_ratio >= criteria.min_pe)
        if criteria.max_pe is not None:
            query = query.where(Company.pe_ratio <= criteria.max_pe)
        if criteria.min_market_cap is not None:
            query = query.where(Company.market_cap >= criteria.min_market_cap)

        query = query.order_by(Company.symbol).limit(criteria.limit)
        result = await self._session.execute(query)
        companies = list(result.scalars().all())

        items: list[ScreenResultItem] = []
        for c in companies:
            matched: list[str] = []
            if criteria.min_roce is not None and c.roce is not None:
                matched.append(f"roce>={criteria.min_roce}")
            if criteria.max_debt_to_equity is not None and c.debt_to_equity is not None:
                matched.append(f"de<={criteria.max_debt_to_equity}")
            if criteria.max_pe is not None and c.pe_ratio is not None:
                matched.append(f"pe<={criteria.max_pe}")
            if criteria.min_market_cap is not None and c.market_cap is not None:
                matched.append(f"mcap>={criteria.min_market_cap}")
            if criteria.sector:
                matched.append(f"sector={criteria.sector}")
            items.append(
                ScreenResultItem(
                    company=CompanyRead.model_validate(c),
                    matched_rules=matched or ["active"],
                )
            )

        return ScreenResponse(criteria=criteria, count=len(items), results=items)
