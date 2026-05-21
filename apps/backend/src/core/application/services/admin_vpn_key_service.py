"""Admin VPN key management service."""

import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any
from uuid import UUID

if TYPE_CHECKING:
    from usipipo_commons.domain.entities.server import Server

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session
from usipipo_commons.domain.entities.vpn_key import VpnKey
from usipipo_commons.domain.enums.key_status import KeyStatus
from usipipo_commons.domain.enums.key_type import KeyType

from src.core.domain.interfaces.i_admin_vpn_key_service import IAdminVpnKeyService
from src.core.domain.interfaces.i_audit_log_repository import IAuditLogRepository
from src.core.domain.interfaces.i_user_repository import IUserRepository
from src.core.domain.interfaces.i_vpn_key_repository import IVpnKeyRepository
from src.infrastructure.api_clients.vpn_agent_client import VpnAgentClient
from src.infrastructure.persistence.models.vpn_server_model import VpnServerModel


class AdminVpnKeyService(IAdminVpnKeyService):
    """Service for administrative VPN key management."""

    def __init__(
        self,
        session: Session,
        user_repo: IUserRepository,
        vpn_key_repo: IVpnKeyRepository,
        audit_log_repo: IAuditLogRepository | None = None,
    ):
        self.session = session
        self.user_repo = user_repo
        self.vpn_key_repo = vpn_key_repo
        self.audit_log_repo = audit_log_repo
        self._agent_clients: dict[uuid.UUID, VpnAgentClient] = {}

    def list_keys(
        self,
        filters: dict[str, Any],
        current_admin_id: UUID,
    ) -> dict[str, Any]:
        """List VPN keys with filters and pagination."""
        try:
            # Get all keys
            all_keys = self.vpn_key_repo.get_all_keys()

            # Apply filters
            filtered_keys = all_keys

            # Filter by user ID (UUID)
            if user_id_str := filters.get("user_id"):
                try:
                    filter_user_id = UUID(user_id_str)
                    filtered_keys = [k for k in filtered_keys if k.user_id == filter_user_id]
                except ValueError:
                    filtered_keys = []

            # Filter by VPN type
            if vpn_type := filters.get("vpn_type"):
                filtered_keys = [k for k in filtered_keys if k.key_type.value == vpn_type]

            # Filter by status
            if status := filters.get("status"):
                filtered_keys = [k for k in filtered_keys if k.status.value == status]

            # Filter by country (requires server lookup)
            if country := filters.get("country"):
                query = select(VpnServerModel).where(VpnServerModel.country_code == country)
                result = self.session.execute(query)
                servers = result.scalars().all()
                server_ids = {s.id for s in servers}
                filtered_keys = [k for k in filtered_keys if k.server_id in server_ids]

            # Search by name
            if search := filters.get("search"):
                filtered_keys = [k for k in filtered_keys if search.lower() in k.name.lower()]

            # Sorting
            sort_by = filters.get("sort_by", "created_at")
            sort_order = filters.get("sort_order", "desc")
            reverse = sort_order == "desc"

            if sort_by == "created_at":
                filtered_keys.sort(
                    key=lambda k: k.created_at or datetime.min.replace(tzinfo=UTC), reverse=reverse
                )
            elif sort_by == "last_used":
                filtered_keys.sort(
                    key=lambda k: k.last_seen_at or datetime.min.replace(tzinfo=UTC),
                    reverse=reverse,
                )
            elif sort_by == "data_used":
                filtered_keys.sort(key=lambda k: k.used_bytes or 0, reverse=reverse)

            # Pagination
            page = filters.get("page", 1)
            page_size = filters.get("page_size", 20)
            total = len(filtered_keys)
            total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_keys = filtered_keys[start_idx:end_idx]

            return {
                "keys": paginated_keys,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1,
            }

        except Exception as e:
            logger.error(f"Error listing keys: {e}", exc_info=True)
            raise

    def get_key_detail(
        self,
        key_id: uuid.UUID,
        current_admin_id: UUID,
    ) -> VpnKey | None:
        """Get detailed information about a specific key."""
        try:
            return self.vpn_key_repo.get_by_id(key_id)
        except Exception as e:
            logger.error(f"Error getting key detail: {e}", exc_info=True)
            raise

    def get_user_keys(
        self,
        user_id: UUID,
        current_admin_id: UUID,
    ) -> list[VpnKey]:
        """Get all keys for a specific user by user ID (UUID)."""
        try:
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return []

            return self.vpn_key_repo.get_by_user_id(user.id)
        except Exception as e:
            logger.error(f"Error getting user keys: {e}", exc_info=True)
            raise

    def create_key(
        self,
        request: dict[str, Any],
        current_admin_id: UUID,
    ) -> VpnKey:
        """Create a new VPN key for a user."""
        try:
            # Get user
            user = self.user_repo.get_by_id(UUID(request["user_id"]))
            if not user:
                raise ValueError(f"User with ID {request['user_id']} not found")

            # Select server by country
            country = request.get("country", "US")
            query = select(VpnServerModel).where(
                VpnServerModel.country_code == country,
                VpnServerModel.status == "online",
            )
            result = self.session.execute(query)
            servers = result.scalars().all()

            if not servers:
                raise ValueError(f"No available servers in {country}")

            # Use first available server (could implement load balancing later)
            server = servers[0]

            # Get agent client
            agent_client = self._get_agent_client(server)

            # Create key on agent (WireGuard only)
            vpn_type = request["vpn_type"].lower()
            wireguard_result = agent_client.create_wireguard_peer(name=request["name"])
            config = wireguard_result["config"]
            external_id = wireguard_result["public_key"]

            # Calculate dates
            now = datetime.now(UTC)
            expires_in_days = request.get("expires_in_days", 30)
            expires_at = now + timedelta(days=expires_in_days)
            data_limit_gb = request.get("data_limit_gb", 5.0)
            data_limit_bytes = int(data_limit_gb * 1024**3)

            # Create entity
            vpn_key = VpnKey(
                id=uuid.uuid4(),
                user_id=user.id,
                name=request["name"],
                key_type=KeyType(vpn_type),
                status=KeyStatus.ACTIVE,
                key_data=config,
                external_id=external_id,
                server_id=server.id,
                created_at=now,
                expires_at=expires_at,
                used_bytes=0,
                data_limit_bytes=data_limit_bytes,
                billing_reset_at=now,
            )

            # Save to DB
            created_key = self.vpn_key_repo.create(vpn_key)

            # Log audit
            self.log_audit(
                operation="create_key",
                target_id=created_key.id,
                admin_id=current_admin_id,
                admin_username="",  # Will be set by caller
                success=True,
                details={
                    "user_id": str(user.id),
                    "vpn_type": vpn_type,
                    "data_limit_gb": data_limit_gb,
                    "country": country,
                },
            )

            logger.info(f"Created VPN key {created_key.id} for user {user.id}")
            return created_key

        except Exception as e:
            logger.error(f"Error creating key: {e}", exc_info=True)
            self.log_audit(
                operation="create_key",
                target_id=uuid.UUID(request.get("key_id", "00000000-0000-0000-0000-000000000000")),
                admin_id=current_admin_id,
                admin_username="",
                success=False,
                error_message=str(e),
            )
            raise

    def toggle_key(
        self,
        key_id: uuid.UUID,
        current_admin_id: UUID,
    ) -> bool:
        """Toggle key active/inactive status."""
        try:
            key = self.vpn_key_repo.get_by_id(key_id)
            if not key:
                raise ValueError(f"Key {key_id} not found")

            # Toggle status between ACTIVE and REVOKED
            new_status = KeyStatus.REVOKED if key.status == KeyStatus.ACTIVE else KeyStatus.ACTIVE
            key.status = new_status

            self.vpn_key_repo.update(key)

            # Log audit
            self.log_audit(
                operation="toggle_key",
                target_id=key_id,
                admin_id=current_admin_id,
                admin_username="",
                success=True,
                details={
                    "user_id": str(key.user_id),
                    "new_status": new_status.value,
                },
            )

            logger.info(f"Toggled key {key_id} to {new_status.value}")
            return True

        except Exception as e:
            logger.error(f"Error toggling key: {e}", exc_info=True)
            raise

    def update_data_limit(
        self,
        key_id: uuid.UUID,
        data_limit_gb: float,
        reason: str | None,
        current_admin_id: UUID,
    ) -> bool:
        """Update data limit for a key."""
        try:
            key = self.vpn_key_repo.get_by_id(key_id)
            if not key:
                raise ValueError(f"Key {key_id} not found")

            old_limit = key.data_limit_bytes
            key.data_limit_bytes = int(data_limit_gb * 1024**3)

            self.vpn_key_repo.update(key)

            # Log audit
            self.log_audit(
                operation="update_data_limit",
                target_id=key_id,
                admin_id=current_admin_id,
                admin_username="",
                success=True,
                details={
                    "user_id": str(key.user_id),
                    "old_limit_gb": old_limit / (1024**3),
                    "new_limit_gb": data_limit_gb,
                    "reason": reason,
                },
            )

            logger.info(f"Updated data limit for key {key_id}: {old_limit} -> {data_limit_gb} GB")
            return True

        except Exception as e:
            logger.error(f"Error updating data limit: {e}", exc_info=True)
            raise

    def reset_usage(
        self,
        key_id: uuid.UUID,
        reason: str | None,
        current_admin_id: UUID,
    ) -> bool:
        """Reset data usage for a key."""
        try:
            key = self.vpn_key_repo.get_by_id(key_id)
            if not key:
                raise ValueError(f"Key {key_id} not found")

            old_usage = key.used_bytes
            key.used_bytes = 0
            key.billing_reset_at = datetime.now(UTC)

            self.vpn_key_repo.update(key)

            # Log audit
            self.log_audit(
                operation="reset_usage",
                target_id=key_id,
                admin_id=current_admin_id,
                admin_username="",
                success=True,
                details={
                    "user_id": str(key.user_id),
                    "old_usage_gb": old_usage / (1024**3),
                    "reason": reason,
                },
            )

            logger.info(f"Reset usage for key {key_id}: {old_usage} bytes -> 0")
            return True

        except Exception as e:
            logger.error(f"Error resetting usage: {e}", exc_info=True)
            raise

    def regenerate_config(
        self,
        key_id: uuid.UUID,
        notify_user: bool,
        current_admin_id: UUID,
    ) -> VpnKey:
        """Regenerate configuration for a key."""
        try:
            key = self.vpn_key_repo.get_by_id(key_id)
            if not key:
                raise ValueError(f"Key {key_id} not found")

            # Get server
            if not key.server_id:
                raise ValueError("Key has no server association")

            server_model = self._get_server_by_id(key.server_id)
            if not server_model:
                raise ValueError("Server not found")

            server_entity = (
                server_model.to_entity() if hasattr(server_model, "to_entity") else server_model
            )

            # Get agent client
            agent_client = self._get_agent_client(server_entity)

            # Delete old config from agent and create new (WireGuard only)
            agent_client.delete_wireguard_peer(key.external_id or "")
            # Create new
            result = agent_client.create_wireguard_peer(name=key.name)
            config = result["config"]
            external_id = result["public_key"]

            # Update key
            key.key_data = config
            key.external_id = external_id

            self.vpn_key_repo.update(key)

            # Log audit
            self.log_audit(
                operation="regenerate_config",
                target_id=key_id,
                admin_id=current_admin_id,
                admin_username="",
                success=True,
                details={
                    "user_id": str(key.user_id),
                    "notify_user": notify_user,
                },
            )

            logger.info(f"Regenerated config for key {key_id}")
            return key

        except Exception as e:
            logger.error(f"Error regenerating config: {e}", exc_info=True)
            raise

    def delete_key(
        self,
        key_id: uuid.UUID,
        current_admin_id: UUID,
    ) -> bool:
        """Delete a VPN key permanently."""
        try:
            key = self.vpn_key_repo.get_by_id(key_id)
            if not key:
                raise ValueError(f"Key {key_id} not found")

            # Delete from agent
            if key.server_id:
                server_model = self._get_server_by_id(key.server_id)
                if server_model:
                    server_entity = (
                        server_model.to_entity()
                        if hasattr(server_model, "to_entity")
                        else server_model
                    )
                    agent_client = self._get_agent_client(server_entity)
                    agent_client.delete_wireguard_peer(key.external_id or "")

            # Delete from DB
            self.vpn_key_repo.delete(key_id)

            # Log audit
            self.log_audit(
                operation="delete_key",
                target_id=key_id,
                admin_id=current_admin_id,
                admin_username="",
                success=True,
                details={
                    "vpn_type": key.key_type.value,
                },
            )

            logger.info(f"Deleted key {key_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting key: {e}", exc_info=True)
            raise

    def _get_agent_client(self, server: "VpnServerModel | Server") -> VpnAgentClient:
        """Get or create agent client for server."""
        if server.id not in self._agent_clients:
            self._agent_clients[server.id] = VpnAgentClient(
                base_url=server.agent_url,
                api_key=server.agent_api_key,
            )
        return self._agent_clients[server.id]

    def _get_server_by_id(self, server_id: uuid.UUID) -> VpnServerModel | None:
        """Get server by ID."""
        query = select(VpnServerModel).where(VpnServerModel.id == server_id)
        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def log_audit(
        self,
        operation: str,
        target_id: uuid.UUID,
        admin_id: UUID,
        admin_username: str,
        success: bool,
        details: dict | None = None,
        error_message: str | None = None,
    ) -> None:
        """Log operation to audit trail."""
        from src.infrastructure.persistence.models.admin_audit_log_model import AdminAuditLogModel

        try:
            audit_log = AdminAuditLogModel(
                operation=operation,
                target_type="vpn_key",
                target_id=target_id,
                admin_id=admin_id,
                admin_username=admin_username,
                target_user_id=None,
                details=details if isinstance(details, dict) else None,
                success=success,
                error_message=error_message,
            )

            if self.audit_log_repo:
                self.audit_log_repo.create(audit_log)
            else:
                # Fallback: just log to application logs
                if success:
                    logger.info(
                        f"Audit: {operation} - target={target_id} - admin={admin_id} "
                        f"({admin_username}) - success={success}"
                    )
                else:
                    logger.error(
                        f"Audit: {operation} - target={target_id} - admin={admin_id} "
                        f"({admin_username}) - success={success} - error={error_message}"
                    )
        except Exception as e:
            logger.error(f"Error logging audit: {e}", exc_info=True)
