# asyncpg → psycopg2 Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Migrate the uSipipo Backend from asyncpg (async) to psycopg2 (sync) PostgreSQL driver.

**Architecture:** Replace all async SQLAlchemy code with sync equivalents. Remove `async/await` from database layer, repositories, services, routes, and interfaces. Change `AsyncSession` to `Session` and `create_async_engine` to `create_engine`. Update .env URL format (remove `+asyncpg`). Configure SSL via `connect_args`.

**Tech Stack:** Python 3.13, psycopg2, SQLAlchemy 2.0, FastAPI

**Order:** Dependencies → database.py → interfaces → repos → services → deps.py → routes → main.py → .env

---

### Task 1: Update Dependencies in pyproject.toml

**Files:**
- Modify: `pyproject.toml:9-30`

**Step 1: Remove asyncpg and psycopg2-binary, keep psycopg2**

Change the dependencies block from:
```toml
dependencies = [
    "usipipo-commons @ file:///home/mowgli/usipipo/common",
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic-settings>=2.0.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.29.0",
    "alembic>=1.13.0",
    "pyjwt>=2.8.0",
    "aiosqlite>=0.20.0",
    "httpx>=0.27.0",
    "psycopg2-binary>=2.9.11",
    "slowapi>=0.1.9",
    "redis>=5.0.0",
    ...
    "psycopg2>=2.9.12",
    ...
]
```

To:
```toml
dependencies = [
    "usipipo-commons @ file:///home/mowgli/usipipo/common",
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic-settings>=2.0.0",
    "sqlalchemy>=2.0.0",
    "alembic>=1.13.0",
    "pyjwt>=2.8.0",
    "aiosqlite>=0.20.0",
    "httpx>=0.27.0",
    "slowapi>=0.1.9",
    "redis>=5.0.0",
    ...
    "psycopg2>=2.9.12",
    ...
]
```

Changes:
- Remove `"asyncpg>=0.29.0"`
- Remove `"psycopg2-binary>=2.9.11"`
- Change `"sqlalchemy[asyncio]>=2.0.0"` to `"sqlalchemy>=2.0.0"`

**Step 2: Sync dependencies**

Run: `uv sync`
Expected: asyncpg removed, psycopg2 retained.

**Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: remove asyncpg, use sqlalchemy sync + psycopg2"
```

---

### Task 2: Rewrite database.py to Sync

**Files:**
- Modify: `src/infrastructure/persistence/database.py`

**Step 1: Replace entire file content**

Replace the async SQLAlchemy code with sync:

```python
"""Configuración de base de datos SQLAlchemy (sync)."""

import logging
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Result
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase

from src.shared.config import settings

logger = logging.getLogger(__name__)


def get_execute_rowcount(result: Result) -> int:
    return getattr(result, "rowcount", 0) or 0


class Base(DeclarativeBase):
    pass


