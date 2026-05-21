"""Data package entity for uSipipo ecosystem."""

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class PackageType(str, Enum):
    """Tipos de paquetes de datos disponibles."""

    BASIC = "basic"
    ESTANDAR = "estandar"
    AVANZADO = "avanzado"
    PREMIUM = "premium"
    UNLIMITED = "unlimited"


@dataclass
class DataPackage:
    """Entidad que representa un paquete de datos comprado."""

    user_id: uuid.UUID
    package_type: PackageType
    data_limit_bytes: int
    stars_paid: int
    expires_at: datetime
    id: Optional[uuid.UUID] = None
    data_used_bytes: int = 0
    purchased_at: Optional[datetime] = None
    is_active: bool = True
    telegram_payment_id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = uuid.uuid4()
        if self.purchased_at is None:
            self.purchased_at = datetime.now(timezone.utc)

    @property
    def remaining_bytes(self) -> int:
        """Calcula los bytes restantes."""
        return max(0, self.data_limit_bytes - self.data_used_bytes)

    @property
    def is_expired(self) -> bool:
        """Verifica si el paquete expiró."""
        now = datetime.now(timezone.utc)
        exp = self.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        else:
            exp = exp.astimezone(timezone.utc)
        return now > exp

    @property
    def is_valid(self) -> bool:
        """Verifica si el paquete es válido."""
        return self.is_active and not self.is_expired

    def add_usage(self, bytes_used: int) -> None:
        """Agrega uso de datos."""
        self.data_used_bytes += bytes_used

    def deactivate(self) -> None:
        """Desactiva el paquete."""
        self.is_active = False
