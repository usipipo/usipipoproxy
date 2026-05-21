"""Servicios de aplicación para gestión de VPN."""

import uuid
from datetime import UTC, datetime, timedelta

from loguru import logger
from usipipo_commons.constants.plans import MAX_KEYS_PER_USER
from usipipo_commons.domain.entities.server import Server
from usipipo_commons.domain.entities.vpn_key import VpnKey
from usipipo_commons.domain.enums.key_status import KeyStatus
from usipipo_commons.domain.enums.key_type import KeyType

from src.core.application.exceptions import (
    AgentOfflineError,
    InvalidVpnTypeError,
    NoAvailableServersError,
    UserNotFoundError,
    VpnKeyLimitReachedError,
    VpnKeyNotFoundError,
    VpnKeyRollbackError,
)
from src.core.application.services.server_registry_service import ServerRegistryService
from src.core.domain.interfaces.i_user_repository import IUserRepository
from src.core.domain.interfaces.i_vpn_repository import IVPNRepository
from src.infrastructure.api_clients.vpn_agent_client import VpnAgentClient
from src.infrastructure.vpn_providers.wireguard_client import WireGuardClient


def _redact_api_key(api_key: str) -> str:
    """Redact API key for logging purposes."""
    if len(api_key) <= 8:
        return "****"
    return f"{api_key[:4]}...{api_key[-4:]}"


