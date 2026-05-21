# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.21.0] - 2026-04-06

### Added
- **KeyType.TRUSTTUNNEL** - Added `"trusttunnel"` enum value for TrustTunnel VPN protocol integration

### Tests
- Added `TestKeyType` class with 2 tests for enum validation

---

## [0.20.0] - 2026-04-05

### Changed
- **AdminUserInfo** - Changed `user_id` from `int` to `UUID` for multi-client support
- **AdminKeyInfo** - Changed `user_id` from `int` to `UUID` for multi-client support
- **Balance** - Changed `user_id` from `int` to `UUID` for multi-client support
- **DataPackage** - Changed `user_id` from `int` to `UUID` for multi-client support
- **Ticket** - Changed `user_id` and `resolved_by` from `int` to `UUID`
- **TicketMessage** - Changed `from_user_id` from `int` to `UUID`
- **admin.py** - Replaced duplicate class definitions with re-exports from dedicated modules

---

## [0.18.0] - 2026-04-03

### Added

- **User Entity** - Added `current_billing_id`, `has_pending_debt`, `consumption_mode_enabled` fields
- **User Methods** - Added `mark_as_has_debt()`, `clear_debt()`, `activate_consumption_mode()`, `deactivate_consumption_mode()`
- **Payment Entity** - Added `@classmethod create()` factory method and `amount` property
- **VpnKey Entity** - Added `set_status()` method for mutable status changes
- **KeyStatus Enum** - Added `INACTIVE = "inactive"` value

### Changed

- **User Entity** - Made `telegram_id` Optional[int] to support email-only users
- **ConsumptionBilling** - Changed `user_id` from `int` to `UUID`
- **ConsumptionInvoice** - Changed `user_id` from `int` to `UUID`
- **Schemas** - Replaced deprecated `class Config: from_attributes = True` with `model_config = ConfigDict(from_attributes=True)` in user.py, vpn.py, payment.py
- **CryptoOrder** - Fixed `datetime.utcnow()` → `datetime.now(timezone.utc)`

### Technical Details

- **Files Modified:** 9 files
- **Tests:** 60 tests (100% passing, 0 warnings)

---

## [0.17.0] - 2026-04-03

### Changed

#### VPN Key Name Validation
- **`validate_vpn_key_name()`** - Enhanced with strict validation rules
  - Added `VPN_KEY_NAME_MIN_LENGTH` (3) and `VPN_KEY_NAME_MAX_LENGTH` (50) constants
  - Added `VPN_KEY_NAME_PATTERN` regex for strict alphanumeric + spaces/hyphens/underscores
  - Now blocks emoji and unicode confusables
  - Returns False for empty strings and names outside length range

### Architecture Fix
- **Removed `get_vpn_key_name_validation_error()`** - Moved to presentation layer (telegram-bot)
  - Domain layer should not contain UI error messages
  - Error message generation belongs in client applications

### Impact

This change provides domain-level validation only:
- ✅ Consistent VPN key naming across all clients
- ✅ Block problematic characters that could cause issues
- ✅ Clean architecture - domain layer stays pure

### Technical Details
- **Files Modified:** 1 (validators.py)
- **Lines:** +38, -6
- **Breaking Changes:** None (backward compatible)

---

## [0.16.0] - 2026-04-03

### Added

#### VPN Key Name Validation
- **`get_vpn_key_name_validation_error()`** - New function for detailed validation error messages
  - Returns descriptive error messages for invalid VPN key names
  - Supports length validation (3-50 characters)
  - Blocks emoji, unicode confusables, and special shell characters
  - Compatible with `validate_vpn_key_name()` function

### Changed

#### VPN Key Name Validation
- **`validate_vpn_key_name()`** - Enhanced with strict validation rules
  - Added `VPN_KEY_NAME_MIN_LENGTH` (3) and `VPN_KEY_NAME_MAX_LENGTH` (50) constants
  - Added `VPN_KEY_NAME_PATTERN` regex for strict alphanumeric + spaces/hyphens/underscores
  - Now blocks emoji and unicode confusables
  - Returns False for empty strings and names outside length range

### Impact

This change enables dependent projects (telegram-bot) to:
- Get detailed validation error messages for user feedback
- Enforce consistent VPN key naming across all clients
- Block problematic characters that could cause issues in shell commands or configs

### Technical Details
- **Files Modified:** 3 (validators.py, schemas/vpn.py, utils/__init__.py)
- **Lines Added:** +139, -10
- **Breaking Changes:** None (backward compatible, only adds new function)

---

## [0.15.0] - 2026-04-01

### Added

#### Type Checking Support
- **py.typed marker files** - Added to enable proper mypy type checking for dependent projects
  - `usipipo_commons/py.typed` - Package root marker
  - `usipipo_commons/domain/py.typed` - Domain package marker
  - `usipipo_commons/domain/entities/py.typed` - Entities package marker

