# User ID Universal Migration - Gap Resolution Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Close all remaining gaps in the telegram_id → user_id UUID migration across commons entities, backend DB models, services, and Telegram bot.

**Architecture:** 5 sequential phases (A-E) on branch `refactor/migrate-to-user-id-universal`. Each phase commits independently with passing tests.

**Tech Stack:** Python 3.13, FastAPI, SQLAlchemy, UUID, pytest, usipipo-commons (PyPI)

---

## Phase A: Commons Entities (Foundation)

### Task 1: Fix AdminUserInfo entity

**Files:**
- Modify: `usipipo_commons/domain/entities/admin_user_info.py`
- Modify: `usipipo_commons/domain/entities/admin.py`

**Step 1: Update admin_user_info.py**

Change `user_id: int` → `user_id: uuid.UUID`:

```python
"""
Admin User Info entity for uSipipo Commons.

This module contains the AdminUserInfo dataclass for administrative user information.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AdminUserInfo:
    """
    Administrative user information.

    This entity contains user data displayed in admin panels
    and used for administrative operations.
    """

    user_id: uuid.UUID
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    total_keys: int
    active_keys: int
    stars_balance: int = 0  # Deprecated - kept for compatibility
    total_deposited: int = 0  # Now represents referral_credits
    referral_credits: int = 0
    registration_date: Optional[datetime] = None
    last_activity: Optional[datetime] = None
```

**Step 2: Update admin.py**

The `admin.py` file has duplicate definitions of `AdminUserInfo` and `AdminKeyInfo`. Replace the entire file to re-export from the dedicated modules:

```python
"""Admin entities for uSipipo ecosystem.

Re-exports from dedicated modules to maintain backward compatibility.
"""

from .admin_user_info import AdminUserInfo
from .admin_key_info import AdminKeyInfo
from .admin_operation_result import AdminOperationResult
from .server_status import ServerStatus

__all__ = ["AdminUserInfo", "AdminKeyInfo", "AdminOperationResult", "ServerStatus"]
```

**Note:** Check if `AdminOperationResult` and `ServerStatus` exist as separate modules. If they don't, keep their definitions inline in `admin.py` but remove the duplicate `AdminUserInfo` and `AdminKeyInfo` classes.

**Step 3: Run commons tests**

```bash
cd /home/mowgli/usipipo/packages/common
uv run pytest tests/ -v
```

Expected: All tests pass.

**Step 4: Commit**

```bash
cd /home/mowgli/usipipo/packages/common
git add usipipo_commons/domain/entities/admin_user_info.py usipipo_commons/domain/entities/admin.py
git commit -m "refactor: change AdminUserInfo.user_id from int to UUID"
```

---

### Task 2: Fix AdminKeyInfo entity

**Files:**
- Modify: `usipipo_commons/domain/entities/admin_key_info.py`

**Step 1: Update admin_key_info.py**

Change `user_id: int` → `user_id: uuid.UUID`:

```python
"""
Admin Key Info entity for uSipipo Commons.

This module contains the AdminKeyInfo dataclass for administrative key information.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AdminKeyInfo:
    """
    Administrative key information.

    This entity contains VPN key data displayed in admin panels
    and used for administrative operations.
    """

    key_id: str
    user_id: uuid.UUID
    user_name: str
    key_type: str
    key_name: str
    access_url: Optional[str]
    created_at: datetime
    last_used: Optional[datetime]
    data_limit: int
    data_used: int
    is_active: bool
    server_status: str
```

**Step 2: Commit**

```bash
cd /home/mowgli/usipipo/packages/common
git add usipipo_commons/domain/entities/admin_key_info.py
git commit -m "refactor: change AdminKeyInfo.user_id from int to UUID"
```

---

### Task 3: Fix Balance entity

**Files:**
- Modify: `usipipo_commons/domain/entities/balance.py`

**Step 1: Update balance.py**

Change `user_id: int` → `user_id: uuid.UUID`:

