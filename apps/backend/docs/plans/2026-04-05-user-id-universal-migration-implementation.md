# User ID Universal Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Migrate all backend repository interfaces, implementations, services, and tests from `telegram_id: int` to `user_id: UUID` as the universal user identifier.

**Architecture:** `user_id: UUID` is the internal identity for all backends operations. `telegram_id: int` becomes a platform-specific attribute (like email), used only during Telegram auth lookup.

**Tech Stack:** Python 3.13, FastAPI, SQLAlchemy, UUID, pytest

---

## Phase 1: Repository Interfaces

### Task 1.1: i_consumption_invoice_repository.py

**Files:**
- Modify: `src/core/domain/interfaces/i_consumption_invoice_repository.py`

**Changes:**
```python
# Before:
async def get_by_user(self, telegram_id: int, current_user_telegram_id: int) -> list[ConsumptionInvoice]:
async def get_pending_by_user(self, telegram_id: int, current_user_telegram_id: int) -> ConsumptionInvoice | None:

# After:
async def get_by_user(self, user_id: UUID, current_user_id: UUID) -> list[ConsumptionInvoice]:
async def get_pending_by_user(self, user_id: UUID, current_user_id: UUID) -> ConsumptionInvoice | None:
```

**Step:** Update signatures and docstrings. Commit.

### Task 1.2: i_data_package_repository.py

**Files:**
- Modify: `src/core/domain/interfaces/i_data_package_repository.py`

**Changes:**
```python
# Before:
async def get_by_user(self, telegram_id: int, current_user_id: int) -> list[DataPackage]:
async def get_active_by_user(self, telegram_id: int, current_user_id: int) -> list[DataPackage]:
async def get_valid_by_user(self, telegram_id: int, current_user_id: int) -> list[DataPackage]:

# After:
async def get_by_user(self, user_id: UUID, current_user_id: UUID) -> list[DataPackage]:
async def get_active_by_user(self, user_id: UUID, current_user_id: UUID) -> list[DataPackage]:
async def get_valid_by_user(self, user_id: UUID, current_user_id: UUID) -> list[DataPackage]:
```

**Step:** Update signatures. Commit.

### Task 1.3: i_user_repository.py

**Files:**
- Modify: `src/core/domain/interfaces/i_user_repository.py`

**Changes:**
- Keep `get_by_telegram_id(telegram_id: int)` as auth lookup
- Ensure `get_by_id(user_id: UUID)` exists as primary method

**Step:** Verify interface has both methods. Commit.

### Task 1.4: i_admin_vpn_key_service.py

**Files:**
- Modify: `src/core/domain/interfaces/i_admin_vpn_key_service.py`

**Changes:**
```python
# Before:
def get_user_keys(self, user_telegram_id: int, ...) -> list[VpnKey]:

# After:
def get_user_keys(self, user_id: UUID, ...) -> list[VpnKey]:
```

**Step:** Update signatures. Commit.

---

## Phase 2: Repository Implementations

### Task 2.1: consumption_invoice_repository.py

**Files:**
- Modify: `src/infrastructure/persistence/repositories/consumption_invoice_repository.py`

**Changes:**
```python
# Before:
async def get_by_user(self, telegram_id: int, current_user_telegram_id: int) -> list[ConsumptionInvoice]:
    result = await self.session.execute(
        select(ConsumptionInvoiceModel).where(ConsumptionInvoiceModel.user_id == telegram_id)
    )

# After:
async def get_by_user(self, user_id: UUID, current_user_id: UUID) -> list[ConsumptionInvoice]:
    result = await self.session.execute(
        select(ConsumptionInvoiceModel).where(ConsumptionInvoiceModel.user_id == user_id)
    )
```

**Step:** Update all method signatures and queries. Commit.

### Task 2.2: data_package_repository.py

**Files:**
- Modify: `src/infrastructure/persistence/repositories/data_package_repository.py`

**Changes:** Same pattern - `telegram_id` → `user_id: UUID` in all methods.

**Step:** Update methods. Commit.

### Task 2.3: user_repository.py

**Files:**
- Modify: `src/infrastructure/persistence/repositories/user_repository.py`

**Changes:**
- Ensure `get_by_id(user_id: UUID)` exists
- Keep `get_by_telegram_id(telegram_id: int)` for auth lookup
- Add `get_by_telegram_id` if missing

**Step:** Verify both methods exist. Commit.

---

## Phase 3: Services

### Task 3.1: consumption_invoice_service.py

**Files:**
- Modify: `src/core/application/services/consumption_invoice_service.py`

**Changes:**
```python
# Before:
async def get_user_invoices(self, telegram_id: int, current_user_id: UUID) -> list[ConsumptionInvoice]:
    return await self.invoice_repo.get_by_user(telegram_id, current_user_id)

# After:
async def get_user_invoices(self, user_id: UUID, current_user_id: UUID) -> list[ConsumptionInvoice]:
    return await self.invoice_repo.get_by_user(user_id, current_user_id)
```

**Step:** Update all service methods. Commit.

### Task 3.2: data_package_service.py

**Files:**
- Modify: `src/core/application/services/data_package_service.py`

**Changes:** Same pattern.

**Step:** Update methods. Commit.

### Task 3.3: user_service.py

**Files:**
- Modify: `src/core/application/services/user_service.py`

**Changes:**
- Update methods to use `user_id: UUID`
- Keep `get_or_create_by_telegram(telegram_id, ...)` for auth flow

**Step:** Update methods. Commit.

### Task 3.4: admin services

**Files:**
- Modify: `src/core/application/services/admin_*.py`

**Changes:** Update `admin_telegram_id` → `admin_id: UUID` in all admin service methods.

**Step:** Update methods. Commit.

---

## Phase 4: Tests

### Task 4.1: Update test fixtures

**Files:**
- Modify: All `tests/unit/**/*.py` files

**Changes:**
```python
# Before:
result = await repository.get_by_user(telegram_id=123456, current_user_telegram_id=123456)

# After:
result = await repository.get_by_user(user_id=uuid.uuid4(), current_user_id=uuid.uuid4())
```

**Step:** Update all test calls. Commit.

### Task 4.2: Fix mypy errors

**Files:**
- Modify: `src/infrastructure/api/v1/routes/*.py`

**Changes:**
- Add `# type: ignore[arg-type]` where needed for legacy code
- Fix `invoice.id` type issues
- Fix admin service call types

**Step:** Run `uv run mypy src/` to verify. Commit.

---

## Phase 5: Telegram Bot Adaptation + Documentation

### Task 5.1: Telegram Bot Auth Flow

**Files:**
- Modify: Telegram bot auth handlers (in usipipo-telegram-bot repo)

**Changes:**
- On `/start`: lookup user by `telegram_id` → get `user_id`
- Store `user_id` in bot session
- All API calls use `user_id` from session, not `telegram_id`

**Step:** Update bot auth flow. Commit.

### Task 5.2: Documentation Rule

**Files:**
- Modify: `QWEN.md` (project root)
- Modify: `usipipo-backend/AGENTS.md`

**Changes:**
Add rule:
> **NEVER use `telegram_id` as internal user identifier.** Always use `user_id: UUID`. `telegram_id` is a platform-specific attribute used only during Telegram auth lookup.

**Step:** Add documentation rule. Commit.

---

## Summary Checklist

- [ ] Phase 1: Repository Interfaces (4 tasks)
- [ ] Phase 2: Repository Implementations (3 tasks)
- [ ] Phase 3: Services (4 tasks)
- [ ] Phase 4: Tests (2 tasks)
- [ ] Phase 5: Telegram Bot + Documentation (2 tasks)
