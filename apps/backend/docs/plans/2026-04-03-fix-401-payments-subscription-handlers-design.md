# Design: Fix 401 Errors in Payments/Subscription Handlers

**Date:** 2026-04-03
**Author:** Brainstorming Session
**Status:** Approved

---

## Problem

Endpoints `/api/v1/payments/history` and `/api/v1/subscriptions/me` return intermittent 401 "Invalid token" errors when called from the Telegram bot, despite using valid JWT tokens that work on other endpoints like `/users/me`.

### Observed Behavior

| Endpoint | Isolated Test | Full Test Suite |
|----------|--------------|-----------------|
| `/payments/history` | 200 OK | 401 "Invalid token" |
| `/subscriptions/me` | 200 OK | 401 "Invalid token" |
| `/users/me` | 200 OK | 200 OK |

### Root Cause

The backend runs with **2 uvicorn workers** (`--workers 2`). The JWT module uses a **global singleton** for Redis connection:

```python
_redis_pool: ConnectionPool | None = None
_redis_client: Redis | None = None
```

When uvicorn forks workers, each worker inherits a copy of this global state, causing:
1. Shared Redis connections across processes (unsafe)
2. Inconsistent revocation state between workers
3. Race conditions in `is_token_revoked()`

---

## Solution: Two-Layer Defense

### Layer 1: Backend - Fix Redis Per-Worker

Replace the global singleton with per-call Redis connections using async context managers.

**File:** `src/shared/security/jwt.py`

**Before:**
```python
_redis_pool: ConnectionPool | None = None
_redis_client: Redis | None = None

def _get_redis_client() -> Redis:
    global _redis_client, _redis_pool
    if _redis_client is None:
        _redis_pool = redis.ConnectionPool.from_url(...)
        _redis_client = redis.Redis(connection_pool=_redis_pool)
    return _redis_client

async def is_token_revoked(token: str) -> bool:
    r = _get_redis_client()
    return await r.exists(f"revoked_token:{token[:32]}") > 0
```

**After:**
```python
# No global singletons

async def revoke_token(token: str, expires_in_seconds: int) -> None:
    """Add token to Redis blacklist. Creates fresh connection per call."""
    async with redis.Redis.from_url(
        settings.REDIS_URL,
        max_connections=5,
        socket_timeout=5,
        decode_responses=True,
    ) as r:
        await r.setex(f"revoked_token:{token[:32]}", expires_in_seconds, "1")

async def is_token_revoked(token: str) -> bool:
    """Check if token is revoked. Creates fresh connection per call."""
    async with redis.Redis.from_url(
        settings.REDIS_URL,
        max_connections=5,
        socket_timeout=5,
        decode_responses=True,
    ) as r:
        return await r.exists(f"revoked_token:{token[:32]}") > 0
```

**Remove:** `_redis_pool`, `_redis_client`, `_get_redis_client()`, `close_redis_pool()`

**Trade-off:** Slightly more connection overhead per request, but:
- Connection pooling still works (pool is per-call, managed by redis-py)
- Safe for multi-worker deployments
- No state sharing between processes

---

### Layer 2: Bot - Retry with Exponential Backoff

Add retry logic to `APIClient` for transient 401 errors.

**File:** `src/infrastructure/api_client.py`

**New method:**
```python
class APIClient:
    MAX_RETRIES = 2
    RETRY_DELAY = 0.5  # seconds

    async def _request_with_retry(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Execute request with retry on 401 and network errors."""
        last_error: Exception | None = None

        for attempt in range(self.MAX_RETRIES + 1):
            try:
                response = await self._client.request(method, url, **kwargs)

                # If 401 and we have retries left, wait and retry
                if response.status_code == 401 and attempt < self.MAX_RETRIES:
                    delay = self.RETRY_DELAY * (2 ** attempt)  # 0.5s, 1.0s
                    logger.warning(
                        f"401 on attempt {attempt + 1}, retrying in {delay}s: {method} {url}"
                    )
                    await asyncio.sleep(delay)
                    continue

                return response
            except httpx.RequestError as e:
                last_error = e
                if attempt < self.MAX_RETRIES:
                    delay = self.RETRY_DELAY * (2 ** attempt)
                    logger.warning(f"Request error, retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                    continue
                raise

        # Should not reach here, but just in case
        if last_error:
            raise last_error
        return response  # type: ignore[possibly-undefined]
```

**Retry schedule:**
- Attempt 1: immediate
- Attempt 2: wait 0.5s
- Attempt 3: wait 1.0s
- If all fail: return last 401 to caller

---

