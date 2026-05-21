"""Repository for audit log persistence."""

from datetime import datetime
from uuid import UUID

from loguru import logger
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from src.core.domain.interfaces.i_audit_log_repository import IAuditLogRepository
from src.infrastructure.persistence.models.admin_audit_log_model import AdminAuditLogModel


class AuditLogRepository(IAuditLogRepository):
    """Repository for audit log persistence."""

    def __init__(self, session: Session):
        """Initialize audit log repository.

        Args:
            session: Async database session.
        """
        self.session = session

    def create(self, audit_log: AdminAuditLogModel) -> AdminAuditLogModel:
        """Create a new audit log entry.

        Args:
            audit_log: Audit log entity to create.

        Returns:
            Created audit log entity.
        """
        try:
            self.session.add(audit_log)
            self.session.commit()
            self.session.refresh(audit_log)
            logger.debug(f"Audit log created: {audit_log.operation} - {audit_log.target_id}")
            return audit_log
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating audit log: {e}", exc_info=True)
            raise

    def get_by_id(self, log_id: UUID) -> AdminAuditLogModel | None:
        """Get audit log by ID.

        Args:
            log_id: UUID of the audit log.

        Returns:
            Audit log entity or None.
        """
        try:
            query = select(AdminAuditLogModel).where(AdminAuditLogModel.id == log_id)
            result = self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting audit log by ID: {e}", exc_info=True)
            raise

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
        try:
            query = (
                select(AdminAuditLogModel)
                .where(AdminAuditLogModel.admin_id == admin_id)
                .order_by(desc(AdminAuditLogModel.timestamp))
                .limit(limit)
            )
            result = self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting audit logs by admin: {e}", exc_info=True)
            raise

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
        try:
            query = (
                select(AdminAuditLogModel)
                .where(AdminAuditLogModel.operation == operation)
                .order_by(desc(AdminAuditLogModel.timestamp))
                .limit(limit)
            )
            result = self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting audit logs by operation: {e}", exc_info=True)
            raise

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
        try:
            query = (
                select(AdminAuditLogModel)
                .where(
                    AdminAuditLogModel.target_type == target_type,
                    AdminAuditLogModel.target_id == target_id,
                )
                .order_by(desc(AdminAuditLogModel.timestamp))
            )
            result = self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting audit logs by target: {e}", exc_info=True)
            raise

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
        try:
            query = (
                select(AdminAuditLogModel).order_by(desc(AdminAuditLogModel.timestamp)).limit(limit)
            )
            result = self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting recent audit logs: {e}", exc_info=True)
            raise

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
        try:
            query = (
                select(AdminAuditLogModel)
                .where(~AdminAuditLogModel.success)
                .order_by(desc(AdminAuditLogModel.timestamp))
                .limit(limit)
            )
            result = self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting failed audit logs: {e}", exc_info=True)
            raise

    def get_logs_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100,
    ) -> list[AdminAuditLogModel]:
        """Get audit logs by date range.

        Args:
            start_date: Start date.
            end_date: End date.
            limit: Maximum number of results.

        Returns:
            List of audit log entities.
        """
        try:
            query = (
                select(AdminAuditLogModel)
                .where(
                    AdminAuditLogModel.timestamp >= start_date,
                    AdminAuditLogModel.timestamp <= end_date,
                )
                .order_by(desc(AdminAuditLogModel.timestamp))
                .limit(limit)
            )
            result = self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting audit logs by date range: {e}", exc_info=True)
            raise