```python
"""Balance entity for uSipipo payment system."""

import uuid
from dataclasses import dataclass


@dataclass
class Balance:
    """
    Representa el saldo de un usuario en el sistema.

    El saldo se mide en 'stars' (unidades de pago de Telegram).
    """

    user_id: uuid.UUID
    stars: int = 0

    def __post_init__(self):
        """Asegura que stars sea siempre un entero no negativo."""
        if self.stars < 0:
            self.stars = 0

    def add(self, amount: int) -> "Balance":
        """Agrega una cantidad al saldo y retorna un nuevo Balance."""
        return Balance(user_id=self.user_id, stars=self.stars + amount)

    def subtract(self, amount: int) -> "Balance":
        """Resta una cantidad del saldo y retorna un nuevo Balance."""
        new_balance = self.stars - amount
        return Balance(user_id=self.user_id, stars=max(0, new_balance))

    def has_sufficient(self, amount: int) -> bool:
        """Verifica si hay saldo suficiente para una operación."""
        return self.stars >= amount

    def __repr__(self) -> str:
        return f"<Balance(user_id={self.user_id}, stars={self.stars})>"
```

**Step 2: Commit**

```bash
cd /home/mowgli/usipipo/packages/common
git add usipipo_commons/domain/entities/balance.py
git commit -m "refactor: change Balance.user_id from int to UUID"
```

---

### Task 4: Fix DataPackage entity

**Files:**
- Modify: `usipipo_commons/domain/entities/data_package.py`

**Step 1: Update data_package.py**

Change `user_id: int` → `user_id: uuid.UUID`:

```python
# Change the field:
user_id: uuid.UUID  # was: user_id: int
```

Keep everything else unchanged.

**Step 2: Commit**

```bash
cd /home/mowgli/usipipo/packages/common
git add usipipo_commons/domain/entities/data_package.py
git commit -m "refactor: change DataPackage.user_id from int to UUID"
```

---

### Task 5: Fix Ticket entity

**Files:**
- Modify: `usipipo_commons/domain/entities/ticket.py`

**Step 1: Update ticket.py**

Change:
- `user_id: int` → `user_id: uuid.UUID`
- `resolved_by: Optional[int]` → `resolved_by: Optional[uuid.UUID]`
- `update_status` method: `admin_id: Optional[int]` → `admin_id: Optional[uuid.UUID]`

**Step 2: Commit**

```bash
cd /home/mowgli/usipipo/packages/common
git add usipipo_commons/domain/entities/ticket.py
git commit -m "refactor: change Ticket user_id and resolved_by from int to UUID"
```

---

### Task 6: Fix TicketMessage entity

**Files:**
- Modify: `usipipo_commons/domain/entities/ticket_message.py`

**Step 1: Update ticket_message.py**

Change `from_user_id: int` → `from_user_id: uuid.UUID`.

**Step 2: Commit**

```bash
cd /home/mowgli/usipipo/packages/common
git add usipipo_commons/domain/entities/ticket_message.py
git commit -m "refactor: change TicketMessage.from_user_id from int to UUID"
```

---

### Task 7: Version bump + PyPI publish

**Files:**
- Modify: `usipipo-commons/pyproject.toml`

**Step 1: Bump version**

Change `version = "0.19.0"` → `version = "0.20.0"`

**Step 2: Build and publish**

```bash
cd /home/mowgli/usipipo/packages/common
uv build
uv publish
```

**Step 3: Commit**

```bash
cd /home/mowgli/usipipo/packages/common
git add pyproject.toml
git commit -m "chore: bump version to 0.20.0 for user_id UUID migration"
```

**Step 4: Push + tag**

```bash
git push origin refactor/migrate-to-user-id-universal
git tag v0.20.0
git push origin v0.20.0
```

---

## Phase B: Backend DB Models + Migration

### Task 8: Update AdminAuditLogModel

**Files:**
- Modify: `usipipo-backend/src/infrastructure/persistence/models/admin_audit_log_model.py`

**Step 1: Update the model**

Replace `admin_telegram_id` and `target_user_telegram_id` with UUID columns:

```python
# Change imports:
from sqlalchemy import Boolean, DateTime, Index, String, Text
# Remove BigInteger from imports

# Change columns:
admin_telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
# →
admin_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)

target_user_telegram_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
# →
target_user_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
```

**Step 2: Update to_entity()**

