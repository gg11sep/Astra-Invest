"""Valuation API."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas.valuation import ValuationRequest, ValuationResult
from app.services.valuation_service import ValuationService

router = APIRouter(prefix="/valuation", tags=["Valuation"])


@router.post("", response_model=ValuationResult, summary="Estimate intrinsic value")
async def estimate_value(
    data: ValuationRequest,
    session: AsyncSession = Depends(get_db),
) -> ValuationResult:
    """Two-stage DCF style valuation with margin of safety.

    Provide current earnings/FCF, growth, discount rate, and optional
    shares outstanding + current price to get per-share value and upside.
    """
    service = ValuationService(session)
    return await service.value(data)
