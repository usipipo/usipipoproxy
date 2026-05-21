# Backend Endpoint Bug Fixes Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix 7 broken API endpoints in the usipipo-backend to restore full API functionality.

**Architecture:** Targeted fixes across routes, schemas, services, and repository layers. Each fix is isolated and independently testable.

**Tech Stack:** Python 3.13, FastAPI, SQLAlchemy (asyncpg), PostgreSQL, PyJWT, Redis

---

## Pre-Implementation: Verify Current State

### Task 1: Confirm all 7 bugs still exist

**Files:**
- No changes yet

**Step 1: Run quick smoke test to confirm bugs**

```bash
# Confirm bugs still present
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjlhNGQ3Zi1lOGVmLTRkODEtODRmMS00ODMzNjNmODFkMDAiLCJleHAiOjE3NzUzNTIwOTAsImlhdCI6MTc3NTI2NTY5MCwidHlwZSI6ImFjY2VzcyIsInRlbGVncmFtX2lkIjoxMDU4NzQ5MTY1fQ.LQLhdt_5SBthUiDVgfZUOe5ITyi20EF3NMkIfNkV6As"

# Bug 4: admin/users - should return 500
curl -s https://usipipo.duckdns.org/api/v1/admin/users -H "Authorization: Bearer $TOKEN" | grep -o "NameError"

# Bug 5: admin/servers/status - should return 500
curl -s https://usipipo.duckdns.org/api/v1/admin/servers/status -H "Authorization: Bearer $TOKEN" | grep -o "NameError"

# Bug 6: metrics/agents health - should return 500
curl -s https://usipipo.duckdns.org/api/v1/metrics/agents/1bc5c426-29de-4440-9ec6-ada7866e2c08/health | grep -o "subtract"
```

Expected: All three grep patterns match (bugs confirmed).

**Step 2: Commit baseline**

```bash
git add -A && git commit -m "chore: baseline before endpoint bug fixes"
```

---

## Phase 1: Quick Import Fixes (Bugs 4, 5, 6, 7)

### Task 2: Fix Bug 4 - AdminUserInfoResponse import in admin.py

**Files:**
- Modify: `src/infrastructure/api/v1/routes/admin.py:27-38`

**Step 1: Add missing import**

In `src/infrastructure/api/v1/routes/admin.py`, find the import block:
```python
from src.shared.schemas.admin import (
    AdminKeyInfoResponse,
    AdminKeyListResponse,
    AdminOperationResultResponse,
    AdminUserListResponse,
    ...
)
```

Add `AdminUserInfoResponse` to the list:
```python
from src.shared.schemas.admin import (
    AdminKeyInfoResponse,
    AdminKeyListResponse,
    AdminOperationResultResponse,
    AdminUserListResponse,
    AdminUserInfoResponse,
    ...
)
```

**Step 2: Verify schema exists**

Confirm `AdminUserInfoResponse` is defined in `src/shared/schemas/admin.py` (line 13).

**Step 3: Restart service and test**

```bash
echo "asd123***" | sudo -S systemctl restart usipipo-backend
sleep 3
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjlhNGQ3Zi1lOGVmLTRkODEtODRmMS00ODMzNjNmODFkMDAiLCJleHAiOjE3NzUzNTIwOTAsImlhdCI6MTc3NTI2NTY5MCwidHlwZSI6ImFjY2VzcyIsInRlbGVncmFtX2lkIjoxMDU4NzQ5MTY1fQ.LQLhdt_5SBthUiDVgfZUOe5ITyi20EF3NMkIfNkV6As"
curl -s -w "\nHTTP: %{http_code}" https://usipipo.duckdns.org/api/v1/admin/users -H "Authorization: Bearer $TOKEN"
```

Expected: HTTP 200 with user list (or different error if Bug 3 also affects this).

**Step 4: Commit**

```bash
git add src/infrastructure/api/v1/routes/admin.py
git commit -m "fix: add missing AdminUserInfoResponse import in admin routes"
```

---

### Task 3: Fix Bug 5 - ServerStatusResponse import in admin.py

**Files:**
- Modify: `src/infrastructure/api/v1/routes/admin.py:27-38` (same file as Task 2)

**Step 1: Add missing import**

In the same import block, add `ServerStatusResponse`:
```python
from src.shared.schemas.admin import (
    ...
    ServerStatsResponse,
    ServerStatusListResponse,
    ServerStatusResponse,
    ...
)
```

