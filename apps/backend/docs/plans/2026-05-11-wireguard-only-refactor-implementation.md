# WireGuard-Only Backend Refactor Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove ALL Outline VPN and TrustTunnel VPN support from the uSipipo Backend, leaving only WireGuard as the VPN protocol.

**Architecture:** 8 sequential phases (foundation → presentation), each committing independently with passing tests. Files are deleted, schemas/services/routes/tests are cleaned. DB schema changes are deferred (columns stay, code stops using them).

**Tech Stack:** Python 3.13, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL, Pydantic v2, pytest, usipipo-commons

**Design Doc:** `docs/plans/2026-05-11-wireguard-only-refactor-design.md`

---

## Prerequisites

```bash
cd /home/mowgli/usipipo/backend
git checkout -b refactor/wireguard-only-backend
uv run pytest tests/ -v --tb=short -x 2>&1 | tail -20
```

Expected: All tests pass (baseline).

---

## Phase 0: Delete Complete Files

### Task 0.1: Delete 7 files (Outline + TrustTunnel + Tests)

**Files:**
- Delete: `src/infrastructure/vpn_providers/outline_client.py`
- Delete: `src/infrastructure/persistence/models/outline_metric_model.py`
- Delete: `src/infrastructure/persistence/models/trusttunnel_metric_model.py`
- Delete: `src/infrastructure/api/v1/routes/admin_trusttunnel_rules.py`
- Delete: `migrations/versions/dfe1fcfb5354_create_outline_metrics_table.py`
- Delete: `migrations/versions/2026_04_06_0001_add_trusttunnel_metrics_table.py`
- Delete: `tests/unit/services/test_metrics_service_outline.py`
- Delete: `tests/unit/api_clients/test_vpn_agent_client.py`

**Step 1: Verify files exist**

```bash
ls -la src/infrastructure/vpn_providers/outline_client.py \
  src/infrastructure/persistence/models/outline_metric_model.py \
  src/infrastructure/persistence/models/trusttunnel_metric_model.py \
  src/infrastructure/api/v1/routes/admin_trusttunnel_rules.py \
  migrations/versions/dfe1fcfb5354_create_outline_metrics_table.py \
  "migrations/versions/2026_04_06_0001_add_trusttunnel_metrics_table.py" \
  tests/unit/services/test_metrics_service_outline.py \
  tests/unit/api_clients/test_vpn_agent_client.py
```

Expected: All 8 files exist.

**Step 2: Delete files**

```bash
rm src/infrastructure/vpn_providers/outline_client.py
rm src/infrastructure/persistence/models/outline_metric_model.py
rm src/infrastructure/persistence/models/trusttunnel_metric_model.py
rm src/infrastructure/api/v1/routes/admin_trusttunnel_rules.py
rm migrations/versions/dfe1fcfb5354_create_outline_metrics_table.py
rm "migrations/versions/2026_04_06_0001_add_trusttunnel_metrics_table.py"
rm tests/unit/services/test_metrics_service_outline.py
rm tests/unit/api_clients/test_vpn_agent_client.py
```

**Step 3: Verify deletion**

```bash
ls src/infrastructure/vpn_providers/outline_client.py 2>&1 || echo "outline_client.py DELETED"
ls src/infrastructure/persistence/models/trusttunnel_metric_model.py 2>&1 || echo "trusttunnel_metric_model.py DELETED"
```

Expected: Both show "DELETED".

**Step 4: Commit**

```bash
git add -A
git commit -m "refactor: delete Outline and TrustTunnel source files, migrations, and tests"
```

---

## Phase 1: Schemas & Config

### Task 1.1: Remove OUTLINE_* config vars from config.py

**Files:**
- Modify: `src/shared/config.py`

**Step 1: Open config.py and remove Outline config block**

Read `src/shared/config.py` (around line 108-117):

```python
    # ===== OUTLINE VPN CONFIGURATION =====
    OUTLINE_API_URL: str = ""
    OUTLINE_VERIFY_SSL: bool = False
    OUTLINE_API_PORT: str = ""
    OUTLINE_KEYS_PORT: str = ""
    OUTLINE_SERVER_IP: str = ""
    OUTLINE_DASHBOARD_URL: str = ""
    OUTLINE_CERT_SHA256: str = ""
    OUTLINE_CERT_PEM: str = ""
```

