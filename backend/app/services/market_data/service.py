"""Market data ingestion service."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.company import Company
from app.models.price import Price
from app.schemas.price import PriceRead
from app.services.market_data.provider import MarketDataProvider
from app.services.market_data.yahoo import YahooFinanceProvider

logger = get_logger(__name__)


class MarketDataService:
    def __init__(
        self,
        session: AsyncSession,
        provider: MarketDataProvider | None = None,
    ) -> None:
        self._session = session
        self._provider = provider or YahooFinanceProvider()

    async def refresh_company_prices(
        self, company_id: UUID, days: int = 30
    ) -> list[PriceRead]:
        result = await self._session.execute(
            select(Company).where(Company.id == company_id)
        )
        company = result.scalar_one_or_none()
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

        bars = await self._provider.fetch_daily(
            company.symbol, company.exchange, days=days
        )
        if not bars:
            logger.warning(
                "no_bars_returned",
                symbol=company.symbol,
                exchange=company.exchange,
            )
            return []

        upserted: list[Price] = []
        for bar in bars:
            existing = await self._session.execute(
                select(Price).where(
                    Price.company_id == company_id,
                    Price.trade_date == bar.trade_date,
                )
            )
            price = existing.scalar_one_or_none()
            if price is None:
                price = Price(
                    company_id=company_id,
                    trade_date=bar.trade_date,
                    open=bar.open,
                    high=bar.high,
                    low=bar.low,
                    close=bar.close,
                    volume=bar.volume,
                    adj_close=bar.adj_close,
                )
                self._session.add(price)
            else:
                price.open = bar.open
                price.high = bar.high
                price.low = bar.low
                price.close = bar.close
                price.volume = bar.volume
                price.adj_close = bar.adj_close
            upserted.append(price)

        await self._session.flush()
        for p in upserted:
            await self._session.refresh(p)

        logger.info(
            "prices_refreshed",
            symbol=company.symbol,
            count=len(upserted),
        )
        return [PriceRead.model_validate(p) for p in upserted]

    async def refresh_by_symbol(
        self, symbol: str, exchange: str = "NSE", days: int = 30
    ) -> list[PriceRead]:
        result = await self._session.execute(
            select(Company).where(
                Company.symbol == symbol.upper(),
                Company.exchange == exchange.upper(),
            )
        )
        company = result.scalar_one_or_none()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company {symbol}:{exchange} not found — create it first",
            )
        return await self.refresh_company_prices(company.id, days=days)
