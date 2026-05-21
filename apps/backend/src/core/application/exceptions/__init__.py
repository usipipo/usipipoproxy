"""Excepciones del dominio."""

from .domain_exceptions import (
    AgentOfflineError,
    DomainException,
    InsufficientBalanceError,
    InvalidPlanTypeError,
    InvalidVpnTypeError,
    NoAvailableServersError,
    PaymentAlreadyCompletedError,
    PaymentExpiredError,
    PaymentNotFoundError,
    SubscriptionAlreadyActiveError,
    SubscriptionNotFoundError,
    UserNotFoundError,
    VpnKeyLimitReachedError,
    VpnKeyNotFoundError,
    VpnKeyRollbackError,
)

__all__ = [
    "DomainException",
    "UserNotFoundError",
    "VpnKeyNotFoundError",
    "VpnKeyLimitReachedError",
    "InvalidVpnTypeError",
    "NoAvailableServersError",
    "PaymentNotFoundError",
    "PaymentExpiredError",
    "PaymentAlreadyCompletedError",
    "InsufficientBalanceError",
    "InvalidPlanTypeError",
    "SubscriptionAlreadyActiveError",
    "SubscriptionNotFoundError",
    "AgentOfflineError",
    "VpnKeyRollbackError",
]