### Changed

#### Build Configuration
- Updated `pyproject.toml` to include py.typed files in wheel builds using hatchling's force-include
- Ensures type information is available when package is installed from PyPI

### Impact

This change fixes CI type checking errors in dependent projects:
- ✅ usipipo-telegram-bot (fixed 65 mypy errors)
- ✅ All other uSipipo projects can now use proper type checking

### Technical Details
- **Files Added:** 3 py.typed marker files
- **Files Modified:** 1 (pyproject.toml)
- **Breaking Changes:** None (backward compatible)

## [0.14.0] - 2026-03-31

### Changed

#### VpnKey Entity
- **server_id**: Added optional field for VPN server selection
- Enables users to select preferred server during key creation

## [0.13.0] - 2026-03-22

### Added

#### Server Entity
- New `Server` entity for VPN server management
- Fields: id, name, country, city, endpoint, max_connections, current_connections, load_percentage, is_active, protocol

## [0.12.0] - 2026-03-22

### Changed

#### VpnKey Entity
- **id**: `Optional[str]` → `UUID` (always has value via `default_factory=uuid4`)
- **user_id**: `Optional[UUID]` → `UUID` (always has value)
- **Added status**: `KeyStatus` field (ACTIVE, EXPIRED, REVOKED, PENDING)
- **is_active**: Now a property based on status (backward compatible)

#### VpnKeyResponse Schema
- **vpn_type**: `VpnType` → **key_type**: `KeyType`
- **CreateVpnKeyRequest**: vpn_type → key_type

#### Enums
- **Deleted**: `enums/vpn_type.py` (duplicate of KeyType)
- **KeyType** is now the single source of truth

### Breaking Changes

**VpnKey entity refactored:**
- `id` is now always a UUID (not Optional[str])
- `status: KeyStatus` field added for full lifecycle management
- `is_active` is now a read-only property

**Schema naming:**
- `vpn_type` → `key_type` in all request/response schemas

### Migration Notes

Update code using VpnKey:

**Before (v0.11.0):**
```python
from usipipo_commons.domain.entities import VpnKey
from usipipo_commons.domain.enums import VpnType

key = VpnKey(
    id="some-string",
    user_id=some_uuid,
    vpn_type=VpnType.WIREGUARD,
)
```

**After (v0.12.0):**
```python
from usipipo_commons.domain.entities import VpnKey
from usipipo_commons.domain.enums import KeyType, KeyStatus

key = VpnKey(
    user_id=some_uuid,
    key_type=KeyType.WIREGUARD,
    status=KeyStatus.ACTIVE,
)

# Access is_active as property
if key.is_active:  # Returns key.status == KeyStatus.ACTIVE
    ...
```

---

## [0.11.0] - 2026-03-22

### Changed

#### SubscriptionPlan Entity
- **user_id**: Changed from `int` to `UUID` for multi-client support
- **Changed to `@dataclass`**: Migrated from Pydantic `BaseModel` to `@dataclass` for consistency with other entities
- **Added fields**: `id`, `created_at`, `updated_at` for full entity tracking
- **New properties**: `days_remaining`, `is_expiring_soon` for subscription management

#### SubscriptionTransaction Entity
- **user_id**: Changed from `int` to `UUID` for multi-client support

#### Wallet Entities
- **Fixed datetime usage**: Changed `datetime.utcnow()` to `datetime.now(timezone.utc)` (Python 3.12+ compatible)
- **WalletPool**: Added missing `updated_at` field

### Breaking Changes

**`SubscriptionPlan.user_id` and `SubscriptionTransaction.user_id` are now `UUID` instead of `int`**

This is a breaking change for code that directly accesses these fields:

**Before (v0.10.0):**
```python
from usipipo_commons.domain.entities import SubscriptionPlan

plan = SubscriptionPlan(user_id=123456)  # int (Telegram ID)
```

**After (v0.11.0):**
```python
from uuid import UUID
from usipipo_commons.domain.entities import SubscriptionPlan

plan = SubscriptionPlan(user_id=UUID("369a4d7f-e8ef-4d81-84f1-483363f81d00"))  # UUID
```

### Migration Notes

This change enables multi-client support (Android, Desktop, Web) without requiring Telegram.
The backend will need to:
1. Update database schema with Alembic migration
2. Update service signatures to use `UUID` instead of `int`
3. Update routers to use `current_user.id` instead of `current_user.telegram_id`

---

## [0.10.0] - 2026-03-22

### Changed

#### VpnKey Entity
- **user_id**: Changed from `int` to `UUID` for consistency with backend database schema
- This change aligns the entity with the backend's `vpn_keys.user_id` column which uses UUID type
- Backward compatible with existing code that doesn't directly access user_id

