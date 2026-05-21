# Fix 401 Errors in Payments/Subscription Handlers Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Fix intermittent 401 "Invalid token" errors on `/payments/history` and `/subscriptions/me` endpoints by replacing Redis singleton with per-call connections in backend and adding retry logic in bot.

**Architecture:** Two-layer defense: (1) Backend JWT module uses per-call Redis connections instead of global singleton, (2) Bot APIClient wraps all requests with exponential backoff retry and token re-registration fallback.

**Tech Stack:** Python, FastAPI, redis.asyncio, httpx, python-telegram-bot, JWT

---

## Phase 1: Backend - Fix Redis Singleton in JWT Module

### Task 1: Remove Redis Singleton from jwt.py

**Files:**
- Modify: `/home/mowgli/usipipo/apps/backend/src/shared/security/jwt.py`
- Test: Run existing backend tests

**Step 1: Understand current structure**

Read `src/shared/security/jwt.py`. The problematic code is:
- Lines 12-14: Global singleton variables `_redis_pool`, `_redis_client`
- Lines 17-34: `_get_redis_client()` function with global state
- Lines 37-47: `revoke_token()` uses singleton
- Lines 50-60: `is_token_revoked()` uses singleton
- Lines 63-70: `close_redis_pool()` cleanup function

**Step 2: Replace singleton with per-call connections**

Replace the entire top section of `jwt.py` (from imports through `is_token_revoked`) with:

```python
"""Seguridad JWT para autenticación."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
import redis.asyncio as redis

from ...shared.config import settings


async def revoke_token(token: str, expires_in_seconds: int) -> None:
    """
    Añade token a blacklist en Redis.

    Crea una conexión nueva por llamada (seguro para multi-worker).

    Args:
        token: JWT token a revocar
        expires_in_seconds: Tiempo de expiración en segundos
    """
    async with redis.Redis.from_url(
        settings.REDIS_URL,
        max_connections=5,
        socket_timeout=5,
        decode_responses=True,
    ) as r:
        await r.setex(f"revoked_token:{token[:32]}", expires_in_seconds, "1")


async def is_token_revoked(token: str) -> bool:
    """
    Verifica si el token fue revocado.

    Crea una conexión nueva por llamada (seguro para multi-worker).

    Args:
        token: JWT token a verificar

    Returns:
        bool: True si fue revocado, False si no
    """
    async with redis.Redis.from_url(
        settings.REDIS_URL,
        max_connections=5,
        socket_timeout=5,
        decode_responses=True,
    ) as r:
        return await r.exists(f"revoked_token:{token[:32]}") > 0
```

**Key changes:**
- Remove: `from redis.asyncio import ConnectionPool, Redis` (no longer needed)
- Remove: `_redis_pool`, `_redis_client`, `_get_redis_client()`
- Remove: `close_redis_pool()`
- Each function creates its own connection via `async with redis.Redis.from_url(...)`

**Step 3: Remove close_redis_pool from lifespan**

In `src/main.py`, remove:
```python
from .shared.security.jwt import close_redis_pool
```

And in the lifespan function, remove:
```python
    await close_redis_pool()
    logger.info("Redis connection pool closed")
```

Change to just:
```python
    # Shutdown
    await close_db()
    logger.info("Application shutdown complete")
```

**Step 4: Run backend tests**

```bash
cd /home/mowgli/usipipo/apps/backend
uv run pytest tests/ -v --tb=short 2>&1 | tail -30
```

Expected: All tests pass (same as before, since JWT logic is internal)

**Step 5: Restart backend service**

```bash
echo "asd123***" | sudo -S systemctl restart usipipo-backend.service
echo "asd123***" | sudo -S systemctl status usipipo-backend.service --no-pager | head -15
```

Expected: Service starts successfully with 2 workers

**Step 6: Commit**

```bash
cd /home/mowgli/usipipo/apps/backend
git add src/shared/security/jwt.py src/main.py
git commit -m "fix: replace Redis singleton with per-call connections in JWT module

- Remove global _redis_pool and _redis_client singletons
- Each revoke_token/is_token_revoked call creates fresh connection
- Fixes 401 errors caused by shared state across uvicorn workers
- Remove close_redis_pool() from lifespan shutdown"
```

---

## Phase 2: Bot - Add Retry Logic to APIClient

### Task 2: Add Retry Wrapper to APIClient

