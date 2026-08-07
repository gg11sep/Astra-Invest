"""create companies table

Revision ID: 20260806_0001
Revises:
Create Date: 2026-08-06 21:00:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260806_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("exchange", sa.String(length=16), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("isin", sa.String(length=12), nullable=True),
        sa.Column("sector", sa.String(length=128), nullable=True),
        sa.Column("industry", sa.String(length=128), nullable=True),
        sa.Column("country", sa.String(length=2), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="INR"),
        sa.Column("market_cap", sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column("pe_ratio", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("pb_ratio", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("dividend_yield", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("roce", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("roe", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("debt_to_equity", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("listing_date", sa.Date(), nullable=True),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_companies"),
        sa.UniqueConstraint("isin", name="uq_companies_isin"),
        sa.UniqueConstraint("symbol", "exchange", name="uq_companies_symbol_exchange"),
    )
    op.create_index("ix_companies_symbol", "companies", ["symbol"], unique=False)
    op.create_index("ix_companies_exchange", "companies", ["exchange"], unique=False)
    op.create_index("ix_companies_sector", "companies", ["sector"], unique=False)
    op.create_index(
        "ix_companies_sector_industry",
        "companies",
        ["sector", "industry"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_companies_sector_industry", table_name="companies")
    op.drop_index("ix_companies_sector", table_name="companies")
    op.drop_index("ix_companies_exchange", table_name="companies")
    op.drop_index("ix_companies_symbol", table_name="companies")
    op.drop_table("companies")
