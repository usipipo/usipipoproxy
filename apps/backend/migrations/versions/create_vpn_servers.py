"""create vpn_servers table

Revision ID: create_vpn_servers
Revises: 838b09c44981
Create Date: 2026-03-28

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "create_vpn_servers"
down_revision = "838b09c44981"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vpn_servers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("country_code", sa.CHAR(length=2), nullable=False),
        sa.Column("country_name", sa.String(100), nullable=False),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("region", sa.String(50), nullable=True),
        sa.Column("agent_url", sa.String(length=500), nullable=False),
        sa.Column("agent_api_key", sa.String(length=255), nullable=False),
        sa.Column("supports_outline", sa.Boolean(), nullable=True, default=True),
        sa.Column("supports_wireguard", sa.Boolean(), nullable=True, default=True),
        sa.Column("supports_trust_tunnel", sa.Boolean(), nullable=True, default=False),
        sa.Column("status", sa.String(length=20), nullable=True, default="online"),
        sa.Column("max_connections", sa.Integer(), nullable=True, default=1000),
        sa.Column("current_connections", sa.Integer(), nullable=True, default=0),
        sa.Column(
            "created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=True
        ),
        sa.Column(
            "updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=True
        ),
        sa.Column("last_heartbeat_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("country_code", "region"),
    )


def downgrade() -> None:
    op.drop_table("vpn_servers")
