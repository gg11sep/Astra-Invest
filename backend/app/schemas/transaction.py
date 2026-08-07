"""Transaction and holding schemas."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


TxnType = Literal["BUY", "SELL", "DIVIDEND", "SPLIT", "ADJUST"]


class TransactionCreate(BaseModel):
    company_id: UUID
    txn_type: TxnType
    quantity: Decimal = Field(..., gt=0)
    price: Decimal = Field(..., ge=0)
    fees: Decimal = Field(default=Decimal("0"), ge=0)
    trade_date: date
    notes: str | None = None


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    portfolio_id: UUID
    company_id: UUID
    txn_type: str
    quantity: Decimal
    price: Decimal
    fees: Decimal
    trade_date: date
    notes: str | None
    created_at: datetime


class TransactionListResponse(BaseModel):
    items: list[TransactionRead]
    total: int


class HoldingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    portfolio_id: UUID
    company_id: UUID
    quantity: Decimal
    average_cost: Decimal
    created_at: datetime
    updated_at: datetime


class HoldingListResponse(BaseModel):
    items: list[HoldingRead]
    total: int
