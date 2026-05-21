# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.16.0] - 2026-04-07

### Added
- **TrustTunnel Deep Link Delivery** — Users receive clickable `tt://` deeplink for instant mobile configuration
  - Deep link sent as primary UX before `.toml` file backup
  - Graceful fallback to TOML-only flow if deeplink unavailable
  - `KEY_CREATED_WITH_DEEPLINK` message template with setup instructions
- **TrustTunnel Key Actions** — New buttons in key details view:
  - `📋 Copiar Deeplink` — Sends deeplink as copyable text message
  - `📥 Descargar .toml` — Compact layout (side-by-side with copy deeplink)
  - `DEEPLINK_COPY_SUCCESS` and `DEEPLINK_NOT_AVAILABLE` message templates

### Technical Details
- **Files Modified:** 4 (`src/bot/handlers/keys.py`, `src/bot/handlers/trusttunnel.py`, `src/bot/keyboards/messages_trusttunnel.py`, `src/bot/keyboards/trusttunnel.py`)
- **Lines Added:** ~60

---

## [0.15.1] - 2026-04-06

### Fixed
- **TrustTunnel Key Creation Flow** - Fixed broken flow where bot stopped responding after user entered key name
  - `vpn_type` mapping now correctly handles `trusttunnel` (was incorrectly mapped to `wireguard`)
  - Added response handler to send `.toml` config file + setup instructions after key creation
  - QA reported flow broke at name input step — now delivers config file and setup guide

### Technical Details
- **Files Modified:** 1 (`src/bot/handlers/keys.py`)
- **Lines Added:** 46
- **Tests:** 458 tests passing (100%)
- **Quality:** Ruff clean

---

## [0.15.0] - 2026-04-06

### Added
- **TrustTunnel Protocol Support** - Full TrustTunnel (AdGuard) integration as third VPN protocol alongside Outline and WireGuard
- **Setup Instructions** - Step-by-step configuration guides with direct download buttons for all 3 protocols (TrustTunnel, WireGuard, Outline)

### TrustTunnel Integration
- New `TrustTunnelHandler` with key details, metrics display, config export (TOML), and deletion
- TrustTunnel metrics display: active clients, total bandwidth, per-client breakdown (top 5)
- TOML config file download with inline keyboard buttons for app store links
- Protocol selection keyboard now includes TrustTunnel option
- Main menu shows TrustTunnel key count

### Setup Instructions (All Protocols)
- **TrustTunnel**: Play Store, App Store, GitHub Releases buttons
- **WireGuard**: Play Store, App Store, wireguard.com/install buttons
- **Outline**: Play Store, App Store, outline-vpn.com buttons
- Each guide includes: app download, config import steps, connection instructions, support link

### Technical Details
- **Files Created:** 3 files (`trusttunnel.py` handler, `trusttunnel.py` keyboards, `messages_trusttunnel.py`)
- **Files Modified:** 4 files (`keys.py` handler, `keys.py` keyboards, `messages_keys.py`, `main.py`)
- **Tests:** 477 tests passing (19 new TrustTunnel tests)
- **Quality:** Ruff clean, mypy clean

### Backend Integration
- GET `/vpn/servers/{server_id}/trusttunnel/metrics` - TrustTunnel metrics fetch
- GET `/vpn/keys/{key_id}/config` - TOML config export for TrustTunnel keys
- `KeyType.TRUSTTUNNEL` support in key creation flow

---

## [0.14.0] - 2026-04-06

### Fixed
- **Profile data** - Send `username`, `first_name`, `last_name` from Telegram to auto-register endpoint
- **Referral credits** - `_apply_referral_code` now blocks with 1 retry during registration
- **Referral count** - Profile displays `total_referrals` instead of `referred_users_with_purchase`

### Technical Details
- **Files Modified:** 4 files (`auth.py`, `user_profile.py`, 2 test files)
- **Lines Changed:** +139 / -23
- **Tests:** 439 tests passing (+5 new)
- **Quality:** Ruff clean, pre-commit hooks passing

### Bug Fixes
- Profile no longer shows "No disponible" for username/name
- Referred users now receive their 50-credit new user bonus
- Profile shows correct referral count (all referred users, not just purchasers)

## [0.13.0] - 2026-04-05

### Changed
- **Auth handler** - `_apply_referral_code` now sends `user_id` (UUID) instead of `telegram_id` to backend
- Referral apply endpoint compatibility with backend's `register_referral_by_user_id`

### Technical Details
- **Files Modified:** 1 file (`src/bot/handlers/auth.py`)
- **Lines Changed:** ~10 lines
- **Tests:** Existing tests passing

## [0.10.0] - 2026-04-05

### Added

**WireGuard Metrics Display:**
- ✅ Conditional WireGuard metrics display in key details
- ✅ WireGuard metrics constants (connected, disconnected, unavailable)
- ✅ Last handshake time formatting
- ✅ `_fetch_wireguard_metrics()` helper method
- ✅ Byte transfer display (RX/TX) for WireGuard keys
- ✅ Graceful fallback when metrics unavailable

### Changed

**Server Name Display:**
- ✅ Bot now displays `server_name` from VPN key response instead of `server` field

### Technical Details

