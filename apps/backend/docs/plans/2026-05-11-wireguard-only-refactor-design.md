# Design: WireGuard-Only Backend Refactor

**Date:** 2026-05-11
**Author:** Kilo (diagnose + brainstorming)
**Status:** Approved

## Overview

Remove ALL Outline VPN and TrustTunnel VPN support from the uSipipo Backend, leaving only WireGuard as the VPN protocol. This mirrors the agent refactor plan (`2026-05-10-wireguard-only-refactor.md`) applied to the backend.

**Goal:** Clean, WireGuard-only backend with no dead code, no Outline/TrustTunnel schemas, services, routes, models, or documentation.

**Architecture:** 8 sequential phases, bottom-up (foundation first, presentation last). Each phase commits independently with passing tests.

**Tech Stack:** Python 3.13, FastAPI, SQLAlchemy (asyncpg), PostgreSQL, Pydantic v2

---

## Files to Delete (8)

| # | File | Lines | Description |
|---|------|-------|-------------|
| 1 | `src/infrastructure/vpn_providers/outline_client.py` | ~267 | Complete Outline API client |
| 2 | `src/infrastructure/persistence/models/outline_metric_model.py` | ~85 | SQLAlchemy model for outline_metrics table |
| 3 | `src/infrastructure/persistence/models/trusttunnel_metric_model.py` | ~51 | SQLAlchemy model for trusttunnel_metrics table |
| 4 | `src/infrastructure/api/v1/routes/admin_trusttunnel_rules.py` | ~135 | TrustTunnel admin rules routes |
| 5 | `migrations/versions/dfe1fcfb5354_create_outline_metrics_table.py` | ~59 | Alembic migration for outline_metrics |
| 6 | `migrations/versions/2026_04_06_0001_add_trusttunnel_metrics_table.py` | ~53 | Alembic migration for trusttunnel_metrics |
| 7 | `tests/unit/services/test_metrics_service_outline.py` | ~319 | Outline metrics ingestion tests |
| 8 | `tests/unit/api_clients/test_vpn_agent_client.py` | ~95 | TrustTunnel agent client tests (Outline/WG tests moved) |

---

## Files to Modify (~30)

### Phase 1: Schemas & Config (5 files)

| File | Changes |
|------|---------|
| `src/shared/config.py` | Remove 9 `OUTLINE_*` config vars |
| `src/shared/schemas/vpn.py` | Remove `OutlineConsumerEntry`, `OutlineTimeSeriesPoint`, `OutlineSummary`, `OutlineStatusResponse`, `OutlineMetricsResponse` + trusttunnel refs in docstrings |
| `src/shared/schemas/admin.py` | Remove `outline` field from `ServerStatusListResponse`, `outline_keys`/`outline_pct` from `ServerStatsResponse` |
| `src/shared/schemas/agent_registration.py` | Remove `supports_outline: bool` field |
| `src/shared/schemas/admin_vpn_keys.py` | Change `Literal["outline", "wireguard"]` → `Literal["wireguard"]` |

### Phase 2: DB Models (3 files)

| File | Changes |
|------|---------|
| `src/infrastructure/persistence/models/vpn_server_model.py` | Remove `supports_outline`, `supports_trust_tunnel` columns + `to_entity()`/`from_entity()` mappings |
| `src/infrastructure/persistence/models/server_metric_model.py` | Remove `outline_active_keys` column + `to_dict()` mapping |
| `src/infrastructure/persistence/models/__init__.py` | Remove `OutlineMetricModel` import and export |

### Phase 3: Core Services (9 files)

| File | Changes |
|------|---------|
| `src/core/application/services/vpn_service.py` | Remove `outline_client` param/field; remove KeyType.OUTLINE and KeyType.TRUSTTUNNEL branches in create_key, delete_key, revoke_key, get_key_usage |
| `src/core/application/services/vpn_infrastructure_service.py` | Remove `outline_client` param/field; remove OUTLINE branches in enable_key, disable_key, get_key_usage |
| `src/core/application/services/metrics_service.py` | Remove imports of OutlineMetricModel/TrustTunnelMetricModel; remove Outline metrics extraction in ingest_agent_metrics; remove TT metrics extraction; remove `get_latest_outline_metric`, `get_outline_metrics_by_range`, `get_latest_trusttunnel_metric`, `get_trusttunnel_metrics_by_range`; remove TT/Outline cleanup in cleanup_old_metrics |
| `src/core/application/services/server_registry_service.py` | Remove `supports_outline`, `supports_trust_tunnel` from ServerMetadata; remove protocol filtering for outline |
| `src/core/application/services/admin_vpn_key_service.py` | Remove `if vpn_type == "outline"` branches in create/delete/regenerate |
| `src/core/application/services/admin_key_service.py` | Remove `outline_client` param/field; remove outline branches in delete_key |
| `src/core/application/services/admin_server_service.py` | Remove Outline server status computation |
| `src/core/application/services/admin_stats_service.py` | Remove `outline_keys`, `outline_pct` computation |
| `src/core/application/services/agent_registration_service.py` | Remove `supports_outline` parameter |

