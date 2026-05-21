# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

## [0.26.0] - 2026-05-11

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
- 7 TrustTunnel methods from VpnAgentClient
- 4 Outline/TrustTunnel REST API endpoints
- All Outline/TrustTunnel-related tests (~400 lines)

### Changed
- `vpn_type` literals restricted to `"wireguard"` only
- Server registry no longer filters by Outline protocol
- Metrics service no longer ingests or queries Outline/TrustTunnel data
- All documentation updated to reflect WireGuard-only architecture

---

## [0.25.0] - 2026-04-07

### Added
- **TrustTunnel Deep Link Export** — `POST /vpn/keys` now returns `deeplink` field for TrustTunnel keys
  - Added `export_trusttunnel_deeplink()` to `VpnAgentClient`
  - Added `deeplink` field to `VpnKeyResponse` schema
  - Automatic deeplink export after key creation (graceful degradation on failure)

### Technical Details
- **Files Modified:** 4 (`vpn_agent_client.py`, `vpn.py` route, `vpn.py` schema, CHANGELOG)
- **Files Added:** 1 test in `test_vpn_agent_client.py`
- **New Field:** `deeplink: str` in `VpnKeyResponse` (empty for Outline/WireGuard)

---

## [0.24.0] - 2026-04-06

### Added
- **TrustTunnel VPN Protocol** — Full integration as first-class protocol alongside Outline and WireGuard
- **VpnAgentClient** — 6 new TrustTunnel methods: create/delete/export client, get metrics, add/remove rules
- **VpnService** — TrustTunnel key creation with auto-generated username/password, config export, saga rollback
- **TrustTunnelMetricModel** — Time-series metrics table with JSONB client_bytes
- **MetricsService** — TrustTunnel ingestion, query methods, cleanup
- **GET /vpn/servers/{server_id}/trusttunnel/metrics** — User-facing time-series endpoint
- **POST/DELETE /admin/servers/{server_id}/trusttunnel/rules** — Admin rules management

### Changed
- **usipipo-commons** dependency bumped to >=0.21.0 (TRUSTTUNNEL KeyType)

### Technical Details
- **Files Created:** 4 (model, migration, admin routes, agent client tests)
- **Files Modified:** 5 (vpn_agent_client, vpn_service, metrics_service, vpn routes, main.py)
- **Tests:** 338 unit tests passing (9 new TrustTunnel tests)
- **Alembic Migration:** 2026_04_06_0001 (trusttunnel_metrics table)

## [Unreleased]

## [0.23.3] - 2026-04-05

### Removed
- **Integration tests** — 22 files removed from `tests/integration/`. Moved to manual QA due to WireGuard `/etc/wireguard` permission errors on CI
- **Outline VPN unit tests** — `test_vpn_outline_metrics.py` and `test_vpn_outline_status.py` removed (filesystem permission errors on CI)

### Added
- **respx** dev dependency for E2E test HTTP mocking
- **E2E tests in release CI** — release workflow now runs `tests/unit` + `tests/e2e`

### Changed
- **Release workflow** — test job runs both unit and E2E tests on tag releases
- **pyproject.toml** — version bumped to 0.23.2

## [0.23.2] - 2026-04-05

### Fixed
- Removed `uv.lock` from `.dockerignore` (needed by Dockerfile for `uv sync --frozen`)

## [0.23.1] - 2026-04-05

### Fixed
- Pinned `usipipo-commons` to `>=0.19.0` temporarily during PyPI publish window for v0.20.0

## [0.23.0] - 2026-04-05

### Changed
- **AdminAuditLogModel** - Migrated `admin_telegram_id`/`target_user_telegram_id` to `admin_id`/`target_user_id` (UUID)
- **StaffRoleModel** - Added `admin_id` UUID column, made `telegram_id` nullable, `granted_by` → UUID
- **TicketModel** - FK from `users.telegram_id` → `users.id` for `user_id` and `resolved_by`
- **TicketMessageModel** - `from_user_id` from BigInteger → UUID
- **DataPackageModel** - `user_id` from BigInteger → UUID
- **UserModel** - `telegram_id` default handling for nullable

### Services
- **wallet_management_service** - Removed `telegram_id` param, uses `user_id` only
- **wallet_pool_service** - Removed `telegram_id` param from all methods
- **subscription_payment_service** - `_send_stars_invoice` uses `user_id`, looks up `telegram_id` internally
- **referral_service** - Renamed `register_referral_by_telegram_id` → `register_referral_by_user_id`
- **admin_key_service** - Uses `user.id` instead of `user.telegram_id`
- **admin_user_service** - Uses `user.id` instead of `user.telegram_id`
- **admin_vpn_key_service** - Audit logging uses `admin_id` UUID
- **ticket_service** - All `user_id` params from `int` → `UUID`

### API Routes
- **wallets.py** - Removed `telegram_id` from wallet service calls
- **referrals.py** - Uses `user_id` for referral registration
- **tickets.py** - Uses `current_user.id` instead of `current_user.telegram_id`
- **admin.py** - Path params changed from `int` to `UUID`
- **data_packages.py** - Uses `current_user.id`
- **consumption_invoices.py** - Path params from `telegram_id: int` → `user_id: UUID`
- **admin_vpn_keys.py** - UUID throughout

### Schemas
- **referral.py** - `ReferralApplyOnRegisterRequest.user_id: UUID` (was `telegram_id: int`)
- **ticket.py** - `user_id`, `resolved_by`, `from_user_id` now `UUID`
- **admin.py** - `user_id` now `UUID`
- **admin_vpn_keys.py** - `user_id` now `UUID`, removed `user_telegram_id`
- **consumption_invoice.py** - `id` now `UUID | None`

### Database
- **Alembic migration** - `2026_04_05_0001_user_id_universal_gaps.py`
  - Backfills UUID columns from existing telegram_id via users table join
  - Drops old BigInteger columns
  - Creates indexes on new UUID columns
  - Full downgrade path

### Tests
- 368 unit tests passing
- Updated test fixtures for UUID user_id
- Updated referral service tests (renamed methods)
- Updated ticket repository/service tests
- Updated data package repository tests

### Technical Details
- **Files Modified:** 30+ files
- **Lines Added:** ~1700 lines
- **Tests:** 368 unit tests (100% passing)
- **Mypy:** 0 new errors (6 pre-existing in metrics_service.py)

### Backend Integration
- All API endpoints now use `user_id: UUID` for user identification
- `/referrals/apply-on-register` now expects `user_id` instead of `telegram_id`
- JWT structure unchanged (`sub` claim already contains `user_id`)

## [Unreleased]

### Added
- **server_name field in VpnKeyResponse** - VPN key responses now include server name
  - All VPN key endpoints populate `server_name` from server registry
  - Fixes bot display showing "N/A" instead of actual server name
