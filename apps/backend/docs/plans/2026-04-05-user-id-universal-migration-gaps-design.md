# Remaining User ID Universal Migration - Gap Resolution Design

**Date:** 2026-04-05
**Status:** Approved
**Branch:** `refactor/migrate-to-user-id-universal`

## Problem

Phases 1-4 of the User ID Universal Migration (repository interfaces, implementations, services, tests) were completed, but 4 gaps remain that still use `telegram_id` as the user identifier instead of `user_id: UUID`.

## Gap Analysis

| # | Gap | Location | Impact |
|---|-----|----------|--------|
| 1 | `AdminAuditLogModel` uses `BigInteger` for `admin_telegram_id` and `target_user_telegram_id` | Backend DB model | Semantic error, type mismatch |
| 2 | `AdminUserInfo` and `AdminKeyInfo` in commons use `user_id: int` | usipipo-commons | Propagates wrong type to all consumers |
| 3 | Services use `telegram_id` as parameter (wallet_management, wallet_pool, subscription_payment, referral, admin services, user_service) | Backend services | Core logic uses wrong identifier |
| 4 | Telegram bot not adapted to use `user_id` from JWT | usipipo-telegram-bot | Bot sends wrong identifier to API |

## Design Principle

`telegram_id` is a **platform-specific attribute** used only during Telegram auth lookup. `user_id: UUID` is the **universal identity** for all internal operations.

**Exception:** Services that are inherently Telegram-specific (notification_service, telegram_auth_code_service) keep `telegram_id` as their parameter because they operate on the Telegram platform directly.

---

## Phase A: Commons Entities (Foundation)

### A.1: AdminUserInfo

**Files:**
- `usipipo_commons/domain/entities/admin_user_info.py`
- `usipipo_commons/domain/entities/admin.py` (duplicate class)

**Changes:**
- `user_id: int` → `user_id: uuid.UUID`
- Consolidate duplicate: `admin.py` AdminUserInfo should either be removed or re-export from `admin_user_info.py`

### A.2: AdminKeyInfo

**Files:**
- `usipipo_commons/domain/entities/admin_key_info.py`
- `usipipo_commons/domain/entities/admin.py` (duplicate class)

**Changes:**
- `user_id: int` → `user_id: uuid.UUID`
- Same consolidation approach as AdminUserInfo

### A.3: Other commons entities still using `int`

These entities also use `user_id: int` and need migration to UUID for consistency:
- `balance.py`: `user_id: int` → `user_id: uuid.UUID`
- `data_package.py`: `user_id: int` → `user_id: uuid.UUID`
- `ticket.py`: `user_id: int` → `user_id: uuid.UUID`
- `ticket_message.py`: `from_user_id: int` → `from_user_id: uuid.UUID`

### A.4: Version bump

- `pyproject.toml`: version bump (e.g., 0.19.0 → 0.20.0)
- Publish to PyPI

---

## Phase B: Backend DB Models + Migration

### B.1: AdminAuditLogModel

**File:** `src/infrastructure/persistence/models/admin_audit_log_model.py`

**Changes:**
- `admin_telegram_id: Mapped[int]` (BigInteger) → `admin_id: Mapped[UUID]` (PGUUID)
- `target_user_telegram_id: Mapped[int | None]` (BigInteger) → `target_user_id: Mapped[UUID | None]` (PGUUID)
- Update `to_entity()`: return `admin_id` and `target_user_id` instead of telegram_id variants
- Update `from_dict()`: accept `admin_id` and `target_user_id` keys

### B.2: StaffRoleModel

**File:** `src/infrastructure/persistence/models/staff_role_model.py`

**Changes:**
- Keep `telegram_id: Mapped[int]` as a nullable lookup column (admins still need telegram_id for platform identification)
- Add `admin_id: Mapped[UUID]` as the primary identifier (unique, not null)
- This is additive — no data loss

### B.3: TicketModel

**File:** `src/infrastructure/persistence/models/ticket_model.py`

**Changes:**
- `created_by` FK: `ForeignKey("users.telegram_id")` → `ForeignKey("users.id")`
- `assigned_to` FK: `ForeignKey("users.telegram_id")` → `ForeignKey("users.id")`
- Column type: `BigInteger` → `PGUUID(as_uuid=True)`

### B.4: Alembic Migration

**New migration file:** `migrations/versions/2026_04_05_xxxx_user_id_universal_gaps.py`

**Operations:**
1. ALTER TABLE `admin_audit_logs`: change `admin_telegram_id` column type from BigInteger to UUID (requires data migration strategy — drop and recreate, or add new column + migrate + drop old)
2. ALTER TABLE `admin_audit_logs`: change `target_user_telegram_id` column type similarly
3. ALTER TABLE `staff_roles`: ADD COLUMN `admin_id` UUID (nullable initially, then backfill from users table via telegram_id join, then set NOT NULL)
4. ALTER TABLE `tickets`: change `created_by` and `assigned_to` FK from `users.telegram_id` to `users.id`

