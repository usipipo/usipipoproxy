# Design: VpnKey `server_id` Persistence Fix

**Date:** 2026-04-03
**Author:** Qwen Code (via brainstorming)
**Status:** Approved

## Problem Statement

The `VpnKey` entity in `usipipo-commons` has a `server_id: Optional[UUID]` field, but the SQLAlchemy model `VpnKeyModel` in the backend does NOT include this field. A migration exists (`add_server_id_to_vpn_keys.py`) that adds the column to the database, but the model layer was never updated.

**Impact:**
- `server_id` is silently dropped when creating/updating VPN keys
- Cannot query keys by server
- Cannot track latency metrics per key
- Data inconsistency between domain entity and persistence layer

## Root Cause Analysis

Using systematic debugging (Phase 1-4):

1. **Entity has field:** `usipipo-commons/domain/entities/vpn_key.py` → `server_id: Optional[UUID]`
2. **Model missing field:** `usipipo-backend/src/infrastructure/persistence/models/vpn_key_model.py` → NO `server_id`
3. **Migration exists:** `add_server_id_to_vpn_keys.py` → adds `server_id`, `latency_ms`, `last_latency_check`
4. **Conversion methods omit field:** `to_entity()` and `from_entity()` don't map `server_id`

## Architecture

Fix follows concentric layers principle:

```
Layer 1: Database Model (VpnKeyModel)
  ↓ Add missing columns
Layer 2: Conversion (to_entity/from_entity)
  ↓ Map server_id, latency_ms, last_latency_check
Layer 3: Repositories
  ↓ Verify persistence/retrieval
Layer 4: Services
  ↓ Verify consistent server_id usage
Layer 5: API Schemas
  ↓ Expose server_id in responses
Layer 6: Tests
  ↓ Update factories and verify
```

## Data Flow

### Before Fix (Bug)
```
VpnService.create_key() → VpnKey(server_id=server.id)
  → VpnKeyModel.from_entity() → ❌ drops server_id
  → INSERT without server_id → DB: server_id = NULL
```

### After Fix
```
VpnService.create_key() → VpnKey(server_id=server.id)
  → VpnKeyModel.from_entity() → ✅ maps server_id
  → INSERT with server_id → DB: server_id = server.id
```

## Implementation Details

### File 1: `vpn_key_model.py` (CRITICAL)

**Add columns:**
```python
server_id: Mapped[UUID | None] = mapped_column(nullable=True, index=True)
latency_ms: Mapped[float | None] = mapped_column(Numeric(precision=8, scale=2), nullable=True)
last_latency_check: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

**Update `to_entity()`:**
```python
return VpnKey(
    ...
    server_id=self.server_id,  # ADD
    ...
)
```

**Update `from_entity()`:**
```python
return cls(
    ...
    server_id=entity.server_id,  # ADD
    ...
)
```

### File 2: `vpn_key_repository.py` (DOCUMENT)

Add comment documenting that `server_id` is immutable after creation (intentional design).

### File 3: `schemas/vpn.py` and `admin_vpn_keys.py` (ADD)

Add `server_id: UUID | None = None` to response schemas.

### File 4: Tests (VERIFY)

Factory already has `server_id`. Verify all tests pass after fix.

## Error Handling

| Scenario | Behavior |
|----------|----------|
| `server_id` is None | Acceptable (backward compatibility) |
| `server_id` points to non-existent server | FK constraint fails (correct behavior) |
| `latency_ms` negative | Validate at service layer |

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Migration already applied | Idempotent migration handles this |
| Breaking existing queries | `server_id` is nullable, no breaking changes |
| Test failures | Update factories, verify all tests pass |

## Success Criteria

1. ✅ `VpnKeyModel` has `server_id`, `latency_ms`, `last_latency_check` columns
2. ✅ `to_entity()` and `from_entity()` map all three fields
3. ✅ `server_id` persists correctly when creating VPN keys
4. ✅ `server_id` retrieves correctly when reading VPN keys
5. ✅ All existing tests pass
6. ✅ No regression in existing functionality