- **Pydantic v2 migration** - Replaced deprecated `class Config` with `model_config = ConfigDict` in `payment.py` and `device.py`
- **POST /referrals/apply-on-register** - Apply referral code during registration (unauthenticated)
  - New endpoint for unauthenticated clients to apply referral codes
  - Idempotent design: safe to call multiple times without duplicates
  - Awards credits to both referrer (100) and new user (50)
  - Returns 200 even for 'already_referred' (not an error)
- **ReferralService.register_referral_by_telegram_id()** - New service method for telegram-based referral lookup
- **ReferralApplyOnRegisterRequest/Response** - New Pydantic schemas for unauthenticated referral application

### Technical Details
- **Files Modified:** 4 (vpn.py schema, vpn.py routes, payment.py, device.py)
- **Files Created:** 1 (VpnKeyResponse tests)
- **Tests:** 4 new tests for VpnKeyResponse with server_name (all passing)

---

## [0.19.0] - 2026-04-04

### 🐛 Bug Fixes

**WireGuard Client Configuration Address Mask:**
- ✅ Fix client config `Address = x.x.x.x/24` → `Address = x.x.x.x/32`
- ✅ Each WireGuard peer must use `/32` (single host) not `/24` (subnet)
- ✅ Fixes client connectivity issues caused by incorrect subnet mask

### Technical Details
- **Files Modified:** 1 file (`wireguard_client.py`)
- **Lines Changed:** 1 line

---

## [0.18.0]

### Changed
- **Referral integration tests** - Added 4 new tests for apply-on-register endpoint
- **Referral unit tests** - Added 5 new tests for register_referral_by_telegram_id method
- **E2E tests** - Added comprehensive end-to-end test for complete referral flow with idempotency verification

### Technical Details
- **Files Created:** 2 files (test_referral_e2e.py, test_referral_schemas.py)
- **Files Modified:** 4 files (referral_service.py, referrals.py, test_referral_service.py, test_referrals.py)
- **Lines Added:** ~560 lines
- **Tests:** 15 tests (6 schema + 5 unit + 4 integration + 1 e2e, 100% passing)

### Backend Integration
- POST /api/v1/referrals/apply-on-register - Apply referral code during registration (no auth)

### Fixed
- **vpn_key_model**: Add missing `server_id`, `latency_ms`, and `last_latency_check` fields to SQLAlchemy model
  - Fields existed in database migration (`add_server_id_to_vpn_keys`) but were not mapped in model
  - `server_id` now persists correctly when creating VPN keys
  - `to_entity()` and `from_entity()` now map all three fields
  - Backward compatible: `server_id` remains nullable for legacy keys
  - Added integration tests for server_id persistence round-trip

## [0.16.0] - 2026-04-03

### Added
- **Outline Metrics REST API Endpoints** - Real-time VPN server metrics via REST API
  - `GET /api/v1/vpn/servers/{id}/outline` - Current Outline server status
  - `GET /api/v1/vpn/servers/{id}/outline/metrics?since=24h` - Historical metrics with time range filter (1h, 24h, 7d, 30d)
  - JWT authentication required
  - Authorization: users can only access servers where they own VPN keys

- **Outline Metrics Database Storage** - Time-series metrics ingestion
  - Updated `MetricsService.ingest_agent_metrics()` to extract and store Outline data from agent payload
  - `outline_metrics` table with JSONB columns for time-series data and top consumers
  - Alembic migration `dfe1fcfb5354` for table creation with optimized indexes

- **Pydantic Schemas for Outline Metrics** - API response validation
  - `OutlineStatusResponse` - Current server status schema
  - `OutlineMetricsResponse` - Historical metrics with time-series, top consumers, and summary
  - Supporting schemas: `OutlineTimeSeriesPoint`, `OutlineConsumerEntry`, `OutlineSummary`

- **Comprehensive Test Coverage** - 104 tests for Outline metrics functionality
  - 10 unit tests for MetricsService Outline ingestion
  - 9 integration tests for `/outline` status endpoint
  - 30 integration tests for `/outline/metrics` endpoint
  - 36 schema validation tests
  - 19 existing VPN server tests (no regressions)

### Changed
- **MetricsService** - Fixed Outline data source from `vpn.outline` to top-level `outline` key in agent payload
- **Error isolation** - Outline metric extraction failures no longer prevent ServerMetricModel from being saved

### Technical Details
- All endpoints follow existing project patterns and conventions
- Helper functions: `parse_time_range()` and `calculate_uptime()` for time-series processing
- Coverage: 99% schemas, 74% routes (remaining 26% covered by separate CRUD test files)

---

## [0.15.0] - 2026-04-02

### Added
- **E2E Test Suite** - Complete end-to-end testing infrastructure
  - E2E test framework with pytest fixtures
  - Factory pattern for test data (User, VPN Key, VPN Server)
  - VPN key lifecycle flow tests (creation, list operations, deletion)
  - Integration with existing test infrastructure

- **VPN Service Health Checks** - Server health validation during key creation
  - Automatic health check before creating VPN keys
  - Fallback to alternative servers when health check fails
  - Unit tests for health check logic

- **Saga Rollback Pattern** - Distributed transaction rollback for VPN key creation
  - Automatic cleanup on failure during key creation
  - Rollback for both Outline and WireGuard protocols
  - Comprehensive error handling and logging
  - Unit tests for rollback scenarios

- **Rate Limiter** - API rate limiting utility
  - JWT-based user identification
  - IP-based fallback for unauthenticated requests
  - Custom rate limit exceeded handler with JSON responses
  - Retry-After header support

- **Agent API Key Encryption** - Security enhancement for VPN agent API keys
  - Migration to encrypt existing plaintext API keys
  - Fernet encryption with environment-based key management
  - Base64 URL-safe encoding for storage
  - Heuristic detection of already-encrypted values

### Technical Details
- **Files Created:** 15 files
  - `tests/e2e/` - E2E test suite (11 files, ~1100 lines)
  - `tests/unit/services/test_vpn_service_health_check.py` (232 lines)
  - `tests/unit/services/test_vpn_service_saga_rollback.py` (624 lines)
  - `src/shared/rate_limiter.py` (77 lines)
  - `migrations/versions/2026_04_01_0000_encrypt_existing_agent_api_keys.py` (148 lines)
  - `.env.example` - Environment configuration reference
- **Lines Added:** ~2400 lines
- **Tests:** E2E flows + unit tests for health checks and saga rollback

### Changed
- **Documentation Structure** - Moved implementation documentation to central docs repo
  - ENCRYPTION_TEST_PLAN.md → usipipo-docs/plans/
  - SAGA_ROLLBACK_IMPLEMENTATION.md → usipipo-docs/plans/
  - Keeps backend repo focused on code and essential docs (README, CHANGELOG, etc.)

