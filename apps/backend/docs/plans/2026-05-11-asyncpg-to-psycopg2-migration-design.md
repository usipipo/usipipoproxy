# Design: asyncpg → psycopg2 Database Driver Migration

**Date:** 2026-05-11  
**Status:** Approved  
**Author:** Kilo AI  
**Project:** uSipipo Backend

---

## Overview

Migrate the uSipipo Backend from **asyncpg** (async PostgreSQL driver) to **psycopg2** (sync PostgreSQL driver) to enable compatibility with Supabase connection pooler and simplify the architecture by removing async complexity.

**Why psycopg2:**
- Supabase free tier requires connection pooler (IPv4 only). asyncpg has SSL/compatibility issues.
- psycopg2 is the most mature, battle-tested PostgreSQL driver for Python.
- Simplifies codebase by removing `async/await` from data access layer.
- FastAPI handles sync routes efficiently (threadpool).

---

## Scope

**99 files** with async/await usage, **~1341 lines** of async DB operations to migrate.

| Layer | Files | Max Lines/Files | Lines Changed |
|-------|-------|-----------------|---------------|
| Database engine | 2 | 90 | 90 |
| Interfaces/Ports | 5 | 50 | 150 |
| Repositories | 20 | 162 | 300 |
| Services | 15 | 120 | 250 |
| Deps | 1 | 256 | 256 |
| Routes | 22 | 200 | 350 |
| Webhooks | 2 | 100 | 80 |
| Entry points | 2 | 50 | 50 |

---

## Design

### 1. Database Layer (`database.py`)

**Before:**
```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(settings.DATABASE_URL, ...)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

**After:**
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=10,
    pool_timeout=settings.DB_TIMEOUT,
    connect_args={"sslmode": "require"} if "supabase.co" in settings.DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
```

### 2. Repositories (20 files)

Standard change pattern per repository method:

```diff
- async def get_by_id(self, user_id: UUID) -> User | None:
-     result = await self.session.execute(select(Model).where(...))
+ def get_by_id(self, user_id: UUID) -> User | None:
+     result = self.session.execute(select(Model).where(...))
```

- Remove `async` from all method definitions
- Remove `await` from all session calls (execute, commit, refresh, merge, delete, rollback)
- Change `AsyncSession` → `Session` type hints
- Remove `from sqlalchemy.ext.asyncio import AsyncSession`

### 3. Interfaces/Ports

```diff
- async def get_by_id(self, user_id: UUID) -> User | None: ...
+ def get_by_id(self, user_id: UUID) -> User | None: ...
```

All interface methods lose `async` keyword.

### 4. Application Services (15 files)

```diff
- async def get_user_profile(self, user_id: UUID) -> User:
-     return await self.user_repo.get_by_id(user_id)
+ def get_user_profile(self, user_id: UUID) -> User:
+     return self.user_repo.get_by_id(user_id)
```

Same pattern: remove `async`, remove `await`.

### 5. Route Handlers (22 route files + 2 webhooks + deps.py)

```diff
- async def get_user(
-     user_id: UUID,
-     db: AsyncSession = Depends(get_db),
- ) -> User:
-     user = await user_service.get_by_id(user_id)
+ def get_user(
+     user_id: UUID,
+     db: Session = Depends(get_db),
+ ) -> User:
+     user = user_service.get_by_id(user_id)
```

- `async def` → `def`
- `AsyncSession` → `Session`
- Remove `await` from service/repo calls in route handlers
- Remove `await` from `is_token_revoked()` calls if applicable

### 6. Dependencies (`deps.py`)

Change all dependency factory functions from `async def` to `def`:
- `get_current_user()` → sync
- `get_user_service()` → sync
- `get_vpn_service()` → sync
- etc.

### 7. Entry Points

**`main.py`:**
- `lifespan` async context manager → sync
- `init_db()` / `close_db()` → remove async/await
- Remove `asynccontextmanager` import

**`__main__.py`:**
- Keep `uvicorn.run()` — no changes needed (uvicorn accepts sync app)

### 8. `migrations/env.py`

- `get_sync_url()` stays (converts `+asyncpg` URL to sync)
- `run_migrations_online()` may need SSL args for Supabase
- No major changes (Alembic already sync)

### 9. `pyproject.toml`

```diff
- "asyncpg>=0.29.0",
- "psycopg2-binary>=2.9.11",
- "psycopg2>=2.9.12",   # keep
+ "psycopg2>=2.9.12",
+ # asyncpg removed, psycopg2-binary removed
```

### 10. `.env`

```diff
- DATABASE_URL=postgresql+asyncpg://...
+ DATABASE_URL=postgresql://postgres:Turing.940204@db.irbtvtggzwxrlzrfaksv.supabase.co:5432/postgres
```

---

## Execution Order

The migration follows dependency chain strictly:

1. **`pyproject.toml`** — Update dependencies (foundation for build)
2. **`database.py`** — Core engine + session change (foundation for all DB operations)
3. **`migrations/env.py`** — Alembic configuration adjustment
4. **Interfaces/Ports** — Contracts that repos implement (foundation for repos)
5. **Repositories** (20 files) — Implement interfaces, depend on database.py
6. **Services** (15 files) — Depend on repositories
7. **`deps.py`** — Dependency injection, depends on database.py + services
8. **Routes** (22 files) + **Webhooks** (2 files) — Depend on deps + services
9. **`main.py`** — App entry, depends on database.py
10. **`.env`** — Update connection string

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Missing `await` removal in repository | After each repo change, verify no `await` keywords remain |
| Interface mismatch (async vs sync) | Change interfaces BEFORE repos, verify all impls match |
| Route still uses `async def` with sync DB | FastAPI handles this fine (warns but works). Eventually convert all to `def` |
| SSL connection failure | Use `connect_args={"sslmode": "require"}` with Supabase detection |
| Broken migration chain | Edit migration files only if needed (Alembic env.py changes minimal) |

---

## Testing Strategy

After migration:
1. **Static verification:** `grep -rn "async def" src/` should show 0 results (except FastAPI lifecycle handlers)
2. **Compile check:** `uv run python -c "from src.main import app"` (ensures imports work)
3. **Start server:** `uv run python -m src`
4. **Health check:** `curl http://localhost:8000/health`
5. **DB migration:** `uv run alembic upgrade head`