Delete these 9 lines.

Also remove the `OUTLINE_` import reference if any at the top of the file.

**Step 2: Verify deletion**

```bash
grep -n "OUTLINE_" src/shared/config.py
```

Expected: No matches (or only in comments).

**Step 3: Commit**

```bash
git add src/shared/config.py
git commit -m "refactor(config): remove OUTLINE_* configuration variables"
```

---

### Task 1.2: Remove Outline schemas from vpn.py

**Files:**
- Modify: `src/shared/schemas/vpn.py`

**Step 1: Read the file and identify Outline schemas**

Open `src/shared/schemas/vpn.py`. Remove these classes entirely:
- `OutlineConsumerEntry` (line ~91)
- `OutlineTimeSeriesPoint` (line ~102)
- `OutlineSummary` (line ~113)
- `OutlineStatusResponse` (line ~125)
- `OutlineMetricsResponse` (line ~145)

Also remove the `# Outline Metrics Schemas` comment block.

**Step 2: Remove trusttunnel references in docstrings**

Search for "trusttunnel" in the file and remove from docstrings and type hints.

**Step 3: Verify**

```bash
grep -n "class Outline\|OutlineConsumer\|OutlineTimeSeries\|OutlineSummary\|OutlineStatus\|OutlineMetrics" src/shared/schemas/vpn.py
```

Expected: No matches.

**Step 4: Commit**

```bash
git add src/shared/schemas/vpn.py
git commit -m "refactor(schemas): remove Outline metrics schemas from vpn.py"
```

---

### Task 1.3: Remove Outline fields from admin.py schemas

**Files:**
- Modify: `src/shared/schemas/admin.py`

**Step 1: Read admin.py**

Remove:
- `outline: ServerStatusResponse | None = None` from `ServerStatusListResponse`
- `outline_keys: int` and `outline_pct: float` from `ServerStatsResponse` (or similar struct)

Also remove `key_type: str = Field(..., description="Key type (wireguard, outline)")` → change to just `wireguard`.

**Step 2: Commit**

```bash
grep -n "outline" src/shared/schemas/admin.py
# Expected: No matches (except maybe in comments)
git add src/shared/schemas/admin.py
git commit -m "refactor(schemas): remove Outline fields from admin schemas"
```

---

### Task 1.4: Remove supports_outline from agent_registration.py

**Files:**
- Modify: `src/shared/schemas/agent_registration.py`

**Step 1: Read file**

Remove `supports_outline: bool = Field(True, description="Supports Outline VPN")` from the schema.

Also remove from `__all__` if listed.

**Step 2: Commit**

```bash
git add src/shared/schemas/agent_registration.py
git commit -m "refactor(schemas): remove supports_outline from agent registration"
```

---

### Task 1.5: Update admin_vpn_keys.py literal type

**Files:**
- Modify: `src/shared/schemas/admin_vpn_keys.py`

**Step 1: Read file**

Change:
```python
vpn_type: Literal["outline", "wireguard"] | None = ...
```
To:
```python
vpn_type: Literal["wireguard"] | None = ...
```

And the non-optional variant similarly.

**Step 2: Commit**

```bash
git add src/shared/schemas/admin_vpn_keys.py
git commit -m "refactor(schemas): restrict vpn_type literal to wireguard only"
```

---

## Phase 2: DB Models

### Task 2.1: Update vpn_server_model.py

**Files:**
- Modify: `src/infrastructure/persistence/models/vpn_server_model.py`

**Step 1: Read file and identify columns to remove**

Remove:
- `supports_outline: Mapped[bool] = mapped_column(Boolean, default=True)` (line ~37)
- `supports_trust_tunnel: Mapped[bool] = mapped_column(Boolean, default=False)` (line ~39)
- Remove from `to_entity()`: lines `supports_outline=self.supports_outline,` and `supports_trust_tunnel=self.supports_trust_tunnel,`
- Remove from `from_entity()`: lines `supports_outline=entity.supports_outline,` and `supports_trust_tunnel=entity.supports_trust_tunnel,`

**Step 2: Verify**

```bash
grep -n "supports_outline\|supports_trust" src/infrastructure/persistence/models/vpn_server_model.py
```

Expected: No matches.

