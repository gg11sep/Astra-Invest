"""Price schemas."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PriceCreate(BaseModel):
    company_id: UUID
    trade_date: date
    open: Decimal | None = None
    high: Decimal | None = None
    low: Decimal | None = None
    close: Decimal = Field(...)
    volume: Decimal | None = None
    adj_close: Decimal | None = None


class PriceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    trade_date: date
    open: Decimal | None
    high: Decimal | None
    low: Decimal | None
    close: Decimal
    volume: Decimal | None
    adj_close: Decimal | None
    created_at: datetime


class PriceListResponse(BaseModel):
    items: list[PriceRead]
    total: int
