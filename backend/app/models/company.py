"""Company master model — the central entity of Astra-Invest."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    Date,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Company(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Listed company master record.

    This is the heart of the platform. Almost every other feature
    (portfolio, research, valuation, news) links back to a Company.
    """

    __tablename__ = "companies"

    # Identity
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    exchange: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    isin: Mapped[str | None] = mapped_column(String(12), nullable=True, unique=True)

    # Classification
    sector: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    industry: Mapped[str | None] = mapped_column(String(128), nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)  # ISO 3166-1 alpha-2
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")

    # Market data snapshot (updated by market data engine later)
    market_cap: Mapped[Decimal | None] = mapped_column(Numeric(20, 2), nullable=True)
    pe_ratio: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    pb_ratio: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    dividend_yield: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    roce: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    roe: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    debt_to_equity: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    listing_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Flexible metadata (AI summaries, extra attributes, etc.)
    meta: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("symbol", "exchange", name="uq_companies_symbol_exchange"),
        Index("ix_companies_sector_industry", "sector", "industry"),
    )

    def __repr__(self) -> str:
        return f"<Company {self.symbol}:{self.exchange} ({self.name})>"
