"""Watchlist schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WatchlistCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: str | None = None


class WatchlistUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    description: str | None = None


class WatchlistRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class WatchlistListResponse(BaseModel):
    items: list[WatchlistRead]
    total: int


class WatchlistItemCreate(BaseModel):
    company_id: UUID
    notes: str | None = None


class WatchlistItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    watchlist_id: UUID
    company_id: UUID
    notes: str | None
    added_at: datetime


class WatchlistItemListResponse(BaseModel):
    items: list[WatchlistItemRead]
    total: int
