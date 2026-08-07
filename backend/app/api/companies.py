"""Company API endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas.company import (
    CompanyCreate,
    CompanyListResponse,
    CompanyRead,
    CompanyUpdate,
)
from app.services.company_service import CompanyService

router = APIRouter(prefix="/companies", tags=["Companies"])


def get_company_service(session: AsyncSession = Depends(get_db)) -> CompanyService:
    """Dependency that provides a CompanyService."""
    return CompanyService(session)


@router.post(
    "",
    response_model=CompanyRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create company",
)
async def create_company(
    data: CompanyCreate,
    service: CompanyService = Depends(get_company_service),
) -> CompanyRead:
    """Create a new company in the master list."""
    return await service.create_company(data)


@router.get(
    "",
    response_model=CompanyListResponse,
    summary="List companies",
)
async def list_companies(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sector: str | None = Query(None, description="Filter by sector"),
    exchange: str | None = Query(None, description="Filter by exchange"),
    is_active: bool | None = Query(True, description="Filter by active status"),
    search: str | None = Query(None, description="Search name or symbol"),
    service: CompanyService = Depends(get_company_service),
) -> CompanyListResponse:
    """Return a paginated list of companies with optional filters."""
    return await service.list_companies(
        page=page,
        page_size=page_size,
        sector=sector,
        exchange=exchange,
        is_active=is_active,
        search=search,
    )


@router.get(
    "/{company_id}",
    response_model=CompanyRead,
    summary="Get company",
)
async def get_company(
    company_id: UUID,
    service: CompanyService = Depends(get_company_service),
) -> CompanyRead:
    """Return a single company by ID."""
    return await service.get_company(company_id)


@router.patch(
    "/{company_id}",
    response_model=CompanyRead,
    summary="Update company",
)
async def update_company(
    company_id: UUID,
    data: CompanyUpdate,
    service: CompanyService = Depends(get_company_service),
) -> CompanyRead:
    """Partially update a company."""
    return await service.update_company(company_id, data)


@router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete company",
)
async def delete_company(
    company_id: UUID,
    service: CompanyService = Depends(get_company_service),
) -> None:
    """Delete a company."""
    await service.delete_company(company_id)