### Security
- **Agent API Key Encryption** - All agent API keys now encrypted at rest
  - Prevents credential exposure in case of database breach
  - Migration automatically encrypts existing plaintext keys
  - Requires ENCRYPTION_KEY environment variable

### Quality Gates
- ✅ All tests passing (E2E + unit + integration)
- ✅ Ruff linting and formatting clean
- ✅ Mypy type checking clean
- ✅ Bandit security scan clean
- ✅ Pre-commit hooks: all passing

---

## [0.14.0] - 2026-03-31

### Added
- **VPN Server Selection** - Users can now select their preferred VPN server during key creation
  - New `GET /api/v1/vpn/servers` endpoint for fetching available servers
  - Server list with real-time load indicators (🟢 low, 🟡 medium, 🔴 high)
  - Protocol filtering (Outline/WireGuard)
  - Top 5 recommended servers (lowest load)
  - Optional `server_id` parameter in VPN key creation
  - Auto-selection fallback when no server specified

### Changed
- **VPN Key Creation Flow** - Enhanced to support server selection
  - Added `server_id` field to `CreateVpnKeyRequest` schema (optional)
  - Updated `VpnService.create_key()` to accept and validate server selection
  - Server validation: checks existence and online status
  - Backward compatible: existing behavior preserved when server_id not provided

### Technical Details
- **Files Created:** 4 files
  - `tests/shared/schemas/test_vpn_schemas.py` (228 lines)
  - `tests/unit/services/test_server_registry_service.py` (193 lines)
  - `tests/infrastructure/api/v1/routes/test_vpn_servers.py` (312 lines)
  - `tests/unit/services/test_vpn_service_server_id.py` (178 lines)
- **Files Modified:** 5 files
  - `src/shared/schemas/vpn.py` - Added VpnServerResponse, VpnServersListResponse
  - `src/core/application/services/server_registry_service.py` - Added get_servers_for_user()
  - `src/core/application/services/vpn_service.py` - Added server_id parameter
  - `src/infrastructure/api/v1/routes/vpn.py` - Added GET /servers endpoint
  - `src/infrastructure/api/v1/routes/vpn.py` - Updated create_key to pass server_id
- **Lines Added:** ~900 lines (code + tests)
- **Tests:** 64 server-related tests (100% passing)

### Backend API Endpoints
- `GET /api/v1/vpn/servers?protocol=outline|wireguard` - Get available servers with load indicators
  - Authentication: JWT required (user token)
  - Response: servers list + recommended (top 5)
  - Load levels: low (0-50%), medium (51-80%), high (81-100%)

### Quality Gates
- ✅ All tests passing (64 new tests + existing suite)
- ✅ Ruff clean (linting + formatting)
- ✅ Mypy clean (type checking)
- ✅ Bandit clean (security scan)
- ✅ Pre-commit hooks: all passing

### Impact
- ✅ User-facing feature: server transparency and control
- ✅ Load balancing: users can select servers with lowest load
- ✅ Backward compatible: existing API clients unaffected
- ✅ No breaking changes

## [0.13.1] - 2026-03-30

### Fixed
- **User Profile Endpoint** - Added missing fields required by usipipo-commons User entity
  - Added `updated_at` field to `/api/v1/users/me` response
  - Added `referred_by` field to `/api/v1/users/me` response
  - Fixes bot integration tests failing with KeyError

### Impact
- ✅ Fixes telegram-bot integration tests (11 failing tests now passing)
- ✅ Ensures compatibility with usipipo-commons>=0.14.0 User entity
- ✅ Backend API now returns complete user data

### Technical Details
- **Files Modified:** 1 file (`src/infrastructure/api/v1/routes/users.py`)
- **Fields Added:** 2 fields (`updated_at`, `referred_by`)
- **Breaking Changes:** None (additive only)

### Testing
- ✅ Bot integration tests: 367/367 passing (was 356 passing)
- ✅ Backend tests: All existing tests still passing

## [0.13.0] - 2026-03-30

### 🎯 Admin VPN Keys CRUD API

**New feature:** Complete CRUD API for VPN key management with role-based access control and audit logging.

#### Database Changes
- **admin_audit_logs** - New table for audit trail
  - `id`, `timestamp`, `admin_telegram_id`, `admin_username`
  - `operation`, `target_type`, `target_id`, `target_user_telegram_id`
  - `details` (JSONB), `ip_address` (INET)
  - `success`, `error_message`, `created_at`
  - Indexes on timestamp, admin, operation, and target

- **staff_roles** - New table for role-based access control
  - `id`, `telegram_id` (unique), `username`
  - `role` (support/admin), `granted_by`, `granted_at`
  - `is_active`, `created_at`, `updated_at`
  - Indexes on telegram_id and role

#### API Endpoints
- `GET /api/v1/admin/vpn-keys` - List all keys with pagination and filters
- `GET /api/v1/admin/vpn-keys/{key_id}` - Get key details
- `GET /api/v1/admin/users/{telegram_id}/keys` - List keys by user
- `POST /api/v1/admin/vpn-keys` - Create key manually (Admin only)
- `PATCH /api/v1/admin/vpn-keys/{key_id}/toggle` - Toggle status (Support+)
- `PATCH /api/v1/admin/vpn-keys/{key_id}/data-limit` - Update data limit (Admin only)
- `PATCH /api/v1/admin/vpn-keys/{key_id}/reset-usage` - Reset usage (Admin only)
- `POST /api/v1/admin/vpn-keys/{key_id}/regenerate` - Regenerate config (Admin only)
- `DELETE /api/v1/admin/vpn-keys/{key_id}` - Delete key (Admin only)

#### Technical Details
- **Files Created:** 16 files
- **Files Modified:** 6 files
- **Lines Added:** ~2500 lines
- **Tests:** 27 tests (15 unit + 12 integration, 100% passing)

#### Role-Based Access Control
- **Support role:** Read operations + toggle key status
- **Admin role:** Full CRUD operations including create, update limits, reset usage, regenerate, delete

#### Audit Logging
- All admin operations logged to admin_audit_logs table
- Includes operation type, target, admin details, success/failure, and error messages

### 🧪 Testing
- Unit tests for AdminVpnKeyService
- Integration tests for all API endpoints
- Tests for authentication and authorization requirements

---

## [0.12.0] - 2026-03-29

### 🤖 VPN Agent Auto-Registration

**New feature:** VPN agents can now automatically register with the backend on first startup, eliminating manual database entries.

