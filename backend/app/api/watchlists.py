"""Watchlist endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db import get_db
from app.models.user import User
from app.schemas.watchlist import (
    WatchlistCreate,
    WatchlistItemCreate,
    WatchlistItemListResponse,
    WatchlistItemRead,
    WatchlistListResponse,
    WatchlistRead,
    WatchlistUpdate,
)
from app.services.watchlist_service import WatchlistService

router = APIRouter(prefix="/watchlists", tags=["Watchlists"])


def get_wl_service(session: AsyncSession = Depends(get_db)) -> WatchlistService:
    return WatchlistService(session)


@router.post("", response_model=WatchlistRead, status_code=status.HTTP_201_CREATED)
async def create_watchlist(
    data: WatchlistCreate,
    current_user: User = Depends(get_current_user),
    service: WatchlistService = Depends(get_wl_service),
) -> WatchlistRead:
    return await service.create(current_user.id, data)


@router.get("", response_model=WatchlistListResponse)
async def list_watchlists(
    current_user: User = Depends(get_current_user),
    service: WatchlistService = Depends(get_wl_service),
) -> WatchlistListResponse:
    return await service.list_for_user(current_user.id)


@router.get("/{watchlist_id}", response_model=WatchlistRead)
async def get_watchlist(
    watchlist_id: UUID,
    current_user: User = Depends(get_current_user),
    service: WatchlistService = Depends(get_wl_service),
) -> WatchlistRead:
    return await service.get(current_user.id, watchlist_id)


@router.patch("/{watchlist_id}", response_model=WatchlistRead)
async def update_watchlist(
    watchlist_id: UUID,
    data: WatchlistUpdate,
    current_user: User = Depends(get_current_user),
    service: WatchlistService = Depends(get_wl_service),
) -> WatchlistRead:
    return await service.update(current_user.id, watchlist_id, data)


@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watchlist(
    watchlist_id: UUID,
    current_user: User = Depends(get_current_user),
    service: WatchlistService = Depends(get_wl_service),
) -> None:
    await service.delete(current_user.id, watchlist_id)


@router.post(
    "/{watchlist_id}/items",
    response_model=WatchlistItemRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_watchlist_item(
    watchlist_id: UUID,
    data: WatchlistItemCreate,
    current_user: User = Depends(get_current_user),
    service: WatchlistService = Depends(get_wl_service),
) -> WatchlistItemRead:
    return await service.add_item(current_user.id, watchlist_id, data)


@router.get("/{watchlist_id}/items", response_model=WatchlistItemListResponse)
async def list_watchlist_items(
    watchlist_id: UUID,
    current_user: User = Depends(get_current_user),
    service: WatchlistService = Depends(get_wl_service),
) -> WatchlistItemListResponse:
    return await service.list_items(current_user.id, watchlist_id)


@router.delete(
    "/{watchlist_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_watchlist_item(
    watchlist_id: UUID,
    item_id: UUID,
    current_user: User = Depends(get_current_user),
    service: WatchlistService = Depends(get_wl_service),
) -> None:
    await service.remove_item(current_user.id, watchlist_id, item_id)