### Migration Notes

If you're using `VpnKey.user_id` directly:

**Before (v0.9.0):**
```python
from usipipo_commons.domain.entities import VpnKey

key = VpnKey(user_id=123456)  # int
```

**After (v0.10.0):**
```python
from uuid import UUID
from usipipo_commons.domain.entities import VpnKey

key = VpnKey(user_id=UUID("369a4d7f-e8ef-4d81-84f1-483363f81d00"))  # UUID
```

---

## [0.9.0] - 2026-03-21

### Added
- **Wallet Management Entities**: 
  - `Wallet` entity for BSC wallet management (address, balance, transaction tracking)
  - `WalletPool` entity for reusable wallet pool (expired order wallet recycling)
  - `WalletStatus` enum: ACTIVE, INACTIVE, AVAILABLE, IN_USE
- **Wallet Repository Interfaces**:
  - `IWalletRepository` with CRUD operations and reusable wallet methods
  - `IWalletPoolRepository` with pool management and cleanup methods
- **Wallet Methods**:
  - `Wallet.create()`: Factory method for new wallets
  - `Wallet.update_balance()`: Balance and transaction tracking
  - `Wallet.deactivate()` / `Wallet.activate()`: Status management
  - `WalletPool.create()`: Factory method for pool entries
  - `WalletPool.mark_reused()`: Mark wallet as reused by user
  - `WalletPool.is_available()`: Check availability for reuse
  - `WalletPool.is_expired()`: Check expiration status

## [0.8.0] - 2026-03-21

### Added
- **Referral Entity**: New `Referral` entity representing a referral relationship between users
- **User Bonus Fields**: Added `referral_credits`, `purchase_count`, `loyalty_bonus_percent`, `welcome_bonus_used`, `referred_users_with_purchase` to `User` entity
- **Data Package Export**: Exported `DataPackage` and `PackageType` from `usipipo_commons.domain.entities`

## [0.7.0] - 2026-03-21

### Added
- **Admin Panel Entities Export**: Exported `AdminUserInfo`, `AdminKeyInfo`, `ServerStatus`, `AdminOperationResult` from `usipipo_commons.domain.entities`
  - `AdminUserInfo` entity for administrative user information (user_id, username, keys count, referral_credits, etc.)
  - `AdminKeyInfo` entity for VPN key administration (key details, usage, status)
  - `ServerStatus` entity for VPN server health monitoring
  - `AdminOperationResult` entity for standardized admin operation responses

## [0.6.0] - 2026-03-21

### Added
- **Ticket System Entities Export**: Exported `Ticket`, `TicketMessage`, `TicketCategory`, `TicketPriority`, `TicketStatus` from `usipipo_commons.domain.entities`
  - `Ticket` entity with full support ticket workflow (create, update, close, resolve)
  - `TicketMessage` entity for ticket conversation threads
  - `TicketCategory` enum: VPN_FAIL, PAYMENT, ACCOUNT, OTHER
  - `TicketPriority` enum: HIGH, MEDIUM, LOW
  - `TicketStatus` enum: OPEN, RESPONDED, RESOLVED, CLOSED
  - Helper properties: `ticket_number`, `is_open`, `is_resolved`, `is_closed`
  - Status update method: `update_status()`

---

## [0.5.6] - 2026-03-21

### Added
- **Admin Entities**: `AdminUserInfo`, `AdminKeyInfo`, `ServerStatus`, `AdminOperationResult`
- **Balance Entity**: `Balance` with `add()`, `subtract()`, `has_sufficient()` methods
- **Data Package Entity**: `DataPackage` with `PackageType` enum (BASIC, ESTANDAR, AVANZADO, PREMIUM, UNLIMITED)
- **Subscription Transaction Entity**: `SubscriptionTransaction` with status tracking
- **Ticket System Entities**: `Ticket`, `TicketMessage` with full support workflow
- **VPN Key Enhancements**: 
  - `KeyType` enum (OUTLINE, WIREGUARD)
  - Usage tracking methods: `used_mb()`, `used_gb()`, `remaining_bytes()`
  - Billing management: `needs_reset()`, `reset_billing_cycle()`, `add_usage()`
  - Serialization: `to_dict()` method
- **New Enums**:
  - `SubscriptionTransactionStatus` (PENDING, ACTIVE, COMPLETED, FAILED, REFUNDED)
  - `BillingStatus` (PENDING, PROCESSING, COMPLETED, FAILED)
  - `InvoiceStatus` (DRAFT, ISSUED, PAID, OVERDUE, CANCELLED)
  - `ConsumptionPaymentMethod` (STRIPE, CRYPTO, MANUAL)

