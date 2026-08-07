"""Market data provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class Bar:
    trade_date: date
    open: Decimal | None
    high: Decimal | None
    low: Decimal | None
    close: Decimal
    volume: Decimal | None
    adj_close: Decimal | None = None


class MarketDataProvider(ABC):
    """Abstract market data source."""

    @abstractmethod
    async def fetch_daily(
        self, symbol: str, exchange: str = "NSE", days: int = 30
    ) -> list[Bar]:
        """Return recent daily bars for a symbol."""
        ...
