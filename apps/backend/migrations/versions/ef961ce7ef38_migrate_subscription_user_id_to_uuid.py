"""migrate_subscription_user_id_to_uuid

Revision ID: ef961ce7ef38
Revises: a0fe055ac6cb
Create Date: 2026-03-22 17:16:25.206925

Migrate subscription_plans.user_id and subscription_transactions.user_id
from int (Telegram ID) to UUID (User ID) for multi-client support.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "ef961ce7ef38"
down_revision: str | Sequence[str] | None = "a0fe055ac6cb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Migrate subscription_plans.user_id from int to UUID.

    Steps:
    1. Add new column user_uuid (UUID, nullable)
    2. Populate user_uuid using JOIN with users table (users.telegram_id = subscription_plans.user_id)
    3. Make user_uuid NOT NULL
    4. Drop old user_id column
    5. Rename user_uuid to user_id
    6. Add foreign key to users.id
    """
    # === subscription_plans ===

    # 1. Add new nullable UUID column
    op.add_column(
        "subscription_plans", sa.Column("user_uuid", postgresql.UUID(as_uuid=True), nullable=True)
    )

    # 2. Populate using JOIN with users table
    op.execute("""
        UPDATE subscription_plans sp
        SET user_uuid = u.id
        FROM users u
        WHERE u.telegram_id = sp.user_id
    """)

    # 3. Make NOT NULL
    op.alter_column("subscription_plans", "user_uuid", nullable=False)

    # 4. Drop old user_id column
    op.drop_column("subscription_plans", "user_id")

    # 5. Rename user_uuid to user_id
    op.alter_column("subscription_plans", "user_uuid", new_column_name="user_id")

    # 6. Add foreign key
    op.create_foreign_key(
        "fk_subscription_plans_user_id",
        "subscription_plans",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # === subscription_transactions ===

    # 1. Add new nullable UUID column
    op.add_column(
        "subscription_transactions",
        sa.Column("user_uuid", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # 2. Populate using JOIN with users table
    op.execute("""
        UPDATE subscription_transactions st
        SET user_uuid = u.id
        FROM users u
        WHERE u.telegram_id = st.user_id
    """)

    # 3. Make NOT NULL
    op.alter_column("subscription_transactions", "user_uuid", nullable=False)

    # 4. Drop old user_id column
    op.drop_column("subscription_transactions", "user_id")

    # 5. Rename user_uuid to user_id
    op.alter_column("subscription_transactions", "user_uuid", new_column_name="user_id")

    # 6. Add foreign key
    op.create_foreign_key(
        "fk_subscription_transactions_user_id",
        "subscription_transactions",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """
    Revert subscription_plans.user_id and subscription_transactions.user_id back to int.

    Note: This will lose data if users were created without telegram_id.
    """
    # === subscription_transactions ===

    # 1. Add new nullable int column for telegram_id
    op.add_column(
        "subscription_transactions", sa.Column("telegram_id", sa.Integer(), nullable=True)
    )

    # 2. Populate using JOIN with users table
    op.execute("""
        UPDATE subscription_transactions st
        SET telegram_id = u.telegram_id
        FROM users u
        WHERE u.id = st.user_id
    """)

    # 3. Make NOT NULL
    op.alter_column("subscription_transactions", "telegram_id", nullable=False)

    # 4. Drop foreign key and UUID column
    op.drop_constraint(
        "fk_subscription_transactions_user_id", "subscription_transactions", type_="foreignkey"
    )
    op.drop_column("subscription_transactions", "user_id")

    # 5. Rename telegram_id to user_id
    op.alter_column("subscription_transactions", "telegram_id", new_column_name="user_id")

    # === subscription_plans ===

    # 1. Add new nullable int column for telegram_id
    op.add_column("subscription_plans", sa.Column("telegram_id", sa.Integer(), nullable=True))

    # 2. Populate using JOIN with users table
    op.execute("""
        UPDATE subscription_plans sp
        SET telegram_id = u.telegram_id
        FROM users u
        WHERE u.id = sp.user_id
    """)

    # 3. Make NOT NULL
    op.alter_column("subscription_plans", "telegram_id", nullable=False)

    # 4. Drop foreign key and UUID column
    op.drop_constraint("fk_subscription_plans_user_id", "subscription_plans", type_="foreignkey")
    op.drop_column("subscription_plans", "user_id")

    # 5. Rename telegram_id to user_id
    op.alter_column("subscription_plans", "telegram_id", new_column_name="user_id")
