"""merge_encrypt_agent_api_keys_with_supabase_config

Revision ID: 0b7731b59cc0
Revises: encrypt_existing_agent_api_keys, 2026_05_11_2300
Create Date: 2026-05-12 01:45:53.249379

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0b7731b59cc0"
down_revision: str | Sequence[str] | None = (
    "encrypt_existing_agent_api_keys",
    "2026_05_11_2300",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Merge branch: encrypt_agent_api_keys + supabase_config."""
    pass


def downgrade() -> None:
    """Unmerge branches."""
    pass
