"""add_auth_providers_table

Revision ID: d65d5b972e88
Revises: c28f4257bb35
Create Date: 2026-03-22 19:00:29.466352

Add auth_providers table for multi-client authentication.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d65d5b972e88"
down_revision: str | Sequence[str] | None = "c28f4257bb35"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Create auth_providers table for multi-client authentication.

    This table allows users to authenticate via multiple methods:
    - Telegram (existing users)
    - Email/password (new Android/Desktop users)
    - Google OAuth (future)
    - Apple Sign In (future)
    """
    op.create_table(
        "auth_providers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "provider",
            sa.String(20),
            nullable=False,
            comment="Provider type: telegram, email, google, apple",
        ),
        sa.Column(
            "provider_user_id",
            sa.String(255),
            nullable=False,
            comment="Unique identifier within provider",
        ),
        sa.Column(
            "password_hash",
            sa.String(255),
            nullable=True,
            comment="Hashed password (only for email provider)",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "last_used_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Last successful authentication",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index("ix_auth_providers_user_id", "auth_providers", ["user_id"])
    op.create_index(
        "ix_auth_providers_provider_user_id",
        "auth_providers",
        ["provider", "provider_user_id"],
        unique=True,
    )

    # Migrate existing Telegram users to auth_providers
    # This assumes all existing users are Telegram users
    op.execute(
        sa.text("""
        INSERT INTO auth_providers (id, user_id, provider, provider_user_id, created_at)
        SELECT gen_random_uuid(), id, 'telegram', telegram_id::text, created_at
        FROM users
        WHERE telegram_id IS NOT NULL
    """)
    )


def downgrade() -> None:
    """
    Drop auth_providers table.

    Note: This will lose all authentication provider data.
    Users will need to re-authenticate after downgrade.
    """
    op.drop_index("ix_auth_providers_provider_user_id")
    op.drop_index("ix_auth_providers_user_id")
    op.drop_table("auth_providers")