**Files:**
- Modify: `/home/mowgli/usipipo/apps/bot/src/infrastructure/api_client.py`
- Test: `/home/mowgli/usipipo/apps/bot/test_all_handlers.py`

**Step 1: Add retry constants and wrapper method**

Add to the `APIClient` class (after `__init__`):

```python
    # Retry configuration for transient failures
    MAX_RETRIES = 2
    RETRY_DELAY = 0.5  # seconds

    async def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Execute HTTP request with retry on 401 and network errors.

        Uses exponential backoff: 0.5s, 1.0s between retries.
        """
        import asyncio

        last_response: httpx.Response | None = None

        for attempt in range(self.MAX_RETRIES + 1):
            try:
                client = await self._get_client()
                response = await client.request(method, endpoint, **kwargs)
                last_response = response

                # If 401 and we have retries left, wait and retry
                if response.status_code == 401 and attempt < self.MAX_RETRIES:
                    delay = self.RETRY_DELAY * (2**attempt)  # 0.5s, 1.0s
                    logger.warning(
                        f"401 on attempt {attempt + 1}, retrying in {delay}s: {method} {endpoint}"
                    )
                    await asyncio.sleep(delay)
                    continue

                return response
            except httpx.RequestError as e:
                if attempt < self.MAX_RETRIES:
                    delay = self.RETRY_DELAY * (2**attempt)
                    logger.warning(f"Request error, retrying in {delay}s: {e}")
                    import asyncio
                    await asyncio.sleep(delay)
                    continue
                raise

        # All retries exhausted, return last response
        if last_response is None:
            raise RuntimeError("Request failed without response")
        return last_response
```

**Step 2: Update get() method to use retry wrapper**

Replace the `get()` method:

```python
    async def get(
        self, endpoint: str, params: Optional[dict] = None, headers: Optional[dict] = None
    ) -> dict[str, Any]:
        """Realiza una petición GET al backend con retry logic."""
        response = await self._request_with_retry(
            "GET",
            endpoint,
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()
```

**Step 3: Update post() method to use retry wrapper**

Replace the `post()` method:

```python
    async def post(
        self, endpoint: str, data: Optional[dict] = None, headers: Optional[dict] = None
    ) -> dict[str, Any]:
        """Realiza una petición POST al backend con retry logic."""
        response = await self._request_with_retry(
            "POST",
            endpoint,
            json=data,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()
```

**Step 4: Update delete() method to use retry wrapper**

Replace the `delete()` method:

```python
    async def delete(self, endpoint: str, headers: Optional[dict] = None) -> dict[str, Any]:
        """
        Realiza una petición DELETE al backend con retry logic.

        Args:
            endpoint: Endpoint de la API (sin base_url)
            headers: Headers opcionales (ej: Authorization)

        Returns:
            dict: {"success": True} si la operación fue exitosa
        """
        response = await self._request_with_retry(
            "DELETE",
            endpoint,
            headers=headers,
        )
        response.raise_for_status()
        return {"success": True}
```

**Step 5: Update put() method to use retry wrapper**

Replace the `put()` method:

```python
    async def put(
        self, endpoint: str, data: Optional[dict] = None, headers: Optional[dict] = None
    ) -> dict[str, Any]:
        """Realiza una petición PUT al backend con retry logic."""
        response = await self._request_with_retry(
            "PUT",
            endpoint,
            json=data,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()
```

**Step 6: Verify imports**

Ensure the top of `api_client.py` has:
```python
import os
from typing import Any, Optional

import httpx
```

No new imports needed (asyncio is used inline).

**Step 7: Commit**

```bash
cd /home/mowgli/usipipo/apps/bot
git add src/infrastructure/api_client.py
git commit -m "feat: add retry logic with exponential backoff to APIClient

- Add _request_with_retry() method (3 attempts, 0.5s/1.0s backoff)
- Wrap all HTTP methods (GET, POST, PUT, DELETE) with retry
- Handles transient 401 errors from backend Redis race conditions
- Logs warnings on retry for debugging"
```

---

## Phase 3: Bot - Add Token Re-registration Fallback

### Task 3: Add Token Refresh to TokenStorage

**Files:**
- Modify: `/home/mowgli/usipipo/apps/bot/src/infrastructure/token_storage.py`

**Step 1: Add refresh_token method**

Add to the end of `TokenStorage` class:

