"""Company repository — data access layer."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyRepository:
    """Handles all database operations for Company."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: CompanyCreate) -> Company:
        """Insert a new company."""
        company = Company(**data.model_dump())
        self._session.add(company)
        await self._session.flush()
        await self._session.refresh(company)
        return company

    async def get_by_id(self, company_id: UUID) -> Company | None:
        """Fetch a company by primary key."""
        result = await self._session.execute(
            select(Company).where(Company.id == company_id)
        )
        return result.scalar_one_or_none()

    async def get_by_symbol_exchange(
        self, symbol: str, exchange: str
    ) -> Company | None:
        """Fetch by unique (symbol, exchange) pair."""
        result = await self._session.execute(
            select(Company).where(
                Company.symbol == symbol.upper(),
                Company.exchange == exchange.upper(),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        sector: str | None = None,
        exchange: str | None = None,
        is_active: bool | None = True,
        search: str | None = None,
    ) -> tuple[list[Company], int]:
        """Return a paginated list of companies with optional filters."""
        query = select(Company)
        count_query = select(func.count()).select_from(Company)

        if is_active is not None:
            query = query.where(Company.is_active == is_active)
            count_query = count_query.where(Company.is_active == is_active)

        if sector:
            query = query.where(Company.sector == sector)
            count_query = count_query.where(Company.sector == sector)

        if exchange:
            query = query.where(Company.exchange == exchange.upper())
            count_query = count_query.where(Company.exchange == exchange.upper())

        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(Company.name.ilike(pattern), Company.symbol.ilike(pattern))
            )
            count_query = count_query.where(
                or_(Company.name.ilike(pattern), Company.symbol.ilike(pattern))
            )

        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        query = query.order_by(Company.symbol).offset(offset).limit(page_size)

        result = await self._session.execute(query)
        items = list(result.scalars().all())
        return items, total

    async def update(self, company: Company, data: CompanyUpdate) -> Company:
        """Apply partial update to an existing company."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(company, field, value)
        await self._session.flush()
        await self._session.refresh(company)
        return company

    async def delete(self, company: Company) -> None:
        """Hard-delete a company."""
        await self._session.delete(company)
        await self._session.flush()
