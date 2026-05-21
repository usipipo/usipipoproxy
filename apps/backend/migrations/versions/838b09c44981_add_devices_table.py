"""add_devices_table

Revision ID: 838b09c44981
Revises: d65d5b972e88
Create Date: 2026-03-22 19:37:56.668184

Add devices table for push notifications.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "838b09c44981"
down_revision: str | Sequence[str] | None = "d65d5b972e88"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Create devices table for push notifications.

    This table allows users to register multiple devices for receiving
    push notifications across different platforms (Android, iOS, etc.)
    """
    op.create_table(
        "devices",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "platform",
            sa.String(20),
            nullable=False,
            comment="Platform: android, ios, windows, linux, telegram",
        ),
        sa.Column(
            "push_token", sa.String(500), nullable=True, comment="FCM token for push notifications"
        ),
        sa.Column("app_version", sa.String(20), nullable=True, comment="App version"),
        sa.Column("device_name", sa.String(100), nullable=True, comment="Device name"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index("ix_devices_user_id", "devices", ["user_id"])
    op.create_index("ix_devices_platform", "devices", ["platform"])
    op.create_index("ix_devices_is_active", "devices", ["is_active"])


def downgrade() -> None:
    """
    Drop devices table.

    Note: This will lose all registered device information.
    Users will need to re-register devices after downgrade.
    """
    op.drop_index("ix_devices_is_active")
    op.drop_index("ix_devices_platform")
    op.drop_index("ix_devices_user_id")
    op.drop_table("devices")