**Files Modified:**
- `src/bot/handlers/keys.py` - Added WireGuard metrics fetch and conditional display
- `src/bot/keyboards/messages_keys.py` - Added WireGuard metrics message constants

**Lines Added:** ~70 lines

---

## [Unreleased]

### Changed
- **Use server_name from API** - Bot now displays `server_name` from VPN key response instead of `server` field
  - Fixes display showing "N/A" when backend provides `server_name`

### Added
- Helper methods for VPN key metrics integration
  - `_format_last_seen()` - Human-readable Spanish timestamps ("Hace 5 minutos", "Hace 2 horas")
  - `_format_bytes()` - Bytes to KB/MB/GB conversion
  - `_fetch_server_metrics()` - Outline server metrics fetch from backend API
- 15 unit tests for helper methods (100% passing)

### Technical Details
- **Files Created:** 1 file (`tests/unit/bot/handlers/test_keys_helpers.py`)
- **Files Modified:** 1 file (`src/bot/handlers/keys.py`)
- **Lines Added:** ~100 lines
- **Tests:** 15 new tests (40 total bot tests passing)

## [0.6.0] - 2026-04-04

### Fixed
- **401 Errors in Payments/Subscription Handlers** - Fixed intermittent "Invalid token" errors on `/payments/history` and `/subscriptions/me` endpoints caused by Redis singleton race conditions across uvicorn workers
  - Added retry logic with exponential backoff to APIClient (3 attempts, 0.5s/1.0s delays)
  - Added token refresh fallback via auto-register endpoint as last resort
  - All HTTP methods (GET, POST, PUT, DELETE) now use retry wrapper

### Changed
- **APIClient** - Added `_request_with_retry()` method for resilient HTTP requests
- **TokenStorage** - Added `refresh_token()` method for token re-registration fallback

### Technical Details
- **Files Created:** 1 file (`test_all_handlers.py` - comprehensive handler tests)
- **Files Modified:** 2 files (`api_client.py`, `token_storage.py`)
- **Tests:** 16/16 handler tests passing (was 14/16), 6/6 integration tests passing

### Backend Integration
- Backend fix (already merged): Replaced Redis singleton with per-call connections in JWT module

---

## [0.5.0] - 2026-04-01

### Fixed
- **CI Type Checking Errors** - Fixed all 65 mypy type errors that were blocking CI pipeline
  - Added explicit type annotations for empty list variables in handlers
  - Fixed None handling with proper union type checks
  - Corrected SuccessfulPayment attribute name (telegram_payment_id → telegram_payment_charge_id)
  - Added missing put() method to APIClient
  - Fixed type mismatches in main.py handler registrations

### Changed
- **API Client** - Changed parameter name from `json=` to `data=` for consistency
- **Mypy Configuration** - Added mypy configuration to pyproject.toml with ignore_missing_imports

### Technical Details
- **Files Modified:** 9 files
  - `src/bot/handlers/keys.py` - Fixed None handling, type annotations
  - `src/bot/handlers/payments.py` - Fixed type annotations, attribute names
  - `src/bot/handlers/packages.py` - Fixed type annotations, attribute names
  - `src/bot/handlers/referrals.py` - Fixed API client parameter usage
  - `src/bot/handlers/subscriptions.py` - Fixed type annotations
  - `src/infrastructure/api_client.py` - Added put() method
  - `src/main.py` - Fixed type mismatches with assertions
  - `pyproject.toml` - Added mypy configuration
  - `tests/bot/test_referrals_handlers.py` - Updated test to match API client usage

### Quality Gates
- ✅ All 421 tests passing
- ✅ mypy passes with 0 errors
- ✅ ruff clean

## [0.4.0] - 2026-03-31

### Added
- **VPN Server Selection Feature** - Users can now select their preferred VPN server during key creation
  - New server selection conversation state in VPN key creation flow
  - Real-time server list with load indicators (🟢 low, 🟡 medium, 🔴 high)
  - Protocol filtering (Outline/WireGuard)
  - Top 5 recommended servers (lowest load first)
  - "Show all servers" option for full list
  - Server details display: country, city, server name, load percentage

### Changed
- **VPN Key Creation Flow** - Enhanced multi-step conversation
  - **Before:** Protocol → Name → Key Created
  - **After:** Protocol → **Server Selection** → Name → Key Created
  - Optional server_id parameter sent to backend (backward compatible)
  - Auto-selection fallback when user doesn't select server

### Technical Details
- **Files Created:** 2 files
  - `src/bot/keyboards/servers.py` - ServerKeyboards factory (106 lines)
  - `tests/bot/keyboards/test_servers.py` - Keyboard tests (552 lines)
  - `tests/bot/handlers/test_keys_server_selection.py` - Conversation tests (19 tests)
- **Files Modified:** 2 files
  - `src/bot/handlers/keys.py` - Added SELECT_SERVER state, protocol_selected(), server_selected()
  - `src/bot/keyboards/servers.py` - Updated to support dict and object formats
- **Tests:** 46 server-related tests (100% passing)
- **Total Tests:** 421 tests (375 existing + 46 new)

### Backend Integration
- **GET /api/v1/vpn/servers?protocol=outline|wireguard** - Fetch available servers
  - Authentication: JWT token (user)
  - Response: servers list + recommended (top 5)
  - Load levels: low (0-50%), medium (51-80%), high (81-100%)