#### Database Changes
- **agent_api_keys** - New table for API key management
  - `id`, `api_key_hash` (SHA-256 hashed)
  - `status` (active, used, revoked, expired)
  - `server_id` FK → vpn_servers
  - `created_at`, `used_at`, `expires_at`
  - `description`, `created_by`
  - Check constraint on status values
  - Indexes on `api_key_hash` and `status`

- **vpn_servers** - Added metadata columns
  - `agent_version` - Agent software version
  - `os_type` - Operating system (linux, windows, etc.)
  - `os_arch` - Architecture (amd64, arm64, etc.)
  - `last_registration_ip` - IP address at registration (INET type)

#### New Services
- **AgentRegistrationService** - Handles agent registration and API key management
  - `generate_api_key()` - Generate secure API keys (format: `agent_<32 hex chars>`)
  - `hash_api_key()` - SHA-256 hashing
  - `create_api_key()` - Store hashed keys in database
  - `validate_api_key()` - Verify key validity (not expired/revoked/used)
  - `register_agent()` - Create server record from agent metadata

#### New API Endpoints

**Agent Registration:**
- `POST /api/v1/servers/register-agent` - Register new agent
  - Authentication: `X-API-Key` header
  - Auto-collects: hostname, IP, country, OS, version
  - Returns: `server_id` (UUID)
  - Idempotent: same key returns existing server

- `GET /api/v1/servers/register-agent?api_key=...` - Check registration status
  - Returns existing `server_id` if registered
  - 404 if not yet registered

**Admin API Key Management:**
- `POST /api/v1/admin/agent-api-keys` - Generate new API key
  - Authentication: Admin JWT
  - Optional: `description`, `expires_in_days`
  - Returns: `api_key` (shown once only!)

- `GET /api/v1/admin/agent-api-keys` - List API keys
  - Filter by `status` (active, used, revoked, expired)
  - Pagination: `limit`, `offset`

#### New Schemas
- `AgentRegistrationRequest` - Agent metadata
- `AgentRegistrationResponse` - Registration result
- `GenerateApiKeyRequest/Response` - Key generation
- `ApiKeyListResponse` - Key listing

#### Security Features
- ✅ API keys hashed with SHA-256 before storage
- ✅ Keys shown only once during generation
- ✅ Single-use keys (status: active → used)
- ✅ Optional expiration dates
- ✅ Admin-only key generation
- ✅ Rate limiting on all endpoints

#### Agent Workflow
```
1. Admin generates API key via /admin/agent-api-keys
2. Admin copies key to agent .env (AGENT_API_KEY=...)
3. Agent starts → collects metadata (hostname, IP, country, etc.)
4. Agent POST /servers/register-agent → Backend
5. Backend validates key → creates server → returns UUID
6. Agent saves UUID to .env (SERVER_ID=...)
7. Agent sends metrics every 1 minute using UUID
```

#### Tests
- Integration tests for registration flow
- Tests for API key generation and listing
- Tests for duplicate registration prevention
- Tests for invalid/expired key handling

#### Documentation
- Auto-Registration Guide (`AUTO-REGISTRATION-GUIDE.md`)
- Updated `.env.example` with new variables

### 📦 Dependencies
- No new external dependencies

### ⚠️ Breaking Changes
- None (backward compatible with existing agents)

### 📝 Related
- Enables大规模 VPN Agent deployment (200+ countries)
- Part of multi-country VPN orchestration architecture
- See: `usipipo-agent/AUTO-REGISTRATION-GUIDE.md`

---

## [0.11.0] - 2026-03-28

### 🌍 Multi-Server Orchestration Support

#### Dependencies Updated
- **usipipo-commons**: `0.12.0` → `0.13.0`
  - Adds `Server` entity for multi-country VPN server management
  - Adds `ServerStatus` enum (online, offline, maintenance)
  - Enables VPN Agent architecture with centralized orchestration

#### Database Migrations
- **create_vpn_servers** - New table for VPN server registry
  - `id`, `name`, `country_code`, `country_name`, `city`, `region`
  - `agent_url`, `agent_api_key` - Agent communication
  - `supports_outline`, `supports_wireguard`, `supports_trust_tunnel`
  - `status`, `max_connections`, `current_connections`
  - `last_heartbeat_at` - Health monitoring

- **create_server_metrics** - Time-series metrics table
  - System metrics: CPU, memory, disk, network
  - VPN metrics: active keys/peers, bytes transferred
  - Latency metrics: avg, p95, p99
  - Indexed by `(server_id, timestamp DESC)` for efficient queries

- **add_server_id_to_vpn_keys** - Modify existing vpn_keys table
  - Add `server_id` foreign key → vpn_servers
  - Add `latency_ms` for performance tracking
  - Add `last_latency_check` timestamp

### 🔌 Backend Services (Pending Implementation)
- ServerRegistry Service - Server CRUD and selection
- VpnAgentClient - HTTP client for remote agents
- MetricsService - Ingest and query agent metrics
- VpnService modified to use agents instead of local VPN

### 📈 Related
- Part of VPN Agent implementation plan
- Enables multi-country deployment (USA, Germany, Belgium)
- Prepares for 200+ countries scalability

---

## [0.10.0] - 2026-03-24

### 🎉 Telegram Bot Invisible Authentication

#### New Authentication Endpoints
- **POST /api/v1/auth/telegram/auto-register** - Invisible auth for Telegram Bot
  - Creates or finds user by telegram_id automatically
  - Returns JWT tokens without user intervention
  - Used exclusively by Telegram Bot for seamless authentication

- **POST /api/v1/auth/refresh** - Token refresh endpoint (updated)
  - Now uses typed `RefreshTokenRequest` schema
  - Returns new access and refresh tokens
  - Enables silent token renewal for all clients

#### New Schemas
- `TelegramAutoRegisterRequest` - Auto-registration request with telegram_id
- `RefreshTokenRequest` - Typed refresh token request (replaces dict)

### Code Quality Improvements
- Fix E712: Avoid equality comparisons to `True` in device_repository.py
- Fix W293: Remove whitespace from blank lines
- Fix mypy unused type ignore comments
- All quality checks passing:
  - mypy: 0 errors in 143 files
  - ruff: All checks passed
  - pytest: All tests passing
  - bandit: No security issues

### Files Modified
- `src/infrastructure/api/v1/routes/auth.py` - New auto-register endpoint
- `src/shared/schemas/auth.py` - New request schemas
- `src/infrastructure/persistence/repositories/device_repository.py` - Fix E712
- `src/infrastructure/persistence/models/device_model.py` - Fix W293

### Integration
- Works with Telegram Bot PR: uSipipo-Team/usipipo-telegram-bot#3
- Enables invisible authentication flow (no manual login required)
- Redis-based token storage with 30-day refresh tokens

---

## [0.9.0] - 2026-03-22

### 🎉 Device Registration for Push Notifications

