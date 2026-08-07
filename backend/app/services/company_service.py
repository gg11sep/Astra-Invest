"""Company application service — use-case logic."""

from __future__ import annotations

from math import ceil
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.company import (
    CompanyCreate,
    CompanyListResponse,
    CompanyRead,
    CompanyUpdate,
)
from app.services.company_repository import CompanyRepository


class CompanyService:
    """Orchestrates company-related use cases."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = CompanyRepository(session)

    async def create_company(self, data: CompanyCreate) -> CompanyRead:
        """Create a new company after checking for duplicates."""
        existing = await self._repo.get_by_symbol_exchange(
            data.symbol, data.exchange
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Company with symbol '{data.symbol}' "
                    f"on exchange '{data.exchange}' already exists"
                ),
            )

        # Normalize
        payload = data.model_copy(
            update={
                "symbol": data.symbol.upper().strip(),
                "exchange": data.exchange.upper().strip(),
            }
        )
        company = await self._repo.create(payload)
        return CompanyRead.model_validate(company)

    async def get_company(self, company_id: UUID) -> CompanyRead:
        """Return a single company or 404."""
        company = await self._repo.get_by_id(company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found",
            )
        return CompanyRead.model_validate(company)

    async def list_companies(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        sector: str | None = None,
        exchange: str | None = None,
        is_active: bool | None = True,
        search: str | None = None,
    ) -> CompanyListResponse:
        """Return a paginated, filtered list of companies."""
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        items, total = await self._repo.list(
            page=page,
            page_size=page_size,
            sector=sector,
            exchange=exchange,
            is_active=is_active,
            search=search,
        )
        pages = ceil(total / page_size) if page_size else 0

        return CompanyListResponse(
            items=[CompanyRead.model_validate(c) for c in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def update_company(
        self, company_id: UUID, data: CompanyUpdate
    ) -> CompanyRead:
        """Update an existing company."""
        company = await self._repo.get_by_id(company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found",
            )

        # If symbol/exchange are being changed, check uniqueness
        new_symbol = data.symbol.upper().strip() if data.symbol else company.symbol
        new_exchange = (
            data.exchange.upper().strip() if data.exchange else company.exchange
        )
        if (new_symbol != company.symbol) or (new_exchange != company.exchange):
            existing = await self._repo.get_by_symbol_exchange(
                new_symbol, new_exchange
            )
            if existing and existing.id != company.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Another company already uses this symbol/exchange",
                )

        updated = await self._repo.update(company, data)
        return CompanyRead.model_validate(updated)

    async def delete_company(self, company_id: UUID) -> None:
        """Delete a company."""
        company = await self._repo.get_by_id(company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found",
            )
        await self._repo.delete(company)