- **POST /api/v1/vpn/keys** - Optional server_id parameter
  - Backward compatible: server_id is optional
  - Auto-selection when server_id not provided

### Quality Gates
- ✅ All tests passing (421 passed)
- ✅ Ruff linting clean
- ✅ Mypy type checking clean
- ✅ Bandit security scan clean
- ✅ Pre-commit hooks all passing
- ✅ TDD followed (tests written before implementation)
- ✅ Clean Architecture patterns maintained

### UX Improvements
- **Server List Message:** Formatted with visual boxes and emoji indicators
- **Load Indicators:** 🟢 Low (0-50%), 🟡 Medium (51-80%), 🔴 High (81-100%)
- **Button Format:** `{FLAG} {COUNTRY_CODE} - {CITY} {LOAD_EMOJI}`
- **Error Handling:** Graceful handling of API failures with retry option
- **Navigation:** "🔙 Volver" and "🔍 Ver todos los servidores" buttons

### Impact
- ✅ User-facing feature: server transparency and control
- ✅ Load balancing: users can select servers with lowest load
- ✅ Backward compatible: existing behavior preserved
- ✅ No breaking changes

---

## [0.3.0] - 2026-03-31

### Added
- **User Profile "Mis Datos" Feature** - Complete user profile display with rich information
  - New "💾 Mis Datos" button now functional in main menu
  - Professional profile message with 5 sections:
    - Personal Info (username, name, Telegram ID)
    - Balance & Data (current balance, total purchased, VPN keys count)
    - Referral Program (code, referrals count, credits earned)
    - Loyalty Program (tier level, bonus percent, purchase count, welcome bonus status)
    - Account Info (creation date, last update)
  - Automatic loyalty tier calculation (Standard, Bronze, Silver, Gold, Platinum)
  - Error handling for unauthenticated users and API failures
  - Back navigation to main menu

### Changed
- **Version bump** - Updated from v0.2.0 to v0.3.0 in README.md
- **Main handler registration** - Added user profile handler to main.py

### Technical Details
- **Files Created:** 6 files
  - `src/bot/keyboards/messages_user_profile.py` - Message templates
  - `src/bot/keyboards/user_profile.py` - Inline keyboard
  - `src/bot/handlers/user_profile.py` - Handler logic
  - `tests/unit/bot/keyboards/test_messages_user_profile.py` - 5 unit tests
  - `tests/unit/bot/keyboards/test_user_profile_keyboard.py` - 1 unit test
  - `tests/bot/test_user_profile_handlers.py` - 2 integration tests
- **Files Modified:** 2 files
  - `src/main.py` - Handler registration
  - `README.md` - Feature documentation
- **Tests:** 8 new tests, all 375 tests passing

### Quality Gates
- ✅ All tests passing (375 passed, 1 skipped)
- ✅ Ruff linting clean
- ✅ TDD followed (tests written before implementation)
- ✅ Clean Architecture patterns maintained

---

## [1.3.0] - 2026-03-30

### Fixed
- **Bot-Backend Integration** - Complete API endpoint alignment with backend v0.13.0
  - Fixed 8 endpoint mismatches between bot adapter and backend routes
  - Auto-register: `/api/v1/auth/telegram/auto-register` (was `/api/v1/auth/auto-register`)
  - User Profile: `/api/v1/users/me` (was `/api/v1/users/profile`)
  - VPN Keys: `/api/v1/vpn/keys` (was `/api/v1/vpn-keys`)
  - Referrals: `/api/v1/referrals/me` (was `/api/v1/referrals/code` and `/api/v1/referrals/stats`)

- **Backend User Profile** - Added missing fields in backend `/users/me` endpoint
  - Added `updated_at` field (required by User entity)
  - Added `referred_by` field (required by User entity)

- **Test Suite** - Fixed 11 failing tests (367 tests now passing)
  - AuthMessages: Added `{plan_name}` placeholder to `ME_AUTHENTICATED`
  - Help handler test: Updated to expect 2 messages (HELP + SUPPORT)
  - Payments tests: Updated button values to match actual keyboard
  - Referrals tests: Fixed mock configuration (handler.api vs mock_api.api_client)
  - Backend adapter tests: Updated referral code response structure

### Changed
- **BackendApiAdapter** - Complete endpoint refactoring for backend API alignment
  - `auto_register()` - Updated to `/api/v1/auth/telegram/auto-register`
  - `get_user_profile()` - Updated to `/api/v1/users/me`
  - `list_vpn_keys()` - Updated to `/api/v1/vpn/keys`
  - `create_vpn_key()` - Updated to `/api/v1/vpn/keys`
  - `delete_vpn_key()` - Updated to `/api/v1/vpn/keys/{id}`
  - `get_key_config()` - Updated to `/api/v1/vpn/keys/{id}/config`
  - `get_referral_code()` - Updated to `/api/v1/referrals/me`
  - `get_referral_stats()` - Updated to `/api/v1/referrals/me`

### Technical Details
- **Files Modified:** 8 files
  - Bot: `src/bot/keyboards/auth.py`, `src/infrastructure/secondary_adapters/backend_api/backend_api_adapter.py`
  - Backend: `src/infrastructure/api/v1/routes/users.py`
  - Tests: 5 test files updated
