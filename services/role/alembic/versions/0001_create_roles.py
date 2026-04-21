"""Crea tablas roles.roles y roles.user_roles

Revision ID: 0001
Revises:
Create Date: 2026-04-21
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from alembic import op

revision: str = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS roles")
    op.create_table(
        "roles",
        sa.Column("id", PG_UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(80), nullable=False, unique=True),
        sa.Column("description", sa.String(240), nullable=True),
        sa.Column("permissions", JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        schema="roles",
    )
    op.create_index("ix_roles_roles_name", "roles", ["name"], schema="roles")

    op.create_table(
        "user_roles",
        sa.Column("user_id", PG_UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "role_id",
            PG_UUID(as_uuid=True),
            sa.ForeignKey("roles.roles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        schema="roles",
    )


def downgrade() -> None:
    op.drop_table("user_roles", schema="roles")
    op.drop_index("ix_roles_roles_name", table_name="roles", schema="roles")
    op.drop_table("roles", schema="roles")
