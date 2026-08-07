"""Portfolio, holdings, transactions and watchlist models."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Portfolio(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """User portfolio (a user can have multiple portfolios)."""

    __tablename__ = "portfolios"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    is_default: Mapped[bool] = mapped_column(default=False)

    holdings: Mapped[list[Holding]] = relationship(
        "Holding", back_populates="portfolio", cascade="all, delete-orphan"
    )
    transactions: Mapped[list[Transaction]] = relationship(
        "Transaction", back_populates="portfolio", cascade="all, delete-orphan"
    )


class Holding(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Current position in a company within a portfolio."""

    __tablename__ = "holdings"

    portfolio_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False, default=0)
    average_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    # market value fields can be computed or refreshed later

    portfolio: Mapped[Portfolio] = relationship("Portfolio", back_populates="holdings")

    __table_args__ = (
        UniqueConstraint("portfolio_id", "company_id", name="uq_holdings_portfolio_company"),
    )


class Transaction(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Buy / sell trade or corporate action."""

    __tablename__ = "transactions"

    portfolio_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    txn_type: Mapped[str] = mapped_column(
        String(16), nullable=False
    )  # BUY, SELL, DIVIDEND, SPLIT, ADJUST
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    fees: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    portfolio: Mapped[Portfolio] = relationship("Portfolio", back_populates="transactions")


class Watchlist(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Named watchlist belonging to a user."""

    __tablename__ = "watchlists"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    items: Mapped[list[WatchlistItem]] = relationship(
        "WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan"
    )


class WatchlistItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Company entry inside a watchlist."""

    __tablename__ = "watchlist_items"

    watchlist_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("watchlists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    watchlist: Mapped[Watchlist] = relationship("Watchlist", back_populates="items")

    __table_args__ = (
        UniqueConstraint("watchlist_id", "company_id", name="uq_watchlist_items_wl_company"),
    )