- **Tests:** 367 tests passing (was 356 passing, 11 failing)
- **Test Coverage:** 100% of integration tests passing

### Quality Gates
- ✅ 367/367 tests passing (100%)
- ✅ Ruff clean
- ✅ Mypy clean
- ✅ Integration tests verified with production backend

### Documentation
- Created `BOT-BACKEND-INTEGRATION-DEBUG.md` - Systematic debugging report
- Created `BOT-BACKEND-INTEGRATION-FIX.md` - Fix summary and verification
- Created `TEST-FIXES-SUMMARY.md` - Complete test fixes documentation

## [1.2.0] - 2026-03-28

### Added
- **MainMenuKeyboard** - Menú principal de botones inline para navegación visual
  - Botones: 🔑 Mis Claves VPN, ➕ Nueva Clave, ⚙️ Operaciones, 💾 Mis Datos, ❓ Ayuda
  - Consistente con el bot legacy (@usipipobot)
  - Navegación visual sin necesidad de memorizar comandos

- **Global main_menu Handler** - Handler para callback `main_menu`
  - Muestra menú principal con botones al hacer click en "🔙 Volver al Menú Principal"
  - Registrado en `src/main.py`

- **BACK_TO_MAIN Message** - Mensaje de navegación en `BasicMessages`
  - Mensaje consistente para retorno al menú principal

### Changed
- **AuthHandler** - `/start` ahora muestra menú con botones
  - Usuarios nuevos ven botones inmediatamente después de autenticarse
  - Usuarios existentes ven botones en bienvenida

- **operations.py** - `back_to_main_menu` usa MainMenuKeyboard
- **packages.py** - `back_to_main_menu` usa MainMenuKeyboard
- **consumption.py** - `back_to_main_menu` usa MainMenuKeyboard

### Technical Details
- **Files Created:** 2 files (`src/bot/keyboards/main_menu.py`, `src/bot/handlers/main_menu.py`)
- **Files Modified:** 6 files (auth.py, operations.py, packages.py, consumption.py, main.py, keyboards/main.py)
- **Lines Added:** ~150 lines
- **Tests:** Testing manual en Telegram

### UX Improvements
- ✅ Navegación visual con botones inline
- ✅ Consistente con bot legacy
- ✅ Menos dependencia de comandos de texto
- ✅ Mejor experiencia para usuarios nuevos

## [0.9.0] - 2026-03-28

### Removed
- **Tickets System Migration** - Support tickets moved to dedicated @uSipipoSupport_Bot
  - Removed commands: `/tickets`, `/nuevoticket`, `/mistickets`
  - Users should now use @uSipipoSupport_Bot for all support ticket operations
  - Support bot provides dedicated ticket management with same features

- **Deleted Files**
  - `src/bot/handlers/tickets.py` - Migrated to usipipo-support-bot
  - `src/bot/keyboards/tickets.py` - Migrated to usipipo-support-bot
  - `src/bot/keyboards/messages_tickets.py` - Migrated to usipipo-support-bot
  - `tests/bot/test_tickets_handlers.py` - Migrated to usipipo-support-bot
  - `tests/bot/test_tickets_keyboards.py` - Migrated to usipipo-support-bot
  - `tests/bot/test_tickets_messages.py` - Migrated to usipipo-support-bot
  - `tests/integration/test_tickets_integration.py` - Migrated to usipipo-support-bot

### Changed
- **Main Bot Focus** - Now focused on core VPN and payment features
- **Support Separation** - Support tickets handled by dedicated bot for better organization
- **Test Suite** - Reduced from 323 to ~290 tests (ticket tests migrated)

### Migration Guide
Users should:
1. Use @usipipobot for VPN, payments, subscriptions, referrals
2. Use @uSipipoSupport_Bot for support tickets and technical assistance

### Technical Details
- **Files Removed:** 7
- **Lines Removed:** ~800
- **Tests Migrated:** 58 tests to usipipo-support-bot
- **Breaking Change:** Yes - ticket commands no longer available

## [0.8.0] - 2026-03-28

### Added
- **Referrals System** - Invite friends, earn credits
  - Commands: `/referidos`, `/invitar`
  - Referral stats display with credits
  - Referral link generation (t.me/usipipobot?start={code})
  - Credit redemption (10 credits = 1 GB)
  
- **Tickets System** - Support ticket management
  - Commands: `/tickets`, `/nuevoticket`, `/mistickets`
  - Ticket creation with category selection (technical, billing, services, general)
  - Ticket list with status indicators (🟢 OPEN, 🟡 RESPONDED, 🔵 RESOLVED, 🔴 CLOSED)
  - Ticket detail view
  - Ticket closure

- **Referrals Components**
  - `ReferralsHandler` - Main handler with show_referrals, get_referral_link, redeem_credits_callback, apply_code_callback
  - `ReferralsKeyboard` - Inline keyboards: menu(), redeem_confirmation(), apply_code(), back_to_menu()
  - `ReferralsMessages` - UI messages: REFERRAL_STATS, INVITE_LINK, REDEEM_CONFIRMATION, APPLY_SUCCESS

