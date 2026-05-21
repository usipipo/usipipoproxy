# VpnKey `server_id` Persistence Fix Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix the mismatch between VpnKey entity and VpnKeyModel by adding missing `server_id`, `latency_ms`, and `last_latency_check` fields to the persistence layer.

**Architecture:** Update the SQLAlchemy model to match the domain entity, ensure bidirectional conversion works correctly, and verify all layers (repositories, services, schemas, tests) are consistent.

**Tech Stack:** Python 3.13, SQLAlchemy 2.0 (async), Alembic, Pydantic, pytest

**Design Doc:** `docs/plans/2026-04-03-vpn-key-server-id-fix-design.md`

---

## Prerequisites

**Branch:** Create a new branch for this fix:
```bash
cd /home/mowgli/usipipo/apps/backend
git checkout -b fix/vpn-key-server-id-persistence
```

**Run existing tests first to establish baseline:**
```bash
pytest tests/ -v --tb=short -x
```

---

### Task 1: Add Missing Fields to VpnKeyModel

**Files:**
- Modify: `src/infrastructure/persistence/models/vpn_key_model.py`

**Step 1: Add import for Numeric type**

Add `Numeric` to the SQLAlchemy imports:

```python
from sqlalchemy import BigInteger, DateTime, String, Text, Numeric
```

**Step 2: Add the three missing columns to VpnKeyModel**

After the `billing_reset_at` field (around line 37), add:

```python
    server_id: Mapped[UUID | None] = mapped_column(nullable=True, index=True)
    latency_ms: Mapped[float | None] = mapped_column(Numeric(precision=8, scale=2), nullable=True)
    last_latency_check: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

**Step 3: Update `to_entity()` method to map `server_id`**

In the `to_entity()` method, add `server_id` to the VpnKey constructor:

```python
    def to_entity(self) -> VpnKey:
        return VpnKey(
            id=self.id,
            user_id=self.user_id,
            server_id=self.server_id,  # ← ADD THIS LINE
            name=self.name,
            key_type=self.key_type,
            status=self.status,
            key_data=self.key_data,
            external_id=self.external_id,
            created_at=self.created_at,
            expires_at=self.expires_at,
            last_seen_at=self.last_seen_at,
            used_bytes=self.used_bytes,
            data_limit_bytes=self.data_limit_bytes,
            billing_reset_at=self.billing_reset_at,
        )
```

**Step 4: Update `from_entity()` method to map `server_id`**

In the `from_entity()` classmethod, add `server_id` to the model constructor:

```python
    @classmethod
    def from_entity(cls, entity: VpnKey) -> "VpnKeyModel":
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            server_id=entity.server_id,  # ← ADD THIS LINE
            name=entity.name,
            key_type=entity.key_type,
            status=entity.status,
            key_data=entity.key_data,
            external_id=entity.external_id,
            created_at=entity.created_at,
            expires_at=entity.expires_at,
            last_seen_at=entity.last_seen_at,
            used_bytes=entity.used_bytes,
            data_limit_bytes=entity.data_limit_bytes,
            billing_reset_at=entity.billing_reset_at,
        )
```

**Step 5: Verify the model file is syntactically correct**

Run:
```bash
python -c "from src.infrastructure.persistence.models.vpn_key_model import VpnKeyModel; print('✅ Model imports successfully')"
```

Expected: Success message printed

---

### Task 2: Document server_id Immutability in Repository

**Files:**
- Modify: `src/infrastructure/persistence/repositories/vpn_key_repository.py`

**Step 1: Add documentation comment to update() method**

Before the `update()` method, add a docstring clarifying that `server_id` is intentionally NOT updated:

```python
    async def update(self, vpn_key: VpnKey) -> VpnKey:
        """
        Updates an existing VPN key.

        Note: server_id is intentionally NOT updated after creation.
        The server association is immutable - if a key needs to be moved
        to a different server, it should be deleted and recreated.
        """
```

**Step 2: Verify repository still works**

Run:
```bash
python -c "from src.infrastructure.persistence.repositories.vpn_key_repository import VpnKeyRepository; print('✅ Repository imports successfully')"
```

Expected: Success message printed

---

### Task 3: Update API Response Schemas

**Files:**
- Modify: `src/shared/schemas/vpn.py`
- Modify: `src/shared/schemas/admin_vpn_keys.py`

**Step 1: Add server_id to VpnKeyResponse**

In `src/shared/schemas/vpn.py`, add `server_id` to the response model:

```python
class VpnKeyResponse(BaseModel):
    id: UUID
    user_id: UUID
    server_id: UUID | None = None  # ← ADD THIS LINE
    name: str
    key_type: str
    status: str
    # ... rest of fields
```

**Step 2: Add server_id to admin response schemas**

In `src/shared/schemas/admin_vpn_keys.py`, add `server_id` to:

1. `VpnKeyListItemResponse`:
```python
class VpnKeyListItemResponse(BaseModel):
    id: UUID
    user_id: UUID
    server_id: UUID | None = None  # ← ADD
    name: str
    # ... rest
```

2. `VpnKeyDetailResponse`:
```python
class VpnKeyDetailResponse(BaseModel):
    id: UUID
    user_id: UUID
    server_id: UUID | None = None  # ← ADD
    name: str
    # ... rest
