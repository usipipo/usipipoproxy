# uSipipo Commons - Project Context

## 📋 Overview

**usipipo-commons** is the shared Python library for the uSipipo VPN ecosystem. It contains domain entities, enums, Pydantic schemas, constants, and utilities used across all services.

**Current Version:** v0.5.6  
**Status:** Published on PyPI  
**Python Version:** 3.13+

---

## 🏗️ Architecture

### Project Structure

```
usipipo_commons/
├── domain/
│   ├── entities/           # Dataclasses del dominio
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── vpn_key.py
│   │   ├── payment.py
│   │   ├── balance.py
│   │   ├── crypto_order.py
│   │   ├── crypto_transaction.py
│   │   ├── webhook_token.py
│   │   ├── admin.py
│   │   ├── consumption_billing.py
│   │   ├── consumption_invoice.py
│   │   ├── data_package.py
│   │   ├── subscription_plan.py
│   │   ├── subscription_transaction.py
│   │   ├── ticket.py
│   │   └── ticket_message.py
│   └── enums/              # Enums del dominio
│       ├── __init__.py
│       ├── vpn_type.py
│       ├── key_type.py
│       ├── key_status.py
│       ├── payment_status.py
│       ├── payment_method.py
│       ├── crypto_order_status.py
│       ├── crypto_transaction_status.py
│       ├── package_type.py
│       ├── plan_type.py
│       ├── ticket_category.py
│       ├── ticket_priority.py
│       ├── ticket_status.py
│       ├── billing_status.py
│       ├── invoice_status.py
│       ├── consumption_payment_method.py
│       └── subscription_transaction_status.py
├── schemas/                # Pydantic models
│   ├── __init__.py
│   ├── create_vpn_key_request.py
│   ├── payment_response.py
│   └── ...
├── constants/              # Constantes compartidas
│   ├── __init__.py
│   ├── plans.py            # FREE_GB, PREMIUM_GB, etc.
│   ├── bonuses.py          # REFERRAL_BONUS_GB
│   ├── error_codes.py      # Error codes
│   └── crypto.py           # Crypto constants
└── utils/                  # Utilitarios
    ├── __init__.py
    ├── validators.py       # validate_telegram_id, etc.
    └── formatters.py       # format_bytes, etc.
```

### Entity Categories

**Core Entities:**
- `User` - User account management
- `VpnKey` - VPN key with usage tracking methods
- `Payment` - Payment transaction tracking
- `Balance` - Account balance with add/subtract/has_sufficient

**Crypto Payment Entities:**
- `CryptoOrder` - Crypto payment orders with state machine
- `CryptoTransaction` - Blockchain transaction tracking
- `WebhookToken` - Secure webhook validation

**Admin Entities:**
- `AdminUserInfo` - Admin user information
- `AdminKeyInfo` - Admin key information
- `ServerStatus` - Server status
- `AdminOperationResult` - Operation result

**Consumption Billing Entities:**
- `ConsumptionBilling` - Billing cycle tracking
- `ConsumptionInvoice` - Invoice generation

**Subscription Entities:**
- `SubscriptionPlan` - Plan definitions
- `SubscriptionTransaction` - Transaction tracking

**Ticket/Support Entities:**
- `Ticket` - Support ticket management
- `TicketMessage` - Message thread

**Data Package Entities:**
- `DataPackage` - Data package definitions

---

## 🚀 Building and Running

### Prerequisites

- Python 3.13+
- uv package manager

### Local Development

```bash
cd packages/common

# Install dependencies
uv sync --dev

# Run tests
uv run pytest

# Run linter
uv run ruff check .

# Run type checker
uv run mypy .
```

### Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=usipipo_commons --cov-report=html

# Specific test file
uv run pytest tests/test_entities.py -v
```

### Building

```bash
# Build package
uv build

# Publish to PyPI
uv publish
```

---

## 📦 Usage Examples

### Importing Entities

```python
from usipipo_commons.domain.entities import (
    User, VpnKey, Payment, Balance,
    SubscriptionPlan, Ticket
)
```

### Importing Enums

```python
from usipipo_commons.domain.enums import (
    VpnType, KeyType, KeyStatus,
    PaymentStatus, PaymentMethod,
    PlanType, BillingStatus
)
```

### Using Constants

```python
from usipipo_commons.constants import (
    FREE_GB,
    PREMIUM_GB,
    REFERRAL_BONUS_GB,
    CRYPTO_CONFIRMATIONS_REQUIRED
)
```

### Using Utilities

```python
from usipipo_commons.utils import (
    validate_telegram_id,
    format_bytes,
    validate_crypto_address
)

