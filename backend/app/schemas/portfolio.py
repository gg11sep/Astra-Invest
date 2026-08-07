"""Portfolio-related schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PortfolioCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: str | None = None
    base_currency: str = Field(default="INR", min_length=3, max_length=3)
    is_default: bool = False


class PortfolioUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    description: str | None = None
    base_currency: str | None = Field(None, min_length=3, max_length=3)
    is_default: bool | None = None


class PortfolioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    description: str | None
    base_currency: str
    is_default: bool
    created_at: datetime
    updated_at: datetime


class PortfolioListResponse(BaseModel):
    items: list[PortfolioRead]
    total: int
