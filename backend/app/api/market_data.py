"""Market data feed endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas.price import PriceRead
from app.services.market_data import MarketDataService

router = APIRouter(prefix="/market-data", tags=["Market Data"])


@router.post(
    "/companies/{company_id}/refresh",
    response_model=list[PriceRead],
    summary="Fetch & store recent prices for a company",
)
async def refresh_company_prices(
    company_id: UUID,
    days: int = Query(30, ge=5, le=365),
    session: AsyncSession = Depends(get_db),
) -> list[PriceRead]:
    """Pull daily bars from Yahoo Finance and upsert into the prices table."""
    service = MarketDataService(session)
    return await service.refresh_company_prices(company_id, days=days)


@router.post(
    "/refresh",
    response_model=list[PriceRead],
    summary="Refresh by symbol/exchange",
)
async def refresh_by_symbol(
    symbol: str = Query(..., min_length=1),
    exchange: str = Query("NSE"),
    days: int = Query(30, ge=5, le=365),
    session: AsyncSession = Depends(get_db),
) -> list[PriceRead]:
    service = MarketDataService(session)
    return await service.refresh_by_symbol(symbol, exchange, days=days)