**Step 3: Commit**

```bash
git add src/infrastructure/persistence/models/vpn_server_model.py
git commit -m "refactor(model): remove supports_outline and supports_trust_tunnel from vpn_server_model"
```

---

### Task 2.2: Update server_metric_model.py

**Files:**
- Modify: `src/infrastructure/persistence/models/server_metric_model.py`

**Step 1: Read file**

Remove:
- `outline_active_keys: Mapped[int] = ...` column
- Remove from `to_dict()` mapping

**Step 2: Verify**

```bash
grep -n "outline_active_keys" src/infrastructure/persistence/models/server_metric_model.py
```

Expected: No matches.

**Step 3: Commit**

```bash
git add src/infrastructure/persistence/models/server_metric_model.py
git commit -m "refactor(model): remove outline_active_keys from server_metric_model"
```

---

### Task 2.3: Update models/__init__.py

**Files:**
- Modify: `src/infrastructure/persistence/models/__init__.py`

**Step 1: Read file**

Remove:
- `from .outline_metric_model import OutlineMetricModel` import
- `"OutlineMetricModel"` from `__all__`

**Step 2: Commit**

```bash
git add src/infrastructure/persistence/models/__init__.py
git commit -m "refactor(models): remove OutlineMetricModel import"
```

---

## Phase 3: Core Services

### Task 3.1: Clean vpn_service.py

**Files:**
- Modify: `src/core/application/services/vpn_service.py`

**Step 1: Read file and plan changes**

Changes needed:
- Remove `from ...outline_client import OutlineClient` import
- Remove `outline_client` from `__init__` parameter and `self.outline_client` assignment
- In `create_key`: remove `elif key_type_enum == KeyType.OUTLINE:` block (lines ~142-146) and `elif key_type_enum == KeyType.TRUSTTUNNEL:` block (lines ~150-161)
- In `delete_key`: remove `elif key_type_enum == KeyType.OUTLINE:` and `elif key_type_enum == KeyType.TRUSTTUNNEL:` blocks
- In `revoke_key`: remove `if key.key_type == KeyType.OUTLINE:` and `if key.key_type == KeyType.TRUSTTUNNEL:` blocks
- In `get_key_usage`: remove `if key.key_type == KeyType.OUTLINE:` block

Keep only WireGuard branches.

**Step 2: Verify compilation**

```bash
cd /home/mowgli/usipipo/backend && python -c "from src.core.application.services.vpn_service import VpnService; print('OK')"
```

Expected: OK (if imports cleaned properly). Might fail until all dependent files are updated — that's fine.

**Step 3: Commit**

```bash
git add src/core/application/services/vpn_service.py
git commit -m "refactor(service): remove Outline and TrustTunnel from VpnService"
```

---

### Task 3.2: Clean vpn_infrastructure_service.py

**Files:**
- Modify: `src/core/application/services/vpn_infrastructure_service.py`

**Step 1: Read file**

Remove:
- `from ...outline_client import OutlineClient` import
- `outline_client` from `__init__`
- All `elif vpn_type == KeyType.OUTLINE:` branches in `enable_key`, `disable_key`, `get_key_usage`

Keep only WireGuard branches.

**Step 2: Commit**

```bash
git add src/core/application/services/vpn_infrastructure_service.py
git commit -m "refactor(service): remove Outline from VpnInfrastructureService"
```

---

### Task 3.3: Clean metrics_service.py

**Files:**
- Modify: `src/core/application/services/metrics_service.py`

**Step 1: Read file and plan changes**

This is the most complex change. Remove:

1. **Imports:**
   - `from ...outline_metric_model import OutlineMetricModel`
   - `from ...trusttunnel_metric_model import TrustTunnelMetricModel`

2. **In `ingest_agent_metrics()`:**
   - Remove `outline_keys = vpn.get("outline", {}).get("active_keys", 0)` (line ~78)
   - Remove `outline_active_keys=outline_keys` from ServerMetricModel creation
   - Remove entire block that extracts and stores Outline metrics (lines ~111-143)
   - Remove entire block that extracts and stores TrustTunnel metrics (lines ~176-195)

3. **Remove methods:**
   - `get_latest_outline_metric` (line ~365)
   - `get_outline_metrics_by_range` (line ~397)
   - `get_latest_trusttunnel_metric` (line ~527)
   - `get_trusttunnel_metrics_by_range` (line ~559)

