"""
VPN Server factory for creating test servers.
"""

import uuid

from src.infrastructure.persistence.models.vpn_server_model import VpnServerModel


class VpnServerFactory:
    """Factory for creating test VPN servers."""

    @staticmethod
    def create(
        name: str = None,
        agent_url: str = "http://test-agent",
        agent_api_key: str = "agent_test123",
        location: str = "US",
        is_active: bool = True,
        server_type: str = "both",
    ) -> VpnServerModel:
        """Create a test VPN server."""
        return VpnServerModel(
            id=uuid.uuid4(),
            name=name or f"Test Server {location}",
            agent_url=agent_url,
            _agent_api_key=agent_api_key,
            location=location,
            is_active=is_active,
            server_type=server_type,
        )