### Phase 4: Infrastructure (5 files)

| File | Changes |
|------|---------|
| `src/infrastructure/vpn_providers/__init__.py` | Remove `OutlineClient` import and export |
| `src/infrastructure/api/v1/routes/vpn.py` | Remove imports of Outline schemas; remove Outline endpoints `GET /servers/{id}/outline`, `GET /servers/{id}/outline/metrics`; remove TT metrics endpoint; remove TT deeplink export in create/update key; simplify protocol validation to only "wireguard"; remove Outline helper functions |
| `src/infrastructure/api/v1/routes/metrics.py` | Remove `"outline"` key from metrics payload |
| `src/infrastructure/api/v1/routes/admin.py` | Remove `OutlineClient` import, instantiation, and `AdminServerService(outline_client)` |
| `src/infrastructure/api/v1/routes/agent_registration.py` | Remove `supports_outline=request.supports_outline` |
| `src/infrastructure/api/v1/deps.py` | Remove `OutlineClient` import, instantiation, and passing to services |

### Phase 5: API Client (1 file)

| File | Changes |
|------|---------|
| `src/infrastructure/api_clients/vpn_agent_client.py` | Remove 7 TrustTunnel methods (create/delete/export client, export deeplink, get metrics, add/remove rules) + their docstrings. Keep Outline methods (3) for now |

### Phase 6: Main Entry (1 file)

| File | Changes |
|------|---------|
| `src/main.py` | Remove import of `admin_trusttunnel_rules_router` and `app.include_router(...)` line |

### Phase 7: Tests (13 files)

| File | Changes |
|------|---------|
| `tests/conftest.py` | Remove `outline_metrics` from `unsupported_tables` |
| `tests/e2e/conftest.py` | Remove Outline mock data and mock routes for `/outline/keys` |
| `tests/e2e/test_vpn_key_creation_flow.py` | Remove test_create_outline_key_happy_path |
| `tests/e2e/test_vpn_key_deletion_flow.py` | Remove test_delete_outline_key_happy_path |
| `tests/e2e/test_vpn_key_list_operations.py` | Remove Outline key test data |
| `tests/unit/schemas/test_vpn_schemas.py` | Remove ALL Outline schema tests (~96 lines) |
| `tests/unit/services/test_vpn_service_health_check.py` | Remove Outline key mocks and assertions |
| `tests/unit/services/test_vpn_service_saga_rollback.py` | Remove Outline + TrustTunnel rollback tests |
| `tests/unit/services/test_vpn_service_server_id.py` | Remove Outline key test case |
| `tests/unit/services/test_server_registry_service.py` | Remove Outline-only server fixtures, protocol="outline" tests |
| `tests/unit/infrastructure/api/v1/routes/test_vpn_servers.py` | Remove protocol="outline" test cases |

### Phase 8: Documentation (7 files)

| File | Changes |
|------|---------|
| `.env.example` | Remove `OUTLINE_*` vars section |
| `example.env` | Remove entire `VPN - OUTLINE CONFIGURATION` section |
| `AGENTS.md` | Update references: "WireGuard + Outline" → "WireGuard" |
| `QWEN.md` | Update references: remove outline_client.py reference |
| `README.md` | Update features, architecture diagram, env vars table |
| `CONTRIBUTING.md` | Update vpn_type examples to WireGuard-only |
| `CHANGELOG.md` | Add v0.25.0 or v0.26.0 entry for breaking change |

---

## Key Decisions

### 1. KeyType Enum (usipipo-commons)
The `KeyType.OUTLINE` and `KeyType.TRUSTTUNNEL` enum values in `usipipo-commons` are **NOT removed in this refactor**. The backend simply stops using them. This avoids a breaking change in the shared library. A future cleanup can remove them from commons.

### 2. Migration Files
The migration files are kept in the repo (not deleted from disk) to maintain migration chain integrity. However, the actual `outline_metrics` and `trusttunnel_metrics` tables in the DB will NOT be dropped — existing data is preserved. Only the code referencing them is removed.

### 3. Outline Methods in VPN Agent Client
The `VpnAgentClient` keeps its 3 Outline methods (`create_outline_key`, `delete_outline_key`, `regenerate_outline_key`) temporarily because the service layer still references them during the transition. These will be removed in a follow-up when vpn_service.py is fully cleaned.

### 4. WireGuard Becomes Default
After this refactor, `KeyType.WIREGUARD` is the only valid key type. All `vpn_type` parameters and validation should default to/only accept `"wireguard"`.

### 5. No DB Schema Changes
This refactor does NOT include Alembic migrations to drop columns. The `supports_outline`, `supports_trust_tunnel`, `outline_active_keys` columns remain in the database but are no longer used by the application code. DB cleanup is deferred to a future migration.

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Breaking existing API clients | API response schemas change (missing outline fields). Document in CHANGELOG |
| Orphaned DB columns | Documented technical debt, no data loss |
| Commons KeyType still has OUTLINE | Backend imports but never uses those values |
| Agent still sends outline metrics | Backend silently ignores unknown keys in metrics payload |
| Test coverage drops | All WireGuard tests preserved; Outline/TT tests removed |
