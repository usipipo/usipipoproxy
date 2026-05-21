"""Interfaces de repositorio para la capa de dominio."""

import uuid
from abc import ABC, abstractmethod

from usipipo_commons.domain.entities.consumption_billing import (
    BillingStatus,
    ConsumptionBilling,
)


class IConsumptionBillingRepository(ABC):
    """
    Contrato para la persistencia de ciclos de facturación por consumo.
    Define cómo interactuamos con la tabla de billing en la BD.
    """

    @abstractmethod
    def save(
        self, billing: ConsumptionBilling, current_user_id: uuid.UUID
    ) -> ConsumptionBilling:
        """Guarda un nuevo ciclo de facturación o actualiza uno existente."""
        pass

    @abstractmethod
    def get_by_id(
        self, billing_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> ConsumptionBilling | None:
        """Busca un ciclo de facturación específico por su ID."""
        pass

    @abstractmethod
    def get_by_user(
        self, user_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> list[ConsumptionBilling]:
        """Recupera todos los ciclos de facturación de un usuario."""
        pass

    @abstractmethod
    def get_active_by_user(
        self, user_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> ConsumptionBilling | None:
        """
        Recupera el ciclo de facturación activo de un usuario.
        Solo puede haber uno activo por usuario.
        """
        pass

    @abstractmethod
    def get_by_status(
        self, status: BillingStatus, current_user_id: uuid.UUID
    ) -> list[ConsumptionBilling]:
        """Recupera todos los ciclos con un estado específico."""
        pass

    @abstractmethod
    def get_expired_active_cycles(
        self, days: int, current_user_id: uuid.UUID
    ) -> list[ConsumptionBilling]:
        """
        Recupera ciclos activos que han excedido el límite de días.
        Útil para el cron job de cierre automático.
        """
        pass

    @abstractmethod
    def update_status(
        self, billing_id: uuid.UUID, status: BillingStatus, current_user_id: uuid.UUID
    ) -> bool:
        """Actualiza el estado de un ciclo de facturación."""
        pass

    @abstractmethod
    def add_consumption(
        self, billing_id: uuid.UUID, mb_used: float, current_user_id: uuid.UUID
    ) -> bool:
        """Agrega consumo a un ciclo activo."""
        pass

    @abstractmethod
    def delete(self, billing_id: uuid.UUID, current_user_id: uuid.UUID) -> bool:
        """Elimina un ciclo de facturación de la base de datos."""
        pass
