"""Payment repository implementation with SQLAlchemy."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from usipipo_commons.domain.entities.payment import Payment

from src.core.domain.interfaces.i_payment_repository import IPaymentRepository
from src.infrastructure.persistence.models.payment_model import PaymentModel


class PaymentRepository(IPaymentRepository):
    """SQLAlchemy implementation of payment repository."""

    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Payment]:
        """Gets all payments."""
        result = self.session.execute(select(PaymentModel))
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    def get_by_id(self, payment_id: UUID) -> Payment | None:
        """Gets payment by ID."""
        result = self.session.execute(
            select(PaymentModel).where(PaymentModel.id == payment_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    def get_by_user_id(self, user_id: UUID) -> list[Payment]:
        """Gets all payments for a user."""
        result = self.session.execute(
            select(PaymentModel)
            .where(PaymentModel.user_id == user_id)
            .order_by(PaymentModel.created_at.desc())
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    def create(self, payment: Payment) -> Payment:
        """Creates a new payment."""
        model = PaymentModel.from_entity(payment)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model.to_entity()

    def update(self, payment: Payment) -> Payment:
        """Updates an existing payment."""
        model = PaymentModel.from_entity(payment)
        self.session.merge(model)
        self.session.commit()
        self.session.refresh(model)
        return model.to_entity()

    def delete(self, payment_id: UUID) -> bool:
        """Deletes a payment."""
        result = self.session.execute(
            select(PaymentModel).where(PaymentModel.id == payment_id)
        )
        model = result.scalar_one_or_none()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False
