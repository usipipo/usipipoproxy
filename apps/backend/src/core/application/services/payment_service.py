"""Payment service for managing payments."""

from datetime import UTC, datetime
from uuid import UUID

from usipipo_commons.domain.entities.payment import Payment
from usipipo_commons.domain.enums.payment_method import PaymentMethod
from usipipo_commons.domain.enums.payment_status import PaymentStatus

from src.core.application.exceptions import (
    PaymentAlreadyCompletedError,
    PaymentExpiredError,
    PaymentNotFoundError,
    UserNotFoundError,
)
from src.core.domain.interfaces.i_payment_repository import IPaymentRepository
from src.core.domain.interfaces.i_user_repository import IUserRepository


class PaymentService:
    """Application service for payment management."""

    def __init__(
        self,
        payment_repo: IPaymentRepository,
        user_repo: IUserRepository,
    ):
        self.payment_repo = payment_repo
        self.user_repo = user_repo

    def create_payment(
        self,
        user_id: UUID,
        amount_usd: float,
        gb_purchased: float,
        method: str,
        crypto_address: str | None = None,
        crypto_network: str | None = None,
        telegram_star_invoice_id: str | None = None,
        expires_at: datetime | None = None,
    ) -> Payment:
        """Creates a new payment."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        payment = Payment.create(
            user_id=user_id,
            amount_usd=amount_usd,
            gb_purchased=gb_purchased,
            method=method if isinstance(method, PaymentMethod) else PaymentMethod(method),
            crypto_address=crypto_address,
            crypto_network=crypto_network,
            telegram_star_invoice_id=telegram_star_invoice_id,
            expires_at=expires_at,
        )

        return self.payment_repo.create(payment)

    def complete_payment(
        self,
        payment_id: UUID,
        transaction_hash: str | None = None,
    ) -> Payment:
        """Completes a payment."""
        payment = self.payment_repo.get_by_id(payment_id)
        if not payment:
            raise PaymentNotFoundError(f"Payment {payment_id} not found")

        if payment.status == PaymentStatus.COMPLETED:
            raise PaymentAlreadyCompletedError(f"Payment {payment_id} already completed")

        if payment.status == PaymentStatus.EXPIRED:
            raise PaymentExpiredError(f"Payment {payment_id} expired")

        payment.status = PaymentStatus.COMPLETED
        payment.paid_at = datetime.now(UTC)
        payment.transaction_hash = transaction_hash

        updated_payment = self.payment_repo.update(payment)

        user = self.user_repo.get_by_id(payment.user_id)
        if user:
            user.balance_gb += payment.gb_purchased
            user.total_purchased_gb += payment.gb_purchased
            self.user_repo.update(user)

        return updated_payment

    def get_payment_by_id(self, payment_id: UUID) -> Payment | None:
        """Gets payment by ID."""
        return self.payment_repo.get_by_id(payment_id)

    def get_user_payments(self, user_id: UUID) -> list[Payment]:
        """Gets all payments for a user."""
        return self.payment_repo.get_by_user_id(user_id)

    def expire_payment(self, payment_id: UUID) -> Payment:
        """Expires a payment."""
        payment = self.payment_repo.get_by_id(payment_id)
        if not payment:
            raise PaymentNotFoundError(f"Payment {payment_id} not found")

        payment.status = PaymentStatus.EXPIRED
        return self.payment_repo.update(payment)