- **Tickets Components**
  - `TicketsHandler` - Main handler with list_tickets, create_ticket, view_ticket_callback, close_ticket_callback, select_category_callback
  - `TicketsKeyboard` - Inline keyboards: tickets_list(), ticket_detail(), categories(), ticket_actions(), back_to_tickets()
  - `TicketsMessages` - UI messages: TICKETS_LIST, TICKET_DETAIL, CREATE_TICKET, TICKET_CREATED, TICKET_CLOSED

- **Tests**
  - 32 new unit tests (15 tickets, 13 referrals, 4 keyboards/messages each)
  - 4 integration tests (2 referrals, 2 tickets)
  - Total: 323 tests (319 passed, 1 skipped, 3 pre-existing failures)

- **Documentation**
  - Design doc: `usipipo-docs/plans/telegram-bot/2026-03-28-phase-7-referrals-tickets-design.md`
  - Flow docs: `usipipo-docs/flows/telegram-bot/referrals-flow.md`, `tickets-flow.md`
  - Migration progress updated to 75% (68/92 files)

### Backend Integration
- GET /api/v1/referrals/me - Referral statistics
- POST /api/v1/referrals/apply - Apply referral code
- POST /api/v1/referrals/redeem - Redeem credits for data
- POST /api/v1/tickets - Create support ticket
- GET /api/v1/tickets - List user tickets
- GET /api/v1/tickets/{id} - Get ticket with messages
- PATCH /api/v1/tickets/{id}/close - Close ticket

### Quality
- 32 new tests (323 total)
- Ruff clean
- Mypy clean
- Code review approved
- Branch protection enabled

### Files Created
- `src/bot/handlers/referrals.py` (~400 lines)
- `src/bot/handlers/tickets.py` (~500 lines)
- `src/bot/keyboards/referrals.py` (~120 lines)
- `src/bot/keyboards/messages_referrals.py` (~180 lines)
- `src/bot/keyboards/tickets.py` (~150 lines)
- `src/bot/keyboards/messages_tickets.py` (~220 lines)
- `tests/bot/test_referrals_handlers.py` (13 tests)
- `tests/bot/test_tickets_handlers.py` (15 tests)
- `tests/integration/test_referrals_integration.py` (2 tests)
- `tests/integration/test_tickets_integration.py` (2 tests)

## [0.7.1] - 2026-03-28

### 🔧 Pricing Corrections (Legacy Alignment)

#### Fixed
- **Data Packages Pricing** - Corrected to match legacy bot values
  - Básico: 10GB - 250 Stars ($2.08 USDT) ← was 5GB/600 Stars
  - Estándar: 30GB - 600 Stars ($5.00 USDT) ← was 10GB/1200 Stars
  - Avanzado: 60GB - 960 Stars ($8.00 USDT) ← was 25GB/3000 Stars
  - Premium: 120GB - 1440 Stars ($12.00 USDT) ← was 50GB/6000 Stars
  - Ilimitado: 200GB - 1800 Stars ($15.00 USDT) ← NEW

- **Subscriptions Pricing** - Corrected to match legacy bot values
  - 1 Month: 360 Stars ($2.99 USDT)
  - 3 Months: 900 Stars ($7.49 USDT)
  - 6 Months: 1680 Stars ($13.99 USDT)
  - 12 Months: 3000 Stars ($24.99 USDT)

#### Added
- **STARS_PER_USDT Constant** - Exchange rate configuration
  - `STARS_PER_USDT = 120` (1 USDT = 120 Telegram Stars)
  - Added in `src/infrastructure/config.py`

- **Pricing Documentation** - Comprehensive pricing reference
  - Created `/home/mowgli/usipipo/usipipo-docs/apis/pricing-structure.md`
  - 530 lines of pricing tables, formulas, and comparisons

#### Changed
- **Payment Keyboards** - Updated with correct USDT amounts
- **Payment Messages** - Updated menu with both Stars and USDT prices
- **packages.py** - Updated fallback packages with legacy pricing
- **subscriptions.py** - Updated fallback plans with legacy pricing

#### Technical Details
- **Exchange Rate:** 1 USDT = 120 Telegram Stars
- **Formula:** USDT = Stars / 120
- **Files Modified:** 5 (packages.py, subscriptions.py, payments.py, messages_payments.py, config.py)
- **Documentation:** 1 new file (530 lines)
- **Lines Changed:** 108 insertions, 65 deletions

---

## [0.7.0] - 2026-03-28

### 🎉 Payments + Subscriptions Complete

#### Added
- **Payments System** - Crypto (TronDealer) + Telegram Stars payments
- **Subscriptions System** - Plan management, activation, and renewal
- **Payment History** - View user payment history with pagination

- **New Commands**
  - `/pago` - Payment menu
  - `/pagar` - Payment menu (alias)
  - `/historial` - View payment history
  - `/suscripcion` - View subscription status
  - `/planes` - View available plans
  - `/renovar` - Renew subscription

- **New Handlers** (`src/bot/handlers/payments.py`)
  - `PaymentsHandler` class with all payment flows
  - Crypto payment via TronDealer
  - Stars payment via Telegram invoices
  - Payment history display

- **New Handlers** (`src/bot/handlers/subscriptions.py`)
  - `SubscriptionsHandler` class with all subscription flows
  - Plan selection and display
  - Subscription activation
  - Subscription renewal
  - Status display

