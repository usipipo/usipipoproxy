"""Merge agent_api_keys with admin_audit_logs

Revision ID: f770a6670f95
Revises: 176f92841904, 2026_03_30_0002
Create Date: 2026-03-30 18:47:23.598669

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "f770a6670f95"
down_revision: str | Sequence[str] | None = ("176f92841904", "2026_03_30_0002")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
