"""Interface for VPN key repository."""

from abc import ABC, abstractmethod
from uuid import UUID

from usipipo_commons.domain.entities.vpn_key import VpnKey


class IVpnKeyRepository(ABC):
    """Contract for VPN key repository."""

    @abstractmethod
    def get_by_id(self, key_id: UUID) -> VpnKey | None:
        """Gets VPN key by ID."""
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> list[VpnKey]:
        """Gets all VPN keys for a user."""
        pass

    @abstractmethod
    def create(self, vpn_key: VpnKey) -> VpnKey:
        """Creates a new VPN key."""
        pass

    @abstractmethod
    def update(self, vpn_key: VpnKey) -> VpnKey:
        """Updates an existing VPN key."""
        pass

    @abstractmethod
    def delete(self, key_id: UUID) -> bool:
        """Deletes a VPN key."""
        pass

    @abstractmethod
    def update_usage(self, key_id: UUID, data_used_gb: float) -> bool:
        """Updates data usage for a VPN key."""
        pass

    @abstractmethod
    def reset_data_usage(self, key_id: UUID) -> bool:
        """Resets data usage for a VPN key (new billing cycle)."""
        pass

    @abstractmethod
    def update_data_limit(self, key_id: UUID, data_limit_gb: float) -> bool:
        """Updates data limit for a VPN key."""
        pass

    @abstractmethod
    def get_keys_needing_reset(self) -> list[VpnKey]:
        """Gets keys that need billing cycle reset."""
        pass

    @abstractmethod
    def get_all_active(self) -> list[VpnKey]:
        """Gets all active VPN keys in the system."""
        pass

    @abstractmethod
    def get_all_keys(self) -> list[VpnKey]:
        """Gets all VPN keys in the system (active and inactive)."""
        pass
