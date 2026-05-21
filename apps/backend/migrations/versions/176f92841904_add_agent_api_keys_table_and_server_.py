"""add agent_api_keys table and server metadata columns

Revision ID: 176f92841904
Revises: add_server_id_to_vpn_keys
Create Date: 2026-03-29 19:48:31.486846

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "176f92841904"
down_revision: str | Sequence[str] | None = "add_server_id_to_vpn_keys"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create agent_api_keys table
    op.create_table(
        "agent_api_keys",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("api_key_hash", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, default="active"),
        sa.Column("server_id", sa.UUID(), nullable=True),
        sa.Column(
            "created_at", sa.TIMESTAMP(timezone=True), nullable=True, server_default=sa.func.now()
        ),
        sa.Column("used_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("api_key_hash"),
        sa.ForeignKeyConstraint(["server_id"], ["vpn_servers.id"], ondelete="SET NULL"),
        sa.CheckConstraint("status IN ('active', 'used', 'revoked', 'expired')", name="chk_status"),
    )

    # Create indexes
    op.create_index("idx_agent_api_keys_hash", "agent_api_keys", ["api_key_hash"])
    op.create_index("idx_agent_api_keys_status", "agent_api_keys", ["status"])

    # Add metadata columns to vpn_servers
    op.add_column("vpn_servers", sa.Column("agent_version", sa.String(length=20), nullable=True))
    op.add_column("vpn_servers", sa.Column("os_type", sa.String(length=50), nullable=True))
    op.add_column("vpn_servers", sa.Column("os_arch", sa.String(length=20), nullable=True))
    op.add_column(
        "vpn_servers", sa.Column("last_registration_ip", postgresql.INET(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove columns from vpn_servers
    op.drop_column("vpn_servers", "last_registration_ip")
    op.drop_column("vpn_servers", "os_arch")
    op.drop_column("vpn_servers", "os_type")
    op.drop_column("vpn_servers", "agent_version")

    # Drop indexes
    op.drop_index("idx_agent_api_keys_status", table_name="agent_api_keys")
    op.drop_index("idx_agent_api_keys_hash", table_name="agent_api_keys")

    # Drop table
    op.drop_table("agent_api_keys")
