"""Screening schemas."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.company import CompanyRead


class ScreenCriteria(BaseModel):
    """Configurable screening rules (matches the original buy_rules idea)."""

    min_roce: Decimal | None = Field(None, description="Minimum ROCE %")
    max_debt_to_equity: Decimal | None = Field(None, description="Maximum D/E")
    min_pe: Decimal | None = None
    max_pe: Decimal | None = None
    min_market_cap: Decimal | None = None
    sector: str | None = None
    exchange: str | None = None
    limit: int = Field(default=50, ge=1, le=200)


class ScreenResultItem(BaseModel):
    company: CompanyRead
    matched_rules: list[str]


class ScreenResponse(BaseModel):
    criteria: ScreenCriteria
    count: int
    results: list[ScreenResultItem]
