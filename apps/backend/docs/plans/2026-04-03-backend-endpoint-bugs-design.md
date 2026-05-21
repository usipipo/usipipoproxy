# Design: Fix 7 Backend Endpoint Bugs

**Date:** 2026-04-03
**Author:** Qwen Code (systematic debugging + brainstorming)

## Overview

7 bugs were identified in the usipipo-backend API endpoints through systematic testing. This document describes root causes and fixes.

---

## Bug 1: POST /auth/telegram - 500 KeyError: 'init_data'

**Root cause:** Route accesses `request.state.init_data` but no middleware parses form body and sets it on `request.state`.

**Fix:** Use FastAPI's `Form()` dependency to read `init_data` from form-encoded body:
```python
from fastapi import Form

async def authenticate_telegram(
    request: Request,
    init_data: str = Form(...),
    user_service: UserService = Depends(get_user_service),
):
```

**Files affected:** `src/infrastructure/api/v1/routes/auth.py`

---

## Bug 2: POST /auth/register - 500 duplicate key violates unique constraint

**Root cause:** `create_with_email` creates user with `telegram_id=0` default. Test user already has `telegram_id=0`, violating unique constraint.

**Fix:**
1. Alter `users.telegram_id` column to allow NULL
2. Update `create_with_email` to pass `telegram_id=None`
3. Update unique constraint/index to handle NULLs

**Files affected:**
- `src/core/application/services/user_service.py`
- DB migration: `ALTER TABLE users ALTER COLUMN telegram_id DROP NOT NULL`

---

## Bug 3: GET /invoices/user/{id} - 500 bigint = uuid type mismatch

**Root cause:** `consumption_invoices.user_id` is `BigInteger` (FK to `users.telegram_id`), but route accepts `user_id: uuid.UUID`.

**Fix:**
1. Change route parameter from `user_id: uuid.UUID` to `telegram_id: int`
2. Update repository `get_by_user` to accept `int` instead of `uuid.UUID`
3. Update route path to `/invoices/telegram/{telegram_id}` for clarity

**Files affected:**
- `src/infrastructure/api/v1/routes/consumption_invoices.py`
- `src/infrastructure/persistence/repositories/consumption_invoice_repository.py`
- `src/core/domain/interfaces/i_consumption_invoice_repository.py`

---

## Bug 4: GET /admin/users - 500 NameError: AdminUserInfoResponse not defined

**Root cause:** `AdminUserInfoResponse` used in list comprehension but not imported.

**Fix:** Add `AdminUserInfoResponse` to imports from `src.shared.schemas.admin`.

**Files affected:** `src/infrastructure/api/v1/routes/admin.py`

---

## Bug 5: GET /admin/servers/status - 500 NameError: ServerStatusResponse not defined

**Root cause:** `ServerStatusResponse` used but not imported (only `ServerStatusListResponse` is imported).

**Fix:** Add `ServerStatusResponse` to imports.

**Files affected:** `src/infrastructure/api/v1/routes/admin.py`

---

## Bug 6: GET /metrics/agents/{id}/health - 500 datetime subtraction error

**Root cause:** `datetime.now()` returns naive datetime, `datetime.fromisoformat()` returns aware datetime.

**Fix:** Use `datetime.now(UTC)` instead of `datetime.now()`.

**Files affected:** `src/infrastructure/api/v1/routes/metrics.py`

---

## Bug 7: GET /vpn/servers - 422 protocol required

**Root cause:** `protocol` query param is required but not obvious to callers.

**Fix:** Make `protocol` optional with default `None`. When `None`, return all servers.

**Files affected:** `src/infrastructure/api/v1/routes/vpn.py`

---

## Implementation Order

1. Bug 4 + Bug 5 (simple import fixes - 2 lines each)
2. Bug 6 (datetime.now -> datetime.now(UTC) - 1 line)
3. Bug 7 (make protocol optional - 1 line)
4. Bug 1 (Form() dependency - 2 lines)
5. Bug 3 (type mismatch fix - route + repository)
6. Bug 2 (DB migration + service change - most complex)