```python
def to_entity(self) -> dict:
    return {
        "id": self.id,
        "timestamp": self.timestamp,
        "admin_id": self.admin_id,
        "admin_username": self.admin_username,
        "operation": self.operation,
        "target_type": self.target_type,
        "target_id": self.target_id,
        "target_user_id": self.target_user_id,
        "details": self.details,
        "ip_address": self.ip_address,
        "success": self.success,
        "error_message": self.error_message,
        "created_at": self.created_at,
    }
```

**Step 3: Update from_dict()**

```python
@classmethod
def from_dict(cls, data: dict) -> "AdminAuditLogModel":
    return cls(
        id=data.get("id", uuid4()),
        timestamp=data.get("timestamp", datetime.now()),
        admin_id=data["admin_id"],
        admin_username=data.get("admin_username"),
        operation=data["operation"],
        target_type=data["target_type"],
        target_id=data["target_id"],
        target_user_id=data.get("target_user_id"),
        details=data.get("details"),
        ip_address=data.get("ip_address"),
        success=data["success"],
        error_message=data.get("error_message"),
    )
```

**Step 4: Commit**

```bash
cd /home/mowgli/usipipo/apps/backend
git add src/infrastructure/persistence/models/admin_audit_log_model.py
git commit -m "refactor: migrate AdminAuditLogModel telegram_id columns to UUID"
```

---

### Task 9: Update StaffRoleModel

**Files:**
- Modify: `usipipo-backend/src/infrastructure/persistence/models/staff_role_model.py`

**Step 1: Add admin_id column, keep telegram_id as nullable lookup**

```python
class StaffRoleModel(Base):
    __tablename__ = "staff_roles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    admin_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), unique=True, nullable=False, index=True)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, nullable=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, server_default="support")
    granted_by: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=func.true())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
```

**Step 2: Update to_entity()**

```python
def to_entity(self) -> dict:
    return {
        "id": self.id,
        "admin_id": self.admin_id,
        "telegram_id": self.telegram_id,
        "username": self.username,
        "role": self.role,
        "granted_by": self.granted_by,
        "granted_at": self.granted_at,
        "is_active": self.is_active,
        "created_at": self.created_at,
        "updated_at": self.updated_at,
    }
```

**Step 3: Update from_dict()**

```python
@classmethod
def from_dict(cls, data: dict) -> "StaffRoleModel":
    return cls(
        id=data.get("id", uuid4()),
        admin_id=data["admin_id"],
        telegram_id=data.get("telegram_id"),
        username=data.get("username"),
        role=data.get("role", "support"),
        granted_by=data.get("granted_by"),
        granted_at=data.get("granted_at", datetime.now()),
        is_active=data.get("is_active", True),
    )
```

**Step 4: Commit**

```bash
cd /home/mowgli/usipipo/apps/backend
git add src/infrastructure/persistence/models/staff_role_model.py
git commit -m "refactor: add admin_id UUID to StaffRoleModel, make telegram_id nullable"
```

---

### Task 10: Update TicketModel

**Files:**
- Modify: `usipipo-backend/src/infrastructure/persistence/models/ticket_model.py`

**Step 1: Fix FK references and column types**

```python
# Change imports:
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as SQLUUID
# Remove BigInteger import

# Change columns:
user_id: Mapped[int] = mapped_column(
    BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False
)
# →
user_id: Mapped[uuid.UUID] = mapped_column(
    SQLUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
)

resolved_by: Mapped[int | None] = mapped_column(
    BigInteger, ForeignKey("users.telegram_id", ondelete="SET NULL"), nullable=True
)
# →
resolved_by: Mapped[uuid.UUID | None] = mapped_column(
    SQLUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
)
```

**Step 2: Commit**

```bash
cd /home/mowgli/usipipo/apps/backend
git add src/infrastructure/persistence/models/ticket_model.py
git commit -m "refactor: fix TicketModel FK from telegram_id to users.id"
```

---

### Task 11: Create Alembic Migration

**Files:**
- Create: `usipipo-backend/migrations/versions/2026_04_05_0001_user_id_universal_gaps.py`

**Step 1: Generate migration**

```bash
cd /home/mowgli/usipipo/apps/backend
uv run alembic revision -m "user_id_universal_gaps"
```

**Step 2: Write migration content**