4. **In `cleanup_old_metrics()`:**
   - Remove `delete(OutlineMetricModel)...` block
   - Remove `delete(TrustTunnelMetricModel)...` block

**Step 2: Verify removal**

```bash
grep -n "OutlineMetricModel\|TrustTunnelMetricModel\|get_latest_outline\|get_outline_metrics_by_range\|get_latest_trusttunnel\|get_trusttunnel_metrics" src/core/application/services/metrics_service.py
```

Expected: No matches.

**Step 3: Commit**

```bash
git add src/core/application/services/metrics_service.py
git commit -m "refactor(service): remove Outline and TrustTunnel metrics ingestion, queries, cleanup"
```

---

### Task 3.4: Clean server_registry_service.py

**Files:**
- Modify: `src/core/application/services/server_registry_service.py`

**Step 1: Read file**

Remove:
- `supports_outline="outline" in protocols,` from ServerMetadata construction
- `supports_trust_tunnel="trust_tunnel" in protocols,` from ServerMetadata construction
- Remove protocol filtering for `"outline"` in `get_servers_for_user()` (the `if protocol.lower() == "outline"` block)

Keep only WireGuard protocol handling.

**Step 2: Commit**

```bash
git add src/core/application/services/server_registry_service.py
git commit -m "refactor(service): remove Outline and TrustTunnel from ServerRegistryService"
```

---

### Task 3.5: Clean admin_vpn_key_service.py

**Files:**
- Modify: `src/core/application/services/admin_vpn_key_service.py`

**Step 1: Read file**

Remove all `if vpn_type == "outline":` branches:
- In key creation: `if vpn_type == "outline": outline_result = await agent_client.create_outline_key(...)` block
- In key deletion: `if key.key_type == KeyType.OUTLINE:` block
- In key regeneration: `if key.key_type == KeyType.OUTLINE:` block

**Step 2: Commit**

```bash
git add src/core/application/services/admin_vpn_key_service.py
git commit -m "refactor(service): remove Outline key operations from AdminVpnKeyService"
```

---

### Task 3.6: Clean admin_key_service.py

**Files:**
- Modify: `src/core/application/services/admin_key_service.py`

**Step 1: Read file**

Remove:
- `outline_client` from `__init__` parameter and field
- `elif key_type.lower() == "outline" and self.outline_client:` block in `delete_key`

**Step 2: Commit**

```bash
git add src/core/application/services/admin_key_service.py
git commit -m "refactor(service): remove Outline client from AdminKeyService"
```

---

### Task 3.7: Clean admin_server_service.py

**Files:**
- Modify: `src/core/application/services/admin_server_service.py`

**Step 1: Read file**

Remove:
- `outline_client` from `__init__`
- Entire Outline server status block (lines ~88-131): `# Outline server status`, outline_keys computation, outline_status creation, `status["outline"] = outline_status`

**Step 2: Commit**

```bash
git add src/core/application/services/admin_server_service.py
git commit -m "refactor(service): remove Outline server status from AdminServerService"
```

---

### Task 3.8: Clean admin_stats_service.py

**Files:**
- Modify: `src/core/application/services/admin_stats_service.py`

**Step 1: Read file**

Remove:
- `outline_keys = sum(...)` computation
- `outline_pct = round(...)` computation
- `"outline_keys": outline_keys` and `"outline_pct": outline_pct` from returned dict

**Step 2: Commit**

```bash
git add src/core/application/services/admin_stats_service.py
git commit -m "refactor(service): remove Outline stats from AdminStatsService"
```

---

### Task 3.9: Clean agent_registration_service.py

**Files:**
- Modify: `src/core/application/services/agent_registration_service.py`

**Step 1: Read file**

Remove `supports_outline: bool = True` parameter from `register_agent()` and `supports_outline=supports_outline` from Server construction.

**Step 2: Commit**

```bash
git add src/core/application/services/agent_registration_service.py
git commit -m "refactor(service): remove supports_outline from AgentRegistrationService"
```

---

## Phase 4: Infrastructure

### Task 4.1: Clean vpn_providers/__init__.py

**Files:**
- Modify: `src/infrastructure/vpn_providers/__init__.py`

