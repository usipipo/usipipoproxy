"""Interfaces de repositorio para la capa de dominio."""

from abc import ABC, abstractmethod
from uuid import UUID

from usipipo_commons.domain.entities.vpn_key import VpnKey


class IVPNRepository(ABC):
    """Contrato para repositorio de claves VPN."""

    @abstractmethod
    def get_all(self) -> list[VpnKey]:
        """Obtiene todas las claves VPN."""
        pass

    @abstractmethod
    def get_by_id(self, key_id: UUID) -> VpnKey | None:
        """Obtiene clave VPN por ID."""
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> list[VpnKey]:
        """Obtiene todas las claves VPN de un usuario."""
        pass

    @abstractmethod
    def create(self, vpn_key: VpnKey) -> VpnKey:
        """Crea una nueva clave VPN."""
        pass

    @abstractmethod
    def update(self, vpn_key: VpnKey) -> VpnKey:
        """Actualiza clave VPN existente."""
        pass

    @abstractmethod
    def delete(self, key_id: UUID) -> bool:
        """Elimina clave VPN."""
        pass