- **New Keyboards** (`src/bot/keyboards/payments.py`, `subscriptions.py`)
  - Payment method selection (Crypto/Stars)
  - Crypto amount selection ($10, $25, $50, $100)
  - Stars amount selection
  - Payment history pagination
  - Plans list and selection
  - Subscription status menu

- **New Messages** (`src/bot/keyboards/messages_payments.py`, `messages_subscriptions.py`)
  - Payment instructions (Crypto & Stars)
  - Payment success/failure messages
  - Plan details and features
  - Subscription status messages
  - Activation/renewal confirmations

- **Testing**
  - 103 new unit tests (45 payments + 58 subscriptions)
  - Tests for all message templates and placeholders
  - Tests for all keyboard layouts
  - Tests for payment flows (Crypto & Stars)
  - 263 tests total (263 passed)

#### Changed
- Updated `src/main.py` to register PaymentsHandler and SubscriptionsHandler
- Enhanced bot structure with payments and subscriptions modules

#### Technical Details
- **Backend Integration:**
  - `POST /api/v1/payments/crypto` - Create crypto payment
  - `POST /api/v1/payments/stars` - Create Stars payment
  - `GET /api/v1/payments/history` - Get payment history
  - `GET /api/v1/subscriptions/me` - Get user subscription
  - `GET /api/v1/subscriptions/plans` - List available plans
  - `POST /api/v1/subscriptions/activate` - Activate subscription
  - `POST /api/v1/subscriptions/renew` - Renew subscription
- **Quality:** ruff (passed), pytest (263/263 passed), mypy (clean for new code)
- **Files Created:** 8 (handlers, keyboards, messages, tests)
- **Files Modified:** 1 (main.py)
- **Lines Added:** 3,726

#### Payment Methods
```python
# Crypto (USDT via TronDealer)
- $10, $25, $50, $100 amounts
- TronDealer webhook integration
- Automatic payment confirmation

# Telegram Stars
- 600, 1200, 3000, 6000 Stars
- Telegram invoice integration
- Pre-checkout validation
```

#### Subscription Plans
```python
[
    {"id": "basic", "name": "Basic", "price_usd": 9.99, "duration_days": 30},
    {"id": "standard", "name": "Standard", "price_usd": 19.99, "duration_days": 30},
    {"id": "premium", "name": "Premium", "price_usd": 29.99, "duration_days": 30},
]
```

---

## [0.6.0] - 2026-03-28

### 🎉 Data Packages Complete

#### Added
- **Data Packages System** - Buy GB data packages with flexible payment options
- **Telegram Stars Integration** - In-app purchases via Telegram
- **Crypto Payments** - USDT payments via TronDealer
- **Data Slots Management** - Manage multiple data packages
- **Data Usage Summary** - View consumption statistics

- **New Commands**
  - `/comprar` - Buy data packages
  - `/paquetes` - View available packages (alias)
  - `/packages` - View available packages (English alias)

- **New Handlers** (`src/bot/handlers/packages.py`)
  - `PackagesHandler` class with all package flows
  - Package selection and display
  - Stars payment flow with Telegram invoices
  - Crypto payment flow with TronDealer integration
  - Data slots management
  - Data usage summary display

- **New Keyboards** (`src/bot/keyboards/packages.py`)
  - `PackagesKeyboard` class with inline keyboards
  - Package selection menu
  - Payment method selection (Stars/Crypto)
  - Data summary display
  - Slots management menu
  - Payment success/failure keyboards

- **New Messages** (`src/bot/keyboards/messages_packages.py`)
  - `PackagesMessages` class with UI messages
  - Package menu and details
  - Payment instructions (Stars & Crypto)
  - Data summary format
  - Slots management messages
  - Error and success messages

- **Testing**
  - 55 new unit tests for data packages
  - Tests for all message templates and placeholders
  - Tests for all keyboard layouts
  - Tests for payment flows (Stars & Crypto)
  - 160 tests total (160 passed)

#### Changed
- Updated `src/main.py` to register PackagesHandler and all handlers
- Enhanced bot structure with data packages module

#### Technical Details
- **Backend Integration:**
  - `GET /api/v1/data-packages` - List available packages
  - `POST /api/v1/payments/stars` - Create Stars payment
  - `POST /api/v1/payments/stars/activate` - Activate package after payment
  - `POST /api/v1/payments/crypto` - Create crypto payment
  - `GET /api/v1/payments/crypto/{id}/status` - Check payment status
  - `GET /api/v1/users/me/data-summary` - Get user data usage
  - `GET /api/v1/users/me/slots` - Get user's data slots
  - `POST /api/v1/users/me/slots` - Buy extra slot
- **Quality:** ruff (passed), pytest (160/160 passed), mypy (clean for new code)
- **Files Created:** 4 (handlers, keyboards, messages, tests)
- **Files Modified:** 1 (main.py)
- **Lines Added:** 2,067

#### Package Options
```python
[
    {"id": "small", "name": "Pequeño", "data_gb": 5, "price_usd": 5.00, "price_stars": 600},
    {"id": "medium", "name": "Mediano", "data_gb": 10, "price_usd": 10.00, "price_stars": 1200},
    {"id": "large", "name": "Grande", "data_gb": 25, "price_usd": 25.00, "price_stars": 3000},
    {"id": "xl", "name": "XL", "data_gb": 50, "price_usd": 50.00, "price_stars": 6000},
]
```

