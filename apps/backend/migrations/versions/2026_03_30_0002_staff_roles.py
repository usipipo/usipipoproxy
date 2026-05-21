"""create staff_roles table

Revision ID: 2026_03_30_0002
Revises: 2026_03_30_0001
Create Date: 2026-03-30 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "2026_03_30_0002"
down_revision = "2026_03_30_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "staff_roles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="support"),
        sa.Column("granted_by", sa.BigInteger(), nullable=True),
        sa.Column("granted_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("telegram_id"),
    )

    # Create indexes
    op.create_index("idx_staff_roles_telegram", "staff_roles", ["telegram_id"])
    op.create_index("idx_staff_roles_role", "staff_roles", ["role"])


def downgrade() -> None:
    op.drop_index("idx_staff_roles_role")
    op.drop_index("idx_staff_roles_telegram")
    op.drop_table("staff_roles")
