"""user_id_universal_gaps

Revision ID: 2026_04_05_0001
Revises: 2026_04_05_0000
Create Date: 2026-04-05
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID as PGUUID

revision = "2026_04_05_0001"
down_revision = "2026_04_05_0000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. admin_audit_logs: add new UUID columns
    op.add_column("admin_audit_logs", sa.Column("admin_id", PGUUID(as_uuid=True), nullable=True))
    op.add_column(
        "admin_audit_logs", sa.Column("target_user_id", PGUUID(as_uuid=True), nullable=True)
    )

    # 2. Backfill admin_id from users table
    op.execute("""
        UPDATE admin_audit_logs
        SET admin_id = (
            SELECT id FROM users
            WHERE users.telegram_id = admin_audit_logs.admin_telegram_id
        )
    """)

    # 3. Backfill target_user_id from users table
    op.execute("""
        UPDATE admin_audit_logs
        SET target_user_id = (
            SELECT id FROM users
            WHERE users.telegram_id = admin_audit_logs.target_user_telegram_id
        )
    """)

    # 4. Make admin_id NOT NULL
    op.alter_column("admin_audit_logs", "admin_id", nullable=False)

    # 4b. Create index on admin_id
    op.create_index("ix_admin_audit_logs_admin_id", "admin_audit_logs", ["admin_id"])

    # 5. Drop old BigInteger columns
    op.drop_column("admin_audit_logs", "admin_telegram_id")
    op.drop_column("admin_audit_logs", "target_user_telegram_id")

    # 6. staff_roles: add admin_id column
    op.add_column("staff_roles", sa.Column("admin_id", PGUUID(as_uuid=True), nullable=True))

    # 7. Backfill admin_id from users table
    op.execute("""
        UPDATE staff_roles
        SET admin_id = (
            SELECT id FROM users
            WHERE users.telegram_id = staff_roles.telegram_id
        )
    """)

    # 8. Make admin_id NOT NULL + unique
    op.alter_column("staff_roles", "admin_id", nullable=False)
    op.create_unique_constraint("uq_staff_roles_admin_id", "staff_roles", ["admin_id"])
    op.create_index("ix_staff_roles_admin_id", "staff_roles", ["admin_id"])

    # 9. Change granted_by from BigInteger to UUID
    op.add_column("staff_roles", sa.Column("granted_by_uuid", PGUUID(as_uuid=True), nullable=True))
    op.execute("""
        UPDATE staff_roles
        SET granted_by_uuid = (
            SELECT id FROM users
            WHERE users.telegram_id = staff_roles.granted_by
        )
    """)
    op.drop_column("staff_roles", "granted_by")
    op.alter_column("staff_roles", "granted_by_uuid", new_column_name="granted_by")

    # 10. Make telegram_id nullable
    op.alter_column("staff_roles", "telegram_id", nullable=True)

    # 11. tickets: change user_id FK from telegram_id to users.id
    op.drop_constraint("tickets_user_id_fkey", "tickets", type_="foreignkey")
    op.drop_column("tickets", "user_id")
    op.add_column("tickets", sa.Column("user_id", PGUUID(as_uuid=True), nullable=False))
    op.create_foreign_key(
        "tickets_user_id_fkey", "tickets", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )

    # 12. tickets: change resolved_by FK
    op.drop_constraint("tickets_resolved_by_fkey", "tickets", type_="foreignkey")
    op.drop_column("tickets", "resolved_by")
    op.add_column("tickets", sa.Column("resolved_by", PGUUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "tickets_resolved_by_fkey", "tickets", "users", ["resolved_by"], ["id"], ondelete="SET NULL"
    )


def downgrade() -> None:
    op.drop_constraint("tickets_resolved_by_fkey", "tickets", type_="foreignkey")
    op.alter_column("tickets", "resolved_by", type_=sa.BigInteger(), nullable=True)
    op.create_foreign_key(
        "tickets_resolved_by_fkey",
        "tickets",
        "users",
        ["resolved_by"],
        ["telegram_id"],
        ondelete="SET NULL",
    )

    op.drop_constraint("tickets_user_id_fkey", "tickets", type_="foreignkey")
    op.alter_column("tickets", "user_id", type_=sa.BigInteger())
    op.create_foreign_key(
        "tickets_user_id_fkey", "tickets", "users", ["user_id"], ["telegram_id"], ondelete="CASCADE"
    )

    op.alter_column("staff_roles", "telegram_id", nullable=False)
    op.drop_column("staff_roles", "granted_by")
    op.add_column("staff_roles", sa.Column("granted_by", sa.BigInteger(), nullable=True))
    op.drop_constraint("uq_staff_roles_admin_id", "staff_roles", type_="unique")
    op.drop_index("ix_staff_roles_admin_id", "staff_roles")
    op.drop_column("staff_roles", "admin_id")

    op.add_column(
        "admin_audit_logs", sa.Column("admin_telegram_id", sa.BigInteger(), nullable=False)
    )
    op.add_column(
        "admin_audit_logs", sa.Column("target_user_telegram_id", sa.BigInteger(), nullable=True)
    )
    op.drop_index("ix_admin_audit_logs_admin_id", "admin_audit_logs")
    op.drop_column("admin_audit_logs", "admin_id")
    op.drop_column("admin_audit_logs", "target_user_id")
