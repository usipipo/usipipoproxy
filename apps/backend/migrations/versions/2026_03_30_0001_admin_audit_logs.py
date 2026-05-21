"""create admin_audit_logs table

Revision ID: 2026_03_30_0001
Revises: ef961ce7ef38
Create Date: 2026-03-30 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "2026_03_30_0001"
down_revision = "ef961ce7ef38"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "admin_audit_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "timestamp", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("admin_telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("admin_username", sa.String(length=255), nullable=True),
        sa.Column("operation", sa.String(length=50), nullable=False),
        sa.Column("target_type", sa.String(length=50), nullable=False),
        sa.Column("target_id", sa.UUID(), nullable=False),
        sa.Column("target_user_telegram_id", sa.BigInteger(), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),  # IPv6 max length
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index("idx_audit_logs_timestamp", "admin_audit_logs", ["timestamp"])
    op.create_index("idx_audit_logs_admin", "admin_audit_logs", ["admin_telegram_id"])
    op.create_index("idx_audit_logs_operation", "admin_audit_logs", ["operation"])
    op.create_index("idx_audit_logs_target", "admin_audit_logs", ["target_type", "target_id"])


def downgrade() -> None:
    op.drop_index("idx_audit_logs_target")
    op.drop_index("idx_audit_logs_operation")
    op.drop_index("idx_audit_logs_admin")
    op.drop_index("idx_audit_logs_timestamp")
    op.drop_table("admin_audit_logs")
