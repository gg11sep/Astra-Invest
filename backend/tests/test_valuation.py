"""Unit tests for valuation logic (no DB required for pure math path)."""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.valuation import ValuationRequest


def test_valuation_request_rejects_bad_growth() -> None:
    with pytest.raises(ValidationError):
        ValuationRequest(
            company_id=uuid4(),
            current_earnings_or_fcf=Decimal("100"),
            growth_rate=Decimal("1.5"),  # > 100%
        )


def test_valuation_request_valid() -> None:
    req = ValuationRequest(
        company_id=uuid4(),
        current_earnings_or_fcf=Decimal("1000"),
        growth_rate=Decimal("0.10"),
        discount_rate=Decimal("0.12"),
        years=5,
        shares_outstanding=Decimal("100"),
        margin_of_safety=Decimal("0.25"),
        current_price=Decimal("80"),
    )
    assert req.years == 5
    assert req.margin_of_safety == Decimal("0.25")
