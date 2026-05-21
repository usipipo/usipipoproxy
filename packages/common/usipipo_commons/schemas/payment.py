from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from uuid import UUID

from ..domain.enums.payment_status import PaymentStatus
from ..domain.enums.payment_method import PaymentMethod


class PaymentResponse(BaseModel):
    """Respuesta de pago."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    amount_usd: float
    gb_purchased: float
    method: PaymentMethod
    status: PaymentStatus
    crypto_address: Optional[str] = None
    crypto_network: Optional[str] = None
    telegram_star_invoice_id: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    transaction_hash: Optional[str] = None


class CreatePaymentRequest(BaseModel):
    """Solicitud para crear pago."""
    amount_usd: float = Field(..., gt=0)
    method: PaymentMethod
    gb_purchased: float = Field(..., gt=0)
