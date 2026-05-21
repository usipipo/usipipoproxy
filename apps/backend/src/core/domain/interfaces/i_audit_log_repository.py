"""Interface for audit log repository."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.infrastructure.persistence.models.admin_audit_log_model import AdminAuditLogModel


class IAuditLogRepository(ABC):
    """Interface for audit log repository."""

    @abstractmethod
    def create(self, audit_log: AdminAuditLogModel) -> AdminAuditLogModel:
        """Create a new audit log entry.

        Args:
            audit_log: Audit log entity to create.

        Returns:
            Created audit log entity.
        """
        pass

    @abstractmethod
    def get_by_id(self, log_id: UUID) -> AdminAuditLogModel | None:
        """Get audit log by ID.

        Args:
            log_id: UUID of the audit log.

        Returns:
            Audit log entity or None.
        """
        pass

    @abstractmethod
    def get_by_admin_id(
        self,
        admin_id: UUID,
        limit: int = 100,
    ) -> list[AdminAuditLogModel]:
        """Get audit logs by admin UUID.

        Args:
            admin_id: UUID of the admin.
            limit: Maximum number of results.

        Returns:
            List of audit log entities.
        """
        pass

    @abstractmethod
    def get_by_operation(
        self,
        operation: str,
        limit: int = 100,
    ) -> list[AdminAuditLogModel]:
        """Get audit logs by operation type.

        Args:
            operation: Operation name.
            limit: Maximum number of results.

        Returns:
            List of audit log entities.
        """
        pass

    @abstractmethod
    def get_by_target(
        self,
        target_type: str,
        target_id: UUID,
    ) -> list[AdminAuditLogModel]:
        """Get audit logs by target entity.

        Args:
            target_type: Type of target entity.
            target_id: UUID of the target.

        Returns:
            List of audit log entities.
        """
        pass

    @abstractmethod
    def get_recent_logs(
        self,
        limit: int = 100,
    ) -> list[AdminAuditLogModel]:
        """Get recent audit logs.

        Args:
            limit: Maximum number of results.

        Returns:
            List of recent audit log entities.
        """
        pass

    @abstractmethod
    def get_failed_logs(
        self,
        limit: int = 100,
    ) -> list[AdminAuditLogModel]:
        """Get failed audit logs.

        Args:
            limit: Maximum number of results.

        Returns:
            List of failed audit log entities.
        """
        pass
