# uSipipo Commons

> Shared library for the uSipipo VPN ecosystem

[![PyPI version](https://img.shields.io/pypi/v/usipipo-commons.svg)](https://pypi.org/project/usipipo-commons/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/usipipo-commons.svg)](https://pypi.org/project/usipipo-commons/)
[![License](https://img.shields.io/pypi/l/usipipo-commons.svg)](https://github.com/uSipipo-Team/usipipo/blob/main/LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/usipipo-commons.svg)](https://pypi.org/project/usipipo-commons/)

## Overview

**uSipipo Commons** is the shared library for the uSipipo VPN ecosystem, providing domain entities, enums, constants, and utilities used across all uSipipo services.

### What It Provides

- **Domain Entities**: Core business entities (User, VpnKey, Payment, Subscription, etc.)
- **Enums**: Type-safe enumerations for statuses, methods, and types
- **Constants**: Shared constants for plans, limits, and error codes
- **Utilities**: Validation and formatting helper functions

### What Projects Use It

- [`usipipo-backend`](https://github.com/uSipipo-Team/usipipo) - FastAPI backend API
- [`usipipo-telegram-bot`](https://github.com/uSipipo-Team/usipipo) - Telegram bot
- [`usipipo-miniapp-web`](https://github.com/uSipipo-Team/usipipo-miniapp-web) - Telegram Mini App
- [`usipipo-landing`](https://github.com/uSipipo-Team/usipipo-landing) - Marketing site

---

## Installation

### From PyPI (Recommended)

```bash
pip install usipipo-commons
```

### From GitHub (Development)

```bash
pip install git+https://github.com/uSipipo-Team/usipipo.git
```

### Local Development

```bash
# Clone the repository
git clone https://github.com/uSipipo-Team/usipipo.git
cd packages/common

# Install with uv (recommended)
uv sync --dev

# Or with pip
pip install -e .
```

---

## Quick Start

```python
from usipipo_commons.domain.entities import User, VpnKey, Payment, SubscriptionPlan
from usipipo_commons.domain.enums import KeyType, KeyStatus, PaymentStatus, PlanType
from usipipo_commons.schemas import CreateVpnKeyRequest, PaymentResponse
from usipipo_commons.constants import FREE_GB, REFERRAL_BONUS_GB, PRICE_PER_GB
from usipipo_commons.utils import validate_telegram_id, format_bytes, format_datetime
from datetime import datetime, timezone
from uuid import uuid4

# Create a User entity
user = User(
    id=uuid4(),
    telegram_id=123456789,
    username="johndoe",
    first_name="John",
    last_name="Doe",
    is_admin=False,
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
    balance_gb=5.0,
    total_purchased_gb=0.0,
    referral_code="JOHN123",
    referred_by=None,
)

# Create a VPN Key entity
vpn_key = VpnKey(
    user_id=user.id,
    key_type=KeyType.OUTLINE,
    status=KeyStatus.ACTIVE,
    name="My VPN Key",
    key_data="ss://...",
    data_limit_bytes=5 * 1024**3,  # 5 GB
)

# Use constants
print(f"Free GB: {FREE_GB}")  # 5.0
print(f"Referral Bonus: {REFERRAL_BONUS_GB} GB")  # 5.0
print(f"Price per GB: ${PRICE_PER_GB}")  # $0.50

# Use utilities
assert validate_telegram_id(123456789) == True
print(format_bytes(5.5))  # "5.50 GB"
print(format_datetime(datetime.now(timezone.utc)))  # "2026-03-22 12:00:00 UTC"

# Convert entity to dict for serialization
user_dict = user.to_dict()
vpn_key_dict = vpn_key.to_dict()
```

---

## Domain Entities

### Core Entities

#### User

Represents a user in the uSipipo ecosystem.

**Properties:**
- `id: UUID` - Unique user identifier
- `telegram_id: int` - Telegram user ID
- `username: Optional[str]` - Telegram username
- `first_name: Optional[str]` - User's first name
- `last_name: Optional[str]` - User's last name
- `is_admin: bool` - Whether user has admin privileges
- `created_at: datetime` - Account creation timestamp
- `updated_at: datetime` - Last update timestamp
- `balance_gb: float` - Available data balance in GB
- `total_purchased_gb: float` - Total GB purchased historically
- `referral_code: str` - User's unique referral code
- `referred_by: Optional[UUID]` - ID of user who referred this user
- `referral_credits: int` - Credits earned from referrals
- `purchase_count: int` - Number of purchases made
- `loyalty_bonus_percent: int` - Loyalty bonus percentage
- `welcome_bonus_used: bool` - Whether welcome bonus was used
- `referred_users_with_purchase: int` - Number of referred users who made purchases

**Example:**
```python
from usipipo_commons.domain.entities import User
from datetime import datetime, timezone
from uuid import uuid4

user = User(
    id=uuid4(),
    telegram_id=123456789,
    username="johndoe",
    first_name="John",
    last_name="Doe",
    is_admin=False,
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
    balance_gb=5.0,
    total_purchased_gb=10.0,
    referral_code="JOHN123",
    referred_by=None,
    referral_credits=5,
    purchase_count=2,
)
```

#### VpnKey

Represents a VPN access credential.

**Properties:**
- `id: UUID` - Unique key identifier
- `user_id: UUID` - Owner's user ID
- `key_type: KeyType` - VPN type (OUTLINE or WIREGUARD)
- `status: KeyStatus` - Key status (ACTIVE, EXPIRED, REVOKED, PENDING)
- `name: str` - User-friendly key name
- `key_data: str` - Connection string (ss://... or WireGuard config)
- `external_id: str` - Server-assigned ID (Outline/WireGuard)
- `created_at: datetime` - Creation timestamp
- `used_bytes: int` - Data consumed in bytes
- `last_seen_at: Optional[datetime]` - Last client activity
- `data_limit_bytes: int` - Data limit in bytes
- `billing_reset_at: datetime` - Billing cycle reset date
- `expires_at: Optional[datetime]` - Key expiration date

**Computed Properties:**
- `is_active: bool` - True if status is ACTIVE
- `used_mb: float` - Usage in MB
- `used_gb: float` - Usage in GB
- `data_limit_gb: float` - Limit in GB
- `remaining_bytes: int` - Remaining data in bytes
- `is_over_limit: bool` - True if over data limit

**Methods:**
- `needs_reset() -> bool` - Check if 30 days passed since last reset
- `reset_billing_cycle()` - Reset billing cycle
- `add_usage(bytes_used: int)` - Add data usage
- `to_dict() -> dict` - Convert to dictionary

**Example:**
```python
from usipipo_commons.domain.entities import VpnKey
from usipipo_commons.domain.enums import KeyType, KeyStatus
from uuid import uuid4

vpn_key = VpnKey(
    user_id=uuid4(),
    key_type=KeyType.OUTLINE,
    status=KeyStatus.ACTIVE,
    name="Home VPN",
    key_data="ss://YWVzLTI1Ni1nY206...",
    data_limit_bytes=5 * 1024**3,  # 5 GB
)

print(f"Used: {vpn_key.used_gb:.2f} GB")
print(f"Remaining: {vpn_key.remaining_bytes / 1024**3:.2f} GB")
print(f"Active: {vpn_key.is_active}")

# Add usage
vpn_key.add_usage(1024 * 1024 * 500)  # 500 MB
```

#### Balance

Represents user balance in stars (Telegram payment units).

**Properties:**
- `user_id: UUID` - User identifier
- `stars: int` - Balance in stars

**Methods:**
- `add(amount: int) -> Balance` - Add amount and return new Balance
- `subtract(amount: int) -> Balance` - Subtract amount and return new Balance
- `has_sufficient(amount: int) -> bool` - Check if balance is sufficient

**Example:**
```python
from usipipo_commons.domain.entities import Balance
import uuid

balance = Balance(user_id=uuid.uuid4(), stars=1000)

# Add stars
new_balance = balance.add(500)
print(new_balance.stars)  # 1500

# Check sufficient
print(balance.has_sufficient(800))  # True

# Subtract
remaining = balance.subtract(300)
print(remaining.stars)  # 700
```

---

### Payment Entities

#### Payment

Represents a payment transaction.

**Properties:**
- `id: UUID` - Unique payment identifier
- `user_id: UUID` - User who made the payment
- `amount_usd: float` - Payment amount in USD
- `gb_purchased: float` - GB purchased in this payment
- `method: PaymentMethod` - Payment method used
- `status: PaymentStatus` - Payment status
- `crypto_address: Optional[str]` - Crypto wallet address (if crypto payment)
- `crypto_network: Optional[str]` - Crypto network (e.g., BSC, TRC20)
- `telegram_star_invoice_id: Optional[str]` - Telegram Stars invoice ID
- `created_at: datetime` - Payment creation timestamp
- `expires_at: Optional[datetime]` - Payment expiration timestamp
- `paid_at: Optional[datetime]` - Payment completion timestamp
- `transaction_hash: Optional[str]` - Blockchain transaction hash

**Example:**
```python
from usipipo_commons.domain.entities import Payment
from usipipo_commons.domain.enums import PaymentMethod, PaymentStatus
from datetime import datetime, timezone
from uuid import uuid4

payment = Payment(
    id=uuid4(),
    user_id=uuid4(),
    amount_usd=5.00,
    gb_purchased=10.0,
    method=PaymentMethod.CRYPTO_USDT,
    status=PaymentStatus.PENDING,
    crypto_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    crypto_network="BSC",
    created_at=datetime.now(timezone.utc),
)
```

#### CryptoOrder

Represents a cryptocurrency order.

**Properties:**
- `id: UUID` - Unique order identifier
- `user_id: UUID` - User who created the order
- `package_type: str` - Package type purchased
- `amount_usdt: float` - Amount in USDT
- `wallet_address: str` - Destination wallet address
- `tron_dealer_order_id: Optional[str]` - TronDealer order ID
- `status: CryptoOrderStatus` - Order status
- `created_at: datetime` - Order creation timestamp
- `expires_at: datetime` - Order expiration timestamp
- `tx_hash: Optional[str]` - Transaction hash
- `confirmed_at: Optional[datetime]` - Confirmation timestamp

**Methods:**
- `create(user_id, package_type, amount_usdt, wallet_address) -> CryptoOrder` - Factory method
- `to_dict() -> dict` - Convert to dictionary

**Example:**
```python
from usipipo_commons.domain.entities import CryptoOrder
from uuid import uuid4

order = CryptoOrder.create(
    user_id=uuid4(),
    package_type="premium",
    amount_usdt=10.0,
    wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
)
```

#### CryptoTransaction

Represents a detected blockchain transaction.

**Properties:**
- `id: UUID` - Unique transaction identifier
- `user_id: Optional[UUID]` - Associated user ID
- `wallet_address: str` - Wallet address involved
- `amount: float` - Transaction amount
- `token_symbol: str` - Token symbol (default: USDT)
- `tx_hash: str` - Transaction hash
- `status: CryptoTransactionStatus` - Transaction status
- `confirmations: int` - Number of confirmations
- `confirmed_at: Optional[datetime]` - Confirmation timestamp
- `created_at: datetime` - Detection timestamp
- `raw_payload: dict` - Raw transaction data

**Properties:**
- `is_confirmed: bool` - True if status is CONFIRMED
- `is_pending: bool` - True if status is PENDING

**Methods:**
- `confirm()` - Mark as confirmed
- `fail()` - Mark as failed
- `create(wallet_address, amount, tx_hash, token_symbol, raw_payload) -> CryptoTransaction` - Factory method

**Example:**
```python
from usipipo_commons.domain.entities import CryptoTransaction

tx = CryptoTransaction.create(
    wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    amount=10.0,
    tx_hash="0xabc123...",
    token_symbol="USDT",
)

tx.confirm()
print(tx.is_confirmed)  # True
```

#### WebhookToken

Token for validating webhooks.

**Properties:**
- `id: UUID` - Unique token identifier
- `token_hash: str` - Hashed token value
- `purpose: str` - Token purpose (default: "tron_dealer")
- `created_at: datetime` - Creation timestamp
- `expires_at: datetime` - Expiration timestamp
- `used_at: Optional[datetime]` - Usage timestamp
- `extra_data: dict` - Additional data

**Properties:**
- `is_expired: bool` - True if token is expired
- `is_used: bool` - True if token was used

**Methods:**
- `mark_used()` - Mark token as used
- `create(token_hash, purpose) -> WebhookToken` - Factory method

**Example:**
```python
from usipipo_commons.domain.entities import WebhookToken

token = WebhookToken.create(
    token_hash="abc123...",
    purpose="tron_dealer",
)

if not token.is_expired and not token.is_used:
    token.mark_used()
```

---

### Subscription Entities

#### SubscriptionPlan

Represents an active user subscription plan.

**Properties:**
- `user_id: UUID` - User ID
- `plan_type: PlanType` - Plan type (ONE_MONTH, THREE_MONTHS, SIX_MONTHS)
- `stars_paid: int` - Stars paid for subscription
- `payment_id: str` - Associated payment ID
- `starts_at: datetime` - Subscription start date
- `expires_at: datetime` - Subscription expiration date
- `id: UUID` - Unique subscription identifier
- `is_active: bool` - Whether subscription is active
- `created_at: datetime` - Creation timestamp
- `updated_at: datetime` - Last update timestamp

**Properties:**
- `is_expired: bool` - True if subscription is expired
- `days_remaining: int` - Days remaining until expiration
- `is_expiring_soon: bool` - True if expires within 7 days

**Example:**
```python
from usipipo_commons.domain.entities import SubscriptionPlan
from usipipo_commons.domain.enums import PlanType
from datetime import datetime, timezone, timedelta
from uuid import uuid4

now = datetime.now(timezone.utc)
plan = SubscriptionPlan(
    user_id=uuid4(),
    plan_type=PlanType.ONE_MONTH,
    stars_paid=1200,
    payment_id="pay_123",
    starts_at=now,
    expires_at=now + timedelta(days=30),
)

print(f"Days remaining: {plan.days_remaining}")
print(f"Expiring soon: {plan.is_expiring_soon}")
```

#### SubscriptionTransaction

Represents a subscription transaction for tracking and idempotency.

**Properties:**
- `transaction_id: str` - Unique transaction identifier
- `user_id: UUID` - User ID
- `plan_type: str` - Plan type
- `amount_stars: int` - Amount in stars
- `payload: str` - Transaction payload
- `status: SubscriptionTransactionStatus` - Transaction status
- `created_at: Optional[datetime]` - Creation timestamp
- `expires_at: Optional[datetime]` - Expiration timestamp (30 minutes)
- `completed_at: Optional[datetime]` - Completion timestamp
- `id: Optional[UUID]` - Internal ID

**Properties:**
- `is_pending: bool` - True if status is PENDING
- `is_completed: bool` - True if status is COMPLETED
- `is_expired: bool` - True if transaction is expired

**Methods:**
- `mark_completed()` - Mark as completed
- `mark_failed()` - Mark as failed
- `mark_expired()` - Mark as expired

**Example:**
```python
from usipipo_commons.domain.entities import SubscriptionTransaction
from uuid import uuid4

tx = SubscriptionTransaction(
    transaction_id="tx_123",
    user_id=uuid4(),
    plan_type="one_month",
    amount_stars=1200,
    payload="{}",
)

tx.mark_completed()
print(tx.is_completed)  # True
```

---

### Consumption Billing Entities

#### ConsumptionBilling

Represents a billing cycle for consumption-based billing.

**Properties:**
- `user_id: int` - User ID
- `started_at: datetime` - Cycle start date
- `status: BillingStatus` - Cycle status (ACTIVE, CLOSED, PAID, CANCELLED)
- `id: Optional[UUID]` - Unique cycle identifier
- `ended_at: Optional[datetime]` - Cycle end date
- `mb_consumed: Decimal` - MB consumed in cycle
- `total_cost_usd: Decimal` - Total cost in USD
- `price_per_mb_usd: Decimal` - Price per MB (default: $0.000244140625)
- `created_at: datetime` - Creation timestamp

**Properties:**
- `is_active: bool` - True if status is ACTIVE
- `is_closed: bool` - True if status is CLOSED
- `is_paid: bool` - True if status is PAID
- `gb_consumed: Decimal` - GB consumed (formatted)

**Methods:**
- `add_consumption(mb_used: Decimal)` - Add consumption to cycle
- `close_cycle()` - Close the billing cycle
- `mark_as_paid()` - Mark cycle as paid
- `get_formatted_cost() -> str` - Get formatted cost string
- `get_formatted_consumption() -> str` - Get formatted consumption string

**Example:**
```python
from usipipo_commons.domain.entities import ConsumptionBilling
from usipipo_commons.domain.enums import BillingStatus
from datetime import datetime, timezone
from decimal import Decimal

cycle = ConsumptionBilling(
    user_id=123456789,
    started_at=datetime.now(timezone.utc),
)

# Add consumption
cycle.add_consumption(Decimal("512.5"))  # 512.5 MB
print(cycle.get_formatted_consumption())  # "512.50 MB"
print(cycle.get_formatted_cost())  # "$0.13 USD"

# Close cycle
cycle.close_cycle()
print(cycle.is_closed)  # True

# Mark as paid
cycle.mark_as_paid()
print(cycle.is_paid)  # True
```

#### ConsumptionInvoice

Represents an invoice for consumption payment.

**Properties:**
- `billing_id: UUID` - Associated billing cycle ID
- `user_id: int` - User ID
- `amount_usd: Decimal` - Invoice amount in USD
- `wallet_address: str` - Wallet address for payment
- `payment_method: ConsumptionPaymentMethod` - Payment method (STARS or CRYPTO)
- `status: InvoiceStatus` - Invoice status (PENDING, PAID, EXPIRED, CANCELLED)
- `id: Optional[UUID]` - Unique invoice identifier
- `expires_at: Optional[datetime]` - Expiration timestamp (30 minutes)
- `paid_at: Optional[datetime]` - Payment timestamp
- `transaction_hash: Optional[str]` - Transaction hash (crypto)
- `telegram_payment_id: Optional[str]` - Telegram payment ID (Stars)
- `created_at: datetime` - Creation timestamp

**Properties:**
- `is_pending: bool` - True if status is PENDING
- `is_paid: bool` - True if status is PAID
- `is_expired: bool` - True if invoice is expired
- `is_usdt_payment: bool` - True if wallet starts with "0x"
- `time_remaining_seconds: int` - Seconds remaining to pay
- `time_remaining_formatted: str` - Formatted time (MM:SS)

**Methods:**
- `mark_as_paid(transaction_hash, telegram_payment_id)` - Mark as paid
- `mark_as_expired()` - Mark as expired
- `get_payment_instructions() -> str` - Get payment instructions
- `get_stars_amount() -> int` - Get amount in Stars (1 USDT = 120 Stars)
- `get_formatted_amount() -> str` - Get formatted amount string

**Example:**
```python
from usipipo_commons.domain.entities import ConsumptionInvoice
from usipipo_commons.domain.enums import ConsumptionPaymentMethod, InvoiceStatus
from datetime import datetime, timezone
from decimal import Decimal
import uuid

invoice = ConsumptionInvoice(
    billing_id=uuid.uuid4(),
    user_id=123456789,
    amount_usd=Decimal("5.50"),
    wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    payment_method=ConsumptionPaymentMethod.CRYPTO,
)

print(f"Amount: {invoice.get_formatted_amount()}")  # "$5.50 USD"
print(f"Time remaining: {invoice.time_remaining_formatted}")  # "29:45"
print(invoice.get_payment_instructions())
```

---

### Data Package Entities

#### DataPackage

Represents a purchased data package.

**Properties:**
- `user_id: UUID` - User ID
- `package_type: PackageType` - Package type (BASIC, ESTANDAR, AVANZADO, PREMIUM, UNLIMITED)
- `data_limit_bytes: int` - Data limit in bytes
- `stars_paid: int` - Stars paid for package
- `expires_at: datetime` - Package expiration date
- `id: Optional[UUID]` - Unique package identifier
- `data_used_bytes: int` - Data consumed in bytes
- `purchased_at: Optional[datetime]` - Purchase timestamp
- `is_active: bool` - Whether package is active
- `telegram_payment_id: Optional[str]` - Telegram payment ID

**Properties:**
- `remaining_bytes: int` - Remaining data in bytes
- `is_expired: bool` - True if package is expired
- `is_valid: bool` - True if active and not expired

**Methods:**
- `add_usage(bytes_used: int)` - Add data usage
- `deactivate()` - Deactivate the package

**Example:**
```python
from usipipo_commons.domain.entities import DataPackage, PackageType
from datetime import datetime, timezone, timedelta
import uuid

package = DataPackage(
    user_id=uuid.uuid4(),
    package_type=PackageType.PREMIUM,
    data_limit_bytes=50 * 1024**3,  # 50 GB
    stars_paid=5000,
    expires_at=datetime.now(timezone.utc) + timedelta(days=30),
)

print(f"Remaining: {package.remaining_bytes / 1024**3:.2f} GB")
print(f"Valid: {package.is_valid}")

package.add_usage(5 * 1024**3)  # 5 GB used
```

---

### Admin Entities

#### AdminUserInfo

Administrative user information for admin panels.

**Properties:**
- `user_id: UUID` - User ID
- `username: Optional[str]` - Telegram username
- `first_name: str` - First name
- `last_name: Optional[str]` - Last name
- `total_keys: int` - Total VPN keys owned
- `active_keys: int` - Active VPN keys count
- `stars_balance: int` - Stars balance (deprecated, for compatibility)
- `total_deposited: int` - Total deposited (referral credits)
- `referral_credits: int` - Referral credits earned
- `registration_date: Optional[datetime]` - Registration date
- `last_activity: Optional[datetime]` - Last activity timestamp

**Example:**
```python
from usipipo_commons.domain.entities import AdminUserInfo
from datetime import datetime, timezone
import uuid

admin_user = AdminUserInfo(
    user_id=uuid.uuid4(),
    username="johndoe",
    first_name="John",
    last_name="Doe",
    total_keys=5,
    active_keys=3,
    referral_credits=25,
    registration_date=datetime.now(timezone.utc),
)
```

#### AdminKeyInfo

Administrative VPN key information for admin panels.

**Properties:**
- `key_id: str` - Key identifier
- `user_id: UUID` - Owner's user ID
- `user_name: str` - Owner's username
- `key_type: str` - VPN type (outline, wireguard)
- `key_name: str` - Key name
- `access_url: Optional[str]` - Access URL
- `created_at: datetime` - Creation timestamp
- `last_used: Optional[datetime]` - Last usage timestamp
- `data_limit: int` - Data limit in bytes
- `data_used: int` - Data consumed in bytes
- `is_active: bool` - Whether key is active
- `server_status: str` - Server status

**Example:**
```python
from usipipo_commons.domain.entities import AdminKeyInfo
from datetime import datetime, timezone
import uuid

key_info = AdminKeyInfo(
    key_id="key_123",
    user_id=uuid.uuid4(),
    user_name="johndoe",
    key_type="outline",
    key_name="Home VPN",
    access_url="ss://...",
    created_at=datetime.now(timezone.utc),
    data_limit=5 * 1024**3,
    data_used=1024**3,
    is_active=True,
    server_status="healthy",
)
```

#### ServerStatus

VPN server status information.

**Properties:**
- `server_type: str` - Server type (outline, wireguard)
- `is_healthy: bool` - Whether server is healthy
- `total_keys: int` - Total keys on server
- `active_keys: int` - Active keys count
- `version: Optional[str]` - Server version
- `uptime: Optional[str]` - Server uptime string
- `error_message: Optional[str]` - Error message if any

**Example:**
```python
from usipipo_commons.domain.entities import ServerStatus

status = ServerStatus(
    server_type="outline",
    is_healthy=True,
    total_keys=100,
    active_keys=85,
    version="1.2.3",
    uptime="15d 4h 32m",
)
```

#### AdminOperationResult

Result of an administrative operation.

**Properties:**
- `success: bool` - Whether operation succeeded
- `operation: str` - Operation name
- `target_id: str` - Target entity ID
- `message: str` - Result message
- `details: Optional[Dict]` - Additional details
- `timestamp: Optional[datetime]` - Operation timestamp

**Example:**
```python
from usipipo_commons.domain.entities import AdminOperationResult

result = AdminOperationResult(
    success=True,
    operation="revoke_key",
    target_id="key_123",
    message="Key revoked successfully",
    details={"previous_status": "active"},
)

if result.success:
    print(f"Operation {result.operation} completed: {result.message}")
```

---

### Support Entities

#### Ticket

Support ticket entity.

**Properties:**
- `user_id: UUID` - User who created ticket
- `category: TicketCategory` - Ticket category (VPN_FAIL, PAYMENT, ACCOUNT, OTHER)
- `priority: TicketPriority` - Priority (HIGH, MEDIUM, LOW)
- `subject: str` - Ticket subject
- `id: UUID` - Unique ticket identifier
- `status: TicketStatus` - Status (OPEN, RESPONDED, RESOLVED, CLOSED)
- `created_at: datetime` - Creation timestamp
- `updated_at: datetime` - Last update timestamp
- `resolved_at: Optional[datetime]` - Resolution timestamp
- `resolved_by: Optional[UUID]` - Admin who resolved
- `admin_notes: Optional[str]` - Admin internal notes

**Properties:**
- `ticket_number: str` - Readable ticket number (T-XXXXXXX)
- `is_open: bool` - True if OPEN or RESPONDED
- `is_resolved: bool` - True if RESOLVED
- `is_closed: bool` - True if CLOSED

**Methods:**
- `update_status(new_status, admin_id)` - Update ticket status

**Example:**
```python
from usipipo_commons.domain.entities import Ticket, TicketCategory, TicketPriority, TicketStatus
import uuid

ticket = Ticket(
    user_id=uuid.uuid4(),
    category=TicketCategory.VPN_FAIL,
    priority=TicketPriority.HIGH,
    subject="Cannot connect to VPN",
)

print(f"Ticket #{ticket.ticket_number}")
print(f"Status: {ticket.status.value}")

# Update status
ticket.update_status(TicketStatus.RESPONDED, admin_id=1)
```

#### TicketMessage

Message within a support ticket.

**Properties:**
- `ticket_id: UUID` - Parent ticket ID
- `from_user_id: UUID` - Message sender ID
- `message: str` - Message content
- `from_admin: bool` - True if sent by admin
- `id: UUID` - Unique message identifier
- `created_at: datetime` - Message timestamp

**Example:**
```python
from usipipo_commons.domain.entities import TicketMessage
import uuid

message = TicketMessage(
    ticket_id=uuid.uuid4(),
    from_user_id=uuid.uuid4(),
    message="I'm still having issues connecting",
    from_admin=False,
)
```

---

### Additional Entities

#### Referral

Represents a referral relationship.

**Properties:**
- `referrer_id: UUID` - ID of referring user
- `referred_id: UUID` - ID of referred user
- `id: Optional[UUID]` - Unique referral identifier
- `created_at: Optional[datetime]` - Creation timestamp
- `is_active: bool` - Whether referral is active
- `bonus_applied: bool` - Whether bonus was applied

**Example:**
```python
from usipipo_commons.domain.entities import Referral
from uuid import uuid4

referral = Referral(
    referrer_id=uuid4(),
    referred_id=uuid4(),
)
```

#### Wallet

BSC wallet for crypto payment management.

**Properties:**
- `id: UUID` - Unique wallet identifier
- `user_id: UUID` - Owner's user ID
- `address: str` - Wallet address
- `label: Optional[str]` - Wallet label
- `status: WalletStatus` - Wallet status
- `balance_usdt: float` - Current balance in USDT
- `created_at: datetime` - Creation timestamp
- `updated_at: datetime` - Last update timestamp
- `last_used_at: Optional[datetime]` - Last usage timestamp
- `total_received_usdt: float` - Total received in USDT
- `transaction_count: int` - Number of transactions

**Methods:**
- `create(user_id, address, label) -> Wallet` - Factory method
- `update_balance(amount_usdt)` - Update balance
- `deactivate()` - Deactivate wallet
- `activate()` - Activate wallet
- `to_dict() -> dict` - Convert to dictionary

**Example:**
```python
from usipipo_commons.domain.entities import Wallet
from usipipo_commons.domain.enums import WalletStatus
from uuid import uuid4

wallet = Wallet.create(
    user_id=uuid4(),
    address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    label="Main Wallet",
)

wallet.update_balance(10.0)
print(f"Balance: ${wallet.balance_usdt} USDT")
```

#### WalletPool

Pool of reusable expired wallets.

**Properties:**
- `id: UUID` - Unique pool entry identifier
- `wallet_address: str` - Wallet address
- `original_user_id: UUID` - Original owner's ID
- `status: WalletStatus` - Pool status
- `created_at: datetime` - Creation timestamp
- `released_at: datetime` - Release timestamp
- `expires_at: datetime` - Expiration timestamp
- `reused_by_user_id: Optional[UUID]` - Reused by user ID
- `reused_at: Optional[datetime]` - Reuse timestamp
- `updated_at: Optional[datetime]` - Last update timestamp

**Methods:**
- `create(wallet_address, original_user_id, expires_at) -> WalletPool` - Factory method
- `mark_reused(user_id)` - Mark as reused
- `mark_available()` - Mark as available
- `is_expired() -> bool` - Check if expired
- `is_available() -> bool` - Check if available
- `to_dict() -> dict` - Convert to dictionary

**Example:**
```python
from usipipo_commons.domain.entities import WalletPool
from datetime import datetime, timezone, timedelta
from uuid import uuid4

pool_entry = WalletPool.create(
    wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    original_user_id=uuid4(),
    expires_at=datetime.now(timezone.utc) + timedelta(days=7),
)

if pool_entry.is_available():
    pool_entry.mark_reused(uuid4())
```

---

## Enums Reference

### KeyType

VPN key types supported by the system.

```python
class KeyType(str, Enum):
    OUTLINE = "outline"
    WIREGUARD = "wireguard"
```

### KeyStatus

VPN key status values.

```python
class KeyStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"
```

### PaymentStatus

Payment transaction status values.

```python
class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
```

### PaymentMethod

Supported payment methods.

```python
class PaymentMethod(str, Enum):
    TELEGRAM_STARS = "telegram_stars"
    CRYPTO_USDT = "crypto_usdt"
    CRYPTO_BSC = "crypto_bsc"
```

### BillingStatus

Consumption billing cycle status values.

```python
class BillingStatus(str, Enum):
    ACTIVE = "active"      # Cycle in progress, consuming
    CLOSED = "closed"      # Cycle closed, awaiting payment
    PAID = "paid"          # Cycle paid, completed
    CANCELLED = "cancelled" # Cycle cancelled
```

### InvoiceStatus

Consumption invoice status values.

```python
class InvoiceStatus(str, Enum):
    PENDING = "pending"    # Invoice generated, awaiting payment
    PAID = "paid"          # Invoice paid successfully
    EXPIRED = "expired"    # Invoice expired
    CANCELLED = "cancelled" # Invoice manually cancelled
```

### ConsumptionPaymentMethod

Payment methods for consumption invoices.

```python
class ConsumptionPaymentMethod(str, Enum):
    STARS = "stars"    # Payment with Telegram Stars
    CRYPTO = "crypto"  # Payment with USDT (BSC)
```

### CryptoOrderStatus

Cryptocurrency order status values.

```python
class CryptoOrderStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
```

### CryptoTransactionStatus

Cryptocurrency transaction status values.

```python
class CryptoTransactionStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
```

### PlanType

Subscription plan types.

```python
class PlanType(str, Enum):
    ONE_MONTH = "one_month"
    THREE_MONTHS = "three_months"
    SIX_MONTHS = "six_months"
```

### WalletStatus

BSC wallet status values.

```python
class WalletStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    AVAILABLE = "available"
    IN_USE = "in_use"
```

### PackageType

Data package types available.

```python
class PackageType(str, Enum):
    BASIC = "basic"
    ESTANDAR = "estandar"
    AVANZADO = "avanzado"
    PREMIUM = "premium"
    UNLIMITED = "unlimited"
```

### TicketCategory

Support ticket categories.

```python
class TicketCategory(str, Enum):
    VPN_FAIL = "vpn_fail"
    PAYMENT = "payment"
    ACCOUNT = "account"
    OTHER = "other"
```

### TicketPriority

Ticket priority levels.

```python
class TicketPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

### TicketStatus

Ticket status values.

```python
class TicketStatus(str, Enum):
    OPEN = "open"
    RESPONDED = "responded"
    RESOLVED = "resolved"
    CLOSED = "closed"
```

---

## Constants

### Plan Constants

```python
from usipipo_commons.constants import (
    FREE_GB,              # 5.0 - Free tier data allowance (GB)
    FREE_KEYS_LIMIT,      # 2 - Maximum free VPN keys per user
    WELCOME_BONUS_GB,     # 2.0 - Welcome bonus data (GB)
    LOYALTY_BONUS_GB,     # 1.0 - Loyalty bonus data (GB)
    REFERRAL_BONUS_GB,    # 5.0 - Referral bonus data (GB)
    MAX_KEYS_PER_USER,    # 10 - Maximum VPN keys per user
    MIN_PACKAGE_GB,       # 1.0 - Minimum package size (GB)
    MAX_PACKAGE_GB,       # 100.0 - Maximum package size (GB)
    PRICE_PER_GB,         # 0.50 - Price per GB in USD
    BILLING_CYCLE_DAYS,   # 30 - Billing cycle duration (days)
)
```

### Error Codes

```python
from usipipo_commons.constants import (
    # User errors
    USER_NOT_FOUND,
    USER_ALREADY_EXISTS,
    USER_BANNED,
    
    # VPN key errors
    VPN_KEY_NOT_FOUND,
    VPN_KEY_LIMIT_REACHED,
    VPN_KEY_ALREADY_EXISTS,
    VPN_KEY_GENERATION_FAILED,
    
    # Payment errors
    PAYMENT_NOT_FOUND,
    PAYMENT_ALREADY_COMPLETED,
    PAYMENT_EXPIRED,
    PAYMENT_FAILED,
    INSUFFICIENT_BALANCE,
    
    # Referral errors
    REFERRAL_CODE_INVALID,
    REFERRAL_CODE_ALREADY_USED,
    SELF_REFERRAL_NOT_ALLOWED,
    
    # Authentication errors
    AUTH_INVALID_TOKEN,
    AUTH_TOKEN_EXPIRED,
    AUTH_INVALID_TELEGRAM_DATA,
)
```

---

## Utilities

### Validators

```python
from usipipo_commons.utils import (
    validate_telegram_id,
    validate_referral_code,
    validate_vpn_key_name,
)

# Validate Telegram ID
is_valid = validate_telegram_id(123456789)  # True
is_valid = validate_telegram_id(-1)  # False

# Validate referral code (alphanumeric, 4-16 chars)
is_valid = validate_referral_code("JOHN123")  # True
is_valid = validate_referral_code("abc")  # False (too short)

# Validate VPN key name (letters, numbers, spaces, dashes, max 50 chars)
is_valid = validate_vpn_key_name("Home VPN")  # True
is_valid = validate_vpn_key_name("")  # False
```

### Formatters

```python
from usipipo_commons.utils import (
    format_bytes,
    format_datetime,
    format_duration,
)
from datetime import datetime, timezone

# Format bytes to human-readable
print(format_bytes(5.5))  # "5.50 GB"
print(format_bytes(1500.0))  # "1.50 TB"

# Format datetime
now = datetime.now(timezone.utc)
print(format_datetime(now))  # "2026-03-22 12:00:00 UTC"

# Format duration in seconds
print(format_duration(3665))  # "1h 1m"
print(format_duration(125))  # "2m"
```

---

## Project Structure

```
usipipo_commons/
├── domain/
│   ├── entities/          # Domain entities
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── vpn_key.py
│   │   ├── payment.py
│   │   ├── balance.py
│   │   ├── crypto_order.py
│   │   ├── crypto_transaction.py
│   │   ├── subscription_plan.py
│   │   ├── subscription_transaction.py
│   │   ├── consumption_billing.py
│   │   ├── consumption_invoice.py
│   │   ├── data_package.py
│   │   ├── ticket.py
│   │   ├── ticket_message.py
│   │   ├── admin_user_info.py
│   │   ├── admin_key_info.py
│   │   ├── server_status.py
│   │   ├── admin_operation_result.py
│   │   ├── referral.py
│   │   ├── wallet.py
│   │   └── admin.py
│   ├── enums/             # Shared enumerations
│   │   ├── __init__.py
│   │   ├── key_type.py
│   │   ├── key_status.py
│   │   ├── payment_status.py
│   │   ├── payment_method.py
│   │   ├── billing_status.py
│   │   ├── invoice_status.py
│   │   ├── consumption_payment_method.py
│   │   ├── crypto_order_status.py
│   │   ├── crypto_transaction_status.py
│   │   ├── plan_type.py
│   │   ├── wallet_status.py
│   │   └── ...
│   └── interfaces/        # Repository interfaces
├── schemas/               # Pydantic schemas for API
├── constants/             # Shared constants
│   ├── __init__.py
│   ├── plans.py           # Plan limits and bonuses
│   └── errors.py          # Error codes
└── utils/                 # Utility functions
    ├── __init__.py
    ├── validators.py      # Validation functions
    └── formatters.py      # Formatting functions
```

---

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/uSipipo-Team/usipipo.git
cd packages/common

# Install dependencies with uv (recommended)
uv sync --dev

# Or with pip
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=usipipo_commons --cov-report=html

# Run specific test file
uv run pytest tests/test_entities.py
```

### Code Quality

```bash
# Run linter (ruff)
uv run ruff check .

# Run type checker (mypy)
uv run mypy .

# Format code
uv run ruff format .
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run all hooks
uv run pre-commit run --all-files
```

---

## Publishing

### Build Package

```bash
# Build distribution packages
uv build

# Output:
# dist/
#   usipipo_commons-0.12.0-py3-none-any.whl
#   usipipo_commons-0.12.0.tar.gz
```

### Publish to PyPI

```bash
# Publish to PyPI
uv publish

# Or with explicit token
uv publish --token pypi-xxx...
```

### Version Bumping

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, backward compatible

Update version in `pyproject.toml` before publishing.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

### Quick Start

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`uv run pytest`)
5. Run linters (`uv run ruff check . && uv run mypy .`)
6. Commit with conventional commits
7. Push and open a Pull Request

### Code Style

- **Line Length:** 100 characters
- **Quote Style:** Double quotes
- **Indent:** 4 spaces
- **Type Hints:** Required for all public functions
- **Testing:** 80%+ coverage target

---

## Related Projects

| Project | Description | Status |
|---------|-------------|--------|
| [usipipo-backend](https://github.com/uSipipo-Team/usipipo) | FastAPI backend API | 🟢 Active |
| [usipipo-telegram-bot](https://github.com/uSipipo-Team/usipipo) | Telegram bot | 🟡 Refactoring |
| [usipipo-miniapp-web](https://github.com/uSipipo-Team/usipipo-miniapp-web) | Telegram Mini App | 🟡 Pending |
| [usipipo-landing](https://github.com/uSipipo-Team/usipipo-landing) | Marketing site | 🟢 Production |
| [usipipo-vpn-android](https://github.com/uSipipo-Team/usipipo-vpn-android) | Android VPN app | 🟢 Production |

---

## License

MIT © uSipipo Team

See [LICENSE](LICENSE) for details.
