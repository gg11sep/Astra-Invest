"""Seed sample companies for development.

Usage (from backend/ with DB running):
    python -m scripts.seed
"""

from __future__ import annotations

import asyncio
from decimal import Decimal

from sqlalchemy import select

from app.db.session import close_db, get_session_factory, init_db
from app.models.company import Company

SAMPLE_COMPANIES = [
    {
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "name": "Reliance Industries Ltd",
        "sector": "Energy",
        "industry": "Oil & Gas Refining",
        "country": "IN",
        "currency": "INR",
        "market_cap": Decimal("18000000000000"),
        "pe_ratio": Decimal("28.5"),
        "roce": Decimal("12.0"),
        "roe": Decimal("9.5"),
        "debt_to_equity": Decimal("0.45"),
        "description": "India's largest private sector company.",
    },
    {
        "symbol": "TCS",
        "exchange": "NSE",
        "name": "Tata Consultancy Services Ltd",
        "sector": "Technology",
        "industry": "IT Services",
        "country": "IN",
        "currency": "INR",
        "market_cap": Decimal("14000000000000"),
        "pe_ratio": Decimal("30.2"),
        "roce": Decimal("45.0"),
        "roe": Decimal("40.0"),
        "debt_to_equity": Decimal("0.05"),
        "description": "Leading global IT services company.",
    },
    {
        "symbol": "INFY",
        "exchange": "NSE",
        "name": "Infosys Ltd",
        "sector": "Technology",
        "industry": "IT Services",
        "country": "IN",
        "currency": "INR",
        "market_cap": Decimal("7000000000000"),
        "pe_ratio": Decimal("26.0"),
        "roce": Decimal("38.0"),
        "roe": Decimal("32.0"),
        "debt_to_equity": Decimal("0.08"),
    },
    {
        "symbol": "HDFCBANK",
        "exchange": "NSE",
        "name": "HDFC Bank Ltd",
        "sector": "Financials",
        "industry": "Private Bank",
        "country": "IN",
        "currency": "INR",
        "market_cap": Decimal("12000000000000"),
        "pe_ratio": Decimal("19.5"),
        "roce": Decimal("18.0"),
        "roe": Decimal("16.5"),
        "debt_to_equity": Decimal("0.0"),
    },
    {
        "symbol": "ITC",
        "exchange": "NSE",
        "name": "ITC Ltd",
        "sector": "Consumer",
        "industry": "FMCG",
        "country": "IN",
        "currency": "INR",
        "market_cap": Decimal("5500000000000"),
        "pe_ratio": Decimal("28.0"),
        "roce": Decimal("35.0"),
        "roe": Decimal("28.0"),
        "debt_to_equity": Decimal("0.01"),
    },
    {
        "symbol": "ASIANPAINT",
        "exchange": "NSE",
        "name": "Asian Paints Ltd",
        "sector": "Materials",
        "industry": "Paints",
        "country": "IN",
        "currency": "INR",
        "market_cap": Decimal("3000000000000"),
        "pe_ratio": Decimal("55.0"),
        "roce": Decimal("32.0"),
        "roe": Decimal("28.0"),
        "debt_to_equity": Decimal("0.05"),
    },
]


async def seed() -> None:
    await init_db()
    factory = get_session_factory()
    async with factory() as session:
        created = 0
        for row in SAMPLE_COMPANIES:
            existing = await session.execute(
                select(Company).where(
                    Company.symbol == row["symbol"],
                    Company.exchange == row["exchange"],
                )
            )
            if existing.scalar_one_or_none():
                continue
            session.add(Company(**row))
            created += 1
        await session.commit()
        print(f"Seeded {created} companies ({len(SAMPLE_COMPANIES) - created} already existed)")
    await close_db()


if __name__ == "__main__":
    asyncio.run(seed())
