"""Consumption invoice repository implementation with SQLAlchemy."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session
from usipipo_commons.domain.entities.consumption_invoice import ConsumptionInvoice
from usipipo_commons.domain.enums.invoice_status import InvoiceStatus

from src.core.domain.interfaces.i_consumption_invoice_repository import (
    IConsumptionInvoiceRepository,
)
from src.infrastructure.persistence.models.consumption_invoice_model import (
    ConsumptionInvoiceModel,
)


class ConsumptionInvoiceRepository(IConsumptionInvoiceRepository):
    """SQLAlchemy implementation of consumption invoice repository."""

    def __init__(self, session: Session):
        self.session = session

    def save(
        self, invoice: ConsumptionInvoice, current_user_id: uuid.UUID
    ) -> ConsumptionInvoice:
        """Guarda una nueva factura o actualiza una existente."""
        model = ConsumptionInvoiceModel.from_entity(invoice)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model.to_entity()

    def get_by_id(
        self, invoice_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> ConsumptionInvoice | None:
        """Busca una factura específica por su ID."""
        result = self.session.execute(
            select(ConsumptionInvoiceModel).where(ConsumptionInvoiceModel.id == invoice_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    def get_by_billing(
        self, billing_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> list[ConsumptionInvoice]:
        """Recupera todas las facturas asociadas a un ciclo de facturación."""
        result = self.session.execute(
            select(ConsumptionInvoiceModel)
            .where(ConsumptionInvoiceModel.billing_id == billing_id)
            .order_by(ConsumptionInvoiceModel.created_at.desc())
        )
        models = result.scalars().all()
        return [m.to_entity() for m in models]

    def get_by_user(
        self, user_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> list[ConsumptionInvoice]:
        """Recupera todas las facturas de un usuario by user_id (UUID)."""
        result = self.session.execute(
            select(ConsumptionInvoiceModel)
            .where(ConsumptionInvoiceModel.user_id == user_id)
            .order_by(ConsumptionInvoiceModel.created_at.desc())
        )
        models = result.scalars().all()
        return [m.to_entity() for m in models]

    def get_pending_by_user(
        self, user_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> ConsumptionInvoice | None:
        """
        Recupera la factura pendiente de un usuario.
        Solo puede haber una factura pendiente activa por usuario.
        """
        result = self.session.execute(
            select(ConsumptionInvoiceModel).where(
                ConsumptionInvoiceModel.user_id == user_id,
                ConsumptionInvoiceModel.status == InvoiceStatus.PENDING.value,
            )
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    def get_by_status(
        self, status: InvoiceStatus, current_user_id: uuid.UUID
    ) -> list[ConsumptionInvoice]:
        """Recupera todas las facturas con un estado específico."""
        result = self.session.execute(
            select(ConsumptionInvoiceModel)
            .where(ConsumptionInvoiceModel.status == status.value)
            .order_by(ConsumptionInvoiceModel.created_at.desc())
        )
        models = result.scalars().all()
        return [m.to_entity() for m in models]

    def get_expired_pending(self, current_user_id: uuid.UUID) -> list[ConsumptionInvoice]:
        """
        Recupera facturas pendientes que han expirado.
        Útil para limpieza periódica.
        """
        now = datetime.now(UTC)
        result = self.session.execute(
            select(ConsumptionInvoiceModel).where(
                ConsumptionInvoiceModel.status == InvoiceStatus.PENDING.value,
                ConsumptionInvoiceModel.expires_at < now,
            )
        )
        models = result.scalars().all()
        return [m.to_entity() for m in models]

    def mark_as_paid(
        self, invoice_id: uuid.UUID, transaction_hash: str, current_user_id: uuid.UUID
    ) -> bool:
        """Marca una factura como pagada."""
        model = self.session.get(ConsumptionInvoiceModel, invoice_id)
        if not model:
            return False

        if model.status != InvoiceStatus.PENDING.value:
            return False

        model.status = InvoiceStatus.PAID.value
        model.transaction_hash = transaction_hash
        model.paid_at = datetime.now(UTC)

        self.session.commit()
        return True

    def mark_as_expired(self, invoice_id: uuid.UUID, current_user_id: uuid.UUID) -> bool:
        """Marca una factura como expirada."""
        model = self.session.get(ConsumptionInvoiceModel, invoice_id)
        if not model:
            return False

        if model.status == InvoiceStatus.PAID.value:
            return False

        model.status = InvoiceStatus.EXPIRED.value
        self.session.commit()
        return True

    def update_status(
        self, invoice_id: uuid.UUID, status: InvoiceStatus, current_user_id: uuid.UUID
    ) -> bool:
        """Actualiza el estado de una factura."""
        model = self.session.get(ConsumptionInvoiceModel, invoice_id)
        if not model:
            return False

        model.status = status.value
        self.session.commit()
        return True

    def delete(self, invoice_id: uuid.UUID, current_user_id: uuid.UUID) -> bool:
        """Elimina una factura de la base de datos."""
        model = self.session.get(ConsumptionInvoiceModel, invoice_id)
        if not model:
            return False

        self.session.delete(model)
        self.session.commit()
        return True