#### Device Management Endpoints
- **POST /api/v1/devices/register** - Register new device for push notifications
- **GET /api/v1/devices** - List user's registered devices
- **DELETE /api/v1/devices/{id}** - Remove device
- **POST /api/v1/devices/{id}/deactivate** - Temporarily deactivate device

#### Platform Support
- Android (FCM push tokens)
- iOS (FCM push tokens)
- Windows (future)
- Linux (future)
- Telegram (no push token needed)

### Database Changes

#### New Table: devices
- Stores device registration info
- Tracks platform, push_token, app_version
- Supports multiple devices per user
- Migration: 838b09c44981

### Files Created

**Models:**
- device_model.py: DeviceModel with platform support

**Repositories:**
- device_repository.py: Full CRUD operations

**Schemas:**
- DeviceRegisterRequest, DeviceResponse, DeviceListResponse

**Routes:**
- devices.py: 4 endpoints for device management

### Code Quality

**Centralized SQLAlchemy rowcount type handling:**
- Created get_execute_rowcount() helper in database.py
- Eliminates 17 duplicate type: ignore comments
- DRY, documented, maintainable

### Migration Required
```bash
uv run alembic upgrade head
```

---

## [0.8.0] - 2026-03-22

### 🎉 Multi-Client Authentication

#### Email/Password Authentication
- **POST /auth/register** - Register with email/password
- **POST /auth/login** - Login with email/password
- Password hashing with bcrypt
- Auth providers table for credential storage

#### Telegram Code Authentication
- **POST /auth/telegram/request-code** - Request 6-digit auth code
- **POST /auth/telegram/verify** - Verify code and get tokens
- Codes sent via Telegram Bot API
- 5-minute expiry, one-time use

#### JWT Refresh Tokens
- **POST /auth/refresh** - Refresh access token
- Access token: 30 minutes
- Refresh token: 30 days
- Token revocation via Redis blacklist

#### Updated Telegram Auth
- **POST /auth/telegram** - Now returns refresh tokens
- **POST /auth/logout** - Updated token expiry

### Database Changes

#### New Table: auth_providers
- Stores authentication methods per user
- Supports multiple auth methods (Telegram, email, Google, etc.)
- Password hash storage for email auth
- Migration: d65d5b972e88

### Files Created

**Models:**
- auth_provider_model.py

**Repositories:**
- auth_provider_repository.py
- i_auth_provider_repository.py

**Services:**
- telegram_auth_code_service.py
- client_telegram_bot.py

**Schemas:**
- EmailRegisterRequest, EmailLoginRequest
- TelegramCodeRequest, TelegramVerifyRequest
- RefreshTokenRequest, AuthResponse, CodeSentResponse

### Breaking Changes
- JWT tokens now include refresh_token
- Token expiry changed from 24h to 30min (access) + 30d (refresh)

### Migration Required
```bash
uv run alembic upgrade head
```

---

## [0.7.0] - 2026-03-22

### 🚀 BREAKING CHANGE - VpnKey + Enum Unification (Week 2)

**Align VpnKey model with usipipo-commons v0.12.0 - migrate id to UUID and add KeyStatus.**

#### Models
- **vpn_key_model.py**:
  - `id: Mapped[str]` → `Mapped[UUID]`
  - Added `status: Mapped[KeyStatus]` column (ACTIVE, EXPIRED, REVOKED, PENDING)
  - Updated `to_entity()`/`from_entity()` for status field

#### Migrations
- **c28f4257bb35**: vpn_keys id str → UUID, add status column
  - Adds status column with default 'active'
  - Converts id from string to UUID
  - Creates key_status enum type
  - Adds index on status

#### Dependencies
- usipipo-commons>=0.12.0

### Impact
- ✅ Consistent with commons v0.12.0
- ✅ VpnKey always has valid UUID
- ✅ Full key lifecycle states via status column
- ✅ Backward compatible: is_active property in entity

### Migration Required
```bash
uv run alembic upgrade head
```

---

## [0.6.0] - 2026-03-22

### 🚀 BREAKING CHANGE - Multi-Client Architecture (Week 1)

**Migrate all user_id from int (Telegram ID) to UUID for Android/Desktop/Web support.**

#### Models
- **subscription_plan_model.py**: `user_id: Mapped[int]` → `Mapped[UUID]` with FK to users.id
- **subscription_transaction_model.py**: `user_id: Mapped[int]` → `Mapped[UUID]` with FK to users.id

#### Services
- **subscription_service.py**: All signatures `user_id: int` → `uuid.UUID`
- **subscription_payment_service.py**: All signatures → `uuid.UUID`, added Telegram Stars lookup
- **consumption_billing_service.py**: All signatures → `uuid.UUID`
- **consumption_billing_activation.py**: All signatures → `uuid.UUID`
- **consumption_billing_cycle.py**: All signatures → `uuid.UUID`
- **consumption_invoice_service.py**: All signatures → `uuid.UUID`

#### Repositories
- **subscription_repository.py**: All signatures → `uuid.UUID`
- **consumption_billing_repository.py**: **NEW** - Full implementation
- **consumption_invoice_repository.py**: All signatures → `uuid.UUID`

#### Interfaces
- **i_subscription_repository.py**: All signatures → `uuid.UUID`
- **i_consumption_billing_repository.py**: All signatures → `uuid.UUID`
- **i_consumption_invoice_repository.py**: All signatures → `uuid.UUID`

#### Routers
- **subscriptions.py**: `current_user.telegram_id` → `current_user.id`
- **consumption_invoices.py**: All `user_id: int` → `uuid.UUID`, `current_user.id`

#### Migrations
- **ef961ce7ef38**: `subscription_plans.user_id` int → UUID with FK
- **ef961ce7ef38**: `subscription_transactions.user_id` int → UUID with FK
- Backfill: Data migrated from `users.telegram_id`

### Impact
- ✅ Android clients without Telegram can now activate subscriptions
- ✅ Desktop (Windows/Linux) clients without Telegram supported
- ✅ Web Mini App clients without Telegram supported
- ✅ Telegram Bot remains backward compatible

### Migration Required
```bash
uv run alembic upgrade head
```

---

## [0.5.0] - 2026-03-22

### 🔒 SECURITY - Complete Security Audit (A-01 to A-12)

#### Critical Security Fixes

- **A-01/C-01: Traceback Exposure** - Removed traceback from production error responses
  - Production now returns generic "Internal server error"
  - Development mode still shows detailed errors
  - Prevents information disclosure attacks

- **A-02/C-03: HTTP Security Headers** - Added comprehensive security middleware
  - `TrustedHostMiddleware` - Allowed hosts validation
  - `CORSMiddleware` - Configured CORS origins
  - `SecurityHeadersMiddleware` - X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy

