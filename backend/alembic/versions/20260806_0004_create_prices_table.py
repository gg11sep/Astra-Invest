"""create prices table

Revision ID: 20260806_0004
Revises: 20260806_0003
Create Date: 2026-08-06 22:45:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260806_0004"
down_revision: Union[str, None] = "20260806_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "prices",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("trade_date", sa.Date(), nullable=False),
        sa.Column("open", sa.Numeric(18, 4), nullable=True),
        sa.Column("high", sa.Numeric(18, 4), nullable=True),
        sa.Column("low", sa.Numeric(18, 4), nullable=True),
        sa.Column("close", sa.Numeric(18, 4), nullable=False),
        sa.Column("volume", sa.Numeric(20, 0), nullable=True),
        sa.Column("adj_close", sa.Numeric(18, 4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_prices"),
        sa.UniqueConstraint("company_id", "trade_date", name="uq_prices_company_date"),
    )
    op.create_index("ix_prices_company_id", "prices", ["company_id"])
    op.create_index("ix_prices_trade_date", "prices", ["trade_date"])


def downgrade() -> None:
    op.drop_index("ix_prices_trade_date", table_name="prices")
    op.drop_index("ix_prices_company_id", table_name="prices")
    op.drop_table("prices")
