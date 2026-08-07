"""Watchlist service."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import Watchlist, WatchlistItem
from app.schemas.watchlist import (
    WatchlistCreate,
    WatchlistItemCreate,
    WatchlistItemListResponse,
    WatchlistItemRead,
    WatchlistListResponse,
    WatchlistRead,
    WatchlistUpdate,
)


class WatchlistService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user_id: UUID, data: WatchlistCreate) -> WatchlistRead:
        wl = Watchlist(user_id=user_id, name=data.name, description=data.description)
        self._session.add(wl)
        await self._session.flush()
        await self._session.refresh(wl)
        return WatchlistRead.model_validate(wl)

    async def list_for_user(self, user_id: UUID) -> WatchlistListResponse:
        result = await self._session.execute(
            select(Watchlist).where(Watchlist.user_id == user_id).order_by(Watchlist.name)
        )
        items = list(result.scalars().all())
        return WatchlistListResponse(
            items=[WatchlistRead.model_validate(w) for w in items],
            total=len(items),
        )

    async def get(self, user_id: UUID, watchlist_id: UUID) -> WatchlistRead:
        wl = await self._get_owned(user_id, watchlist_id)
        return WatchlistRead.model_validate(wl)

    async def update(
        self, user_id: UUID, watchlist_id: UUID, data: WatchlistUpdate
    ) -> WatchlistRead:
        wl = await self._get_owned(user_id, watchlist_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(wl, field, value)
        await self._session.flush()
        await self._session.refresh(wl)
        return WatchlistRead.model_validate(wl)

    async def delete(self, user_id: UUID, watchlist_id: UUID) -> None:
        wl = await self._get_owned(user_id, watchlist_id)
        await self._session.delete(wl)
        await self._session.flush()

    async def add_item(
        self, user_id: UUID, watchlist_id: UUID, data: WatchlistItemCreate
    ) -> WatchlistItemRead:
        await self._get_owned(user_id, watchlist_id)
        existing = await self._session.execute(
            select(WatchlistItem).where(
                WatchlistItem.watchlist_id == watchlist_id,
                WatchlistItem.company_id == data.company_id,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Company already in watchlist",
            )
        item = WatchlistItem(
            watchlist_id=watchlist_id,
            company_id=data.company_id,
            notes=data.notes,
        )
        self._session.add(item)
        await self._session.flush()
        await self._session.refresh(item)
        return WatchlistItemRead.model_validate(item)

    async def list_items(
        self, user_id: UUID, watchlist_id: UUID
    ) -> WatchlistItemListResponse:
        await self._get_owned(user_id, watchlist_id)
        result = await self._session.execute(
            select(WatchlistItem).where(WatchlistItem.watchlist_id == watchlist_id)
        )
        items = list(result.scalars().all())
        return WatchlistItemListResponse(
            items=[WatchlistItemRead.model_validate(i) for i in items],
            total=len(items),
        )

    async def remove_item(
        self, user_id: UUID, watchlist_id: UUID, item_id: UUID
    ) -> None:
        await self._get_owned(user_id, watchlist_id)
        result = await self._session.execute(
            select(WatchlistItem).where(
                WatchlistItem.id == item_id,
                WatchlistItem.watchlist_id == watchlist_id,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Watchlist item not found",
            )
        await self._session.delete(item)
        await self._session.flush()

    async def _get_owned(self, user_id: UUID, watchlist_id: UUID) -> Watchlist:
        result = await self._session.execute(
            select(Watchlist).where(
                Watchlist.id == watchlist_id,
                Watchlist.user_id == user_id,
            )
        )
        wl = result.scalar_one_or_none()
        if not wl:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Watchlist not found",
            )
        return wl
