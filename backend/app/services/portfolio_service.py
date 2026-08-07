"""Portfolio application service."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import Portfolio
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioListResponse,
    PortfolioRead,
    PortfolioUpdate,
)


class PortfolioService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user_id: UUID, data: PortfolioCreate) -> PortfolioRead:
        portfolio = Portfolio(
            user_id=user_id,
            name=data.name,
            description=data.description,
            base_currency=data.base_currency,
            is_default=data.is_default,
        )
        self._session.add(portfolio)
        await self._session.flush()
        await self._session.refresh(portfolio)
        return PortfolioRead.model_validate(portfolio)

    async def list_for_user(self, user_id: UUID) -> PortfolioListResponse:
        result = await self._session.execute(
            select(Portfolio).where(Portfolio.user_id == user_id).order_by(Portfolio.name)
        )
        items = list(result.scalars().all())
        return PortfolioListResponse(
            items=[PortfolioRead.model_validate(p) for p in items],
            total=len(items),
        )

    async def get(self, user_id: UUID, portfolio_id: UUID) -> PortfolioRead:
        portfolio = await self._get_owned(user_id, portfolio_id)
        return PortfolioRead.model_validate(portfolio)

    async def update(
        self, user_id: UUID, portfolio_id: UUID, data: PortfolioUpdate
    ) -> PortfolioRead:
        portfolio = await self._get_owned(user_id, portfolio_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(portfolio, field, value)
        await self._session.flush()
        await self._session.refresh(portfolio)
        return PortfolioRead.model_validate(portfolio)

    async def delete(self, user_id: UUID, portfolio_id: UUID) -> None:
        portfolio = await self._get_owned(user_id, portfolio_id)
        await self._session.delete(portfolio)
        await self._session.flush()

    async def _get_owned(self, user_id: UUID, portfolio_id: UUID) -> Portfolio:
        result = await self._session.execute(
            select(Portfolio).where(
                Portfolio.id == portfolio_id,
                Portfolio.user_id == user_id,
            )
        )
        portfolio = result.scalar_one_or_none()
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found",
            )
        return portfolio
