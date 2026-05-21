"""migrate_vpn_keys_to_uuid_add_status

Revision ID: c28f4257bb35
Revises: ef961ce7ef38
Create Date: 2026-03-22 18:45:31.996520

Migrate vpn_keys.id from str to UUID and add status column.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c28f4257bb35"
down_revision: str | Sequence[str] | None = "ef961ce7ef38"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Migrate vpn_keys.id from str to UUID and add status column.

    Steps:
    1. Add status column with default 'active'
    2. For id: str → UUID migration, we need to recreate the column
       since it's the primary key
    """
    # 1. Add status column
    op.add_column(
        "vpn_keys", sa.Column("status", sa.String(20), nullable=False, server_default="active")
    )

    # 2. Create new UUID column
    op.add_column("vpn_keys", sa.Column("id_uuid", postgresql.UUID(as_uuid=True), nullable=True))

    # 3. Convert existing string IDs to UUID format
    # Note: If existing IDs are already UUID strings, this will work
    op.execute(
        text("""
        UPDATE vpn_keys
        SET id_uuid = id::uuid
        WHERE id IS NOT NULL
    """)
    )

    # 4. Make NOT NULL
    op.alter_column("vpn_keys", "id_uuid", nullable=False)

    # 5. Drop old id column and primary key constraint
    op.drop_constraint("vpn_keys_pkey", "vpn_keys", type_="primary")
    op.drop_column("vpn_keys", "id")

    # 6. Rename id_uuid to id and set as primary key
    op.alter_column("vpn_keys", "id_uuid", new_column_name="id")
    op.create_primary_key("vpn_keys_pkey", "vpn_keys", ["id"])

    # 7. Create enum type for status
    status_enum = sa.Enum("ACTIVE", "EXPIRED", "REVOKED", "PENDING", name="key_status")
    status_enum.create(op.get_bind())

    # 8. Drop server_default before altering type
    op.execute(
        sa.text("""
        ALTER TABLE vpn_keys
        ALTER COLUMN status DROP DEFAULT
    """)
    )

    # 9. Update existing values to uppercase enum values
    op.execute(
        sa.text("""
        UPDATE vpn_keys
        SET status = UPPER(status)
    """)
    )

    # 10. Alter status column to use enum with explicit cast
    op.execute(
        sa.text("""
        ALTER TABLE vpn_keys
        ALTER COLUMN status TYPE key_status
        USING status::text::key_status
    """)
    )

    # 11. Set new default for enum
    op.execute(
        sa.text("""
        ALTER TABLE vpn_keys
        ALTER COLUMN status SET DEFAULT 'ACTIVE'
    """)
    )

    # 12. Add index on status
    op.create_index("ix_vpn_keys_status", "vpn_keys", ["status"])


def downgrade() -> None:
    """
    Revert vpn_keys.id from UUID to str and remove status column.
    """
    # 1. Drop status index
    op.drop_index("ix_vpn_keys_status", "vpn_keys")

    # 2. Drop status column
    op.drop_column("vpn_keys", "status")

    # 3. Drop enum type
    op.execute(text("DROP TYPE key_status"))

    # 4. Recreate id as string
    op.add_column("vpn_keys", sa.Column("id_str", sa.String(255), nullable=True))

    # 5. Convert UUID back to string
    op.execute(
        text("""
        UPDATE vpn_keys
        SET id_str = id::text
        WHERE id IS NOT NULL
    """)
    )

    # 6. Make NOT NULL
    op.alter_column("vpn_keys", "id_str", nullable=False)

    # 7. Drop primary key and UUID column
    op.drop_constraint("vpn_keys_pkey", "vpn_keys", type_="primary")
    op.drop_column("vpn_keys", "id")

    # 8. Rename and set as primary key
    op.alter_column("vpn_keys", "id_str", new_column_name="id")
    op.create_primary_key("vpn_keys_pkey", "vpn_keys", ["id"])
