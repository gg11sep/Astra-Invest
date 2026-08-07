"""Tests for SQLAlchemy models and database package."""

from __future__ import annotations

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models import Company
from app.models.company import Company as CompanyModel


def test_company_model_tablename() -> None:
    """Company model uses the expected table name."""
    assert Company.__tablename__ == "companies"
    assert CompanyModel.__tablename__ == "companies"


def test_company_model_has_required_columns() -> None:
    """Company model exposes the core columns we care about."""
    columns = {c.name for c in Company.__table__.columns}
    expected = {
        "id",
        "symbol",
        "exchange",
        "name",
        "isin",
        "sector",
        "industry",
        "currency",
        "is_active",
        "created_at",
        "updated_at",
    }
    assert expected.issubset(columns)


def test_base_metadata_contains_companies() -> None:
    """Base.metadata is aware of the companies table."""
    assert "companies" in Base.metadata.tables


def test_mixins_are_usable() -> None:
    """Mixins can be imported (smoke test)."""
    assert TimestampMixin is not None
    assert UUIDPrimaryKeyMixin is not None
