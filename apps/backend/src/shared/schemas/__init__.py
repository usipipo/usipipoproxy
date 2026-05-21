"""Schemas compartidos."""

from .admin import (
    AdminKeyInfoResponse,
    AdminKeyListResponse,
    AdminOperationResultResponse,
    AdminUserInfoResponse,
    AdminUserListResponse,
    AssignRoleRequest,
    DashboardStatsResponse,
    DeleteKeyResponse,
    ServerStatsResponse,
    ServerStatusListResponse,
    ServerStatusResponse,
    ToggleKeyStatusRequest,
    UpdateUserStatusRequest,
)
from .admin_vpn_keys import (
    AdminOperationResult,
    CreateVpnKeyAdminRequest,
    RegenerateConfigRequest,
    ResetUsageRequest,
    UpdateDataLimitRequest,
    VpnKeyDetailResponse,
    VpnKeyListItemResponse,
    VpnKeyListResponse,
)
from .auth import (
    AuthResponse,
    CodeSentResponse,
    EmailLoginRequest,
    EmailRegisterRequest,
    TelegramCodeRequest,
    TelegramVerifyRequest,
)
from .billing import KeyUsageResponse, UsageResponse
from .consumption_invoice import (
    ConsumptionInvoiceCreateRequest,
    ConsumptionInvoiceListResponse,
    ConsumptionInvoicePaymentRequest,
    ConsumptionInvoiceResponse,
    ConsumptionInvoiceStatusUpdateRequest,
)
from .vpn import CreateVpnKeyRequest, UpdateVpnKeyRequest, VpnKeyResponse
from .wallet import (
    WalletCreateRequest,
    WalletDepositRequest,
    WalletPoolResponse,
    WalletPoolStats,
    WalletResponse,
    WalletUpdateRequest,
    WalletWithdrawRequest,
)

__all__ = [
    # Auth schemas
    "AuthResponse",
    "CodeSentResponse",
    "EmailLoginRequest",
    "EmailRegisterRequest",
    "TelegramCodeRequest",
    "TelegramVerifyRequest",
    # VPN schemas
    "VpnKeyResponse",
    "CreateVpnKeyRequest",
    "UpdateVpnKeyRequest",
    # Admin VPN keys schemas
    "VpnKeyListItemResponse",
    "VpnKeyDetailResponse",
    "VpnKeyListResponse",
    "CreateVpnKeyAdminRequest",
    "UpdateDataLimitRequest",
    "ResetUsageRequest",
    "RegenerateConfigRequest",
    "AdminOperationResult",
    # Billing schemas
    "UsageResponse",
    "KeyUsageResponse",
    # Consumption schemas
    "ConsumptionInvoiceResponse",
    "ConsumptionInvoiceCreateRequest",
    "ConsumptionInvoicePaymentRequest",
    "ConsumptionInvoiceStatusUpdateRequest",
    "ConsumptionInvoiceListResponse",
    # Wallet schemas
    "WalletResponse",
    "WalletCreateRequest",
    "WalletUpdateRequest",
    "WalletDepositRequest",
    "WalletWithdrawRequest",
    "WalletPoolResponse",
    "WalletPoolStats",
    # Admin schemas
    "AdminUserInfoResponse",
    "AdminUserListResponse",
    "AdminKeyInfoResponse",
    "AdminKeyListResponse",
    "ServerStatusResponse",
    "ServerStatusListResponse",
    "ServerStatsResponse",
    "DashboardStatsResponse",
    "AdminOperationResultResponse",
    "UpdateUserStatusRequest",
    "AssignRoleRequest",
    "ToggleKeyStatusRequest",
    "DeleteKeyResponse",
]
