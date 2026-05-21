"""Unit tests for ServerRegistryService.get_servers_for_user method."""

import uuid
from unittest.mock import AsyncMock

import pytest
from usipipo_commons.domain.entities.server import Server

from src.core.application.services.server_registry_service import ServerRegistryService


@pytest.fixture
def mock_session():
    """Create mock database session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def service(mock_session):
    """Create ServerRegistryService instance with mock session."""
    return ServerRegistryService(session=mock_session)


@pytest.fixture
def sample_servers():
    """Create sample servers with different loads and protocol support."""
    return [
        Server(
            id=uuid.uuid4(),
            name="High Load Server",
            country_code="US",
            country_name="United States",
            agent_url="https://server1.example.com",
            agent_api_key="key1",
            supports_wireguard=True,
            status="online",
            max_connections=1000,
            current_connections=800,  # 80% load
        ),
        Server(
            id=uuid.uuid4(),
            name="Low Load Server",
            country_code="US",
            country_name="United States",
            agent_url="https://server2.example.com",
            agent_api_key="key2",
            supports_wireguard=True,
            status="online",
            max_connections=1000,
            current_connections=100,  # 10% load - should be first
        ),
        Server(
            id=uuid.uuid4(),
            name="Medium Load Server",
            country_code="US",
            country_name="United States",
            agent_url="https://server3.example.com",
            agent_api_key="key3",
            supports_wireguard=True,
            status="online",
            max_connections=1000,
            current_connections=500,  # 50% load
        ),
        Server(
            id=uuid.uuid4(),
            name="Offline Server",
            country_code="US",
            country_name="United States",
            agent_url="https://server4.example.com",
            agent_api_key="key4",
            supports_wireguard=True,
            status="offline",  # Should be filtered out
            max_connections=1000,
            current_connections=0,
        ),
        Server(
            id=uuid.uuid4(),
            name="WireGuard Only Server",
            country_code="GB",
            country_name="United Kingdom",
            agent_url="https://server5.example.com",
            agent_api_key="key5",
            supports_wireguard=True,
            status="online",
            max_connections=1000,
            current_connections=300,  # 30% load
        ),
    ]


class TestGetServersForUser:
    """Tests for get_servers_for_user method."""

    @pytest.mark.asyncio
    async def test_returns_servers_sorted_by_load(self, service, sample_servers):
        """Test that servers are returned sorted by load (lowest first)."""
        # Arrange
        service.get_available_servers = AsyncMock(return_value=sample_servers)

        # Act
        result = await service.get_servers_for_user(protocol="wireguard")

        # Assert
        assert len(result) == 4  # Excludes offline server
        assert result[0].name == "Low Load Server"  # 10% load
        assert result[1].name == "WireGuard Only Server"  # 30% load
        assert result[2].name == "Medium Load Server"  # 50% load
        assert result[3].name == "High Load Server"  # 80% load

    @pytest.mark.asyncio
    async def test_filters_by_wireguard_protocol(self, service, sample_servers):
        """Test filtering servers by WireGuard protocol."""
        # Arrange
        service.get_available_servers = AsyncMock(return_value=sample_servers)

        # Act
        result = await service.get_servers_for_user(protocol="wireguard")

        # Assert
        assert len(result) == 4  # Excludes offline server
        for server in result:
            assert server.supports_wireguard is True
            assert server.status == "online"

    @pytest.mark.asyncio
    async def test_filters_offline_servers(self, service, sample_servers):
        """Test that offline servers are filtered out."""
        # Arrange
        service.get_available_servers = AsyncMock(return_value=sample_servers)

        # Act
        result = await service.get_servers_for_user(protocol="wireguard")

        # Assert
        offline_servers = [s for s in result if s.status == "offline"]
        assert len(offline_servers) == 0

    @pytest.mark.asyncio
    async def test_applies_limit_parameter(self, service, sample_servers):
        """Test that limit parameter is applied correctly."""
        # Arrange
        service.get_available_servers = AsyncMock(return_value=sample_servers)

        # Act
        result = await service.get_servers_for_user(protocol="wireguard", limit=2)

        # Assert
        assert len(result) == 2
        assert result[0].name == "Low Load Server"  # 10% load
        assert result[1].name == "WireGuard Only Server"  # 30% load

    @pytest.mark.asyncio
    async def test_handles_empty_server_list(self, service):
        """Test handling empty server list."""
        # Arrange
        service.get_available_servers = AsyncMock(return_value=[])

        # Act
        result = await service.get_servers_for_user(protocol="wireguard")

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_handles_no_matching_protocol(self, service, sample_servers):
        """Test when no servers match the requested protocol."""
        # Arrange
        # Create servers that don't support the requested protocol
        no_wireguard_servers = [
            Server(
                id=uuid.uuid4(),
                name="No WireGuard",
                country_code="US",
                country_name="United States",
                agent_url="https://server1.example.com",
                agent_api_key="key1",
                supports_wireguard=False,
                status="online",
                max_connections=1000,
                current_connections=100,
            )
        ]
        service.get_available_servers = AsyncMock(return_value=no_wireguard_servers)

        # Act
        result = await service.get_servers_for_user(protocol="wireguard")

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_case_insensitive_protocol(self, service, sample_servers):
        """Test that protocol filtering is case-insensitive."""
        # Arrange
        service.get_available_servers = AsyncMock(return_value=sample_servers)

        # Act
        result_wireguard_upper = await service.get_servers_for_user(protocol="WIREGUARD")
        result_wireguard = await service.get_servers_for_user(protocol="WireGuard")

        # Assert
        assert len(result_wireguard_upper) == 4
        assert len(result_wireguard) == 4

    @pytest.mark.asyncio
    async def test_limit_greater_than_available(self, service, sample_servers):
        """Test when limit is greater than available servers."""
        # Arrange
        service.get_available_servers = AsyncMock(return_value=sample_servers)

        # Act
        result = await service.get_servers_for_user(protocol="wireguard", limit=100)

        # Assert
        assert len(result) == 4  # Returns all available servers

    @pytest.mark.asyncio
    async def test_load_calculation_with_zero_max_connections(self, service):
        """Test load calculation handles zero max_connections gracefully."""
        # Arrange
        servers_with_zero_max = [
            Server(
                id=uuid.uuid4(),
                name="Zero Max Server",
                country_code="US",
                country_name="United States",
                agent_url="https://server1.example.com",
                agent_api_key="key1",
                supports_wireguard=True,
                status="online",
                max_connections=0,  # Zero max connections
                current_connections=0,
            ),
            Server(
                id=uuid.uuid4(),
                name="Normal Server",
                country_code="US",
                country_name="United States",
                agent_url="https://server2.example.com",
                agent_api_key="key2",
                supports_wireguard=True,
                status="online",
                max_connections=1000,
                current_connections=100,  # 10% load
            ),
        ]
        service.get_available_servers = AsyncMock(return_value=servers_with_zero_max)

        # Act
        result = await service.get_servers_for_user(protocol="wireguard")

        # Assert - should not raise division by zero error
        assert len(result) == 2
        # Zero max connections results in 0 load (0 / max(0, 1) = 0)
        assert result[0].name == "Zero Max Server"  # 0% load
        assert result[1].name == "Normal Server"  # 10% load

    @pytest.mark.asyncio
    async def test_sorting_stability_same_load(self, service):
        """Test sorting behavior when servers have same load."""
        # Arrange
        servers_same_load = [
            Server(
                id=uuid.uuid4(),
                name="Server A",
                country_code="US",
                country_name="United States",
                agent_url="https://server1.example.com",
                agent_api_key="key1",
                supports_wireguard=True,
                status="online",
                max_connections=1000,
                current_connections=500,  # 50% load
            ),
            Server(
                id=uuid.uuid4(),
                name="Server B",
                country_code="US",
                country_name="United States",
                agent_url="https://server2.example.com",
                agent_api_key="key2",
                supports_wireguard=True,
                status="online",
                max_connections=1000,
                current_connections=500,  # 50% load
            ),
        ]
        service.get_available_servers = AsyncMock(return_value=servers_same_load)

        # Act
        result = await service.get_servers_for_user(protocol="wireguard")

        # Assert - both servers should be returned
        assert len(result) == 2
        assert all(s.current_connections / s.max_connections == 0.5 for s in result)

    @pytest.mark.asyncio
    async def test_limit_zero_returns_empty(self, service, sample_servers):
        """Test that limit=0 returns empty list."""
        # Arrange
        service.get_available_servers = AsyncMock(return_value=sample_servers)

        # Act
        result = await service.get_servers_for_user(protocol="wireguard", limit=0)

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_returns_all_servers_when_no_protocol_filter_matches_all(
        self, service, sample_servers
    ):
        """Test returning all servers when they all support the protocol."""
        # Arrange - all servers support wireguard
        all_wireguard_servers = [
            Server(
                id=uuid.uuid4(),
                name=f"Server {i}",
                country_code="US",
                country_name="United States",
                agent_url=f"https://server{i}.example.com",
                agent_api_key=f"key{i}",
                supports_wireguard=True,
                status="online",
                max_connections=1000,
                current_connections=i * 100,
            )
            for i in range(5)
        ]
        service.get_available_servers = AsyncMock(return_value=all_wireguard_servers)

        # Act
        result = await service.get_servers_for_user(protocol="wireguard")

        # Assert
        assert len(result) == 5
