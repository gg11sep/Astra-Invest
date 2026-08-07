"""Transaction and holdings endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db import get_db
from app.models.user import User
from app.schemas.transaction import (
    HoldingListResponse,
    TransactionCreate,
    TransactionListResponse,
    TransactionRead,
)
from app.services.transaction_service import TransactionService

router = APIRouter(tags=["Transactions"])


def get_txn_service(session: AsyncSession = Depends(get_db)) -> TransactionService:
    return TransactionService(session)


@router.post(
    "/portfolios/{portfolio_id}/transactions",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_transaction(
    portfolio_id: UUID,
    data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_txn_service),
) -> TransactionRead:
    return await service.add_transaction(current_user.id, portfolio_id, data)


@router.get(
    "/portfolios/{portfolio_id}/transactions",
    response_model=TransactionListResponse,
)
async def list_transactions(
    portfolio_id: UUID,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_txn_service),
) -> TransactionListResponse:
    return await service.list_transactions(current_user.id, portfolio_id)


@router.get(
    "/portfolios/{portfolio_id}/holdings",
    response_model=HoldingListResponse,
)
async def list_holdings(
    portfolio_id: UUID,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_txn_service),
) -> HoldingListResponse:
    return await service.list_holdings(current_user.id, portfolio_id)
