"""Consumption billing repository implementation with SQLAlchemy."""

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session
from usipipo_commons.domain.entities.consumption_billing import (
    BillingStatus,
    ConsumptionBilling,
)

from src.core.domain.interfaces.i_consumption_billing_repository import (
    IConsumptionBillingRepository,
)
from src.infrastructure.persistence.models.consumption_billing_model import (
    ConsumptionBillingModel,
)


class ConsumptionBillingRepository(IConsumptionBillingRepository):
    """SQLAlchemy implementation of consumption billing repository."""

    def __init__(self, session: Session):
        self.session = session

    def save(
        self, billing: ConsumptionBilling, current_user_id: uuid.UUID
    ) -> ConsumptionBilling:
        """Guarda un nuevo ciclo de facturación o actualiza uno existente."""
        model = ConsumptionBillingModel.from_entity(billing)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model.to_entity()

    def get_by_id(
        self, billing_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> ConsumptionBilling | None:
        """Busca un ciclo de facturación específico por su ID."""
        result = self.session.execute(
            select(ConsumptionBillingModel).where(ConsumptionBillingModel.id == billing_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    def get_by_user(
        self, user_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> list[ConsumptionBilling]:
        """Recupera todos los ciclos de facturación de un usuario."""
        result = self.session.execute(
            select(ConsumptionBillingModel)
            .where(ConsumptionBillingModel.user_id == user_id)
            .order_by(ConsumptionBillingModel.started_at.desc())
        )
        models = result.scalars().all()
        return [m.to_entity() for m in models]

    def get_active_by_user(
        self, user_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> ConsumptionBilling | None:
        """
        Recupera el ciclo de facturación activo de un usuario.
        Solo puede haber uno activo por usuario.
        """
        result = self.session.execute(
            select(ConsumptionBillingModel).where(
                ConsumptionBillingModel.user_id == user_id,
                ConsumptionBillingModel.status == BillingStatus.ACTIVE.value,
            )
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    def get_by_status(
        self, status: BillingStatus, current_user_id: uuid.UUID
    ) -> list[ConsumptionBilling]:
        """Recupera todos los ciclos con un estado específico."""
        result = self.session.execute(
            select(ConsumptionBillingModel)
            .where(ConsumptionBillingModel.status == status.value)
            .order_by(ConsumptionBillingModel.started_at.desc())
        )
        models = result.scalars().all()
        return [m.to_entity() for m in models]

    def get_expired_active_cycles(
        self, days: int, current_user_id: uuid.UUID
    ) -> list[ConsumptionBilling]:
        """
        Recupera ciclos activos que han excedido el límite de días.
        Útil para el cron job de cierre automático.
        """
        cutoff_date = datetime.now(UTC) - timedelta(days=days)
        result = self.session.execute(
            select(ConsumptionBillingModel).where(
                ConsumptionBillingModel.status == BillingStatus.ACTIVE.value,
                ConsumptionBillingModel.started_at < cutoff_date,
            )
        )
        models = result.scalars().all()
        return [m.to_entity() for m in models]

    def update_status(
        self, billing_id: uuid.UUID, status: BillingStatus, current_user_id: uuid.UUID
    ) -> bool:
        """Actualiza el estado de un ciclo de facturación."""
        model = self.session.get(ConsumptionBillingModel, billing_id)
        if not model:
            return False

        model.status = status.value
        self.session.commit()
        return True

    def add_consumption(
        self, billing_id: uuid.UUID, mb_used: float, current_user_id: uuid.UUID
    ) -> bool:
        """Agrega consumo a un ciclo activo."""
        model = self.session.get(ConsumptionBillingModel, billing_id)
        if not model:
            return False

        if model.status != BillingStatus.ACTIVE.value:
            return False

        model.mb_consumed += Decimal(str(mb_used))
        self.session.commit()
        return True

    def delete(self, billing_id: uuid.UUID, current_user_id: uuid.UUID) -> bool:
        """Elimina un ciclo de facturación de la base de datos."""
        model = self.session.get(ConsumptionBillingModel, billing_id)
        if not model:
            return False

        self.session.delete(model)
        self.session.commit()
        return True