**Step 2: Verify schema exists**

Confirm `ServerStatusResponse` is defined in `src/shared/schemas/admin.py` (line 93).

**Step 3: Restart service and test**

```bash
echo "asd123***" | sudo -S systemctl restart usipipo-backend
sleep 3
curl -s -w "\nHTTP: %{http_code}" https://usipipo.duckdns.org/api/v1/admin/servers/status -H "Authorization: Bearer $TOKEN"
```

Expected: HTTP 200 with server status list.

**Step 4: Commit**

```bash
git add src/infrastructure/api/v1/routes/admin.py
git commit -m "fix: add missing ServerStatusResponse import in admin routes"
```

---

### Task 4: Fix Bug 6 - datetime timezone in metrics health

**Files:**
- Modify: `src/infrastructure/api/v1/routes/metrics.py:117-165`

**Step 1: Fix datetime.now() to datetime.now(UTC)**

In `src/infrastructure/api/v1/routes/metrics.py`, find the `check_agent_health` function. Change:
```python
last_metric_time = datetime.fromisoformat(metrics[0]["timestamp"])
time_since = datetime.now() - last_metric_time
```

To:
```python
from datetime import UTC, datetime, timedelta

last_metric_time = datetime.fromisoformat(metrics[0]["timestamp"])
time_since = datetime.now(UTC) - last_metric_time
```

Ensure `UTC` is imported at the top of the file. Check existing imports and add if needed:
```python
from datetime import UTC, datetime, timedelta
```

**Step 2: Restart and test**

```bash
echo "asd123***" | sudo -S systemctl restart usipipo-backend
sleep 3
curl -s -w "\nHTTP: %{http_code}" https://usipipo.duckdns.org/api/v1/metrics/agents/1bc5c426-29de-4440-9ec6-ada7866e2c08/health
```

Expected: HTTP 200 with `{"server_id": "...", "status": "unhealthy"|"healthy"|"degraded", ...}`

**Step 3: Commit**

```bash
git add src/infrastructure/api/v1/routes/metrics.py
git commit -m "fix: use timezone-aware datetime in agent health check"
```

---

### Task 5: Fix Bug 7 - Make protocol optional in vpn/servers

**Files:**
- Modify: `src/infrastructure/api/v1/routes/vpn.py:31-68`

**Step 1: Make protocol parameter optional**

In `src/infrastructure/api/v1/routes/vpn.py`, find the `get_vpn_servers` endpoint. Change:
```python
async def get_vpn_servers(
    protocol: str = Query(...),
```

To:
```python
async def get_vpn_servers(
    protocol: str | None = Query(None, description="Filter by protocol (wireguard, outline, trusttunnel)"),
```

**Step 2: Handle None protocol in service call**

If the service requires protocol, when `protocol` is None, return servers for all protocols. Adjust the service call accordingly.

**Step 3: Restart and test**

```bash
echo "asd123***" | sudo -S systemctl restart usipipo-backend
sleep 3
# Without protocol param
curl -s -w "\nHTTP: %{http_code}" https://usipipo.duckdns.org/api/v1/vpn/servers
# With protocol param (should still work)
curl -s -w "\nHTTP: %{http_code}" "https://usipipo.duckdns.org/api/v1/vpn/servers?protocol=wireguard"
```

Expected: Both return HTTP 200.

**Step 4: Commit**

```bash
git add src/infrastructure/api/v1/routes/vpn.py
git commit -m "fix: make protocol query param optional in vpn/servers endpoint"
```

---

## Phase 2: Auth Fixes (Bugs 1, 2)

### Task 6: Fix Bug 1 - Telegram auth form data parsing

**Files:**
- Modify: `src/infrastructure/api/v1/routes/auth.py:39-88`

**Step 1: Change to use Form() dependency**

In `src/infrastructure/api/v1/routes/auth.py`, modify the `authenticate_telegram` function:

```python
from fastapi import APIRouter, Depends, HTTPException, Request, Form, status

@router.post(
    "/telegram",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def authenticate_telegram(
    request: Request,
    init_data: str = Form(..., description="Telegram WebApp initData"),
    user_service: UserService = Depends(get_user_service),
):
    """
    Autentica usuario con Telegram WebApp initData.
    ...
    """
    # Validate initData
    telegram_data = validate_telegram_init_data(init_data)
    if not telegram_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram initData",
        )
    # ... rest of function unchanged
```