- **A-03/C-02: API Documentation** - Disabled Swagger/ReDoc in production
  - `/docs`, `/redoc`, `/openapi.json` only available in DEBUG mode
  - Prevents API reconnaissance attacks

- **A-04/C-08: SQL Logging** - Fixed SQLAlchemy DEBUG echo
  - Added `DB_ECHO` configuration (default: False)
  - SQL logging only in explicit development mode
  - Prevents SQL query leakage in logs

- **A-05/C-04: Rate Limiting** - Implemented with SlowAPI
  - Auth endpoints: 5 requests/minute
  - Admin endpoints: 30 requests/minute
  - Default: 60 requests/minute
  - Prevents brute force and DoS attacks

- **A-06/C-05: JWT Token Revocation** - Redis-backed blacklist
  - `/api/v1/auth/logout` endpoint
  - Token revocation check on every request
  - TTL-based expiration matching JWT expiry
  - Connection pooling for production performance

- **A-07/C-06: Command Injection** - Fixed WireGuard shell=True
  - Changed to subprocess with list arguments
  - Removed shell interpolation
  - Using stdin for wg pubkey generation
  - Prevents remote code execution

- **A-08/C-07/C-12: Webhook Verification** - Telegram IP validation
  - Official Telegram IP ranges verification
  - Logging for suspicious requests
  - Prevents fraudulent webhook submissions

- **A-09/C-09: SSL Pinning** - Outline certificate pinning
  - `OUTLINE_CERT_PEM` configuration
  - Automatic certificate extraction in install.sh
  - Prevents MITM attacks on Outline API

- **A-10/C-10: Secure Defaults** - Production-first configuration
  - `DEBUG=False` by default
  - `APP_ENV=production` by default
  - Removed unused `SECRET_KEY`

- **A-11: Dependency Cleanup** - Removed unused SECRET_KEY
  - Cleaned up configuration
  - Documented JWT_SECRET as primary key

- **A-12/C-11: Vulnerable Dependency** - Removed python-jose
  - Only using pyjwt (actively maintained)
  - Reduces attack surface
  - Removes CVE-2024-33664 vulnerability

### 🧹 CODE CLEANUP (B-01 to B-09)

#### Structure Improvements

- **B-01: Empty Modules** - Removed empty directories
  - Deleted: `src/core/domain/entities/`
  - Deleted: `src/infrastructure/cache/`
  - Deleted: `src/shared/utils/`

- **B-02: Duplicate Functions** - Removed `get_session()`
  - All code now uses `get_db()`
  - Updated: payments.py, billing.py, tests/conftest.py

- **B-03: init_db() Implementation** - Added real functionality
  - Verifies database connection on startup
  - Logs connection status

- **B-04: Cache Cleanup** - Removed __pycache__ directories
  - Added to .gitignore
  - Cleaned from repository

- **B-05: Hardcoded Values** - Fixed expires_in
  - Now uses `settings.JWT_EXPIRATION_HOURS * 3600`
  - Removed hardcoded 86400

- **B-06: Webhook Anti-Pattern** - Fixed DB session handling
  - Crypto webhook: Proper dependency injection
  - Telegram Stars webhook: Context manager

- **B-07: Import Organization** - Fixed local imports
  - Moved imports to top level
  - Removed inline imports

- **B-08/B-09: Service Review** - Verified services
  - billing_service.py: Has real implementation
  - notification_service.py: Has real implementation

### 📦 Dependencies

#### Added
- `slowapi>=0.1.9` - Rate limiting
- `redis>=5.0.0` - JWT token blacklist

#### Removed
- `python-jose[cryptography]>=3.3.0` - Vulnerable, unused

### ⚙️ Configuration

#### New Settings
```python
# Rate limiting
RATE_LIMIT_ENABLED: bool = True
RATE_LIMIT_DEFAULT: str = "60/minute"
RATE_LIMIT_AUTH: str = "5/minute"
RATE_LIMIT_ADMIN: str = "30/minute"

# Redis
REDIS_MAX_CONNECTIONS: int = 10
REDIS_SOCKET_TIMEOUT: float = 5.0
REDIS_RETRY_ON_TIMEOUT: bool = True

# Database
DB_ECHO: bool = False

# SSL Pinning
OUTLINE_CERT_PEM: str = ""  # PEM certificate
```

#### Secure Defaults
- `APP_ENV: str = "production"` (was "development")
- `DEBUG: bool = False` (was True)

### 🚀 New Endpoints

- **POST /api/v1/auth/logout** - JWT token revocation

### 🔧 Infrastructure

#### install.sh Improvements
- Automatic SSL certificate extraction
- `OUTLINE_CERT_PEM` auto-populated
- `extract_vpn_vars()` includes certificate

#### example.env Updates
- Added `OUTLINE_CERT_PEM` placeholder
- Added Redis configuration section
- Added rate limiting configuration

### 🧪 Testing

- All unit tests passing
- Integration tests passing
- Security scan (bandit) clean
- Type checking (mypy) clean
- Linting (ruff) clean

---

## [0.4.0] - 2026-03-22

### ✨ Added

#### Documentation
- **Complete API Documentation** - Full endpoint reference with examples
- **GitHub Wiki** - Public documentation site with 4 pages
  - Home.md - Main documentation hub
  - API-Reference.md - 50+ endpoints documented
  - Authentication.md - Auth guide with JavaScript/Python examples
  - Error-Codes.md - HTTP error reference
- **API.md** - Comprehensive API documentation in docs/ folder
- **AGENTS.md** - AI agent development guide
- **CONTRIBUTING.md** - Contribution guidelines
- **LICENSE** - MIT License

#### Testing
- **test_all_endpoints.py** - Complete endpoint test script
  - Tests for all authenticated endpoints
  - Automatic token generation
  - Coverage for VPN, Subscriptions, Payments, Referrals, Data Packages, Wallets, Tickets, Billing

#### API Endpoints
- **GET /api/v1/billing/usage** - User data usage tracking
- **GET /api/v1/billing/usage/{key_id}** - Per-key usage tracking
- **Consumption Invoices** - Full CRUD for consumption-based billing
  - POST /api/v1/invoices - Create invoice
  - GET /api/v1/invoices/{id} - Get invoice details
  - GET /api/v1/invoices/user/{user_id} - List user invoices
  - POST /api/v1/invoices/{id}/pay - Mark as paid
  - POST /api/v1/invoices/{id}/expire - Mark as expired
  - DELETE /api/v1/invoices/{id} - Delete invoice

#### Features
- **Billing Service** - Usage tracking and billing calculations
- **Consumption Billing** - Pay-as-you-go billing system
- **Invoice Management** - Complete invoice lifecycle

### 🔧 Changed

