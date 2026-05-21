"""create server_metrics table

Revision ID: create_server_metrics
Revises: create_vpn_servers
Create Date: 2026-03-28

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "create_server_metrics"
down_revision = "create_vpn_servers"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "server_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("server_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "timestamp", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=True
        ),
        sa.Column("cpu_percent", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("memory_percent", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("disk_percent", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("network_rx_bytes", sa.BigInteger(), nullable=True),
        sa.Column("network_tx_bytes", sa.BigInteger(), nullable=True),
        sa.Column("outline_active_keys", sa.Integer(), nullable=True),
        sa.Column("wireguard_active_peers", sa.Integer(), nullable=True),
        sa.Column("total_bytes_transferred", sa.BigInteger(), nullable=True),
        sa.Column("latency_avg_ms", sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column("latency_p95_ms", sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column("latency_p99_ms", sa.Numeric(precision=8, scale=2), nullable=True),
        sa.ForeignKeyConstraint(["server_id"], ["vpn_servers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create index for efficient time-series queries
    op.create_index(
        "idx_server_timestamp", "server_metrics", ["server_id", sa.text("timestamp DESC")]
    )


def downgrade() -> None:
    op.drop_index("idx_server_timestamp")
    op.drop_table("server_metrics")