**Step 1: Read file**

Remove:
- `from ...outline_client import OutlineClient` import
- `"OutlineClient"` from `__all__`

**Step 2: Commit**

```bash
git add src/infrastructure/vpn_providers/__init__.py
git commit -m "refactor(vpn_providers): remove OutlineClient export"
```

---

### Task 4.2: Clean vpn.py routes

**Files:**
- Modify: `src/infrastructure/api/v1/routes/vpn.py`

**Step 1: Read file and plan changes**

This is the most complex routes change. Remove:

1. **Imports** of Outline schemas (OutlineStatusResponse, OutlineMetricsResponse, etc.)
2. **TrustTunnel deeplink export** in `create_key` and `update_key` endpoints (lines ~136-147 and ~221-234)
3. **Protocol validation**: Change `["outline", "wireguard", "trusttunnel"]` → `["wireguard"]`
4. **Entire Outline Metrics endpoints** (lines ~480-666):
   - `get_outline_status` at `/servers/{server_id}/outline`
   - `get_outline_metrics` at `/servers/{server_id}/outline/metrics`
5. **TrustTunnel Metrics endpoint** (lines ~786-854):
   - `get_trusttunnel_metrics` at `/servers/{server_id}/trusttunnel/metrics`
6. **Outline helper functions** (lines ~424-480): `_build_outline_metrics`, etc.

**Step 2: Verify removal**

```bash
grep -n "OutlineStatusResponse\|OutlineMetricsResponse\|get_outline_status\|get_outline_metrics\|get_trusttunnel_metrics\|trusttunnel" src/infrastructure/api/v1/routes/vpn.py
```

Expected: No matches.

**Step 3: Commit**

```bash
git add src/infrastructure/api/v1/routes/vpn.py
git commit -m "refactor(routes): remove Outline and TrustTunnel endpoints from vpn.py"
```

---

### Task 4.3: Clean metrics.py route

**Files:**
- Modify: `src/infrastructure/api/v1/routes/metrics.py`

**Step 1: Read file**

Remove the `"outline"` key from the metrics payload dictionary (around line 45).

**Step 2: Commit**

```bash
git add src/infrastructure/api/v1/routes/metrics.py
git commit -m "refactor(routes): remove outline key from metrics payload"
```

---

### Task 4.4: Clean admin.py routes

**Files:**
- Modify: `src/infrastructure/api/v1/routes/admin.py`

**Step 1: Read file**

Remove:
- `from ...outline_client import OutlineClient` import
- `outline_client = OutlineClient()` instantiation
- `outline_client` parameter passed to `AdminServerService`
- `outline` field from the response (line ~460: `outline=_to_response(status.get("outline"))`)

**Step 2: Commit**

```bash
git add src/infrastructure/api/v1/routes/admin.py
git commit -m "refactor(routes): remove Outline client from admin routes"
```

---

### Task 4.5: Clean agent_registration.py route

**Files:**
- Modify: `src/infrastructure/api/v1/routes/agent_registration.py`

**Step 1: Read file**

Remove `supports_outline=request.supports_outline` from the service call.

**Step 2: Commit**

```bash
git add src/infrastructure/api/v1/routes/agent_registration.py
git commit -m "refactor(routes): remove supports_outline from agent registration route"
```

---

### Task 4.6: Clean deps.py

**Files:**
- Modify: `src/infrastructure/api/v1/deps.py`

**Step 1: Read file**

Remove:
- `from ...outline_client import OutlineClient` import
- `outline_client = OutlineClient()` instantiation
- `outline_client` parameter passed to services

**Step 2: Commit**

```bash
git add src/infrastructure/api/v1/deps.py
git commit -m "refactor(deps): remove Outline client from dependency injection"
```

---

## Phase 5: API Client

### Task 5.1: Remove TrustTunnel methods from vpn_agent_client.py

**Files:**
- Modify: `src/infrastructure/api_clients/vpn_agent_client.py`

**Step 1: Read file and identify methods to remove**

Remove these 7 methods (and their docstrings):
- `create_trusttunnel_client` (line ~224)
- `delete_trusttunnel_client` (line ~248)
- `export_trusttunnel_client` (line ~269)
- `export_trusttunnel_deeplink` (line ~291)
- `get_trusttunnel_metrics` (line ~313)
- `add_trusttunnel_rule` (line ~332)
- `remove_trusttunnel_rule` (line ~357)

