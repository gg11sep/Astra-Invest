"""Tests for Company schemas."""

from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.company import CompanyCreate, CompanyUpdate


def test_company_create_valid() -> None:
    data = CompanyCreate(
        symbol="reliance",
        exchange="nse",
        name="Reliance Industries Ltd",
        sector="Energy",
        currency="INR",
        pe_ratio=Decimal("25.5"),
    )
    assert data.symbol == "reliance"
    assert data.pe_ratio == Decimal("25.5")


def test_company_create_requires_symbol() -> None:
    with pytest.raises(ValidationError):
        CompanyCreate(exchange="NSE", name="Test")  # type: ignore[call-arg]


def test_company_update_partial() -> None:
    data = CompanyUpdate(name="New Name", pe_ratio=Decimal("30"))
    dumped = data.model_dump(exclude_unset=True)
    assert dumped == {"name": "New Name", "pe_ratio": Decimal("30")}
    assert "symbol" not in dumped
