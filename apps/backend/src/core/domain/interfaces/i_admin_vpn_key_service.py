"""Interface for admin VPN key management service."""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from usipipo_commons.domain.entities.vpn_key import VpnKey


class IAdminVpnKeyService(ABC):
    """Interface for administrative VPN key management."""

    @abstractmethod
    def list_keys(
        self,
        filters: dict[str, Any],
        current_admin_id: UUID,
    ) -> dict[str, Any]:
        """List VPN keys with filters and pagination.

        Args:
            filters: Dictionary containing pagination and filter parameters.
            current_admin_id: UUID of the admin performing the operation.

        Returns:
            Dictionary containing keys list and pagination metadata.
        """
        pass

    @abstractmethod
    def get_key_detail(
        self,
        key_id: UUID,
        current_admin_id: UUID,
    ) -> VpnKey | None:
        """Get detailed information about a specific key.

        Args:
            key_id: UUID of the VPN key.
            current_admin_id: UUID of the admin performing the operation.

        Returns:
            VpnKey entity or None if not found.
        """
        pass

    @abstractmethod
    def get_user_keys(
        self,
        user_id: UUID,
        current_admin_id: UUID,
    ) -> list[VpnKey]:
        """Get all keys for a specific user by user ID (UUID).

        Args:
            user_id: UUID of the user.
            current_admin_id: UUID of the admin performing the operation.

        Returns:
            List of VpnKey entities.
        """
        pass

    @abstractmethod
    def create_key(
        self,
        request: dict[str, Any],
        current_admin_id: UUID,
    ) -> VpnKey:
        """Create a new VPN key for a user.

        Args:
            request: Dictionary containing key creation parameters.
            current_admin_id: UUID of the admin performing the operation.

        Returns:
            Created VpnKey entity.
        """
        pass

    @abstractmethod
    def toggle_key(
        self,
        key_id: UUID,
        current_admin_id: UUID,
    ) -> bool:
        """Toggle key active/inactive status.

        Args:
            key_id: UUID of the VPN key.
            current_admin_id: UUID of the admin performing the operation.

        Returns:
            True if successful.
        """
        pass

    @abstractmethod
    def update_data_limit(
        self,
        key_id: UUID,
        data_limit_gb: float,
        reason: str | None,
        current_admin_id: UUID,
    ) -> bool:
        """Update data limit for a key.

        Args:
            key_id: UUID of the VPN key.
            data_limit_gb: New data limit in GB.
            reason: Optional reason for the change.
            current_admin_id: UUID of the admin performing the operation.

        Returns:
            True if successful.
        """
        pass

    @abstractmethod
    def reset_usage(
        self,
        key_id: UUID,
        reason: str | None,
        current_admin_id: UUID,
    ) -> bool:
        """Reset data usage for a key.

        Args:
            key_id: UUID of the VPN key.
            reason: Optional reason for the reset.
            current_admin_id: UUID of the admin performing the operation.

        Returns:
            True if successful.
        """
        pass

    @abstractmethod
    def regenerate_config(
        self,
        key_id: UUID,
        notify_user: bool,
        current_admin_id: UUID,
    ) -> VpnKey:
        """Regenerate configuration for a key.

        Args:
            key_id: UUID of the VPN key.
            notify_user: Whether to notify the user about the change.
            current_admin_id: UUID of the admin performing the operation.

        Returns:
            Updated VpnKey entity.
        """
        pass

    @abstractmethod
    def delete_key(
        self,
        key_id: UUID,
        current_admin_id: UUID,
    ) -> bool:
        """Delete a VPN key permanently.

        Args:
            key_id: UUID of the VPN key.
            current_admin_id: UUID of the admin performing the operation.

        Returns:
            True if successful.
        """
        pass

    @abstractmethod
    def log_audit(
        self,
        operation: str,
        target_id: UUID,
        admin_id: UUID,
        admin_username: str,
        success: bool,
        details: dict | None = None,
        error_message: str | None = None,
    ) -> None:
        """Log operation to audit trail.

        Args:
            operation: Name of the operation performed.
            target_id: UUID of the target entity.
            admin_id: UUID of the admin.
            admin_username: Username of the admin.
            success: Whether the operation was successful.
            details: Optional additional details.
            error_message: Optional error message if operation failed.
        """
        pass
