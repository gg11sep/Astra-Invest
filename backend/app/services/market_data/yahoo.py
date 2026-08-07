"""Yahoo Finance market data provider (unofficial chart API)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import httpx

from app.core.logging import get_logger
from app.services.market_data.provider import Bar, MarketDataProvider

logger = get_logger(__name__)

# Map common Indian symbols to Yahoo tickers
YAHOO_SUFFIX = {
    "NSE": ".NS",
    "BSE": ".BO",
    "NYSE": "",
    "NASDAQ": "",
}


class YahooFinanceProvider(MarketDataProvider):
    """Fetch daily OHLCV from Yahoo Finance chart endpoint."""

    BASE = "https://query1.finance.yahoo.com/v8/finance/chart"

    def __init__(self, timeout: float = 20.0) -> None:
        self._timeout = timeout

    def _ticker(self, symbol: str, exchange: str) -> str:
        suffix = YAHOO_SUFFIX.get(exchange.upper(), ".NS")
        return f"{symbol.upper()}{suffix}"

    async def fetch_daily(
        self, symbol: str, exchange: str = "NSE", days: int = 30
    ) -> list[Bar]:
        ticker = self._ticker(symbol, exchange)
        period2 = int(datetime.now(UTC).timestamp())
        period1 = int((datetime.now(UTC) - timedelta(days=max(days, 5))).timestamp())
        url = (
            f"{self.BASE}/{ticker}"
            f"?period1={period1}&period2={period2}&interval=1d&events=history"
        )
        headers = {"User-Agent": "Mozilla/5.0 (compatible; Astra-Invest/0.1)"}

        async with httpx.AsyncClient(timeout=self._timeout, headers=headers) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                logger.warning(
                    "yahoo_fetch_failed",
                    ticker=ticker,
                    status=resp.status_code,
                )
                return []
            payload = resp.json()

        try:
            result = payload["chart"]["result"][0]
            timestamps = result["timestamp"]
            quote = result["indicators"]["quote"][0]
            adj = result["indicators"].get("adjclose", [{}])[0].get("adjclose") or []
        except (KeyError, IndexError, TypeError) as exc:
            logger.warning("yahoo_parse_failed", ticker=ticker, error=str(exc))
            return []

        bars: list[Bar] = []
        for i, ts in enumerate(timestamps):
            close = quote["close"][i]
            if close is None:
                continue
            trade_date = datetime.fromtimestamp(ts, tz=UTC).date()
            bars.append(
                Bar(
                    trade_date=trade_date,
                    open=_dec(quote["open"][i]),
                    high=_dec(quote["high"][i]),
                    low=_dec(quote["low"][i]),
                    close=Decimal(str(close)),
                    volume=_dec(quote["volume"][i]),
                    adj_close=_dec(adj[i]) if i < len(adj) else None,
                )
            )
        return bars


def _dec(value: float | None) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))
