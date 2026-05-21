"""Service for managing VPN server registry."""

import uuid
from datetime import datetime

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session
from usipipo_commons.domain.entities.server import Server
from usipipo_commons.domain.enums.server_status import ServerStatus

from src.infrastructure.persistence.models.vpn_server_model import VpnServerModel


class ServerRegistryService:
    """Service for managing VPN server registry.

    This service handles:
    - Registering new VPN servers
    - Selecting best server by country and load
    - Updating server status and heartbeat
    - Getting server information
    """

    def __init__(self, session: Session):
        """Initialize server registry service.

        Args:
            session: Async database session
        """
        self.session = session
        logger.info("ServerRegistryService initialized")

    def register_server(
        self,
        name: str,
        country_code: str,
        country_name: str,
        agent_url: str,
        agent_api_key: str,
        city: str | None = None,
        region: str | None = None,
        protocols: list[str] | None = None,
    ) -> Server:
        """Register a new VPN server.

        Args:
            name: Server name (e.g., "USA East")
            country_code: 2-letter country code (e.g., "US")
            country_name: Full country name (e.g., "United States")
            agent_url: HTTPS URL of the VPN agent
            agent_api_key: API key for agent authentication
            city: Optional city name
            region: Optional region (e.g., "us-east-1")
            protocols: List of supported protocols (default: ["wireguard"])

        Returns:
            Registered Server entity
        """
        if protocols is None:
            protocols = ["wireguard"]

        server = Server(
            id=uuid.uuid4(),
            name=name,
            country_code=country_code,
            country_name=country_name,
            city=city,
            region=region,
            agent_url=agent_url,
            agent_api_key=agent_api_key,
            supports_wireguard="wireguard" in protocols,
            status=ServerStatus.ONLINE,
            max_connections=1000,
            current_connections=0,
        )

        model = VpnServerModel.from_entity(server)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)

        logger.info(f"Registered server {name} ({country_code}) at {agent_url}")
        return model.to_entity()

    def get_server(self, server_id: uuid.UUID) -> Server | None:
        """Get a server by ID.

        Args:
            server_id: UUID of the server

        Returns:
            Server entity or None
        """
        query = select(VpnServerModel).where(VpnServerModel.id == server_id)
        result = self.session.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return model.to_entity()

    def get_available_servers(
        self,
        country: str | None = None,
    ) -> list[Server]:
        """Get available servers, optionally filtered by country.

        Args:
            country: Country code to filter by (optional)

        Returns:
            List of available servers
        """
        query = select(VpnServerModel).where(VpnServerModel.status == ServerStatus.ONLINE)

        if country:
            query = query.where(VpnServerModel.country_code == country)

        result = self.session.execute(query)
        models = result.scalars().all()

        return [model.to_entity() for model in models]

    def select_best_server(
        self,
        country: str,
        protocol: str,
    ) -> Server | None:
        """Select the best server for a given country and protocol.

        Selects server with lowest load (current_connections / max_connections).

        Args:
            country: Country code
            protocol: Protocol type ("wireguard")

        Returns:
            Best server or None if no servers available
        """
        servers = self.get_available_servers(country)

        # Filter by protocol support (WireGuard only)
        if protocol.lower() == "wireguard":
            servers = [s for s in servers if s.supports_wireguard]
        else:
            logger.warning(f"Unsupported protocol: {protocol}")
            return None

        if not servers:
            logger.warning(f"No available servers for {country}/{protocol}")
            return None

        # Select server with lowest load
        best_server = min(servers, key=lambda s: s.current_connections / max(s.max_connections, 1))

        logger.debug(f"Selected server {best_server.name} for {country}/{protocol}")
        return best_server

    def update_server_status(
        self,
        server_id: uuid.UUID,
        status: ServerStatus,
    ) -> None:
        """Update server status.

        Args:
            server_id: UUID of the server
            status: New status
        """
        query = select(VpnServerModel).where(VpnServerModel.id == server_id)
        result = self.session.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            logger.warning(f"Server {server_id} not found")
            return

        model.status = status
        model.updated_at = datetime.now()
        self.session.commit()

        logger.info(f"Updated server {model.name} status to {status}")

    def update_heartbeat(self, server_id: uuid.UUID) -> None:
        """Update server heartbeat timestamp.

        Called when receiving metrics from agent.

        Args:
            server_id: UUID of the server
        """
        query = select(VpnServerModel).where(VpnServerModel.id == server_id)
        result = self.session.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            return

        model.last_heartbeat_at = datetime.now()
        self.session.commit()

    def get_servers_for_user(
        self,
        protocol: str,
        limit: int | None = None,
    ) -> list[Server]:
        """Get available servers for user display, sorted by load.

        Args:
            protocol: Protocol type ("wireguard")
            limit: Optional limit for number of servers returned

        Returns:
            List of available servers sorted by load (lowest first)
        """
        servers = self.get_available_servers()

        # Filter by protocol support (WireGuard only)
        if protocol.lower() == "wireguard":
            servers = [s for s in servers if s.supports_wireguard]
        else:
            servers = []

        # Filter only online servers (already done by get_available_servers, but be explicit)
        servers = [s for s in servers if s.status == "online"]

        # Sort by load (lowest first)
        servers.sort(key=lambda s: s.current_connections / max(s.max_connections, 1))

        # Apply limit if specified
        if limit is not None:
            servers = servers[:limit]

        logger.debug(f"Found {len(servers)} available servers for {protocol}")
        return servers