---

## [0.5.0] - 2026-03-27

### 🎉 Consumption Billing Complete

#### Added
- **Consumption Billing System**
  - Pay-as-you-go consumption mode
  - 30-day billing cycles
  - Dynamic pricing ($0.25/GB)
  - Invoice generation with payment methods

- **New Commands**
  - `/consumo` - Show consumption menu (inactive/active/debt states)
  - `/activar` - Activate consumption mode (2-step confirmation flow)
  - `/cancelar` - Cancel consumption mode (with/without debt summary)
  - `/factura` - View invoices with pagination

- **New Handlers** (`src/bot/handlers/consumption.py`)
  - `ConsumptionHandler` class with all consumption flows
  - Menu with state-aware UI (inactive/active/debt)
  - Activation flow with terms acceptance
  - Cancellation flow with debt summary
  - Status view with consumption stats (GB, cost, days)
  - Invoice listing with pagination

- **New Keyboards** (`src/bot/keyboards/consumption.py`)
  - `ConsumptionKeyboard` class with 12 inline keyboard layouts
  - State-aware main menu (inactive/active/debt)
  - Activation confirmation and success keyboards
  - Cancellation confirmation (with/without debt)
  - Invoice list with pagination controls
  - Back navigation keyboards

- **New Messages** (`src/bot/keyboards/messages_consumption.py`)
  - `ConsumptionMessages` class with 7 nested message categories
  - Menu messages (INACTIVE_STATE, ACTIVE_STATE, DEBT_STATE)
  - Activation terms and conditions with pricing
  - Cancellation summary messages
  - Status display with consumption stats
  - Invoice list and payment messages
  - Comprehensive error messages

- **Testing**
  - 45 new unit tests for consumption billing
  - Tests for all message templates and placeholders
  - Tests for all keyboard layouts
  - Tests for handler initialization and authentication
  - 150 tests total (150 passed)

#### Changed
- Updated `src/main.py` to register ConsumptionHandler and callback handlers
- Enhanced `src/infrastructure/api_client.py` with headers support for GET/POST
- Updated `src/infrastructure/config.py` with consumption pricing constants

#### Technical Details
- **Backend Integration:**
  - `GET /api/v1/consumption/status` - Get consumption status
  - `GET /api/v1/consumption/status/can_activate` - Check activation eligibility
  - `POST /api/v1/consumption/activate` - Activate consumption mode
  - `GET /api/v1/consumption/status/can_cancel` - Check cancellation eligibility
  - `POST /api/v1/consumption/cancel` - Cancel consumption mode
  - `GET /api/v1/consumption/invoices/user/me` - Get user invoices with pagination
- **Quality:** ruff (passed), pytest (150/150 passed), mypy (clean for new code)
- **Files Created:** 4 (handlers, keyboards, messages, tests)
- **Files Modified:** 3 (main.py, api_client.py, config.py)
- **Lines Added:** 1,874

#### Configuration
```python
# Consumption Pricing
CONSUMPTION_PRICE_PER_GB_USD = 0.25
CONSUMPTION_PRICE_PER_MB_USD = 0.000244140625  # 0.25 / 1024
```

---

## [0.4.0] - 2026-03-27

### 🎉 Operations + Profile Complete

#### Added
- **Operations Menu System**
  - Main operations menu with credits display
  - Shop menu with purchase options
  - Transactions history with pagination
  - Referrals program display

- **New Commands**
  - `/operaciones` - Operations menu

- **New Handlers** (`src/bot/handlers/operations.py`)
  - `OperationsHandler` class with all operations
  - Operations menu with credits integration
  - Credits display and redemption flow
  - Shop menu
  - Transactions history
  - Referrals program

- **New Keyboards** (`src/bot/keyboards/operations.py`)
  - `OperationsKeyboard` class with inline keyboards
  - Operations menu with credits
  - Credits redemption options
  - Shop categories
  - Transactions pagination
  - Referrals display

- **New Messages** (`src/bot/keyboards/messages_operations.py`)
  - `OperationsMessages` class with UI messages
  - Menu messages with credits
  - Credits display and redemption
  - Shop welcome message
  - Transactions history format
  - Referrals program info

- **Testing**
  - 21 new unit tests for operations
  - Tests for keyboards, messages, and handlers
  - 128 tests total (128 passed)

#### Changed
- Updated `src/main.py` to register OperationsHandler and callback handlers
- Enhanced bot structure with operations module

#### Technical Details
- **Backend Integration:**
  - `GET /api/v1/referrals/me` - Get referral stats
  - `GET /api/v1/transactions` - Get transactions history
- **Quality:** ruff (passed), pytest (128/128 passed)
- **Files Created:** 4 (handlers, keyboards, messages, tests)
- **Files Modified:** 1 (main.py)

---

## [0.3.0] - 2026-03-27

### 🎉 VPN Key Management Complete

#### Added
- **VPN Key Management System**
  - Full CRUD operations for VPN keys
  - Support for Outline and WireGuard protocols
  - Inline keyboards for key actions

- **New Commands**
  - `/keys` - List user's VPN keys with summary
  - `/newkey` - Create new VPN key (flow starter)

