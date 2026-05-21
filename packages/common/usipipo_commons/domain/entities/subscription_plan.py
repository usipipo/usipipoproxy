"""Subscription plan domain entity."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from usipipo_commons.domain.enums.plan_type import PlanType


@dataclass
class SubscriptionPlan:
    """Plan de suscripción activo de un usuario."""

    user_id: UUID
    plan_type: PlanType
    stars_paid: int
    payment_id: str
    starts_at: datetime
    expires_at: datetime
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_expired(self) -> bool:
        """Verifica si la suscripción ha expirado."""
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def days_remaining(self) -> int:
        """Días restantes hasta la expiración."""
        if self.is_expired:
            return 0
        delta = self.expires_at - datetime.now(timezone.utc)
        return delta.days

    @property
    def is_expiring_soon(self) -> bool:
        """Verifica si la suscripción expira pronto (7 días)."""
        return 0 < self.days_remaining <= 7
