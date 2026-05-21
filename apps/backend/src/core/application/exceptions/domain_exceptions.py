"""Excepciones del dominio de la aplicación."""


class DomainException(Exception):
    """Clase base para excepciones del dominio."""

    pass


class UserNotFoundError(DomainException):
    """Excepción cuando no se encuentra un usuario."""

    def __init__(self, message: str = "User not found"):
        self.message = message
        super().__init__(self.message)


class VpnKeyNotFoundError(DomainException):
    """Excepción cuando no se encuentra una clave VPN."""

    def __init__(self, message: str = "VPN key not found"):
        self.message = message
        super().__init__(self.message)


class VpnKeyLimitReachedError(DomainException):
    """Excepción cuando el usuario alcanzó el límite de claves VPN."""

    def __init__(self, message: str = "VPN key limit reached"):
        self.message = message
        super().__init__(self.message)


class InvalidVpnTypeError(DomainException):
    """Excepción cuando se proporciona un tipo de VPN inválido."""

    def __init__(self, message: str = "Invalid VPN type"):
        self.message = message
        super().__init__(self.message)


class NoAvailableServersError(DomainException):
    """Excepción cuando no hay servidores VPN disponibles para el país/protocolo solicitado."""

    def __init__(self, message: str = "No available servers"):
        self.message = message
        super().__init__(self.message)


class PaymentNotFoundError(DomainException):
    """Excepción cuando no se encuentra un pago."""

    def __init__(self, message: str = "Payment not found"):
        self.message = message
        super().__init__(self.message)


class InsufficientBalanceError(DomainException):
    """Excepción cuando el usuario tiene saldo insuficiente."""

    def __init__(self, message: str = "Insufficient balance"):
        self.message = message
        super().__init__(self.message)


class PaymentExpiredError(DomainException):
    """Excepción cuando un pago ha expirado."""

    def __init__(self, message: str = "Payment expired"):
        self.message = message
        super().__init__(self.message)


class PaymentAlreadyCompletedError(DomainException):
    """Excepción cuando un pago ya está completado."""

    def __init__(self, message: str = "Payment already completed"):
        self.message = message
        super().__init__(self.message)


class SubscriptionAlreadyActiveError(DomainException):
    """Excepción cuando un usuario ya tiene una suscripción activa."""

    def __init__(self, message: str = "Subscription already active"):
        self.message = message
        super().__init__(self.message)


class InvalidPlanTypeError(DomainException):
    """Excepción cuando se proporciona un tipo de plan inválido."""

    def __init__(self, message: str = "Invalid plan type"):
        self.message = message
        super().__init__(self.message)


class SubscriptionNotFoundError(DomainException):
    """Excepción cuando no se encuentra una suscripción."""

    def __init__(self, message: str = "Subscription not found"):
        self.message = message
        super().__init__(self.message)


class AgentOfflineError(DomainException):
    """Excepción cuando el agente VPN está offline o no responde."""

    def __init__(self, message: str = "VPN agent is offline"):
        self.message = message
        super().__init__(self.message)


class VpnKeyRollbackError(DomainException):
    """Excepción cuando falla el rollback de una clave VPN.

    Attributes:
        operation: "create" or "delete"
        key_name: Name of the key (for create operations)
        key_id: ID of the key (for delete operations)
        external_id: External ID on the VPN provider
        server_name: Name of the server
        cleanup_status: "failed", "partial", or "success"
        original_error: The original exception that triggered rollback
        cleanup_error: The exception during cleanup (if any)
    """

    def __init__(
        self,
        operation: str,
        external_id: str = "",
        server_name: str = "",
        cleanup_status: str = "failed",
        key_name: str | None = None,
        key_id: str | None = None,
        original_error: Exception | None = None,
        cleanup_error: Exception | None = None,
    ):
        self.operation = operation
        self.key_name = key_name
        self.key_id = key_id
        self.external_id = external_id
        self.server_name = server_name
        self.cleanup_status = cleanup_status
        self.original_error = original_error
        self.cleanup_error = cleanup_error

        # Build descriptive message
        if operation == "create":
            self.message = (
                f"Rollback failed during VPN key creation for '{key_name}' "
                f"on server '{server_name}' (external_id: {external_id}). "
            )
        elif operation == "delete":
            self.message = (
                f"Rollback failed during VPN key deletion for key {key_id} "
                f"on server '{server_name}' (external_id: {external_id}). "
            )
        else:
            self.message = f"Rollback failed during {operation} operation. "

        if cleanup_status == "failed":
            self.message += "CLEANUP FAILED: Manual intervention required."
        elif cleanup_status == "partial":
            self.message += "CLEANUP PARTIAL: Manual intervention may be required."

        if original_error:
            self.message += f" Original error: {original_error}"
        if cleanup_error:
            self.message += f" Cleanup error: {cleanup_error}"

        super().__init__(self.message)
