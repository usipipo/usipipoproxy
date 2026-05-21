"""uSipipo Commons - Shared library for uSipipo ecosystem."""

from usipipo_commons.domain.entities import (
    User,
    VpnKey,
    Payment,
    ConsumptionBilling,
    ConsumptionInvoice,
    CryptoOrder,
    SubscriptionPlan,
    Wallet,
    WalletPool,
)
from usipipo_commons.domain.enums import (
    KeyType,
    KeyStatus,
    PaymentStatus,
    PaymentMethod,
    BillingStatus,
    InvoiceStatus,
    ConsumptionPaymentMethod,
    CryptoOrderStatus,
    PlanType,
    WalletStatus,
)
from usipipo_commons.domain.interfaces import (
    IWalletRepository,
    IWalletPoolRepository,
)
from usipipo_commons.schemas import (
    UserResponse,
    UserCreateRequest,
    UserUpdateRequest,
    VpnKeyResponse,
    CreateVpnKeyRequest,
    UpdateVpnKeyRequest,
    PaymentResponse,
    CreatePaymentRequest,
)
from usipipo_commons.constants import (
    FREE_GB,
    FREE_KEYS_LIMIT,
    WELCOME_BONUS_GB,
    LOYALTY_BONUS_GB,
    REFERRAL_BONUS_GB,
    MAX_KEYS_PER_USER,
    MIN_PACKAGE_GB,
    MAX_PACKAGE_GB,
    PRICE_PER_GB,
    BILLING_CYCLE_DAYS,
)
from usipipo_commons.utils import (
    validate_telegram_id,
    validate_referral_code,
    validate_vpn_key_name,
    format_bytes,
    format_datetime,
    format_duration,
)

__version__ = "0.9.0"
__all__ = [
    # Entities
    "User",
    "VpnKey",
    "Payment",
    "ConsumptionBilling",
    "ConsumptionInvoice",
    "CryptoOrder",
    "SubscriptionPlan",
    "Wallet",
    "WalletPool",
    # Enums
    "KeyType",
    "KeyStatus",
    "PaymentStatus",
    "PaymentMethod",
    "BillingStatus",
    "InvoiceStatus",
    "ConsumptionPaymentMethod",
    "CryptoOrderStatus",
    "PlanType",
    "WalletStatus",
    # Interfaces
    "IWalletRepository",
    "IWalletPoolRepository",
    # Schemas
    "UserResponse",
    "UserCreateRequest",
    "UserUpdateRequest",
    "VpnKeyResponse",
    "CreateVpnKeyRequest",
    "UpdateVpnKeyRequest",
    "PaymentResponse",
    "CreatePaymentRequest",
    # Constants
    "FREE_GB",
    "FREE_KEYS_LIMIT",
    "WELCOME_BONUS_GB",
    "LOYALTY_BONUS_GB",
    "REFERRAL_BONUS_GB",
    "MAX_KEYS_PER_USER",
    "MIN_PACKAGE_GB",
    "MAX_PACKAGE_GB",
    "PRICE_PER_GB",
    "BILLING_CYCLE_DAYS",
    # Utils
    "validate_telegram_id",
    "validate_referral_code",
    "validate_vpn_key_name",
    "format_bytes",
    "format_datetime",
    "format_duration",
]
