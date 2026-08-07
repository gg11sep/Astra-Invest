"""Price endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.price import Price
from app.schemas.price import PriceCreate, PriceListResponse, PriceRead

router = APIRouter(prefix="/prices", tags=["Prices"])


@router.post("", response_model=PriceRead, status_code=201)
async def create_price(
    data: PriceCreate,
    session: AsyncSession = Depends(get_db),
) -> PriceRead:
    price = Price(**data.model_dump())
    session.add(price)
    await session.flush()
    await session.refresh(price)
    return PriceRead.model_validate(price)


@router.get("", response_model=PriceListResponse)
async def list_prices(
    company_id: UUID = Query(...),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_db),
) -> PriceListResponse:
    result = await session.execute(
        select(Price)
        .where(Price.company_id == company_id)
        .order_by(Price.trade_date.desc())
        .limit(limit)
    )
    items = list(result.scalars().all())
    return PriceListResponse(
        items=[PriceRead.model_validate(p) for p in items],
        total=len(items),
    )
