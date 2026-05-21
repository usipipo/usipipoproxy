import uuid
from typing import Protocol

from usipipo_commons.domain.entities.consumption_invoice import ConsumptionInvoice
from usipipo_commons.domain.enums.invoice_status import InvoiceStatus


class IConsumptionInvoiceRepository(Protocol):
    """
    Contrato para la persistencia de facturas de consumo.
    Define cómo interactuamos con la tabla de invoices en la BD.
    """

    def save(
        self, invoice: ConsumptionInvoice, current_user_id: uuid.UUID
    ) -> ConsumptionInvoice:
        """Guarda una nueva factura o actualiza una existente."""
        ...

    def get_by_id(
        self, invoice_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> ConsumptionInvoice | None:
        """Busca una factura específica por su ID."""
        ...

    def get_by_billing(
        self, billing_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> list[ConsumptionInvoice]:
        """Recupera todas las facturas asociadas a un ciclo de facturación."""
        ...

    def get_by_user(
        self, user_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> list[ConsumptionInvoice]:
        """Recupera todas las facturas de un usuario by user_id (UUID)."""
        ...

    def get_pending_by_user(
        self, user_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> ConsumptionInvoice | None:
        """
        Recupera la factura pendiente de un usuario.
        Solo puede haber una factura pendiente activa por usuario.
        """
        ...

    def get_by_status(
        self, status: InvoiceStatus, current_user_id: uuid.UUID
    ) -> list[ConsumptionInvoice]:
        """Recupera todas las facturas con un estado específico."""
        ...

    def get_expired_pending(self, current_user_id: uuid.UUID) -> list[ConsumptionInvoice]:
        """
        Recupera facturas pendientes que han expirado.
        Útil para limpieza periódica.
        """
        ...

    def mark_as_paid(
        self, invoice_id: uuid.UUID, transaction_hash: str, current_user_id: uuid.UUID
    ) -> bool:
        """Marca una factura como pagada."""
        ...

    def mark_as_expired(self, invoice_id: uuid.UUID, current_user_id: uuid.UUID) -> bool:
        """Marca una factura como expirada."""
        ...

    def update_status(
        self, invoice_id: uuid.UUID, status: InvoiceStatus, current_user_id: uuid.UUID
    ) -> bool:
        """Actualiza el estado de una factura."""
        ...

    def delete(self, invoice_id: uuid.UUID, current_user_id: uuid.UUID) -> bool:
        """Elimina una factura de la base de datos."""
        ...
