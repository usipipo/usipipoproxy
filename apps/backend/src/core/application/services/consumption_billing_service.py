"""
Servicio de facturación por consumo (Facade).

Este servicio ha sido refactorizado. Las implementaciones se han
movido a submódulos especializados para mantener archivos bajo 300 líneas:
- consumption_billing_dtos.py: DTOs (ConsumptionSummary, ActivationResult, etc.)
- consumption_billing_activation.py: Activación y cancelación del modo consumo
- consumption_billing_cycle.py: Gestión de ciclos (cierre, pago, registro, consultas)

Este archivo mantiene la interfaz pública para compatibilidad hacia atrás.

Author: uSipipo Team
Version: 2.0.0 - Refactored into sub-services
"""

import uuid
from decimal import Decimal

from usipipo_commons.domain.entities.consumption_billing import ConsumptionBilling

from src.core.domain.interfaces.i_consumption_billing_repository import (
    IConsumptionBillingRepository,
)
from src.core.domain.interfaces.i_consumption_invoice_repository import (
    IConsumptionInvoiceRepository,
)
from src.core.domain.interfaces.i_user_repository import IUserRepository
from src.shared.config import settings

from .consumption_billing_activation import ConsumptionActivationService
from .consumption_billing_cycle import ConsumptionCycleService
from .consumption_billing_dtos import ActivationResult, CancellationResult, ConsumptionSummary
from .subscription_service import SubscriptionService


class ConsumptionBillingService:
    """
    Servicio de aplicación para gestionar ciclos de facturación por consumo (Facade).

    Delega operaciones a servicios especializados para mantener
    SRP (Single Responsibility Principle):
    - ConsumptionActivationService: activar/cancelar modo consumo
    - ConsumptionCycleService: ciclos, registro de uso, consultas
    """

    def __init__(
        self,
        billing_repo: IConsumptionBillingRepository,
        user_repo: IUserRepository,
        subscription_service: SubscriptionService | None = None,
        invoice_repo: IConsumptionInvoiceRepository | None = None,
    ):
        self.billing_repo = billing_repo
        self.user_repo = user_repo
        self.subscription_service = subscription_service
        self.invoice_repo = invoice_repo
        self.price_per_mb = Decimal(str(settings.CONSUMPTION_PRICE_PER_MB_USD))
        self.cycle_days = settings.CONSUMPTION_CYCLE_DAYS

        self._activation = ConsumptionActivationService(billing_repo, user_repo, self.price_per_mb)
        self._cycle = ConsumptionCycleService(
            billing_repo, user_repo, self.cycle_days, invoice_repo
        )

    # ============================================
    # DELEGACIÓN A ConsumptionActivationService
    # ============================================

    def can_activate_consumption(
        self, user_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> tuple[bool, str | None]:
        """Verifica si un usuario puede activar el modo consumo."""
        return self._activation.can_activate_consumption(user_id, current_user_id)

    def activate_consumption_mode(
        self, user_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> ActivationResult:
        """Activa el modo consumo para un usuario."""
        return self._activation.activate_consumption_mode(user_id, current_user_id)

    def can_cancel_consumption(
        self, user_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> tuple[bool, str | None]:
        """Verifica si un usuario puede cancelar el modo consumo."""
        return self._activation.can_cancel_consumption(user_id, current_user_id)

    def cancel_consumption_mode(
        self, user_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> CancellationResult:
        """Cancela el modo consumo para un usuario."""
        return self._activation.cancel_consumption_mode(user_id, current_user_id)

    # ============================================
    # DELEGACIÓN A ConsumptionCycleService
    # ============================================

    def is_premium_user(self, user_id: uuid.UUID, current_user_id: uuid.UUID) -> bool:
        """Check if user has an active subscription (unlimited data)."""
        if not self.subscription_service:
            return False
        return self.subscription_service.is_premium_user(user_id, current_user_id)

    def record_data_usage(
        self, user_id: uuid.UUID, mb_used: float, current_user_id: uuid.UUID
    ) -> bool:
        """Registra consumo de datos para un usuario."""
        return self._cycle.record_data_usage(user_id, mb_used, current_user_id)

    def get_current_consumption(
        self, user_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> ConsumptionSummary | None:
        """Obtiene el resumen de consumo actual de un usuario."""
        return self._cycle.get_current_consumption(user_id, current_user_id)

    def close_billing_cycle(self, billing_id: uuid.UUID, current_user_id: uuid.UUID) -> bool:
        """Cierra un ciclo de facturación."""
        return self._cycle.close_billing_cycle(billing_id, current_user_id)

    def mark_cycle_as_paid(self, billing_id: uuid.UUID, current_user_id: uuid.UUID) -> bool:
        """Marca un ciclo como pagado."""
        return self._cycle.mark_cycle_as_paid(billing_id, current_user_id)

    def get_billing_history(
        self, user_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> list[ConsumptionSummary]:
        """Obtiene el historial de facturación de un usuario."""
        return self._cycle.get_billing_history(user_id, current_user_id)

    def get_expired_active_cycles(
        self, current_user_id: uuid.UUID
    ) -> list[ConsumptionBilling]:
        """Obtiene ciclos activos que han excedido el período de ciclo."""
        return self._cycle.get_expired_active_cycles(current_user_id)