#### Database
- **vpn_keys table** - Changed user_id from INTEGER to UUID
  - Migration: `6f80ea3bfca9_change_vpn_keys_user_id_from_integer_to_.py`
  - Added foreign key to users.id
- **vpn_keys bytes columns** - Changed to BigInteger
  - `used_bytes`: INTEGER → BIGINT
  - `data_limit_bytes`: INTEGER → BIGINT
  - Migration: `a0fe055ac6cb_change_vpn_keys_bytes_columns_to_bigint.py`

#### Models
- **VpnKeyModel** - Updated user_id to UUID type
- **WalletModel** - Added TYPE_CHECKING import for UserModel forward reference

#### Services
- **VpnService** - Fixed entity attribute mapping
  - Changed `vpn_type` → `key_type` (KeyType enum)
  - Changed `status` → `is_active` (boolean)
  - Changed `config` → `key_data`
  - Changed `data_used_gb` → `used_bytes` / 1024³
  - Changed `data_limit_gb` → `data_limit_bytes` / 1024³
- **BillingService** - Fixed byte to GB conversion
  - Proper conversion: `bytes / (1024 ** 3)` for GB

#### Schemas
- **VpnKeyResponse** - Added computed_field for vpn_type alias
- **CreateVpnKeyRequest** - Changed vpn_type to KeyType enum

#### Repositories
- **VpnKeyRepository** - Fixed UUID comparison
  - Convert UUID to string for VARCHAR comparison: `str(key_id)`

#### Code Quality
- **Mypy** - Fixed all pre-existing errors
  - Removed unused `type: ignore` comments
  - Fixed decorator order (@property before @computed_field)
  - Added proper type hints

### 🐛 Fixed

#### Critical Bugs
- **referral_code generation** - Fixed length to fit VARCHAR(20)
  - Changed from `ref_{telegram_id}_{uuid[:8]}` (23 chars) to `ref_{uuid[:16]}` (20 chars)
- **VPN endpoint 500 errors** - Fixed entity/schema mismatch
  - VpnKey entity now uses correct attributes
  - Proper mapping between service layer and API responses
- **Billing usage endpoint** - Fixed attribute errors
  - Changed from `data_used_gb` to `used_bytes`
  - Proper byte to GB conversion

#### Type Errors
- **wallet_model.py** - Added TYPE_CHECKING import for UserModel
- **wallet_pool_repository.py** - Added `type: ignore[attr-defined]` for rowcount
- **Test files** - Added None checks for optional attributes

#### API Issues
- **Decorator order** - Fixed @computed_field and @property order in schemas
- **Response mapping** - Proper entity to schema conversion in all VPN endpoints

### 📦 Infrastructure

#### Wiki Deployment
- Enabled GitHub Wiki for documentation
- Automated wiki upload script (`upload_wiki.py`)
- 4 documentation pages published

#### Scripts
- **test_endpoints.py** - Basic endpoint testing
- **test_all_endpoints.py** - Comprehensive endpoint testing
- **test_telegram_auth.py** - Telegram auth debugging
- **upload_wiki.py** - Wiki documentation uploader

### 📝 Documentation

#### External (GitHub Wiki)
- Complete API reference with 50+ endpoints
- Authentication guide with code examples
- Error codes reference
- Quick start guide

#### Internal (docs/)
- API.md - Full endpoint documentation
- Updated DEPLOYMENT.md
- Updated ARCHITECTURE.md

### 🔒 Security

- Proper UUID handling to prevent SQL injection
- Type-safe byte calculations
- Validated all user inputs in invoice endpoints

---

## [0.3.1] - 2026-03-21

### 🔧 Changed

#### Database Migrations
- **Consolidated migrations** into single initial schema with UUID primary keys
- Replaced multi-step migration approach with unified schema
- All tables now use UUID primary keys for better distribution and security

#### Migration Files
- Remove: `001_consolidated_schema.py` (402 lines) - old consolidated migration
- Remove: `731a6e4ffeb3_add_subscription_transactions_table.py` (85 lines) - incremental migration
- Add: `a3c6f868712d_initial_schema_uuid.py` (340 lines) - new unified initial schema

#### Configuration
- Updated `alembic.ini` with organized migration file template options
- Updated `migrations/env.py` to import all models for proper autogenerate support
- Removed deprecated `migrations/versions/.gitkeep` file

#### Infrastructure
- Removed deprecated `deploy/usipipo-backend.service` systemd service file

### 📝 Technical Details

**Schema Changes:**
- All primary keys converted to UUID format
- Proper foreign key relationships with UUID references
- Consistent enum types across all tables
- Improved indexing strategy

**Tables Included:**
- users, vpn_keys, payments, data_packages
- crypto_orders, crypto_transactions, webhook_tokens
- subscription_plans, subscription_transactions
- consumption_billings, consumption_invoices
- tickets, ticket_messages, referrals, wallet_pools, wallets

---

## [0.3.0] - 2026-03-19

### ✨ Added

#### VPN Infrastructure
- **OutlineClient** - API REST client for Outline VPN (Shadowbox)
- **WireGuardClient** - Native WireGuard CLI client with caching
- Real VPN key generation (no more placeholders)
- Automatic key revocation on delete
- Usage metrics retrieval from VPN providers
- Peer management with IP allocation
- TLS certificate handling for Outline (self-signed support)

#### VPN Providers
- `src/infrastructure/vpn_providers/outline_client.py` - Outline API integration
- `src/infrastructure/vpn_providers/wireguard_client.py` - WireGuard native integration
- Context manager support for HTTP clients
- Connection pooling and timeout configuration

#### Infrastructure Scripts
- `scripts/install.sh` - Automated VPN server setup (Outline + WireGuard)
- `scripts/wg_server.sh` - WireGuard server installer
- `scripts/ol_server.sh` - Outline server installer
- `scripts/install-caddy.sh` - Caddy reverse proxy setup
- `scripts/setup-duckdns-caddy.sh` - Dynamic DNS configuration
- `scripts/check_ram_cleanup.sh` - System maintenance

#### Configuration
- VPN environment variables in `example.env`
- Outline API URL and certificate configuration
- WireGuard interface, port, and DNS settings
- Dynamic server IP detection
- Support for all variables generated by setup scripts