Keep the 3 Outline methods for now (they'll be cleaned in a follow-up when service layer is fully done):
- `create_outline_key`
- `delete_outline_key`
- `regenerate_outline_key`

**Step 2: Verify**

```bash
grep -n "trusttunnel" src/infrastructure/api_clients/vpn_agent_client.py
```

Expected: No matches.

**Step 3: Commit**

```bash
git add src/infrastructure/api_clients/vpn_agent_client.py
git commit -m "refactor(agent_client): remove TrustTunnel methods from VpnAgentClient"
```

---

## Phase 6: Main Entry

### Task 6.1: Clean main.py

**Files:**
- Modify: `src/main.py`

**Step 1: Read file**

Remove:
- `from .infrastructure.api.v1.routes.admin_trusttunnel_rules import router as admin_trusttunnel_rules_router` import
- `app.include_router(admin_trusttunnel_rules_router, prefix=api_prefix)` line

**Step 2: Verify**

```bash
grep -n "trusttunnel" src/main.py
```

Expected: No matches.

**Step 3: Commit**

```bash
git add src/main.py
git commit -m "refactor(main): remove TrustTunnel rules router import and registration"
```

---

## Phase 7: Tests

### Task 7.1: Update conftest.py

**Files:**
- Modify: `tests/conftest.py`

**Step 1: Read file**

Remove `"outline_metrics"` from the `unsupported_tables` set (line ~78).

**Step 2: Commit**

```bash
git add tests/conftest.py
git commit -m "refactor(tests): remove outline_metrics from conftest unsupported_tables"
```

---

### Task 7.2: Update e2e conftest.py

**Files:**
- Modify: `tests/e2e/conftest.py`

**Step 1: Read file**

Remove:
- `"outline": {"status": "ok"},` from metrics mock data
- `mock.post("http://test-agent/outline/keys").mock(...)` route
- `"id": "outline-key-123",` from mock response
- `mock.delete("http://test-agent/outline/keys/outline-key-123").mock(...)` route

**Step 2: Commit**

```bash
git add tests/e2e/conftest.py
git commit -m "refactor(tests): remove Outline mock data from e2e conftest"
```

---

### Task 7.3: Update e2e test files

**Files:**
- Modify: `tests/e2e/test_vpn_key_creation_flow.py`
- Modify: `tests/e2e/test_vpn_key_deletion_flow.py`
- Modify: `tests/e2e/test_vpn_key_list_operations.py`

**Step 1: For each file:**

- `test_vpn_key_creation_flow.py`: Remove `test_create_outline_key_happy_path` function
- `test_vpn_key_deletion_flow.py`: Remove `test_delete_outline_key_happy_path` function
- `test_vpn_key_list_operations.py`: Remove Outline key test data from fixtures

**Step 2: Commit**

```bash
git add tests/e2e/test_vpn_key_creation_flow.py tests/e2e/test_vpn_key_deletion_flow.py tests/e2e/test_vpn_key_list_operations.py
git commit -m "refactor(tests): remove Outline e2e test cases"
```

---

### Task 7.4: Update schema tests

**Files:**
- Modify: `tests/unit/schemas/test_vpn_schemas.py`

**Step 1: Read file**

Remove ALL Outline-related tests:
- All Outline schema imports
- `create_outline_status_data` helper
- `create_outline_metrics_data` helper
- `TestOutlineTimeSeriesPoint` class
- `TestOutlineConsumerEntry` class
- `TestOutlineSummary` class
- `TestOutlineStatusResponse` class
- `TestOutlineMetricsResponse` class

Keep WireGuard and VPN key schema tests.

**Step 2: Verify**

```bash
grep -n "Outline\|outline" tests/unit/schemas/test_vpn_schemas.py | head -5
```

Expected: No matches (except maybe KeyType.OUTLINE in WireGuard test data — handle that too).

**Step 3: Commit**

```bash
git add tests/unit/schemas/test_vpn_schemas.py
git commit -m "refactor(tests): remove Outline schema tests"
```

---

### Task 7.5: Update service tests

**Files:**
- Modify: `tests/unit/services/test_vpn_service_health_check.py`
- Modify: `tests/unit/services/test_vpn_service_saga_rollback.py`
- Modify: `tests/unit/services/test_vpn_service_server_id.py`
- Modify: `tests/unit/services/test_server_registry_service.py`

**Step 1: For each file, remove Outline/TrustTunnel test cases:**

- `test_vpn_service_health_check.py`: Remove Outline key mocks (`create_outline_key`, `delete_outline_key`), and any tests using them
- `test_vpn_service_saga_rollback.py`: Remove `test_create_key_outline_rollback`, `test_delete_key_outline_type`, `test_create_key_trusttunnel_success`, `test_create_key_trusttunnel_db_failure_triggers_rollback`, `test_delete_key_trusttunnel_type`
- `test_vpn_service_server_id.py`: Remove Outline key test case
- `test_server_registry_service.py`: Remove `test_filters_by_outline_protocol`, Outline-only server fixtures, any `protocol="outline"` tests

Keep all WireGuard tests.

**Step 2: Commit**

```bash
git add tests/unit/services/test_vpn_service_health_check.py tests/unit/services/test_vpn_service_saga_rollback.py tests/unit/services/test_vpn_service_server_id.py tests/unit/services/test_server_registry_service.py
git commit -m "refactor(tests): remove Outline and TrustTunnel service tests"
```

---

### Task 7.6: Update route tests

**Files:**
- Modify: `tests/unit/infrastructure/api/v1/routes/test_vpn_servers.py`

**Step 1: Read file**

Remove or update test cases that use `protocol="outline"`. Change them to `protocol="wireguard"` where appropriate, or remove Outline-specific assertions.

**Step 2: Commit**

```bash
git add tests/unit/infrastructure/api/v1/routes/test_vpn_servers.py
git commit -m "refactor(tests): remove Outline protocol tests from vpn_servers tests"
```

---

## Phase 8: Documentation

### Task 8.1: Clean .env.example

**Files:**
- Modify: `.env.example`

**Step 1: Read file**

Remove the `# OUTLINE VPN CONFIGURATION` section (lines ~89-96): all OUTLINE_* vars.

**Step 2: Commit**

```bash
git add .env.example
git commit -m "docs: remove Outline config from .env.example"
```

---

### Task 8.2: Clean example.env

**Files:**
- Modify: `example.env`

**Step 1: Read file**

Remove the entire `# VPN - OUTLINE CONFIGURATION` section (lines ~47-64).

**Step 2: Commit**

```bash
git add example.env
git commit -m "docs: remove Outline config from example.env"
```

---

### Task 8.3: Update AGENTS.md

**Files:**
- Modify: `AGENTS.md`

**Step 1: Read file**

Update references:
- Line ~59: `"WireGuard + Outline key lifecycle"` → `"WireGuard key lifecycle"`
- Line ~114: `WireGuard + Outline clients` → `WireGuard clients`
- Line ~115: Remove `src/infrastructure/vpn_providers/` listing

**Step 2: Commit**

```bash
git add AGENTS.md
git commit -m "docs: update AGENTS.md for WireGuard-only"
```

---

### Task 8.4: Update QWEN.md

**Files:**
- Modify: `QWEN.md`

**Step 1: Read file**

Remove line ~35: `│   │   └── outline_client.py     # Shadowbox API`

**Step 2: Commit**

```bash
git add QWEN.md
git commit -m "docs: update QWEN.md for WireGuard-only"
```

---

### Task 8.5: Update README.md

**Files:**
- Modify: `README.md`

**Step 1: Read file**

Update:
- Features: "WireGuard and Outline key generation" → "WireGuard key generation"
- Architecture diagram: Remove Outline from the diagram
- API docs: Remove Outline references from protocol parameter descriptions
- Env vars table: Remove `OUTLINE_API_URL` row

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update README.md for WireGuard-only"
```

---

### Task 8.6: Update CONTRIBUTING.md

**Files:**
- Modify: `CONTRIBUTING.md`

**Step 1: Read file**

Update references to Outline in code examples and docstrings.

**Step 2: Commit**

```bash
git add CONTRIBUTING.md
git commit -m "docs: update CONTRIBUTING.md for WireGuard-only"
```

---

### Task 8.7: Update CHANGELOG.md

**Files:**
- Modify: `CHANGELOG.md`

**Step 1: Read file**

Add new version entry at top (after `## [Unreleased]`):

```markdown
## [Unreleased]

### BREAKING CHANGES

- **Removed Outline VPN support** — Outline Manager integration completely removed
- **Removed TrustTunnel VPN support** — TrustTunnel client support eliminated
- **WireGuard-only backend** — Backend now exclusively supports WireGuard VPN protocol

### Removed
- Outline API client (`outline_client.py`)
- Outline metrics model (`OutlineMetricModel`, `outline_metrics` table)
- TrustTunnel metrics model (`TrustTunnelMetricModel`, `trusttunnel_metrics` table)
- TrustTunnel admin rules routes (`admin_trusttunnel_rules.py`)
- 9 Outline configuration variables (`OUTLINE_API_URL`, `OUTLINE_VERIFY_SSL`, etc.)
- `supports_outline` from agent registration schema and server model
- `supports_trust_tunnel` from server model
- `outline_active_keys` from server metric model
- 2 Alembic migrations (outline_metrics, trusttunnel_metrics)
- 7 TrustTunnel methods from VpnAgentClient
- `outline` key in metrics payload
- 4 Outline/TrustTunnel REST API endpoints
- ~400 lines of tests for Outline/TrustTunnel functionality

### Changed
- `vpn_type` literals restricted to `"wireguard"` only
- Server registry no longer filters by Outline protocol
- Metrics service no longer ingests or queries Outline/TrustTunnel data
- All documentation updated to reflect WireGuard-only architecture
```

**Step 2: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: add WireGuard-only refactor to changelog"
```

---

## Final Verification

### Task 9.1: Verify compilation

```bash
cd /home/mowgli/usipipo/backend

# Check for any remaining Outline/TrustTunnel references in source code
echo "=== Outline references in src/ ==="
grep -rn "outline_client\|OutlineClient\|OutlineMetricModel\|OutlineStatusResponse\|OutlineMetricsResponse\|OutlineTimeSeriesPoint\|OutlineSummary\|OutlineConsumerEntry\|supports_outline\|outline_active_keys\|outline_api_reachable" src/ --include="*.py" && echo "FOUND" || echo "CLEAN"

echo ""
echo "=== TrustTunnel references in src/ ==="
grep -rn "trusttunnel\|trust_tunnel\|TrustTunnel" src/ --include="*.py" && echo "FOUND" || echo "CLEAN"
```

Expected: Both print "CLEAN".

### Task 9.2: Run test suite

```bash
cd /home/mowgli/usipipo/backend
uv run pytest tests/ -v --tb=short -x 2>&1 | tail -40
```

Expected: All remaining tests pass (WireGuard-only). Some tests may fail due to removed Outline fixtures — fix them.

### Task 9.3: Run mypy

```bash
cd /home/mowgli/usipipo/backend
uv run mypy src/ 2>&1
```

Expected: 0 errors (or pre-existing ones only).

### Task 9.4: Run ruff

```bash
cd /home/mowgli/usipipo/backend
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

Expected: Clean.

### Task 9.5: Final commit

```bash
cd /home/mowgli/usipipo/backend
git add -A
git commit -m "refactor: complete WireGuard-only backend refactor

- Removed Outline VPN support entirely
- Removed TrustTunnel VPN support entirely
- Cleaned up all schemas, services, routes, models, tests, and docs
- Backend now exclusively supports WireGuard"
```

---

## Summary

| Phase | Tasks | Files Changed |
|-------|-------|---------------|
| Phase 0: Delete files | 1 | 8 deleted |
| Phase 1: Schemas & Config | 5 | 5 modified |
| Phase 2: DB Models | 3 | 3 modified |
| Phase 3: Core Services | 9 | 9 modified |
| Phase 4: Infrastructure | 6 | 6 modified |
| Phase 5: API Client | 1 | 1 modified |
| Phase 6: Main Entry | 1 | 1 modified |
| Phase 7: Tests | 6 | ~13 modified |
| Phase 8: Documentation | 7 | 7 modified |
| Phase 9: Final Verification | 5 | - |
| **Total** | **44 tasks** | **~38 files** |

**Estimated time:** 2-4 hours
**Risk level:** Medium (requires backend service restart)
