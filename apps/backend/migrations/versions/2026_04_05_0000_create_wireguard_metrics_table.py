"""create wireguard_metrics table

Revision ID: 2026_04_05_0000
Revises: dfe1fcfb5354
Create Date: 2026-04-05 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2026_04_05_0000"
down_revision = "f770a6670f95"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "wireguard_metrics",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "server_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("vpn_servers.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("peer_public_key", sa.String(), nullable=False, index=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False, index=True),
        sa.Column("bytes_received", sa.BigInteger(), nullable=True, default=0),
        sa.Column("bytes_sent", sa.BigInteger(), nullable=True, default=0),
        sa.Column("last_handshake", sa.DateTime(), nullable=True),
        sa.Column("is_connected", sa.Boolean(), nullable=True, default=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        "idx_wg_metrics_server_peer_time",
        "wireguard_metrics",
        ["server_id", "peer_public_key", sa.text("timestamp DESC")],
    )
    op.create_index("idx_wg_metrics_timestamp", "wireguard_metrics", [sa.text("timestamp DESC")])


def downgrade() -> None:
    op.drop_index("idx_wg_metrics_timestamp", "wireguard_metrics")
    op.drop_index("idx_wg_metrics_server_peer_time", "wireguard_metrics")
    op.drop_table("wireguard_metrics")