#### Service Updates
- `VpnService` now injects OutlineClient and WireGuardClient
- Real config generation for WireGuard ([Interface], [Peer])
- Real config generation for Outline (ss:// URLs with branding)
- External ID tracking for key management
- Graceful fallback when clients not configured

### 🔧 Changed

#### Dependencies
- Updated `usipipo-commons>=0.2.1` (Pydantic v2 migration)
- Added `httpx>=0.25.0` for async HTTP requests
- Added `ipaddress` for IP allocation logic

#### Configuration
- `src/shared/config.py` - Added VPN settings (OUTLINE_*, WG_*, SERVER_*)
- `example.env` - Complete VPN configuration template
- `.env` - Synced variables from monorepo setup

#### Service Layer
- `VpnService.__init__()` - Now accepts outline_client and wireguard_client
- `VpnService.create_key()` - Uses real VPN providers instead of placeholders
- `VpnService.delete_key()` - Revokes keys from VPN providers
- `VpnService.revoke_key()` - Marks keys as REVOKED and revokes from provider

#### Testing
- Tests now use 32-byte JWT secret (RFC 7518 compliant)
- Fixed asyncio.duration error (use timedelta instead)
- All 13 integration tests passing

### 📝 Documentation

- Updated `example.env` with VPN configuration examples
- Added script usage instructions
- Documented all environment variables

### 🔒 Security

- JWT_SECRET minimum 32 bytes (RFC 7518 compliance)
- Outline SSL verification toggle (for self-signed certs)
- WireGuard peer key validation
- Secure temp file handling for PSK files

### 🐛 Fixed

- `asyncio.duration` AttributeError (use `timedelta` instead)
- Pydantic v2 deprecation warnings in usipipo-commons
- f-string syntax error in VpnKeyLimitReachedError
- Cache TTL comparison for WireGuard metrics

---

## [0.2.0] - 2026-03-19

### ✨ Added

#### Authentication
- **POST /api/v1/auth/telegram** - Telegram WebApp authentication endpoint
- JWT token generation and validation
- Telegram initData validation for secure authentication
- User auto-creation on first login

#### VPN Management
- **GET /api/v1/vpn/keys** - List user's VPN keys
- **POST /api/v1/vpn/keys** - Create new VPN key (WireGuard/Outline)
- **GET /api/v1/vpn/keys/{id}** - Get VPN key details
- **PUT /api/v1/vpn/keys/{id}** - Update VPN key
- **DELETE /api/v1/vpn/keys/{id}** - Delete/revoke VPN key
- VPN key limit enforcement (MAX_KEYS_PER_USER)

#### Architecture
- Hexagonal architecture implementation
- Domain-driven design patterns
- Repository pattern for data access
- Service layer for business logic

#### Infrastructure
- SQLAlchemy models for User and VpnKey
- Async database repositories
- Docker Compose configuration (Backend + PostgreSQL + Redis)

#### Security
- JWT-based authentication
- Telegram WebApp signature validation
- Password-less authentication flow
- Role-based access control (admin endpoints)

#### Testing
- Integration tests for auth endpoints
- Integration tests for VPN endpoints
- Pytest fixtures for test database
- Test coverage configuration (80% minimum)

#### Code Quality
- Pre-commit hooks (ruff, mypy, bandit, pytest)
- Ruff for linting and formatting
- Mypy for static type checking
- Bandit for security vulnerability scanning
- GitHub Actions CI/CD pipeline

### 🔧 Changed

#### Project Structure
```
src/
├── core/
│   ├── domain/
│   │   ├── entities/       # Domain entities (from usipipo-commons)
│   │   └── interfaces/     # Repository interfaces
│   └── application/
│       ├── services/       # Application services (business logic)
│       └── exceptions/     # Domain exceptions
├── infrastructure/
│   ├── api/v1/
│   │   ├── routes/         # API route handlers
│   │   └── deps.py         # Dependency injection
│   └── persistence/
│       ├── models/         # SQLAlchemy models
│       └── repositories/   # Repository implementations
└── shared/
    ├── security/           # JWT, Telegram auth
    ├── schemas/            # Pydantic schemas
    └── config.py           # Application settings
```

#### Dependencies
- Added `pyjwt>=2.8.0` for JWT handling
- Added `python-jose[cryptography]>=3.3.0` for cryptographic operations
- Added `aiosqlite>=0.20.0` for SQLite support in tests
- Added `pre-commit>=3.6.0` for git hooks
- Added `bandit>=1.7.0` for security scanning

#### Configuration
- Updated `pyproject.toml` with ruff, pytest, mypy, coverage settings
- Added `mypy.ini` for type checking configuration
- Added `.pre-commit-config.yaml` for git hooks
- Added `.github/workflows/ci.yml` for CI/CD

### 📦 Infrastructure

#### Docker
- `docker-compose.yml` for local development
- Multi-service setup (Backend, PostgreSQL, Redis)
- Health checks for all services
- Volume persistence for databases

#### CI/CD
- Automated linting on every push
- Automated testing with coverage reporting
- Type checking with mypy
- Security scanning with bandit
- Docker image building

### 📝 Documentation

- `docs/DEVELOPMENT.md` - Development guidelines
- `docs/ARCHITECTURE.md` - Architecture overview
- `docs/API.md` - API documentation
- `docs/DEPLOYMENT.md` - Deployment instructions
- `CHANGELOG.md` - This changelog

### 🧪 Testing

- Integration tests for authentication flow
- Integration tests for VPN CRUD operations
- Test fixtures for database isolation
- Coverage reporting (target: 80%)
- Pytest configuration with markers (slow, integration)

### 🔒 Security

- JWT secret key configuration via environment variables
- Telegram Bot Token validation
- HTTPS-only token transmission
- Secure password-less authentication
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy ORM

### 🐛 Fixed

- Python version compatibility (3.13)
- Ruff configuration for latest version
- Mypy module detection issues
- Pre-commit hook performance

---

## [0.1.0] - 2026-03-18

### Added
- Initial project structure
- Base FastAPI application
- Basic health check endpoint
- README.md with project information
- Dockerfile for containerization
- Example environment configuration

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.4.0 | 2026-03-22 | Complete API Documentation + Billing Endpoints + Bug Fixes |
| 0.3.1 | 2026-03-21 | Consolidated Migrations with UUID Primary Keys |
| 0.3.0 | 2026-03-19 | VPN Providers (Outline + WireGuard) + Infrastructure Scripts |
| 0.2.0 | 2026-03-19 | Auth + VPN endpoints + Pre-commit/CI |
| 0.1.0 | 2026-03-18 | Initial project structure |

---

## Upcoming (v0.5.0)

Planned for next release:

- [ ] Payment integration (Stripe/PayPal)
- [ ] Webhook handlers for payment events
- [ ] Subscription management
- [ ] Invoice generation
- [ ] Usage tracking and billing
- [ ] Admin dashboard endpoints

---

[Unreleased]: https://github.com/uSipipo-Team/usipipo-backend/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/uSipipo-Team/usipipo-backend/releases/tag/v0.4.0
[0.3.1]: https://github.com/uSipipo-Team/usipipo-backend/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/uSipipo-Team/usipipo-backend/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/uSipipo-Team/usipipo-backend/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/uSipipo-Team/usipipo-backend/releases/tag/v0.1.0
