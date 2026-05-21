"""Update database configuration for Supabase

Revision ID: 2026_05_11_2300
Revises: 2026_04_05_0001
Create Date: 2026-05-11 23:00:00.000000

This migration updates the application configuration to use Supabase
as the PostgreSQL provider instead of local PostgreSQL.

Changes:
- alembic.ini: removed hardcoded sqlalchemy.url (now loaded from env)
- .env: Updated DATABASE_URL to point to Supabase
- Driver: asyncpg with SSL (sslmode=require)
- usipipo-commons: switched to local editable install (v0.21.0)

No database schema changes required.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2026_05_11_2300"
down_revision: str | Sequence[str] | None = "2026_04_05_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply configuration changes (no schema modifications)."""
    # This migration only documents configuration changes.
    # Actual database schema remains unchanged.
    pass


def downgrade() -> None:
    """Rollback configuration changes (no schema modifications)."""
    # This migration only documents configuration changes.
    pass
