"""Interface for payment repository."""

from abc import ABC, abstractmethod
from uuid import UUID

from usipipo_commons.domain.entities.payment import Payment


class IPaymentRepository(ABC):
    """Contract for payment repository."""

    @abstractmethod
    def get_all(self) -> list[Payment]:
        """Gets all payments."""
        pass

    @abstractmethod
    def get_by_id(self, payment_id: UUID) -> Payment | None:
        """Gets payment by ID."""
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> list[Payment]:
        """Gets all payments for a user."""
        pass

    @abstractmethod
    def create(self, payment: Payment) -> Payment:
        """Creates a new payment."""
        pass

    @abstractmethod
    def update(self, payment: Payment) -> Payment:
        """Updates an existing payment."""
        pass

    @abstractmethod
    def delete(self, payment_id: UUID) -> bool:
        """Deletes a payment."""
        pass