- **New Handlers** (`src/bot/handlers/keys.py`)
  - `KeysHandler` class with all VPN operations
  - List keys by type (Outline/WireGuard)
  - Show key details with usage statistics
  - Create new keys
  - Delete keys with confirmation
  - Rename keys
  - Download WireGuard .conf files
  - Get Outline access links
  - View key statistics

- **New Keyboards** (`src/bot/keyboards/keys.py`)
  - `KeysKeyboard` class with inline keyboards
  - Main menu with key counts
  - Key list by type
  - Key actions (download, rename, delete)
  - Confirmation dialogs

- **New Messages** (`src/bot/keyboards/messages_keys.py`)
  - `KeysMessages` class with UI messages
  - Main menu, key details, statistics
  - Action success/error messages
  - Progress bars for data usage

- **Testing**
  - 25 new unit tests for VPN key management
  - Tests for keyboards, messages, and handlers
  - 107 tests total (107 passed)

#### Changed
- Updated `src/main.py` to register KeysHandler and callback handlers
- Enhanced bot structure with VPN key management module

#### Technical Details
- **Backend Integration:**
  - `GET /api/v1/vpn/keys` - List keys
  - `POST /api/v1/vpn/keys` - Create key
  - `DELETE /api/v1/vpn/keys/{id}` - Delete key
  - `GET /api/v1/vpn/keys/{id}/config` - Get config
- **Quality:** ruff (passed), pytest (107/107 passed)
- **Files Created:** 4 (handlers, keyboards, messages, tests)
- **Files Modified:** 1 (main.py)

---

## [0.2.0] - 2026-03-24

### 📦 Project Structure + Metadata

#### Added
- **CHANGELOG.md** - Keep a Changelog format
- **README.md** - Updated with production status + version info
- **GitHub Topics** - 10 topics for discoverability
- **Repository Description** - Updated

#### Changed
- Updated project metadata
- Enhanced documentation

---

## [0.1.0] - 2026-03-24

### 🎉 Initial Release - Invisible Authentication

#### Added
- **Invisible Authentication System**
  - Redis-based token storage with auto-refresh
  - AuthHandler with seamless auth flow
  - Auto-refresh 5 minutes before token expiry (30-day refresh tokens)
  
- **New Commands**
  - `/start` - Registration and automatic authentication
  - `/me` - Show user profile with auto-auth check
  - `/unlink` - Revoke bot access and delete tokens
  
- **Infrastructure**
  - `config.py` - pydantic-settings configuration
  - `redis.py` - RedisPool singleton with connection pooling
  - `token_storage.py` - TokenStorage for JWT management
  - `auth.py` (handlers) - AuthHandler class
  - `auth.py` (keyboards) - AuthMessages constants
  
- **CI/CD**
  - GitHub Actions workflow (ci.yml)
    - Lint (Ruff)
    - Type Check (Mypy)
    - Test (Pytest)
    - Security (Bandit)
  - Pre-commit configuration
  
- **Testing**
  - 45 tests total (44 passed, 1 skipped)
  - 6 integration tests with production backend
  - Unit tests for handlers, storage, and config
  
- **Documentation**
  - `INTEGRATION-TEST-SUMMARY.md` - Complete test documentation
  - Updated `README.md` with new commands

#### Changed
- Updated `main.py` to register auth handlers
- Enhanced `api_client.py` with production backend URL
- Updated `.env` with production configuration

#### Fixed
- Entry point duplication (`__main__.py`)
- Missing `__init__.py` files in packages
- mypy type errors in api_client, main, __main__
- ruff linting errors in tests

#### Technical Details
- **Backend Integration:** Production (https://usipipo.duckdns.org)
- **Token Storage:** Redis with 30-day expiry
- **Auto-Refresh:** 5 minutes before expiry
- **Quality:** mypy (0 errors), ruff (passed), pytest (44/45 passed)

---

## [0.0.1] - 2026-03-23

### 🌱 Project Setup

#### Added
- Initial project structure
- Basic commands (`/start`, `/help`, `/status`)
- API client for backend communication
- Logger and error handler
- Basic tests (11 tests)

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.4.0 | 2026-03-27 | Operations + Profile Complete (21 tests, 128 total) |
| 0.3.0 | 2026-03-27 | VPN Key Management Complete (25 tests, 107 total) |
| 0.2.0 | 2026-03-24 | Project Structure + Metadata |
| 0.1.0 | 2026-03-24 | Invisible Authentication + CI/CD + Integration Tests |
| 0.0.1 | 2026-03-23 | Project Setup + Basic Commands |

---

## Upcoming Features

### v0.5.0 - Consumption Billing
- `/consumo` - Consumption menu
- `/activar` - Activate consumption mode
- `/cancelar` - Cancel consumption mode
- `/factura` - View invoices

### v0.6.0 - Data Packages
- `/comprar` - Buy data packages
- `/paquetes` - View available packages
- Payment with crypto and Telegram Stars

### v0.7.0 - Payments Integration
- Crypto payments (TronDealer)
- Telegram Stars
- Subscription activation

---

**Links:**
- **Repository:** https://github.com/uSipipo-Team/usipipo-telegram-bot
- **Releases:** https://github.com/uSipipo-Team/usipipo-telegram-bot/releases
- **PRs:** https://github.com/uSipipo-Team/usipipo-telegram-bot/pulls