**Data migration for admin_audit_logs:** Since existing audit logs reference telegram_id, we cannot simply cast. Strategy:
- Add new columns `admin_id` and `target_user_id` as nullable UUID
- Run SQL: `UPDATE admin_audit_logs SET admin_id = (SELECT id FROM users WHERE telegram_id = admin_audit_logs.admin_telegram_id)`
- Drop old columns after backfill

---

## Phase C: Backend Services

### C.1: wallet_management_service.py

**Changes:**
- `assign_wallet(telegram_id: int, ...)` → `assign_wallet(user_id: UUID, ...)`
- All log messages: `f"user {telegram_id}"` → `f"user {user_id}"`

### C.2: wallet_pool_service.py

**Changes:**
- `get_or_assign_wallet(telegram_id: int, ...)` → `get_or_assign_wallet(user_id: UUID, ...)`
- `_create_new_wallet(user_id, telegram_id, label)` → `_create_new_wallet(user_id, label)` (remove telegram_id param)

### C.3: subscription_payment_service.py

**Changes:**
- `_get_user_telegram_id(user_id: UUID)` → stays as internal helper (legitimate need to look up telegram_id for sending stars invoices)
- `process_subscription_payment(user_id, ...)` — remove `telegram_id` parameter, look up internally via `_get_user_telegram_id`
- `send_stars_invoice(telegram_id, ...)` → `send_stars_invoice(user_id, ...)` — look up telegram_id internally

### C.4: referral_service.py

**Changes:**
- `register_referral_by_telegram_id(telegram_id, code)` → `register_referral(user_id: UUID, code)`
- Internal lookup: `user_repo.get_by_id(user_id)` instead of `get_by_telegram_id(telegram_id)`

### C.5: admin_key_service.py

**Changes:**
- `user_id=user.telegram_id if user else 0` → `user_id=user.id if user else None`
- Update entity construction to use UUID

### C.6: admin_user_service.py

**Changes:**
- `user_id=user.telegram_id` → `user_id=user.id`

### C.7: admin_vpn_key_service.py

**Changes:**
- `admin_telegram_id=0` TODO → `admin_id: UUID` (proper admin ID from context)
- `target_user_telegram_id=None` → `target_user_id: UUID | None`

### C.8: user_service.py

**Changes:**
- `get_or_create_by_telegram(telegram_id, ...)` → **stays as-is** (this IS the auth flow, legitimate)
- `update_profile(telegram_id, ...)` → `update_profile(user_id: UUID, ...)`
- `create_user(telegram_id, ...)` → `create_user(telegram_id, ...)` **stays** (user creation needs telegram_id)
- `update_user_after_payment(telegram_id, ...)` → `update_user_after_payment(user_id: UUID, ...)`

### C.9: Services that stay unchanged

- `notification_service.py`: `notify_user(telegram_id)` — inherently Telegram-specific
- `telegram_auth_code_service.py`: all methods use `telegram_id` — inherently Telegram-specific

---

## Phase D: Telegram Bot Adaptation

### D.1: Auth Flow

**File:** Bot auth handlers in `usipipo-telegram-bot`

**Changes:**
- After `/start` + auto-register: extract `user_id` from JWT `sub` claim
- Store `user_id` in bot session/context (alongside existing `telegram_id` for display purposes)
- All subsequent API calls use `user_id` as the identity

### D.2: API Client

**File:** `src/infrastructure/api_client.py` or equivalent

**Changes:**
- Ensure all API requests pass `user_id` (from JWT) not `telegram_id`
- JWT already contains `{sub: user_id, telegram_id: ...}` — just use `sub`

---

## Phase E: Tests + Verification

### E.1: Update commons tests

- Update any test fixtures using `user_id=int` for AdminUserInfo, AdminKeyInfo, Balance, DataPackage, Ticket, TicketMessage

### E.2: Update backend tests

- Update service tests for wallet_management, wallet_pool, subscription_payment, referral, admin_key, admin_user, admin_vpn_key, user_service
- Fix mock assertions to use `user_id: UUID` instead of `telegram_id: int`

### E.3: Mypy verification

- Run `uv run mypy src/` — must pass with 0 errors

### E.4: Full test suite

- Run `pytest` — all tests must pass

---

## Risk Mitigation

- Each phase commits separately with passing tests
- DB migration is the highest risk — test migration on a copy of production data first
- Services that are inherently Telegram-specific (notification, auth codes) are explicitly excluded from migration
- No changes to JWT structure — `sub` claim already contains `user_id`
