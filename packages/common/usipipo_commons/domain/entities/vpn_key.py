from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from ..enums.key_status import KeyStatus
from ..enums.key_type import KeyType


@dataclass
class VpnKey:
    """
    Entidad que representa una credencial de acceso a la VPN.

    Guarda la información técnica necesaria para que el usuario se conecte.
    Portada fielmente desde el monorepo.
    """

    id: UUID = field(default_factory=uuid4)  # ← Changed from Optional[str] to UUID
    user_id: UUID = field(default_factory=uuid4)  # UUID del dueño
    server_id: Optional[UUID] = None  # ← UUID del servidor (opcional, para compatibilidad)
    key_type: KeyType = KeyType.OUTLINE
    status: KeyStatus = KeyStatus.ACTIVE  # ← Added status field
    name: str = "Nueva Clave"

    # Datos técnicos
    key_data: str = ""  # Aquí va el "ss://..." o el config de WireGuard
    external_id: str = ""  # El ID que le asigna el servidor (Outline/WG)

    # Estado y fechas
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # ← is_active is now a property based on status

    # Métricas de uso (sincronizadas desde los servidores VPN)
    used_bytes: int = 0  # Tráfico consumido en bytes
    last_seen_at: Optional[datetime] = None  # Última actividad del cliente

    data_limit_bytes: int = 5 * 1024**3  # 5 GB por defecto
    billing_reset_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None  # Fecha de expiración de la clave

    # WireGuard IP allocation (optional)
    ip_address: Optional[str] = None  # IPv4 address string (INET)
    ip_last_octet: Optional[int] = None  # Last octet for quick lookup

    def __post_init__(self):
        """
        Se ejecuta automáticamente después de la inicialización.
        Convierte strings ISO a objetos datetime si la BD los devuelve como texto.
        Normaliza todos los datetimes para que sean aware (con timezone UTC).
        """
        if isinstance(self.created_at, str):
            try:
                self.created_at = datetime.fromisoformat(self.created_at)
            except ValueError:
                self.created_at = datetime.now(timezone.utc)

        # Normalizar created_at a UTC aware
        if self.created_at and self.created_at.tzinfo is None:
            self.created_at = self.created_at.replace(tzinfo=timezone.utc)
        elif self.created_at:
            self.created_at = self.created_at.astimezone(timezone.utc)

        if isinstance(self.last_seen_at, str):
            try:
                self.last_seen_at = datetime.fromisoformat(self.last_seen_at)
            except ValueError:
                self.last_seen_at = None

        # Normalizar last_seen_at a UTC aware si existe
        if self.last_seen_at and self.last_seen_at.tzinfo is None:
            self.last_seen_at = self.last_seen_at.replace(tzinfo=timezone.utc)
        elif self.last_seen_at:
            self.last_seen_at = self.last_seen_at.astimezone(timezone.utc)

        if isinstance(self.billing_reset_at, str):
            try:
                self.billing_reset_at = datetime.fromisoformat(self.billing_reset_at)
            except ValueError:
                self.billing_reset_at = datetime.now(timezone.utc)

        # Normalizar billing_reset_at a UTC aware
        if self.billing_reset_at and self.billing_reset_at.tzinfo is None:
            self.billing_reset_at = self.billing_reset_at.replace(tzinfo=timezone.utc)
        elif self.billing_reset_at:
            self.billing_reset_at = self.billing_reset_at.astimezone(timezone.utc)

        if isinstance(self.expires_at, str):
            try:
                self.expires_at = datetime.fromisoformat(self.expires_at)
            except ValueError:
                self.expires_at = None

        # Normalizar expires_at a UTC aware si existe
        if self.expires_at and self.expires_at.tzinfo is None:
            self.expires_at = self.expires_at.replace(tzinfo=timezone.utc)
        elif self.expires_at:
            self.expires_at = self.expires_at.astimezone(timezone.utc)

    @property
    def is_active(self) -> bool:
        """Backward compatibility property - returns True if status is ACTIVE."""
        return self.status == KeyStatus.ACTIVE

    @property
    def used_mb(self) -> float:
        """Calcula el uso en MB."""
        return self.used_bytes / (1024**2)

    @property
    def used_gb(self) -> float:
        """Calcula el uso en GB."""
        return self.used_bytes / (1024**3)

    @property
    def data_limit_gb(self) -> float:
        """Calcula el límite de datos en GB."""
        return self.data_limit_bytes / (1024**3)

    @property
    def remaining_bytes(self) -> int:
        """Calcula los bytes restantes."""
        return max(0, self.data_limit_bytes - self.used_bytes)

    @property
    def is_over_limit(self) -> bool:
        """Verifica si excedió el límite de datos."""
        return self.used_bytes > self.data_limit_bytes

    def needs_reset(self) -> bool:
        """
        Verifica si pasaron 30 días desde el último reset de billing.
        """
        if not self.billing_reset_at:
            return True

        now = datetime.now(timezone.utc)
        reset_date = self.billing_reset_at

        # Asegurar que ambos sean aware
        if reset_date.tzinfo is None:
            reset_date = reset_date.replace(tzinfo=timezone.utc)

        days_since_reset = (now - reset_date).days
        return days_since_reset >= 30

    def reset_billing_cycle(self) -> None:
        """Resetea el ciclo de facturación."""
        self.used_bytes = 0
        self.billing_reset_at = datetime.now(timezone.utc)

    def set_status(self, status: KeyStatus) -> None:
        """Sets the key status."""
        self.status = status

    def add_usage(self, bytes_used: int) -> None:
        """Agrega uso de datos."""
        self.used_bytes += bytes_used
        self.last_seen_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "server_id": str(self.server_id) if self.server_id else None,
            "name": self.name,
            "key_type": self.key_type.value,
            "status": self.status.value,
            "key_data": self.key_data,
            "external_id": self.external_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_seen_at": self.last_seen_at.isoformat() if self.last_seen_at else None,
            "used_bytes": self.used_bytes,
            "data_limit_bytes": self.data_limit_bytes,
            "billing_reset_at": self.billing_reset_at.isoformat(),
            "ip_address": self.ip_address,
            "ip_last_octet": self.ip_last_octet,
        }