```

**Step 3: Verify schemas import**

Run:
```bash
python -c "from src.shared.schemas.vpn import VpnKeyResponse; from src.shared.schemas.admin_vpn_keys import VpnKeyListItemResponse, VpnKeyDetailResponse; print('✅ Schemas import successfully')"
```

Expected: Success message printed

---

### Task 4: Run Full Test Suite

**Files:**
- No file changes
- Verification task

**Step 1: Run unit tests for admin_vpn_key_service**

Run:
```bash
pytest tests/unit/services/test_admin_vpn_key_service.py -v
```

Expected: All tests pass

**Step 2: Run all backend tests**

Run:
```bash
pytest tests/ -v --tb=short
```

Expected: All tests pass (same as baseline or better)

**Step 3: If tests fail, debug and fix**

If any test fails:
1. Read the error message carefully (systematic debugging Phase 1)
2. Determine if it's related to the server_id changes
3. Fix the minimum necessary to make the test pass
4. Re-run the specific failing test

---

### Task 5: Integration Test - Verify server_id Persists

**Files:**
- Create: `tests/integration/test_vpn_key_server_id.py`

**Step 1: Write integration test**

Create a test that verifies the full flow:

```python
"""Integration test for VpnKey server_id persistence."""

import pytest
import uuid
from datetime import datetime, timezone

from usipipo_commons.domain.entities.vpn_key import VpnKey
from usipipo_commons.domain.enums.key_status import KeyStatus
from usipipo_commons.domain.enums.key_type import KeyType
from src.infrastructure.persistence.models.vpn_key_model import VpnKeyModel


@pytest.mark.asyncio
class TestVpnKeyServerIdPersistence:
    """Test that server_id persists correctly through the full stack."""

    async def test_create_vpn_key_with_server_id(self, db_session):
        """Test that server_id is saved when creating a VPN key."""
        server_id = uuid.uuid4()
        user_id = uuid.uuid4()

        vpn_key = VpnKey(
            user_id=user_id,
            server_id=server_id,
            name="Test Key",
            key_type=KeyType.WIREGUARD,
            status=KeyStatus.ACTIVE,
        )

        # Create via model
        model = VpnKeyModel.from_entity(vpn_key)
        db_session.add(model)
        await db_session.commit()
        await db_session.refresh(model)

        # Verify server_id was saved
        assert model.server_id == server_id

        # Read it back
        from sqlalchemy import select
        result = await db_session.execute(
            select(VpnKeyModel).where(VpnKeyModel.id == model.id)
        )
        retrieved_model = result.scalar_one()

        assert retrieved_model.server_id == server_id

    async def test_to_entity_preserves_server_id(self, db_session):
        """Test that to_entity() correctly maps server_id."""
        server_id = uuid.uuid4()

        vpn_key = VpnKey(
            user_id=uuid.uuid4(),
            server_id=server_id,
            name="Test Key",
            key_type=KeyType.WIREGUARD,
        )

        model = VpnKeyModel.from_entity(vpn_key)
        entity = model.to_entity()

        assert entity.server_id == server_id

    async def test_vpn_key_with_null_server_id(self, db_session):
        """Test backward compatibility: VPN keys without server_id."""
        vpn_key = VpnKey(
            user_id=uuid.uuid4(),
            # server_id not set (None by default)
            name="Legacy Key",
            key_type=KeyType.OUTLINE,
        )

        model = VpnKeyModel.from_entity(vpn_key)
        db_session.add(model)
        await db_session.commit()
        await db_session.refresh(model)

        assert model.server_id is None

        # Read it back
        entity = model.to_entity()
        assert entity.server_id is None
```

**Step 2: Run the integration test**

Run:
```bash
pytest tests/integration/test_vpn_key_server_id.py -v
```

Expected: All 3 tests pass

---

### Task 6: Commit and Document

**Step 1: Review all changes**

Run:
```bash
git status
git diff
```

Verify:
- Only the expected files were modified
- No unintended changes
- All tests pass

**Step 2: Stage and commit**

Run:
```bash
git add src/infrastructure/persistence/models/vpn_key_model.py
git add src/infrastructure/persistence/repositories/vpn_key_repository.py
git add src/shared/schemas/vpn.py
git add src/shared/schemas/admin_vpn_keys.py
git add tests/integration/test_vpn_key_server_id.py
git commit -m "fix: add server_id, latency_ms, last_latency_check to VpnKeyModel

- Add missing fields to SQLAlchemy model that exist in migration
- Update to_entity() and from_entity() to map server_id
- Document server_id immutability in repository
- Add server_id to API response schemas
- Add integration tests for server_id persistence

Fixes mismatch between VpnKey entity and persistence layer
where server_id was silently dropped on create/update."
```

**Step 3: Update CHANGELOG**

Add entry to `CHANGELOG.md`:

```markdown
## [Unreleased]

### Fixed
- **vpn_key_model**: Add missing `server_id`, `latency_ms`, and `last_latency_check` fields to SQLAlchemy model
  - Fields existed in database migration but were not mapped in model
  - server_id now persists correctly when creating VPN keys
  - Backward compatible: server_id remains nullable for legacy keys
```

**Step 4: Commit changelog update**

Run:
```bash
git add CHANGELOG.md
git commit -m "docs: add server_id fix to changelog"
```

---

## Summary

**Total Tasks:** 6
**Estimated Commits:** 2 (implementation + changelog)
**Files Modified:** 5
**Files Created:** 1 (integration test)

**Verification Checklist:**
- [ ] VpnKeyModel has `server_id`, `latency_ms`, `last_latency_check` columns
- [ ] `to_entity()` maps all three fields
- [ ] `from_entity()` maps all three fields
- [ ] API schemas include `server_id`
- [ ] All existing tests pass
- [ ] Integration tests pass
- [ ] CHANGELOG updated
- [ ] Code committed with descriptive message

---

## Next Steps After Implementation

1. **Push branch and create PR:**
   ```bash
   git push -u origin fix/vpn-key-server-id-persistence
   ```

2. **Create PR with description linking to this plan**

3. **Merge using GitHub PR/Merge Workflow** (per QWEN.md rules)

4. **Create tag and release after merge**
