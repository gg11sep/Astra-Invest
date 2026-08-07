"""Pydantic schemas for Company."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CompanyBase(BaseModel):
    """Shared fields for create/update."""

    symbol: str = Field(..., min_length=1, max_length=32, examples=["RELIANCE"])
    exchange: str = Field(..., min_length=1, max_length=16, examples=["NSE"])
    name: str = Field(..., min_length=1, max_length=255, examples=["Reliance Industries Ltd"])
    isin: str | None = Field(None, max_length=12)
    sector: str | None = Field(None, max_length=128)
    industry: str | None = Field(None, max_length=128)
    country: str | None = Field(None, min_length=2, max_length=2, examples=["IN"])
    currency: str = Field(default="INR", min_length=3, max_length=3)
    market_cap: Decimal | None = None
    pe_ratio: Decimal | None = None
    pb_ratio: Decimal | None = None
    dividend_yield: Decimal | None = None
    roce: Decimal | None = None
    roe: Decimal | None = None
    debt_to_equity: Decimal | None = None
    is_active: bool = True
    listing_date: date | None = None
    meta: dict[str, Any] | None = None
    description: str | None = None


class CompanyCreate(CompanyBase):
    """Schema for creating a company."""

    pass


class CompanyUpdate(BaseModel):
    """Schema for partial updates (all fields optional)."""

    symbol: str | None = Field(None, min_length=1, max_length=32)
    exchange: str | None = Field(None, min_length=1, max_length=16)
    name: str | None = Field(None, min_length=1, max_length=255)
    isin: str | None = Field(None, max_length=12)
    sector: str | None = Field(None, max_length=128)
    industry: str | None = Field(None, max_length=128)
    country: str | None = Field(None, min_length=2, max_length=2)
    currency: str | None = Field(None, min_length=3, max_length=3)
    market_cap: Decimal | None = None
    pe_ratio: Decimal | None = None
    pb_ratio: Decimal | None = None
    dividend_yield: Decimal | None = None
    roce: Decimal | None = None
    roe: Decimal | None = None
    debt_to_equity: Decimal | None = None
    is_active: bool | None = None
    listing_date: date | None = None
    meta: dict[str, Any] | None = None
    description: str | None = None


class CompanyRead(CompanyBase):
    """Schema returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class CompanyListResponse(BaseModel):
    """Paginated list of companies."""

    items: list[CompanyRead]
    total: int
    page: int
    page_size: int
    pages: int