```python
"""user_id_universal_gaps

Revision ID: 2026_04_05_0001
Revises: 2026_04_05_0000
Create Date: 2026-04-05
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PGUUID

revision = "2026_04_05_0001"
down_revision = "2026_04_05_0000"  # Update to match latest
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. admin_audit_logs: add new UUID columns
    op.add_column("admin_audit_logs", sa.Column("admin_id", PGUUID(as_uuid=True), nullable=True))
    op.add_column("admin_audit_logs", sa.Column("target_user_id", PGUUID(as_uuid=True), nullable=True))

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

    # 4. Make admin_id NOT NULL (all admins should have a user record)
    op.alter_column("admin_audit_logs", "admin_id", nullable=False)

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
    op.alter_column("tickets", "user_id",
        type_=PGUUID(as_uuid=True),
        existing_type=sa.BigInteger(),
        postgresql_using="user_id::uuid"
    )
    op.create_foreign_key("tickets_user_id_fkey", "tickets", "users", ["user_id"], ["id"], ondelete="CASCADE")

    # 12. tickets: change resolved_by FK
    op.drop_constraint("tickets_resolved_by_fkey", "tickets", type_="foreignkey")
    op.alter_column("tickets", "resolved_by",
        type_=PGUUID(as_uuid=True),
        existing_type=sa.BigInteger(),
        postgresql_using="resolved_by::uuid",
        nullable=True
    )
    op.create_foreign_key("tickets_resolved_by_fkey", "tickets", "users", ["resolved_by"], ["id"], ondelete="SET NULL")


def downgrade() -> None:
    # Reverse all operations
    op.drop_constraint("tickets_resolved_by_fkey", "tickets", type_="foreignkey")
    op.alter_column("tickets", "resolved_by", type_=sa.BigInteger(), nullable=True)
    op.create_foreign_key("tickets_resolved_by_fkey", "tickets", "users", ["resolved_by"], ["telegram_id"], ondelete="SET NULL")

    op.drop_constraint("tickets_user_id_fkey", "tickets", type_="foreignkey")
    op.alter_column("tickets", "user_id", type_=sa.BigInteger())
    op.create_foreign_key("tickets_user_id_fkey", "tickets", "users", ["user_id"], ["telegram_id"], ondelete="CASCADE")

    op.alter_column("staff_roles", "telegram_id", nullable=False)
    op.drop_column("staff_roles", "granted_by")
    op.add_column("staff_roles", sa.Column("granted_by", sa.BigInteger(), nullable=True))
    op.drop_constraint("uq_staff_roles_admin_id", "staff_roles", type_="unique")
    op.drop_index("ix_staff_roles_admin_id", "staff_roles")
    op.drop_column("staff_roles", "admin_id")

    op.add_column("admin_audit_logs", sa.Column("admin_telegram_id", sa.BigInteger(), nullable=False))
    op.add_column("admin_audit_logs", sa.Column("target_user_telegram_id", sa.BigInteger(), nullable=True))
    op.drop_column("admin_audit_logs", "admin_id")
    op.drop_column("admin_audit_logs", "target_user_id")
```

**Step 3: Commit**

```bash
cd /home/mowgli/usipipo/apps/backend
git add migrations/versions/2026_04_05_0001_user_id_universal_gaps.py
git commit -m "migration: add user_id universal gaps alembic migration"
```

---

### Task 12: Update backend pyproject.toml to use commons 0.20.0

**Files:**
- Modify: `usipipo-backend/pyproject.toml`

**Step 1: Update dependency**

Change `usipipo-commons>=0.19.0` → `usipipo-commons>=0.20.0`

**Step 2: Lock and sync**

```bash
cd /home/mowgli/usipipo/apps/backend
uv sync
```

**Step 3: Commit**

```bash
cd /home/mowgli/usipipo/apps/backend
git add pyproject.toml
git commit -m "chore: bump usipipo-commons to 0.20.0"
```

---

## Phase C: Backend Services

### Task 13: Fix wallet_management_service.py

**Files:**
- Modify: `usipipo-backend/src/core/application/services/wallet_management_service.py`

**Step 1: Remove telegram_id parameter from assign_wallet**

