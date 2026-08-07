"""Screening API."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas.screening import ScreenCriteria, ScreenResponse
from app.services.screening_service import ScreeningService

router = APIRouter(prefix="/screen", tags=["Screening"])


@router.post("", response_model=ScreenResponse, summary="Screen companies")
async def screen_companies(
    criteria: ScreenCriteria,
    session: AsyncSession = Depends(get_db),
) -> ScreenResponse:
    """Run a fundamental screen with configurable rules.

    Example body:
    {
      "min_roce": 20,
      "max_debt_to_equity": 0.5,
      "max_pe": 30,
      "limit": 25
    }
    """
    service = ScreeningService(session)
    return await service.screen(criteria)