class VpnService:
    """Servicio de aplicación para gestión de claves VPN."""

    def __init__(
        self,
        user_repo: IUserRepository,
        vpn_repo: IVPNRepository,
        server_registry_service: ServerRegistryService,
        wireguard_client: WireGuardClient | None = None,
    ):
        self.user_repo = user_repo
        self.vpn_repo = vpn_repo
        self.server_registry = server_registry_service
        self.wireguard_client = wireguard_client
        self._agent_clients: dict[uuid.UUID, VpnAgentClient] = {}
        logger.info("VpnService initialized with multi-server support")

    def create_key(
        self,
        user_id: uuid.UUID,
        name: str,
        vpn_type: str,
        data_limit_gb: float = 5.0,
        country: str | None = None,
        server_id: uuid.UUID | None = None,
    ) -> VpnKey:
        """
        Crea una nueva clave VPN.

        Args:
            user_id: UUID del usuario propietario
            name: Nombre descriptivo de la clave
            vpn_type: Tipo de VPN ("wireguard")
            country: País para seleccionar servidor (default: US)
            data_limit_gb: Límite de datos en GB
            server_id: UUID del servidor seleccionado (opcional, si no se proporciona se auto-selecciona)

        Returns:
            La clave VPN creada

        Raises:
            UserNotFoundError: Si el usuario no existe
            VpnKeyLimitReachedError: Si el usuario alcanzó el límite de claves
            InvalidVpnTypeError: Si el tipo de VPN es inválido
            NoAvailableServersError: Si no hay servidores disponibles
        """
        # Verificar usuario
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        # Validar tipo de VPN
        try:
            key_type_enum = KeyType(vpn_type.lower())
        except ValueError:
            raise InvalidVpnTypeError(f"Invalid VPN type: {vpn_type}")

        # Verificar límite de claves
        existing_keys = self.vpn_repo.get_by_user_id(user_id)
        active_keys = [k for k in existing_keys if k.is_active]

        if len(active_keys) >= MAX_KEYS_PER_USER:
            raise VpnKeyLimitReachedError(f"User reached max keys ({MAX_KEYS_PER_USER})")

        # Seleccionar servidor: usar server_id proporcionado o auto-seleccionar
        if server_id:
            # Usar servidor seleccionado por el usuario
            server = self.server_registry.get_server(server_id)
            if not server or server.status != "online":
                raise NoAvailableServersError("Selected server is not available")
            logger.info(
                f"Using user-selected server {server.name} ({server.id}) for user {user_id}"
            )
        else:
            # Auto-seleccionar mejor servidor (lógica existente)
            if country is None:
                country = "US"  # Default a USA

            server = self.server_registry.select_best_server(
                country=country, protocol=vpn_type
            )

            if not server:
                logger.warning(f"No available servers for {country}/{vpn_type}")
                raise NoAvailableServersError(f"No available servers for {country}/{vpn_type}")

            logger.info(
                f"Auto-selected server {server.name} ({server.country_code}) for user {user_id}"
            )

        # Obtener cliente del agente para este servidor
        agent_client = self._get_agent_client(server)

        # Health check before proceeding
        is_healthy = agent_client.health_check()
        if not is_healthy:
            raise AgentOfflineError(
                f"VPN agent on server '{server.name}' is offline or not responding"
            )

        # Generar config WireGuard usando agente remoto
        external_id = ""
        if key_type_enum == KeyType.WIREGUARD:
            result = agent_client.create_wireguard_peer(name=name)
            config = result["config"]
            external_id = result["public_key"]
        else:
            raise InvalidVpnTypeError(f"Invalid VPN type: {vpn_type}")

        # Calcular fecha de expiración (30 días por defecto)
        now = datetime.now(UTC)
        expires_at = now + timedelta(days=30)

        # Calcular data_limit_bytes
        data_limit_bytes = int(data_limit_gb * 1024**3)

        # Crear entidad
        vpn_key = VpnKey(
            id=uuid.uuid4(),
            user_id=user_id,
            name=name,
            key_type=key_type_enum,
            status=KeyStatus.ACTIVE,
            key_data=config,
            external_id=external_id,
            server_id=server.id,  # ← Asociar clave con servidor
            created_at=now,
            expires_at=expires_at,
            used_bytes=0,
            data_limit_bytes=data_limit_bytes,
            billing_reset_at=now,
        )

        logger.debug(f"Created VPN key {vpn_key.id} on server {server.name}")

        # Persistir con saga rollback
        try:
            return self.vpn_repo.create(vpn_key)
        except Exception as db_error:
            # DB failed after agent succeeded → rollback agent
            logger.warning(
                f"DB error during key creation, rolling back agent operation "
                f"for key '{name}' (external_id: {external_id}) on server {server.name}: {db_error}"
            )
            try:
                if key_type_enum == KeyType.WIREGUARD:
                    agent_client.delete_wireguard_peer(external_id)
                logger.warning(f"Rollback successful for key '{name}' on server {server.name}")
            except Exception as cleanup_error:
                raise VpnKeyRollbackError(
                    operation="create",
                    key_name=name,
                    external_id=external_id,
                    server_name=server.name,
                    cleanup_status="failed",
                    original_error=db_error,
                    cleanup_error=cleanup_error,
                ) from cleanup_error
            # Re-raise original DB error after successful rollback
            raise

    def _get_agent_client(self, server: Server) -> VpnAgentClient:
        """Get or create VPN agent client for a server.

        Args:
            server: Server entity

        Returns:
            VpnAgentClient instance
        """
        if server.id not in self._agent_clients:
            self._agent_clients[server.id] = VpnAgentClient(
                base_url=server.agent_url,
                api_key=server.agent_api_key,
            )
            logger.debug(
                f"Created VpnAgentClient for server {server.name} (API key: {_redact_api_key(server.agent_api_key)})"
            )
        return self._agent_clients[server.id]

    def get_key_by_id(self, key_id: uuid.UUID) -> VpnKey | None:
        """
        Obtiene una clave VPN por ID.

        Args:
            key_id: UUID de la clave

        Returns:
            La clave VPN o None si no existe
        """
        return self.vpn_repo.get_by_id(key_id)

    def get_user_keys(self, user_id: uuid.UUID) -> list[VpnKey]:
        """
        Obtiene todas las claves VPN de un usuario.

        Args:
            user_id: UUID del usuario

        Returns:
            Lista de claves VPN del usuario
        """
        return self.vpn_repo.get_by_user_id(user_id)

    def delete_key(self, user_id: uuid.UUID, key_id: uuid.UUID) -> bool:
        """
        Elimina una clave VPN.

        Args:
            user_id: UUID del usuario propietario
            key_id: UUID de la clave a eliminar

        Returns:
            True si se eliminó, False si no existía

        Raises:
            VpnKeyNotFoundError: Si la clave no existe
            PermissionError: Si el usuario no es propietario de la clave
        """
        key = self.vpn_repo.get_by_id(key_id)
        if not key:
            raise VpnKeyNotFoundError(f"Key {key_id} not found")

        # Verificar propiedad
        if key.user_id != user_id:
            raise PermissionError("User does not own this key")

        # Obtener servidor asociado a la clave
        if key.server_id:
            server = self.server_registry.get_server(key.server_id)
            if server:
                agent_client = self._get_agent_client(server)

                # Health check before proceeding
                is_healthy = agent_client.health_check()
                if not is_healthy:
                    raise AgentOfflineError(
                        f"VPN agent on server '{server.name}' is offline or not responding"
                    )

                # Revocar usando agente remoto
                if key.key_type == KeyType.WIREGUARD:
                    agent_client.delete_wireguard_peer(key.external_id or "")
                    logger.debug(f"Deleted WireGuard peer {key.external_id} from {server.name}")

                # Eliminar de BD con saga error handling
                try:
                    return self.vpn_repo.delete(key_id)
                except Exception as db_error:
                    # Agent succeeded but DB failed → can't rollback deletion, raise VpnKeyRollbackError
                    raise VpnKeyRollbackError(
                        operation="delete",
                        key_id=str(key_id),
                        external_id=key.external_id or "",
                        server_name=server.name,
                        cleanup_status="partial",
                        original_error=db_error,
                    ) from db_error
            else:
                # Server not found in registry, use local fallback
                logger.debug(f"Server {key.server_id} not found in registry, using local fallback")
                if key.key_type == KeyType.WIREGUARD and self.wireguard_client:
                    self.wireguard_client.delete_client(key.external_id or "")
                return self.vpn_repo.delete(key_id)
        else:
            # Fallback a clientes locales (para claves antiguas sin server_id)
            logger.debug(f"Key {key_id} has no server_id, using local fallback")
            if key.key_type == KeyType.WIREGUARD and self.wireguard_client:
                self.wireguard_client.delete_client(key.external_id or "")

        # Eliminar de BD
        return self.vpn_repo.delete(key_id)

    def update_key(
        self,
        user_id: uuid.UUID,
        key_id: uuid.UUID,
        name: str | None = None,
        data_limit_gb: float | None = None,
    ) -> VpnKey:
        """
        Actualiza una clave VPN.

        Args:
            user_id: UUID del usuario propietario
            key_id: UUID de la clave
            name: Nuevo nombre (opcional)
            data_limit_gb: Nuevo límite de datos (opcional)

        Returns:
            La clave VPN actualizada

        Raises:
            VpnKeyNotFoundError: Si la clave no existe
            PermissionError: Si el usuario no es propietario de la clave
        """
        key = self.vpn_repo.get_by_id(key_id)
        if not key:
            raise VpnKeyNotFoundError(f"Key {key_id} not found")

        # Verificar propiedad
        if key.user_id != user_id:
            raise PermissionError("User does not own this key")

        # Actualizar campos
        updated_key = VpnKey(
            id=key.id,
            user_id=key.user_id,
            name=name if name is not None else key.name,
            key_type=key.key_type,
            key_data=key.key_data,
            status=key.status,
            created_at=key.created_at,
            expires_at=key.expires_at,
            last_seen_at=key.last_seen_at,
            used_bytes=key.used_bytes,
            data_limit_bytes=int(data_limit_gb * 1024**3)
            if data_limit_gb is not None
            else key.data_limit_bytes,
            billing_reset_at=key.billing_reset_at,
        )

        return self.vpn_repo.update(updated_key)

    def revoke_key(self, user_id: uuid.UUID, key_id: uuid.UUID) -> VpnKey:
        """
        Revoca una clave VPN (la marca como revocada).

        Args:
            user_id: UUID del usuario propietario
            key_id: UUID de la clave

        Returns:
            La clave VPN actualizada

        Raises:
            VpnKeyNotFoundError: Si la clave no existe
            PermissionError: Si el usuario no es propietario de la clave
        """
        key = self.vpn_repo.get_by_id(key_id)
        if not key:
            raise VpnKeyNotFoundError(f"Key {key_id} not found")

        # Verificar propiedad
        if key.user_id != user_id:
            raise PermissionError("User does not own this key")

        # Revocar en proveedor VPN
        if key.key_type == KeyType.WIREGUARD and self.wireguard_client:
            self.wireguard_client.delete_client(key.external_id or "")

        # Actualizar estado
        updated_key = VpnKey(
            id=key.id,
            user_id=key.user_id,
            name=key.name,
            key_type=key.key_type,
            status=KeyStatus.REVOKED,
            key_data=key.key_data,
            created_at=key.created_at,
            expires_at=key.expires_at,
            last_seen_at=key.last_seen_at,
            used_bytes=key.used_bytes,
            data_limit_bytes=key.data_limit_bytes,
            billing_reset_at=key.billing_reset_at,
        )

        return self.vpn_repo.update(updated_key)

    def get_active_keys_count(self, user_id: uuid.UUID) -> int:
        """
        Obtiene la cantidad de claves activas de un usuario.

        Args:
            user_id: UUID del usuario

        Returns:
            Cantidad de claves activas
        """
        keys = self.vpn_repo.get_by_user_id(user_id)
        return len([k for k in keys if k.is_active])

    def can_create_more_keys(self, user_id: uuid.UUID) -> bool:
        """
        Verifica si el usuario puede crear más claves.

        Args:
            user_id: UUID del usuario

        Returns:
            True si puede crear más claves, False si alcanzó el límite
        """
        active_count = self.get_active_keys_count(user_id)
        return active_count < MAX_KEYS_PER_USER

    def get_user_keys_for_server(
        self,
        user_id: uuid.UUID,
        server_id: uuid.UUID,
    ) -> list[VpnKey]:
        """Get all VPN keys a user has on a specific server.

        Used for authorization checks on server-specific endpoints.

        Args:
            user_id: UUID of the user
            server_id: UUID of the server

        Returns:
            List of VPN keys the user has on this server
        """
        all_keys = self.vpn_repo.get_by_user_id(user_id)
        return [k for k in all_keys if k.server_id == server_id]
