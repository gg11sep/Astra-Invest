"""Valuation schemas."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class ValuationRequest(BaseModel):
    """Inputs for a simple intrinsic-value estimate."""

    company_id: UUID
    # Free-cash-flow / earnings style inputs (user-supplied for MVP)
    current_earnings_or_fcf: Decimal = Field(..., gt=0, description="Current annual earnings or FCF")
    growth_rate: Decimal = Field(
        ..., ge=0, le=1, description="Expected growth rate (e.g. 0.12 = 12%)"
    )
    discount_rate: Decimal = Field(
        default=Decimal("0.12"), ge=0.01, le=0.5, description="Required return / discount rate"
    )
    terminal_growth: Decimal = Field(
        default=Decimal("0.03"), ge=0, le=0.05, description="Perpetual growth after explicit period"
    )
    years: int = Field(default=10, ge=1, le=30, description="Explicit forecast years")
    shares_outstanding: Decimal | None = Field(
        None, gt=0, description="Shares outstanding for per-share value"
    )
    margin_of_safety: Decimal = Field(
        default=Decimal("0.25"), ge=0, le=0.9, description="Desired margin of safety (0.25 = 25%)"
    )
    current_price: Decimal | None = Field(None, ge=0, description="Current market price (optional)")


class ValuationResult(BaseModel):
    company_id: UUID
    intrinsic_value_total: Decimal
    intrinsic_value_per_share: Decimal | None
    buy_below: Decimal | None  # after margin of safety
    current_price: Decimal | None
    margin_of_safety_pct: Decimal
    upside_pct: Decimal | None
    method: str = "two_stage_dcf"
    assumptions: dict[str, Decimal | int]