# Example
telegram_id = validate_telegram_id(123456789)
formatted = format_bytes(1048576)  # "1.00 MB"
```

### Using Pydantic Schemas

```python
from usipipo_commons.schemas import (
    CreateVpnKeyRequest,
    PaymentResponse,
    UserResponse
)

# Create request
request = CreateVpnKeyRequest(
    user_id=123,
    key_type="WIREGUARD",
    data_limit_gb=10
)
```

---

## 🔧 Development Conventions

### Code Style

- **Line Length:** 100 characters
- **Quote Style:** Double quotes
- **Indent:** 4 spaces
- **Type Hints:** Required for all public functions
- **Dataclasses:** Use `@dataclass` for entities

### Entity Pattern

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from usipipo_commons.domain.enums import VpnType, KeyStatus

@dataclass
class VpnKey:
    id: int
    user_id: int
    key_type: VpnType
    status: KeyStatus
    data_limit_gb: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    def used_mb(self) -> int:
        """Calculate used MB"""
        pass
    
    def remaining_bytes(self) -> int:
        """Calculate remaining bytes"""
        pass
    
    def is_over_limit(self) -> bool:
        """Check if over data limit"""
        pass
    
    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        pass
```

### Testing Practices

- **Framework:** pytest
- **Coverage Target:** 80%+
- **Test Structure:** Arrange-Act-Assert
- **Naming:** `test_<entity>_<method>_<scenario>`

---

## 📊 Entity Summary

### Total Entities: 16

| Category | Count | Entities |
|----------|-------|----------|
| Core | 4 | User, VpnKey, Payment, Balance |
| Crypto | 3 | CryptoOrder, CryptoTransaction, WebhookToken |
| Admin | 4 | AdminUserInfo, AdminKeyInfo, ServerStatus, AdminOperationResult |
| Consumption | 2 | ConsumptionBilling, ConsumptionInvoice |
| Subscription | 2 | SubscriptionPlan, SubscriptionTransaction |
| Support | 2 | Ticket, TicketMessage |
| Data Package | 1 | DataPackage |

### Total Enums: 16

| Category | Count | Enums |
|----------|-------|-------|
| VPN | 3 | VpnType, KeyType, KeyStatus |
| Payment | 2 | PaymentStatus, PaymentMethod |
| Crypto | 2 | CryptoOrderStatus, CryptoTransactionStatus |
| Subscription | 2 | PlanType, SubscriptionTransactionStatus |
| Consumption | 3 | BillingStatus, InvoiceStatus, ConsumptionPaymentMethod |
| Support | 3 | TicketCategory, TicketPriority, TicketStatus |
| Data Package | 1 | PackageType |

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project configuration |
| `CHANGELOG.md` | Version history |
| `usipipo_commons/__init__.py` | Package exports |
| `usipipo_commons/domain/entities/__init__.py` | Entity exports |
| `usipipo_commons/domain/enums/__init__.py` | Enum exports |
| `tests/test_entities.py` | Entity tests |

---

## 🔗 Dependencies

### Runtime

- `pydantic>=2.12.0`

### Development

- `pytest>=8.0.0`
- `pytest-cov>=4.0.0`
- `mypy>=1.0.0`
- `ruff>=0.1.0`

---

## 📚 Documentation

- [GitHub Repository](https://github.com/uSipipo-Team/usipipo)
- [PyPI Package](https://pypi.org/project/usipipo-commons/)
- [Issue Tracker](https://github.com/uSipipo-Team/usipipo/issues)
- [Changelog](CHANGELOG.md)

---

## 🔗 Links

- **GitHub:** https://github.com/uSipipo-Team/usipipo
- **PyPI:** https://pypi.org/project/usipipo-commons/
- **Latest Release:** v0.5.6 (2026-03-21)

---

**Last Updated:** 2026-03-21  
**Maintained By:** uSipipo Team <dev@usipipo.com>
