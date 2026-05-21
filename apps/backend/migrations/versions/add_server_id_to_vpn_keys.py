"""add server_id to vpn_keys

Revision ID: add_server_id_to_vpn_keys
Revises: create_server_metrics
Create Date: 2026-03-28

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "add_server_id_to_vpn_keys"
down_revision = "create_server_metrics"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add server_id column (nullable initially)
    op.add_column("vpn_keys", sa.Column("server_id", postgresql.UUID(as_uuid=True), nullable=True))

    # Add latency tracking columns
    op.add_column(
        "vpn_keys", sa.Column("latency_ms", sa.Numeric(precision=8, scale=2), nullable=True)
    )
    op.add_column(
        "vpn_keys", sa.Column("last_latency_check", sa.TIMESTAMP(timezone=True), nullable=True)
    )

    # Create foreign key constraint
    op.create_foreign_key("fk_vpn_keys_server", "vpn_keys", "vpn_servers", ["server_id"], ["id"])

    # Create index for efficient server-based queries
    op.create_index("ix_vpn_keys_server_id", "vpn_keys", ["server_id"])


def downgrade() -> None:
    op.drop_index("ix_vpn_keys_server_id")
    op.drop_constraint("fk_vpn_keys_server", "vpn_keys", type_="foreignkey")
    op.drop_column("vpn_keys", "last_latency_check")
    op.drop_column("vpn_keys", "latency_ms")
    op.drop_column("vpn_keys", "server_id")
