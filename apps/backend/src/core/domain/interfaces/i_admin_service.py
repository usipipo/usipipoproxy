"""Interfaces para servicios de administración."""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from usipipo_commons.domain.entities.admin_key_info import AdminKeyInfo
from usipipo_commons.domain.entities.admin_operation_result import AdminOperationResult
from usipipo_commons.domain.entities.admin_user_info import AdminUserInfo
from usipipo_commons.domain.entities.server_status import ServerStatus
from usipipo_commons.domain.entities.vpn_key import VpnKey


class IAdminStatsService(ABC):
    """Interface for administrative statistics service."""

    @abstractmethod
    def get_dashboard_stats(self, current_user_id: UUID) -> dict[str, Any]:
        """Generate complete statistics for admin dashboard."""
        pass


class IAdminUserService(ABC):
    """Interface for administrative user management service."""

    @abstractmethod
    def get_all_users(self, current_user_id: UUID) -> list[AdminUserInfo]:
        """Get list of all registered users."""
        pass

    @abstractmethod
    def get_users_paginated(
        self, page: int, per_page: int, current_user_id: UUID
    ) -> dict[str, Any]:
        """Get paginated users."""
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: UUID) -> AdminUserInfo | None:
        """Get detailed information of a user."""
        pass

    @abstractmethod
    def update_user_status(self, user_id: UUID, status: str) -> AdminOperationResult:
        """Update user status (ACTIVE, SUSPENDED, BLOCKED)."""
        pass

    @abstractmethod
    def delete_user(self, user_id: UUID) -> AdminOperationResult:
        """Delete a user and associated keys."""
        pass

    @abstractmethod
    def assign_role_to_user(
        self, user_id: UUID, role: str, duration_days: int | None = None
    ) -> AdminOperationResult:
        """Assign role to a user."""
        pass

    @abstractmethod
    def block_user(self, user_id: UUID) -> AdminOperationResult:
        """Block a user."""
        pass

    @abstractmethod
    def unblock_user(self, user_id: UUID) -> AdminOperationResult:
        """Unblock a user."""
        pass


class IAdminKeyService(ABC):
    """Interface for administrative key management service."""

    @abstractmethod
    def get_user_keys(self, user_id: UUID) -> list[VpnKey]:
        """Get all keys of a specific user."""
        pass

    @abstractmethod
    def get_all_keys(self, current_user_id: UUID) -> list[AdminKeyInfo]:
        """Get all keys from all users."""
        pass

    @abstractmethod
    def delete_key_from_servers(self, key_id: str, key_type: str) -> bool:
        """Delete a key from VPN servers (WireGuard)."""
        pass

    @abstractmethod
    def delete_key_from_db(self, key_id: str) -> bool:
        """Delete a key from database."""
        pass

    @abstractmethod
    def delete_user_key_complete(self, key_id: str) -> dict[str, Any]:
        """Delete a key completely (servers + DB)."""
        pass

    @abstractmethod
    def toggle_key_status(self, key_id: str, active: bool) -> dict[str, Any]:
        """Activate or deactivate a VPN key."""
        pass

    @abstractmethod
    def get_key_usage_stats(self, key_id: str) -> dict[str, Any]:
        """Get usage statistics for a key."""
        pass


class IAdminServerService(ABC):
    """Interface for administrative server management service."""

    @abstractmethod
    def get_server_status(self) -> dict[str, ServerStatus]:
        """Get VPN server status."""
        pass

    @abstractmethod
    def get_server_stats(self, current_user_id: UUID) -> dict[str, Any]:
        """Get server statistics for admin panel."""
        pass
