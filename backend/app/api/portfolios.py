"""Portfolio API endpoints (authenticated)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db import get_db
from app.models.user import User
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioListResponse,
    PortfolioRead,
    PortfolioUpdate,
)
from app.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/portfolios", tags=["Portfolios"])


def get_portfolio_service(session: AsyncSession = Depends(get_db)) -> PortfolioService:
    return PortfolioService(session)


@router.post(
    "",
    response_model=PortfolioRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_portfolio(
    data: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioRead:
    return await service.create(current_user.id, data)


@router.get("", response_model=PortfolioListResponse)
async def list_portfolios(
    current_user: User = Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioListResponse:
    return await service.list_for_user(current_user.id)


@router.get("/{portfolio_id}", response_model=PortfolioRead)
async def get_portfolio(
    portfolio_id: UUID,
    current_user: User = Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioRead:
    return await service.get(current_user.id, portfolio_id)


@router.patch("/{portfolio_id}", response_model=PortfolioRead)
async def update_portfolio(
    portfolio_id: UUID,
    data: PortfolioUpdate,
    current_user: User = Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioRead:
    return await service.update(current_user.id, portfolio_id, data)


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: UUID,
    current_user: User = Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service),
) -> None:
    await service.delete(current_user.id, portfolio_id)