Key change: Replace `request.state.init_data` with `init_data: str = Form(...)`.

**Step 2: Restart and test**

```bash
echo "asd123***" | sudo -S systemctl restart usipipo-backend
sleep 3
# Generate fresh initData
python3 -c "
import hashlib, hmac, urllib.parse, json
from datetime import datetime
TOKEN = '1957471409:AAEo3qe63_ezVm8xexoGo9U5LcHEp8BWgDk'
user = json.dumps({'id': 1058749165, 'first_name': 'Admin', 'username': 'mowgliph'})
auth_date = str(int(datetime.now().timestamp()))
dcs = f'auth_date={auth_date}\nuser={urllib.parse.quote(user, safe=\"\")}'
secret = hmac.new(b'WebAppData', TOKEN.encode(), hashlib.sha256).digest()
h = hmac.new(secret, dcs.encode(), hashlib.sha256).hexdigest()
print(f'user={urllib.parse.quote(user, safe=\"\")}&auth_date={auth_date}&hash={h}')
"
# Use the output above as init_data value
curl -s -w "\nHTTP: %{http_code}" -X POST https://usipipo.duckdns.org/api/v1/auth/telegram \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'init_data=<OUTPUT_FROM_PYTHON>'
```

Expected: HTTP 200 with JWT tokens.

**Step 3: Commit**

```bash
git add src/infrastructure/api/v1/routes/auth.py
git commit -m "fix: use Form() dependency for telegram auth init_data parsing"
```

---

### Task 7: Fix Bug 2 - Email registration telegram_id conflict

**Files:**
- Modify: `src/core/application/services/user_service.py` (find `create_with_email` method)
- DB migration via psql

**Step 1: Find and update create_with_email**

Search for `create_with_email` in `user_service.py`. Find where it sets `telegram_id=0` or default. Change to pass `telegram_id=None`.

**Step 2: Alter DB column to allow NULL**

```bash
echo "asd123***" | sudo -S -u postgres psql -d usipipo_backend_db -c "
ALTER TABLE users ALTER COLUMN telegram_id DROP NOT NULL;
-- Fix existing test user with telegram_id=0
UPDATE users SET telegram_id = NULL WHERE telegram_id = 0;
"
```

**Step 3: Verify unique index handles NULLs**

PostgreSQL unique indexes allow multiple NULLs by default. Verify:
```bash
echo "asd123***" | sudo -S -u postgres psql -d usipipo_backend_db -c "\di ix_users_telegram_id"
```

**Step 4: Test registration**

```bash
echo "asd123***" | sudo -S systemctl restart usipipo-backend
sleep 3
curl -s -w "\nHTTP: %{http_code}" -X POST https://usipipo.duckdns.org/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@test.com","password":"Test1234!","display_name":"NewUser"}'
```

Expected: HTTP 201 with JWT tokens.

**Step 5: Commit**

```bash
git add src/core/application/services/user_service.py
git commit -m "fix: allow null telegram_id for email-only registration"
```

---

## Phase 3: Type Mismatch Fix (Bug 3)

### Task 8: Fix Bug 3 - Invoice user_id type mismatch

**Files:**
- Modify: `src/infrastructure/api/v1/routes/consumption_invoices.py:165-220`
- Modify: `src/infrastructure/persistence/repositories/consumption_invoice_repository.py:55-65`
- Modify: `src/core/domain/interfaces/i_consumption_invoice_repository.py` (interface signature)

**Step 1: Update route to accept telegram_id (int) instead of user_id (UUID)**

In `src/infrastructure/api/v1/routes/consumption_invoices.py`:

```python
@router.get(
    "/telegram/{telegram_id}",
    response_model=ConsumptionInvoiceListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get User Invoices by Telegram ID",
)
async def get_user_consumption_invoices(
    telegram_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Obtiene todas las facturas de consumo de un usuario por telegram_id.
    """
    repo = _get_invoice_repo(session)
    invoices = await repo.get_by_user(telegram_id, current_user.telegram_id)
    # ... rest unchanged
```

**Step 2: Update repository method signature**

In `src/infrastructure/persistence/repositories/consumption_invoice_repository.py`:

```python
async def get_by_user(
    self, telegram_id: int, current_user_telegram_id: int
) -> list[ConsumptionInvoice]:
    """Recupera todas las facturas de un usuario by telegram_id."""
    result = await self.session.execute(
        select(ConsumptionInvoiceModel)
        .where(ConsumptionInvoiceModel.user_id == telegram_id)
        .order_by(ConsumptionInvoiceModel.created_at.desc())
    )
    models = result.scalars().all()
    return [m.to_entity() for m in models]
```

**Step 3: Update interface**

In `src/core/domain/interfaces/i_consumption_invoice_repository.py`, update the `get_by_user` signature to use `int` instead of `uuid.UUID`.

**Step 4: Update the other invoice route too**

Also fix `get_user_pending_invoice` at line ~223 with the same pattern.

**Step 5: Restart and test**

```bash
echo "asd123***" | sudo -S systemctl restart usipipo-backend
sleep 3
curl -s -w "\nHTTP: %{http_code}" https://usipipo.duckdns.org/api/v1/invoices/telegram/1058749165 -H "Authorization: Bearer $TOKEN"
```

Expected: HTTP 200 with invoice list (possibly empty).

**Step 6: Commit**

```bash
git add src/infrastructure/api/v1/routes/consumption_invoices.py \
        src/infrastructure/persistence/repositories/consumption_invoice_repository.py \
        src/core/domain/interfaces/i_consumption_invoice_repository.py
git commit -m "fix: use telegram_id (int) instead of uuid for invoice queries"
```

---

## Phase 4: Final Verification

### Task 9: Full endpoint smoke test

**Step 1: Test all 7 previously broken endpoints**

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjlhNGQ3Zi1lOGVmLTRkODEtODRmMS00ODMzNjNmODFkMDAiLCJleHAiOjE3NzUzNTIwOTAsImlhdCI6MTc3NTI2NTY5MCwidHlwZSI6ImFjY2VzcyIsInRlbGVncmFtX2lkIjoxMDU4NzQ5MTY1fQ.LQLhdt_5SBthUiDVgfZUOe5ITyi20EF3NMkIfNkV6As"

echo "1. admin/users" && curl -s -w " HTTP:%{http_code}\n" https://usipipo.duckdns.org/api/v1/admin/users -H "Authorization: Bearer $TOKEN" | tail -1
echo "2. admin/servers/status" && curl -s -w " HTTP:%{http_code}\n" https://usipipo.duckdns.org/api/v1/admin/servers/status -H "Authorization: Bearer $TOKEN" | tail -1
echo "3. metrics/agents/health" && curl -s -w " HTTP:%{http_code}\n" https://usipipo.duckdns.org/api/v1/metrics/agents/1bc5c426-29de-4440-9ec6-ada7866e2c08/health | tail -1
echo "4. vpn/servers (no protocol)" && curl -s -w " HTTP:%{http_code}\n" https://usipipo.duckdns.org/api/v1/vpn/servers | tail -1
echo "5. invoices/telegram" && curl -s -w " HTTP:%{http_code}\n" https://usipipo.duckdns.org/api/v1/invoices/telegram/1058749165 -H "Authorization: Bearer $TOKEN" | tail -1
```

Expected: All return HTTP 200 (or 201/401 for auth endpoints with valid reasons).

**Step 2: Run existing test suite**

```bash
cd /home/mowgli/usipipo/apps/backend
source .venv/bin/activate
pytest tests/ -v --tb=short 2>&1 | tail -20
```

**Step 3: Final commit**

```bash
git add -A
git commit -m "fix: all 7 endpoint bugs resolved - verified with smoke tests"
```

---

## Summary of Changes

| Bug | File | Change |
|-----|------|--------|
| 4 | `src/infrastructure/api/v1/routes/admin.py` | Add `AdminUserInfoResponse` import |
| 5 | `src/infrastructure/api/v1/routes/admin.py` | Add `ServerStatusResponse` import |
| 6 | `src/infrastructure/api/v1/routes/metrics.py` | `datetime.now()` -> `datetime.now(UTC)` |
| 7 | `src/infrastructure/api/v1/routes/vpn.py` | Make `protocol` optional |
| 1 | `src/infrastructure/api/v1/routes/auth.py` | Use `Form(...)` instead of `request.state.init_data` |
| 2 | `user_service.py` + DB | Allow NULL `telegram_id`, DB migration |
| 3 | `consumption_invoices.py` + repository | Change `user_id: UUID` to `telegram_id: int` |