```python
async def assign_wallet(
    self,
    user_id: UUID,
    label: str | None = None,
) -> BscWallet | None:
    """
    Asigna una wallet BSC a un usuario.

    Intenta reutilizar wallets expiradas antes de crear una nueva.

    Args:
        user_id: UUID del usuario
        label: Label opcional para la wallet

    Returns:
        BscWallet: Wallet reutilizada o nueva, o None si falló
    """
    try:
        reused_address = await self.wallet_repo.get_reusable_wallet_for_user(user_id)

        if reused_address:
            existing = await self.wallet_repo.get_by_address(reused_address)
            if not existing:
                wallet_entity = Wallet.create(
                    user_id=user_id,
                    address=reused_address,
                    label=label or f"user-{user_id}",
                )
                wallet_entity.status = WalletStatus.ACTIVE
                await self.wallet_repo.create(wallet_entity)

                return BscWallet(
                    id="reused",
                    address=reused_address,
                    label=label or f"user-{user_id}",
                    status=TronWalletStatus.ACTIVE,
                )

        async with self.tron_dealer_client as client:
            new_wallet = await client.assign_wallet(label=label or f"user-{user_id}")

        wallet_entity = Wallet.create(
            user_id=user_id,
            address=new_wallet.address,
            label=new_wallet.label,
        )
        await self.wallet_repo.create(wallet_entity)

        return new_wallet

    except TronDealerApiError as e:
        if e.status_code == 401:
            print(f"TronDealer API authentication failed for user {user_id}")
        else:
            print(f"TronDealer API error {e.status_code} for user {user_id}: {e.message}")
        return None
    except Exception as e:
        print(f"Unexpected error assigning wallet to user {user_id}: {e}")
        return None
```

**Step 2: Commit**

```bash
cd /home/mowgli/usipipo/apps/backend
git add src/core/application/services/wallet_management_service.py
git commit -m "refactor: remove telegram_id param from wallet_management_service"
```

---

### Task 14: Fix wallet_pool_service.py

**Files:**
- Modify: `usipipo-backend/src/core/application/services/wallet_pool_service.py`

**Step 1: Remove telegram_id from all methods**

```python
async def get_or_assign_wallet(
    self,
    user_id: UUID,
    label: str | None = None,
) -> BscWallet | None:
    """..."""
    try:
        reusable_wallet = await self.wallet_pool_repo.get_reusable_for_user(user_id)
        if reusable_wallet:
            reusable_wallet.mark_reused(user_id)
            await self.wallet_pool_repo.update(reusable_wallet)
            return BscWallet(
                id="reused",
                address=reusable_wallet.wallet_address,
                label=label or f"user-{user_id}",
                status=TronWalletStatus.ACTIVE,
            )

        any_reusable = await self.wallet_pool_repo.get_any_available()
        if any_reusable:
            any_reusable.mark_reused(user_id)
            await self.wallet_pool_repo.update(any_reusable)
            return BscWallet(
                id="reused",
                address=any_reusable.wallet_address,
                label=label or f"user-{user_id}",
                status=TronWalletStatus.ACTIVE,
            )

        return await self._create_new_wallet(user_id, label)

    except Exception as e:
        print(f"Error en get_or_assign_wallet para user {user_id}: {e}")
        return None

async def _create_new_wallet(
    self,
    user_id: UUID,
    label: str | None = None,
) -> BscWallet | None:
    """Crea una nueva wallet para el usuario."""
    try:
        async with self.tron_dealer_client as client:
            wallet = await client.assign_wallet(label=label or f"user-{user_id}")
        return wallet
    except TronDealerApiError as e:
        if e.status_code == 401:
            print(f"TronDealer API authentication failed for user {user_id}")
        else:
            print(f"TronDealer API error {e.status_code} for user {user_id}: {e.message}")
        return None
    except Exception as e:
        print(f"Unexpected error creating wallet for user {user_id}: {e}")
        return None
```

**Step 2: Commit**

```bash
cd /home/mowgli/usipipo/apps/backend
git add src/core/application/services/wallet_pool_service.py
git commit -m "refactor: remove telegram_id param from wallet_pool_service"
```

---

### Task 15: Fix subscription_payment_service.py

**Files:**
- Modify: `usipipo-backend/src/core/application/services/subscription_payment_service.py`

**Step 1: Remove telegram_id from _send_stars_invoice, look up internally**