### Changed
- **VpnKey Entity**: Complete refactor with monorepo-aligned structure
  - Changed `user_id` from UUID to `int` (telegram_id)
  - Changed `vpn_type` to `key_type` for clarity
  - Fixed dataclass field ordering for Python 3.13 compatibility

### Fixed
- All entity tests updated and passing (33 tests)
- Dataclass field ordering issues in Python 3.13

---

## [0.5.5] - 2026-03-21

### Added
- **SubscriptionPlan Entity**: Complete subscription plan management
- **PlanType Enum**: ONE_MONTH, THREE_MONTHS, SIX_MONTHS

---

## [0.5.4] - 2026-03-21

### Added
- **CryptoOrder Entity**: Crypto payment order management with state machine
- **CryptoOrderStatus Enum**: PENDING, COMPLETED, FAILED, EXPIRED

### Changed
- Fixed `CryptoOrder` dataclass field ordering (user_id moved to end with default)

---

## [0.5.3] - 2026-03-21

### Added
- **Consumption Billing Entities**: 
  - `ConsumptionBilling` with billing cycle tracking
  - `ConsumptionInvoice` with invoice generation
- **New Enums**:
  - `BillingStatus`
  - `InvoiceStatus`
  - `ConsumptionPaymentMethod`

---

## [0.5.2] - 2026-03-20

### Added
- **Crypto Transaction Support**:
  - `CryptoTransaction` entity with blockchain confirmation tracking
  - `WebhookToken` entity for secure webhook validation
  - `CryptoTransactionStatus` enum (PENDING, CONFIRMING, COMPLETED, FAILED)

### Changed
- Added `CRYPTO_CONFIRMATIONS_REQUIRED = 15` constant
- Added `WEBHOOK_TOKEN_EXPIRY_MINUTES = 30` constant

---

## [0.5.1] - 2026-03-20

### Added
- **Core Domain Entities**:
  - `User` - User account management
  - `VpnKey` - VPN key representation
  - `Payment` - Payment transaction tracking
- **Core Enums**:
  - `VpnType` - VPN protocol types
  - `KeyStatus` - Key lifecycle status
  - `PaymentStatus` - Payment state machine
  - `PaymentMethod` - Supported payment methods
- **Pydantic Schemas**: Request/response validation models
- **Constants**: Plans, bonuses, error codes
- **Utilities**: Validators and formatters
- **Test Suite**: 33 comprehensive tests

---

## [0.4.1] - 2026-03-20

### Fixed
- **VpnKey Entity**: Added `to_dict()` method for serialization
- **Tests**: Updated VpnKey tests to match monorepo entity structure

---

## [0.4.0] - 2026-03-20

### Added
- Complete entity library port from monorepo (14 entities, 14 enums)

---

## [0.3.0] - 2026-03-20

### Added
- Crypto payment entities and enums

---

## [0.2.0] - 2026-03-19

### Added
- Initial crypto payment support

---

## [0.1.0] - 2026-03-18

### Added
- Initial release with core domain entities, schemas, and utilities

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.11.0 | 2026-03-22 | Multi-client support: user_id int → UUID in subscriptions |
| 0.10.0 | 2026-03-22 | VpnKey entity: user_id int → UUID |
| 0.9.0 | 2026-03-21 | Wallet Management Entities |
| 0.8.0 | 2026-03-21 | Referral System + User Bonus Fields |
| 0.7.0 | 2026-03-21 | Admin Panel Entities |
| 0.6.0 | 2026-03-21 | Ticket System Entities |
| 0.5.6 | 2026-03-20 | Complete Entity Library |
| 0.5.5 | 2026-03-20 | Subscription Entities |
| 0.5.3 | 2026-03-20 | Crypto Payment Entities |
| 0.5.2 | 2026-03-20 | Consumption Billing Entities |
| 0.4.0 | 2026-03-20 | Initial entity library port |

---

## Links

- [GitHub Repository](https://github.com/uSipipo-Team/usipipo-commons)
- [PyPI Package](https://pypi.org/project/usipipo-commons/)
- [Issue Tracker](https://github.com/uSipipo-Team/usipipo-commons/issues)
- [Latest Release v0.11.0](https://github.com/uSipipo-Team/usipipo-commons/releases/tag/v0.11.0)

---

[Unreleased]: https://github.com/uSipipo-Team/usipipo-commons/compare/v0.11.0...HEAD
[0.11.0]: https://github.com/uSipipo-Team/usipipo-commons/releases/tag/v0.11.0
[0.10.0]: https://github.com/uSipipo-Team/usipipo-commons/releases/tag/v0.10.0
[0.9.0]: https://github.com/uSipipo-Team/usipipo-commons/compare/v0.8.0...v0.9.0