### Layer 3: Bot - Token Re-registration Fallback

If retries exhaust and still 401, re-register the user to get a fresh token.

**File:** `src/infrastructure/token_storage.py`

**New method:**
```python
async def refresh_token(self, telegram_id: int, api_client: "APIClient") -> str | None:
    """Re-register user to get fresh token if current token is invalid."""
    try:
        response = await api_client.post(
            "/auth/telegram/auto-register",
            {"telegram_id": telegram_id},
        )
        if "access_token" in response:
            await self.store(telegram_id, response)
            return response["access_token"]
    except Exception as e:
        logger.error(f"Failed to refresh token for user {telegram_id}: {e}")
    return None
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Telegram Bot                         │
│  ┌──────────────┐    ┌──────────────────────────────────┐   │
│  │  Handler     │───>│  APIClient with Retry Wrapper    │   │
│  │  (payments)  │    │  - 3 attempts, exp backoff       │   │
│  └──────────────┘    │  - 0.5s, 1.0s delays             │   │
│                      │  - Falls back to re-register     │   │
│                      └──────────────┬───────────────────┘   │
└─────────────────────────────────────┼───────────────────────┘
                                      │ HTTPS
                                      ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend (2 workers)                     │
│  ┌─────────────────────┐  ┌─────────────────────────────┐   │
│  │  Worker 1           │  │  Worker 2                   │   │
│  │  ┌───────────────┐  │  │  ┌───────────────┐          │   │
│  │  │get_current_   │  │  │  │get_current_   │          │   │
│  │  │user()         │  │  │  │user()         │          │   │
│  │  └───────┬───────┘  │  │  └───────┬───────┘          │   │
│  │          │          │  │          │                   │   │
│  │  ┌───────▼───────┐  │  │  ┌───────▼───────┐          │   │
│  │  │is_token_      │  │  │  │is_token_      │          │   │
│  │  │revoked()      │  │  │  │revoked()      │          │   │
│  │  └───────┬───────┘  │  │  └───────┬───────┘          │   │
│  │          │          │  │          │                   │   │
│  │  ┌───────▼───────┐  │  │  ┌───────▼───────┐          │   │
│  │  │Redis conn NEW │  │  │  │Redis conn NEW │          │   │
│  │  │(per-call)     │  │  │  │(per-call)     │          │   │
│  │  └───────────────┘  │  │  └───────────────┘          │   │
│  └─────────────────────┘  └─────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│              ┌───────────────────────┐                       │
│              │   Redis (shared)      │                       │
│              │   revoked_token:*     │                       │
│              └───────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Error Handling Matrix

| Scenario | Backend Behavior | Bot Behavior | User Experience |
|----------|-----------------|--------------|-----------------|
| Valid token | 200 OK | - | Success |
| Redis timeout | Skip revocation check, continue | - | Success (with warning log) |
| Transient 401 | - | Retry x3 with backoff | Success (slight delay) |
| Persistent 401 | - | Re-register user | Success (new token) |
| Backend down | - | RequestError -> user message | Graceful error |

---

## Files to Modify

### Backend (`usipipo-backend`)
1. `src/shared/security/jwt.py` - Remove singleton, use per-call Redis connections
2. Remove `close_redis_pool()` calls from shutdown handlers

### Bot (`usipipo-telegram-bot`)
1. `src/infrastructure/api_client.py` - Add `_request_with_retry()` method
2. `src/infrastructure/token_storage.py` - Add `refresh_token()` method
3. Update `get()`, `post()`, `put()`, `delete()` methods to use retry wrapper

---

## Testing Plan

### Backend Tests
1. **Unit:** `is_token_revoked()` creates new connection each call
2. **Unit:** `revoke_token()` works with fresh connection
3. **Integration:** Two workers can both check token revocation independently

### Bot Tests
1. **Unit:** Retry logic - mock 401 then 200, verify retry happens
2. **Unit:** Retry logic - mock 3 consecutive 401s, verify re-registration
3. **Integration:** Run `test_all_handlers.py` - expect 16/16 pass

---

## Rollback Plan

If issues arise:
1. Revert `jwt.py` to previous version (restore singleton)
2. Restart backend: `sudo systemctl restart usipipo-backend.service`
3. Revert bot changes and redeploy

---

## Success Criteria

- [ ] `test_all_handlers.py` passes 16/16 tests (currently 14/16)
- [ ] `/payments/history` returns 200 consistently
- [ ] `/subscriptions/me` returns 200 consistently
- [ ] No 401 errors in bot logs during normal operation
- [ ] Backend handles 2+ workers without token issues