The `_get_user_telegram_id` helper stays (it's a legitimate internal lookup). Change `_send_stars_invoice` to accept `user_id` and look up telegram_id internally:

```python
async def _send_stars_invoice(
    self,
    user_id: uuid.UUID,
    plan_option: "SubscriptionOption",
    payload: str,
) -> dict[str, Any]:
    """Send Telegram Stars invoice to user."""
    telegram_id = await self._get_user_telegram_id(user_id)
    try:
        invoice_result = await self.telegram_stars_client.create_invoice(
            amount_usd=plan_option.usdt,
            user_telegram_id=telegram_id,
        )
        logger.info(
            f"⭐ Stars invoice sent to user {user_id}: {plan_option.name} ({plan_option.stars} XTR)"
        )
        return {"success": True, "invoice_link": invoice_result.get("result", {})}
    except Exception as e:
        logger.error(f"Error sending stars invoice to user {user_id}: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
```

Update `create_stars_invoice` to call `_send_stars_invoice` with `user_id`:

```python
# In create_stars_invoice, change:
invoice_result = await self._send_stars_invoice(
    user_id=user_id,  # was: telegram_id=telegram_id
    plan_option=plan_option,
    payload=payload,
)
```

**Step 2: Commit**

```bash
cd /home/mowgli/usipipo/apps/backend
git add src/core/application/services/subscription_payment_service.py
git commit -m "refactor: use user_id in subscription_payment_service, lookup telegram_id internally"
```

---

### Task 16: Fix referral_service.py

**Files:**
- Modify: `usipipo-backend/src/core/application/services/referral_service.py`

**Step 1: Rename register_referral_by_telegram_id → register_referral_by_user_id**

Replace the method:

```python
async def register_referral_by_user_id(
    self,
    user_id: UUID,
    referral_code: str,
) -> dict[str, Any]:
    """
    Registra un referido usando user_id UUID.
    """
    logger.info(f"Registrando referido por user_id: user_id={user_id}, code={referral_code}")

    try:
        referrer = await self.user_repo.get_by_referral_code(referral_code)
        if not referrer:
            return {"success": False, "error": "invalid_code"}

        new_user = await self.user_repo.get_by_id(user_id)
        if not new_user:
            return {"success": False, "error": "user_not_found"}

        if referrer.id == new_user.id:
            return {"success": False, "error": "self_referral"}

        if new_user.referred_by is not None:
            return {"success": False, "error": "already_referred"}

        new_referral = Referral(referrer_id=referrer.id, referred_id=new_user.id)
        await self.referral_repo.save(new_referral)

        credits_referrer = settings.REFERRAL_CREDITS_PER_REFERRAL
        credits_new_user = settings.REFERRAL_BONUS_NEW_USER

        referrer.referral_credits += credits_referrer
        await self.user_repo.update(referrer)

        new_user.referred_by = referrer.id
        new_user.referral_credits += credits_new_user
        await self.user_repo.update(new_user)

        logger.info(
            f"Referido registrado por user_id: referrer={referrer.id}, "
            f"new_user={new_user.id}, credits_referrer=+{credits_referrer}, "
            f"credits_new_user=+{credits_new_user}"
        )

        return {
            "success": True,
            "referrer_id": referrer.id,
            "credits_to_referrer": credits_referrer,
            "credits_to_new_user": credits_new_user,
        }

    except Exception as e:
        logger.error(f"Error al registrar referido por user_id: {e}")
        return {"success": False, "error": str(e)}
```

**Step 2: Commit**

```bash
cd /home/mowgli/usipipo/apps/backend
git add src/core/application/services/referral_service.py
git commit -m "refactor: change referral_service to use user_id instead of telegram_id"
```

---

### Task 17: Fix admin_key_service.py

**Files:**
- Modify: `usipipo-backend/src/core/application/services/admin_key_service.py`

**Step 1: Fix user_id in AdminKeyInfo construction**

Change line 64:
```python
# Before:
user_id=user.telegram_id if user else 0,

# After:
user_id=user.id if user else uuid.UUID("00000000-0000-0000-0000-000000000000"),
```

Add `import uuid` at top if not present.

**Step 2: Commit**

```bash
cd /home/mowgli/usipipo/apps/backend
git add src/core/application/services/admin_key_service.py
git commit -m "refactor: use user.id instead of user.telegram_id in admin_key_service"
```

---

### Task 18: Fix admin_user_service.py

**Files:**
- Modify: `usipipo-backend/src/core/application/services/admin_user_service.py`

**Step 1: Fix user_id in AdminUserInfo construction**

Two locations to fix:

In `get_all_users()` (line ~46):
```python
# Before:
user_id=user.telegram_id,

# After:
user_id=user.id,
```

In `get_user_by_id()` (line ~106):
```python
# Before:
user_id=user.telegram_id,

# After:
user_id=user.id,
```

**Step 2: Commit**

```bash
cd /home/mowgli/usipipo/apps/backend
git add src/core/application/services/admin_user_service.py
git commit -m "refactor: use user.id instead of user.telegram_id in admin_user_service"
```

---

### Task 19: Fix admin_vpn_key_service.py

**Files:**
- Modify: `usipipo-backend/src/core/application/services/admin_vpn_key_service.py`

**Step 1: Fix log_audit method**

```python
# Before:
audit_log = AdminAuditLogModel(
    operation=operation,
    target_type="vpn_key",
    target_id=target_id,
    admin_telegram_id=0,  # TODO: Migrate to admin_id UUID when model is updated
    admin_username=admin_username,
    target_user_telegram_id=None,  # TODO: Migrate to user_id UUID when model is updated
    details=details if isinstance(details, dict) else None,
    success=success,
    error_message=error_message,
)

# After:
audit_log = AdminAuditLogModel(
    operation=operation,
    target_type="vpn_key",
    target_id=target_id,
    admin_id=admin_id,
    admin_username=admin_username,
    target_user_id=None,  # Can be populated when target user is known
    details=details if isinstance(details, dict) else None,
    success=success,
    error_message=error_message,
)
```

**Step 2: Commit**

```bash
cd /home/mowgli/usipipo/apps/backend
git add src/core/application/services/admin_vpn_key_service.py
git commit -m "refactor: use admin_id UUID in admin_vpn_key_service audit logging"
```

---

### Task 20: Fix user_service.py

**Files:**
- Modify: `usipipo-backend/src/core/application/services/user_service.py`

**Step 1: Update methods**

- `get_by_telegram_id()` → **stays** (legitimate auth lookup)
- `get_or_create_by_telegram()` → **stays** (legitimate auth flow)
- `create_user()` → **stays** (user creation needs telegram_id)
- `update_user()` → **stays** (already uses user_id: UUID)
- `add_balance()` → **stays** (already uses user_id: UUID)

No changes needed in user_service.py — it already correctly separates auth flow (telegram_id) from internal operations (user_id).

**Step 2: Verify**

```bash
cd /home/mowgli/usipipo/apps/backend
git diff src/core/application/services/user_service.py
```

Expected: No changes.

---

### Task 21: Update routes that call changed services

**Files to check:**
- `usipipo-backend/src/infrastructure/api/v1/routes/wallet.py` (or similar)
- `usipipo-backend/src/infrastructure/api/v1/routes/referrals.py`
- `usipipo-backend/src/infrastructure/api/v1/routes/subscriptions.py`
- `usipipo-backend/src/infrastructure/api/v1/routes/admin.py`

**Step 1: Search for callers of changed methods**

```bash
cd /home/mowgli/usipipo/apps/backend
grep -rn "assign_wallet\|get_or_assign_wallet\|register_referral_by_telegram_id\|_send_stars_invoice" src/infrastructure/api/v1/routes/
```

**Step 2: Update each caller**

For each route that calls:
- `assign_wallet(user_id, telegram_id, ...)` → `assign_wallet(user_id, ...)`
- `get_or_assign_wallet(user_id, telegram_id, ...)` → `get_or_assign_wallet(user_id, ...)`
- `register_referral_by_telegram_id(telegram_id, code)` → `register_referral_by_user_id(user_id, code)`

**Step 3: Commit**

```bash
cd /home/mowgli/usipipo/apps/backend
git add src/infrastructure/api/v1/routes/
git commit -m "refactor: update routes to use user_id instead of telegram_id"
```

---

## Phase D: Telegram Bot Adaptation

### Task 22: Update bot auth to use user_id from JWT

**Files:**
- Modify: `usipipo-telegram-bot/src/bot/handlers/auth.py` (or equivalent auth handler)
- Modify: `usipipo-telegram-bot/src/bot/context.py` (or equivalent session storage)

**Step 1: Find auth handler**

```bash
cd /home/mowgli/usipipo/apps/bot
grep -rn "telegram_id\|user_id\|jwt\|token" src/bot/handlers/ | head -30
```

**Step 2: Update auth flow**

After the bot receives the JWT from the backend auto-register endpoint:
- Extract `user_id` from JWT `sub` claim (decode the token)
- Store `user_id` in the bot's user session/context
- Use `user_id` for all subsequent API calls

The JWT already contains `{sub: user_id, telegram_id: ...}`. The bot should:
1. Decode the JWT to get `user_id`
2. Store `user_id` in session
3. Pass `user_id` (not `telegram_id`) in all API request headers or query params

**Step 3: Commit**

```bash
cd /home/mowgli/usipipo/apps/bot
git add src/
git commit -m "refactor: use user_id from JWT in bot auth flow"
```

---

## Phase E: Tests + Verification

### Task 23: Update commons tests

**Files:**
- Modify: `usipipo-commons/tests/test_entities.py` (and any other test files using affected entities)

**Step 1: Update test fixtures**

Replace any `user_id=int` with `user_id=uuid4()` for:
- AdminUserInfo
- AdminKeyInfo
- Balance
- DataPackage
- Ticket
- TicketMessage

**Step 2: Run tests**

```bash
cd /home/mowgli/usipipo/packages/common
uv run pytest tests/ -v
```

Expected: All passing.

**Step 3: Commit**

```bash
cd /home/mowgli/usipipo/packages/common
git add tests/
git commit -m "test: update commons tests for UUID user_id"
```

---

### Task 24: Update backend tests

**Files:**
- Modify: All `usipipo-backend/tests/unit/**/*.py` that test affected services

**Step 1: Find affected test files**

```bash
cd /home/mowgli/usipipo/apps/backend
grep -rn "telegram_id" tests/unit/ | grep -v "__pycache__"
```

**Step 2: Update test fixtures and assertions**

For each test file:
- Replace `telegram_id=123456` with `user_id=uuid.uuid4()` where calling service methods
- Update mock expectations to use UUID parameters
- Fix assertion comparisons

**Step 3: Run tests**

```bash
cd /home/mowgli/usipipo/apps/backend
uv run pytest tests/unit/ -v
```

Expected: All passing.

**Step 4: Commit**

```bash
cd /home/mowgli/usipipo/apps/backend
git add tests/
git commit -m "test: update backend tests for user_id UUID migration"
```

---

### Task 25: Run mypy verification

**Step 1: Run mypy**

```bash
cd /home/mowgli/usipipo/apps/backend
uv run mypy src/
```

Expected: 0 errors.

If errors remain, fix them with targeted type annotations (not `# type: ignore` unless absolutely necessary).

**Step 2: Commit any fixes**

```bash
cd /home/mowgli/usipipo/apps/backend
git add src/
git commit -m "fix: resolve mypy errors from user_id migration"
```

---

### Task 26: Full test suite + final commit

**Step 1: Run full backend test suite**

```bash
cd /home/mowgli/usipipo/apps/backend
uv run pytest tests/ -v --tb=short
```

Expected: All passing.

**Step 2: Push all changes**

```bash
cd /home/mowgli/usipipo/apps/backend
git push origin refactor/migrate-to-user-id-universal
```

**Step 3: Create PR**

```bash
cd /home/mowgli/usipipo/apps/backend
gh pr create \
  --base main \
  --head refactor/migrate-to-user-id-universal \
  --title "refactor: complete user_id universal migration (gaps)" \
  --body "Closes remaining telegram_id → user_id UUID migration gaps across commons entities, DB models, services, and bot."
```

---

## Summary Checklist

- [ ] Phase A: Commons Entities (7 tasks)
- [ ] Phase B: Backend DB Models + Migration (5 tasks)
- [ ] Phase C: Backend Services (9 tasks)
- [ ] Phase D: Telegram Bot Adaptation (1 task)
- [ ] Phase E: Tests + Verification (4 tasks)
