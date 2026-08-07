"""Transaction service — records trades and maintains holdings."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import Holding, Portfolio, Transaction
from app.schemas.transaction import (
    HoldingListResponse,
    HoldingRead,
    TransactionCreate,
    TransactionListResponse,
    TransactionRead,
)


class TransactionService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_transaction(
        self, user_id: UUID, portfolio_id: UUID, data: TransactionCreate
    ) -> TransactionRead:
        await self._assert_portfolio_owner(user_id, portfolio_id)

        if data.txn_type in ("BUY", "SELL") and data.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be positive for BUY/SELL",
            )

        txn = Transaction(
            portfolio_id=portfolio_id,
            company_id=data.company_id,
            txn_type=data.txn_type,
            quantity=data.quantity,
            price=data.price,
            fees=data.fees,
            trade_date=data.trade_date,
            notes=data.notes,
        )
        self._session.add(txn)

        if data.txn_type in ("BUY", "SELL", "ADJUST"):
            await self._apply_to_holding(portfolio_id, data)

        await self._session.flush()
        await self._session.refresh(txn)
        return TransactionRead.model_validate(txn)

    async def list_transactions(
        self, user_id: UUID, portfolio_id: UUID
    ) -> TransactionListResponse:
        await self._assert_portfolio_owner(user_id, portfolio_id)
        result = await self._session.execute(
            select(Transaction)
            .where(Transaction.portfolio_id == portfolio_id)
            .order_by(Transaction.trade_date.desc(), Transaction.created_at.desc())
        )
        items = list(result.scalars().all())
        return TransactionListResponse(
            items=[TransactionRead.model_validate(t) for t in items],
            total=len(items),
        )

    async def list_holdings(
        self, user_id: UUID, portfolio_id: UUID
    ) -> HoldingListResponse:
        await self._assert_portfolio_owner(user_id, portfolio_id)
        result = await self._session.execute(
            select(Holding).where(Holding.portfolio_id == portfolio_id)
        )
        items = list(result.scalars().all())
        return HoldingListResponse(
            items=[HoldingRead.model_validate(h) for h in items],
            total=len(items),
        )

    async def _apply_to_holding(
        self, portfolio_id: UUID, data: TransactionCreate
    ) -> None:
        result = await self._session.execute(
            select(Holding).where(
                Holding.portfolio_id == portfolio_id,
                Holding.company_id == data.company_id,
            )
        )
        holding = result.scalar_one_or_none()

        if data.txn_type == "BUY":
            if holding is None:
                holding = Holding(
                    portfolio_id=portfolio_id,
                    company_id=data.company_id,
                    quantity=data.quantity,
                    average_cost=data.price,
                )
                self._session.add(holding)
            else:
                total_cost = (holding.quantity * holding.average_cost) + (
                    data.quantity * data.price
                )
                new_qty = holding.quantity + data.quantity
                holding.quantity = new_qty
                holding.average_cost = (
                    total_cost / new_qty if new_qty > 0 else Decimal("0")
                )

        elif data.txn_type == "SELL":
            if holding is None or holding.quantity < data.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient holding quantity for SELL",
                )
            holding.quantity -= data.quantity
            if holding.quantity == 0:
                await self._session.delete(holding)

        elif data.txn_type == "ADJUST":
            if holding is None:
                holding = Holding(
                    portfolio_id=portfolio_id,
                    company_id=data.company_id,
                    quantity=data.quantity,
                    average_cost=data.price,
                )
                self._session.add(holding)
            else:
                holding.quantity = data.quantity
                if data.price > 0:
                    holding.average_cost = data.price

    async def _assert_portfolio_owner(
        self, user_id: UUID, portfolio_id: UUID
    ) -> Portfolio:
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
