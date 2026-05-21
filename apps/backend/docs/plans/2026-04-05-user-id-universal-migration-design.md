# User ID Universal Migration Design

**Date:** 2026-04-05
**Status:** Approved
**Branch:** `refactor/migrate-to-user-id-universal`

## Problem

The backend was designed when Telegram was the only frontend. Repository interfaces, services, and schemas use `telegram_id: int` as the primary user identifier. This creates:

1. **Type confusion** - `telegram_id` (int) vs `user_id` (UUID) mixed throughout codebase
2. **Mypy errors** - 17+ type errors from UUID/int mismatches
3. **Multi-frontend blocker** - Android, desktop, and web apps won't have telegram_id
4. **Architectural violation** - Platform-specific ID used as universal identity

## Design Principle

| Identifier | Scope | Type | Purpose |
|---|---|---|---|
| `user_id: UUID` | **Internal** (all backend) | `UUID` | Universal user identity |
| `telegram_id: int \| None` | **External** (Telegram only) | `int \| None` | Platform-specific attribute |

**Rule:** `telegram_id` is an attribute of User, not the User's identity. Like `email` or `username`.

## Auth Flow (Telegram Bot)

```
1. Bot receives /start with Telegram init_data
2. Backend extracts telegram_id from init_data
3. Backend looks up User by telegram_id
4. If exists → return JWT with {sub: user_id, telegram_id: ...}
5. If new → create User(id=UUID, telegram_id=..., init_data=...) → return JWT
6. All subsequent API calls use user_id from JWT `sub` claim
```

## Migration Phases

### Phase 1: Repository Interfaces
- Change all `telegram_id: int` parameters to `user_id: UUID`
- Update interface docstrings
- Keep `get_by_telegram_id(telegram_id)` as a lookup method (not primary)

### Phase 2: Repository Implementations
- Update SQL queries to filter by `user_id` instead of `telegram_id`
- Add `get_by_telegram_id()` method where needed for auth lookup

### Phase 3: Services
- Update all service methods to accept `user_id: UUID`
- Update service docstrings
- Fix type annotations

### Phase 4: Tests
- Update test fixtures to use UUID user_ids
- Update mock calls to use `user_id` parameter names
- Fix assertion comparisons

### Phase 5: Telegram Bot Adaptation + Documentation Rule
- Update Telegram bot auth flow: lookup `telegram_id → user_id` at login
- All subsequent bot API calls use `user_id` from JWT
- Add documentation rule to QWEN.md

## Files Affected (~50)

- `src/core/domain/interfaces/*.py` (8 files)
- `src/infrastructure/persistence/repositories/*.py` (10 files)
- `src/core/application/services/*.py` (12 files)
- `src/infrastructure/api/v1/routes/*.py` (8 files)
- `tests/unit/**/*.py` (12 files)

## Risk Mitigation

- Each phase commits separately with passing tests
- Mypy runs after each phase to catch regressions
- No database schema changes needed (user_id already exists)