```python
    async def refresh_token(
        self,
        telegram_id: int,
        api_client: Any,  # APIClient (avoid circular import)
    ) -> Optional[str]:
        """
        Re-registra usuario para obtener token fresco.

        Usado como fallback cuando los retries agotan y el token sigue inválido.

        Args:
            telegram_id: ID de Telegram del usuario
            api_client: Instancia de APIClient

        Returns:
            Optional[str]: Nuevo access_token o None si falló
        """
        try:
            response = await api_client.post(
                "/auth/telegram/auto-register",
                {"telegram_id": telegram_id},
            )
            if "access_token" in response:
                await self.store(telegram_id, response)
                logger.info(f"Token refreshed for user {telegram_id}")
                return response["access_token"]
        except Exception as e:
            logger.error(f"Failed to refresh token for user {telegram_id}: {e}")
        return None
```

**Step 2: Add import for logger**

At the top of the file, add:
```python
from src.infrastructure.logger import get_logger

logger = get_logger("token_storage")
```

**Step 3: Commit**

```bash
cd /home/mowgli/usipipo/apps/bot
git add src/infrastructure/token_storage.py
git commit -m "feat: add token refresh fallback to TokenStorage

- Add refresh_token() method that re-registers user via auto-register
- Used as last resort when retries exhaust on 401 errors
- Logs success/failure for debugging"
```

---

## Phase 4: Integration Testing

### Task 4: Run Full Handler Test Suite

**Files:**
- Run: `/home/mowgli/usipipo/apps/bot/test_all_handlers.py`

**Step 1: Restart both services**

```bash
echo "asd123***" | sudo -S systemctl restart usipipo-backend.service
echo "asd123***" | sudo -S systemctl restart usipipo-telegram-bot.service
sleep 3
```

**Step 2: Run handler tests**

```bash
cd /home/mowgli/usipipo/apps/bot
.venv/bin/python test_all_handlers.py 2>&1
```

**Expected output:**
```
TOTAL RESULTS:
  Tests Run: 16
  Passed: 16
  Failed: 0
  Success Rate: 100.0%
✅ ALL HANDLER TESTS PASSED
```

**Step 3: Run original integration tests**

```bash
cd /home/mowgli/usipipo/apps/bot
.venv/bin/python test_bot_backend_integration.py 2>&1
```

**Expected output:**
```
✅ ALL TESTS PASSED
```

**Step 4: Check bot logs for errors**

```bash
echo "asd123***" | sudo -S journalctl -u usipipo-telegram-bot.service --since "5 minutes ago" --no-pager -n 30
```

Expected: No 401 errors, no retry warnings (all requests succeed on first attempt now)

**Step 5: Check backend logs**

```bash
echo "asd123***" | sudo -S journalctl -u usipipo-backend.service --since "5 minutes ago" --no-pager -n 30
```

Expected: Normal operation, no JWT decode errors

---

## Phase 5: Run Full Test Suites and Commit

### Task 5: Backend Tests

**Step 1: Run full backend test suite**

```bash
cd /home/mowgli/usipipo/apps/backend
uv run pytest tests/ -v --tb=short 2>&1 | tail -40
```

Expected: All tests pass

### Task 6: Bot Tests

**Step 1: Run bot linting**

```bash
cd /home/mowgli/usipipo/apps/bot
.venv/bin/python -m ruff check src/ 2>&1
.venv/bin/python -m ruff format --check src/ 2>&1
```

### Task 7: Final Commit

**Step 1: Tag the fix**

```bash
cd /home/mowgli/usipipo/apps/backend
git add -A
git commit -m "chore: final changes for 401 fix"

cd /home/mowgli/usipipo/apps/bot
git add -A
git commit -m "chore: final changes for 401 fix"
```

---

## Summary of Changes

| File | Change | Repo |
|------|--------|------|
| `src/shared/security/jwt.py` | Remove Redis singleton, use per-call connections | backend |
| `src/main.py` | Remove `close_redis_pool()` from lifespan | backend |
| `src/infrastructure/api_client.py` | Add `_request_with_retry()` wrapper | bot |
| `src/infrastructure/token_storage.py` | Add `refresh_token()` fallback | bot |

## Success Criteria

- [ ] `test_all_handlers.py` passes 16/16 (was 14/16)
- [ ] `/payments/history` returns 200 consistently
- [ ] `/subscriptions/me` returns 200 consistently
- [ ] No 401 errors in bot logs
- [ ] Backend tests still pass
- [ ] Bot service runs without errors