# Crear engine síncrono con soporte SSL para Supabase
connect_args = {}
if "supabase.co" in settings.DATABASE_URL:
    connect_args["sslmode"] = "require"

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.is_development and settings.DB_ECHO,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=10,
    pool_timeout=settings.DB_TIMEOUT,
    connect_args=connect_args,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obtener sesión de base de datos (sync).

    Yields:
        Session: Sesión síncrona de SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Verifica conexión a BD al arrancar."""
    with engine.begin() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("Database connection verified")


def close_db() -> None:
    """Cierra la conexión a la base de datos."""
    engine.dispose()
```

**Step 2: Verify file compiles**

Run: `uv run python -c "from src.infrastructure.persistence.database import engine, SessionLocal, get_db" 2>&1`
Expected: No errors, no async-related warnings.

**Step 3: Commit**

```bash
git add src/infrastructure/persistence/database.py
git commit -m "refactor: migrate database.py from asyncpg to psycopg2 sync"
```

---

### Task 3: Update migrations/env.py for SSL

**Files:**
- Modify: `migrations/env.py`

**Step 1: Add SSL support for Alembic connections**

In `run_migrations_online()`, add SSL config for Supabase:

```python
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    cfg = config.get_section(config.config_ini_section, {})
    
    # Add SSL for Supabase connections
    if "supabase.co" in sync_url:
        cfg["sqlalchemy.connect_args"] = '{"sslmode": "require"}'
    
    connectable = engine_from_config(
        cfg,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()
```

Also ensure `get_sync_url` properly converts the URL:
```python
def get_sync_url(async_url: str) -> str:
    """Convert asyncpg URL to psycopg2 sync URL for Alembic."""
    return async_url.replace("+asyncpg", "")
```

**Step 2: Verify migrations still parse**

Run: `uv run alembic history`
Expected: Shows migration history (may warn about missing revisions, but should not error).

**Step 3: Commit**

```bash
git add migrations/env.py
git commit -m "refactor: add SSL support to alembic env for Supabase"
```

---

### Task 4: Convert Interfaces/Ports to Sync

**Files:**
- Modify: `src/core/domain/interfaces/*.py`
- Modify: `src/core/ports/*.py`

**Step 1: Find all interface files**

Run: `find src/core -name "*.py" -exec grep -l "async def" {} \;`

**Step 2: For each file, remove `async` from method signatures**

Example from `IUserRepository`:
```diff
-class IUserRepository(ABC):
-    @abstractmethod
-    async def get_by_id(self, user_id: UUID) -> User | None: ...
-
-    @abstractmethod
-    async def get_all(self) -> list[User]: ...
+class IUserRepository(ABC):
+    @abstractmethod
+    def get_by_id(self, user_id: UUID) -> User | None: ...
+
+    @abstractmethod
+    def get_all(self) -> list[User]: ...
```

Apply to ALL interface files. The key transformation is removing `async` before `def`.

**Step 3: Commit**

```bash
git add src/core/domain/interfaces/ src/core/ports/
git commit -m "refactor: remove async from interface/port definitions"
```

---

### Task 5: Convert Repositories to Sync (20 files)

**Files:**
- Modify: ALL files in `src/infrastructure/persistence/repositories/*.py`

**Step 1: For each repository file, perform these changes:**

1. **Import:** Change `from sqlalchemy.ext.asyncio import AsyncSession` → remove import
2. **Init:** `session: AsyncSession` → `session: Session` (add `from sqlalchemy.orm import Session`)
3. **Methods:** Remove `async` from every `async def`
4. **Body:** Remove `await` before `self.session.execute()`, `.commit()`, `.refresh()`, `.merge()`, `.delete()`, `.rollback()`

**Example transformations:**

```diff
-from sqlalchemy.ext.asyncio import AsyncSession
+from sqlalchemy.orm import Session

-class UserRepository(IUserRepository):
-    def __init__(self, session: AsyncSession):
+class UserRepository(IUserRepository):
+    def __init__(self, session: Session):
```

```diff
-    async def get_by_id(self, user_id: UUID) -> User | None:
-        result = await self.session.execute(...)
+    def get_by_id(self, user_id: UUID) -> User | None:
+        result = self.session.execute(...)
```

```diff
-    async def create(self, user: User) -> User:
-        model = UserModel.from_entity(user)
-        self.session.add(model)
-        await self.session.commit()
-        await self.session.refresh(model)
+    def create(self, user: User) -> User:
+        model = UserModel.from_entity(user)
+        self.session.add(model)
+        self.session.commit()
+        self.session.refresh(model)
```

**Repositories list (in order):**
1. `user_repository.py`
2. `vpn_repository.py`
3. `vpn_key_repository.py`
4. `payment_repository.py`
5. `subscription_repository.py`
6. `subscription_transaction_repository.py`
7. `consumption_billing_repository.py`
8. `consumption_invoice_repository.py`
9. `data_package_repository.py`
10. `referral_repository.py`
11. `wallet_repository.py`
12. `wallet_pool_repository.py`
13. `crypto_order_repository.py`
14. `crypto_transaction_repository.py`
15. `ticket_repository.py`
16. `device_repository.py`
17. `auth_provider_repository.py`
18. `audit_log_repository.py`
19. `agent_api_key_repository.py`
20. `webhook_token_repository.py`

**Step 2: Verify no async remains in repos**

Run: `grep -rn "async def\|await " src/infrastructure/persistence/repositories/`
Expected: 0 results

**Step 3: Commit**

```bash
git add src/infrastructure/persistence/repositories/
git commit -m "refactor: migrate 20 repositories from async to sync"
```

---

### Task 6: Convert Application Services to Sync (15 files)

**Files:**
- Modify: ALL files in `src/core/application/services/*.py`

**Step 1: For each service file:**

1. Remove `async` from `async def` method signatures
2. Remove `await` from calls to repository methods
3. Remove `async` from class methods that use repos

**Example:**

```diff
- async def get_user_profile(self, user_id: UUID) -> User:
-     return await self.user_repo.get_by_id(user_id)
+ def get_user_profile(self, user_id: UUID) -> User:
+     return self.user_repo.get_by_id(user_id)
```

**Step 2: Verify no async in services**

Run: `grep -rn "async def\|await " src/core/application/services/`
Expected: 0 results (unless there are genuinely async operations not related to DB)

**Step 3: Commit**

```bash
git add src/core/application/services/
git commit -m "refactor: migrate application services from async to sync"
```

---

### Task 7: Convert deps.py to Sync

**Files:**
- Modify: `src/infrastructure/api/v1/deps.py`

**Step 1: Change all AsyncSession to Session, remove async**

```diff
-from sqlalchemy.ext.asyncio import AsyncSession
+from sqlalchemy.orm import Session

-async def get_current_user(
-    credentials: HTTPAuthorizationCredentials = Depends(security),
-    db: AsyncSession = Depends(get_db),
-) -> User:
-    if await is_token_revoked(token):
+def get_current_user(
+    credentials: HTTPAuthorizationCredentials = Depends(security),
+    db: Session = Depends(get_db),
+) -> User:
+    if is_token_revoked(token):
```

Apply to ALL functions in deps.py:
- `get_current_user`
- `require_admin`
- `get_user_service`
- `get_vpn_service`
- `get_subscription_service`
- `get_ticket_service`
- `get_data_package_service`
- `get_referral_service`
- `get_wallet_management_service`
- `get_wallet_pool_service`

**Step 2: Verify deps.py compiles**

Run: `uv run python -c "from src.infrastructure.api.v1.deps import get_current_user" 2>&1`
Expected: No errors

**Step 3: Commit**

```bash
git add src/infrastructure/api/v1/deps.py
git commit -m "refactor: migrate deps.py from async to sync"
```

---

### Task 8: Convert Routes to Sync (22 route files + 2 webhooks)

**Files:**
- Modify: ALL files in `src/infrastructure/api/v1/routes/*.py`
- Modify: `src/infrastructure/api/v1/webhooks/crypto.py`
- Modify: `src/infrastructure/api/v1/webhooks/telegram_stars.py`

**Step 1: For each route file:**

1. Change `async def` → `def` for each endpoint handler
2. Change `AsyncSession` → `Session` in type hints
3. Remove `await` before calls to services/repos
4. Remove `from sqlalchemy.ext.asyncio import AsyncSession`

**Example transformation:**

```diff
- from sqlalchemy.ext.asyncio import AsyncSession
+ from sqlalchemy.orm import Session

- @router.get("/{user_id}")
- async def get_user(
-     user_id: UUID,
-     db: AsyncSession = Depends(get_db),
- ):
-     user = await user_service.get_by_id(user_id)
+ @router.get("/{user_id}")
+ def get_user(
+     user_id: UUID,
+     db: Session = Depends(get_db),
+ ):
+     user = user_service.get_by_id(user_id)
```

**Route files:**
1. `auth.py`
2. `vpn.py`
3. `payments.py`
4. `billing.py`
5. `subscriptions.py`
6. `consumption_invoices.py`
7. `data_packages.py`
8. `devices.py`
9. `referrals.py`
10. `tickets.py`
11. `wallets.py`
12. `users.py`
13. `admin.py`
14. `admin_vpn_keys.py`
15. `admin_agent_keys.py`
16. `agent_registration.py`
17. `metrics.py`
18. Webhooks: `crypto.py`, `telegram_stars.py`

**Step 2: Verify no async in routes**

Run: `grep -rn "async def\|await " src/infrastructure/api/v1/`
Expected: 0 results (routes should be sync now)

**Step 3: Compile check all routes**

Run: `uv run python -c "from src.main import app" 2>&1`
Expected: FastAPI app loads without errors

**Step 4: Commit**

```bash
git add src/infrastructure/api/v1/routes/ src/infrastructure/api/v1/webhooks/
git commit -m "refactor: migrate routes and webhooks from async to sync"
```

---

### Task 9: Update main.py and __main__.py

**Files:**
- Modify: `src/main.py`
- Modify: `src/__main__.py`

**Step 1: main.py — Convert sync lifecycle**

```diff
-from contextlib import asynccontextmanager
+from contextlib import contextmanager

- @asynccontextmanager
- async def lifespan(app: FastAPI):
-     await init_db()
-     yield
-     await close_db()
+ @contextmanager
+ def lifespan(app: FastAPI):
+     init_db()
+     logger.info("Database connection initialized")
+     yield
+     close_db()
+     logger.info("Application shutdown complete")
```

Note: FastAPI expects `lifespan` to be an async context manager. For sync lifespan, use `contextmanager` and FastAPI will wrap it. Verify this works.

Alternative: Keep `asynccontextmanager` but make body sync:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Database connection initialized")
    yield
    close_db()
    logger.info("Application shutdown complete")
```

This is simpler — the `async` decorator remains but the body has no `await`. FastAPI handles this fine.

**Step 2: __main__.py — Keep as-is**

`__main__.py` already just calls `uvicorn.run()` — no changes needed. The `-m src` entry point works with both sync and async apps.

**Step 3: Verify entry point loads**

Run: `uv run python -c "from src.main import app; print('App loaded:', app.title)"`
Expected: Prints "App loaded: uSipipo Backend API"

**Step 4: Commit**

```bash
git add src/main.py
git commit -m "refactor: migrate main.py lifespan to sync"
```

---

### Task 10: Update .env Connection String

**Files:**
- Modify: `/etc/systemd/system/usipipo-backend.service` and/or `.env`

**Step 1: Update .env with correct URL format**

```bash
echo 'asd123***' | sudo -S sed -i 's|DATABASE_URL=postgresql+asyncpg://|DATABASE_URL=postgresql://|' /home/mowgli/usipipo/backend/.env
```

Verify: `grep DATABASE_URL /home/mowgli/usipipo/backend/.env`
Expected: `DATABASE_URL=postgresql://postgres:Turing.940204@db.irbtvtggzwxrlzrfaksv.supabase.co:5432/postgres`

**Step 2: Restart service**

```bash
echo 'asd123***' | sudo -S systemctl restart usipipo-backend
```

**Step 3: Check startup**

```bash
echo 'asd123***' | sudo -S journalctl -u usipipo-backend -n 20 --no-pager
```
Expected: No import errors, no async errors. May show database connection errors (expected until Supabase is configured).

**Step 4: Commit**

```bash
# .env is not committed (gitignored), so no commit needed
```

---

### Task 11: Final Verification

**Step 1: Check no async remains in DB layer**

Run: `grep -rn "async def\|await " src/ --include="*.py" | grep -v "__pycache__" | grep -v ".pyc" | head -20`
Expected: Only show `async def` from FastAPI's own code (if any). Zero results for DB-related async.

Run: `grep -rn "create_async_engine\|AsyncSession\|async_sessionmaker" src/ --include="*.py"`
Expected: 0 results

**Step 2: Verify app imports work**

Run: `uv run python -c "from src.main import app; print('OK:', app.title)" 2>&1`
Expected: `OK: uSipipo Backend API`

**Step 3: Start test server**

Run: `cd /home/mowgli/usipipo/backend && timeout 5 uv run python -m src 2>&1 || true`
Expected: Should attempt to start on port 8000 (will fail at DB since no local DB, but the app itself loads).

**Step 4: Verify Alembic still works**

Run: `uv run alembic history 2>&1 | head -5`
Expected: Shows migration history without crash
