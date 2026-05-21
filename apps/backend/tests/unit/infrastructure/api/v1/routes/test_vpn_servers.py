"""Integration tests for VPN servers endpoint."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import AsyncClient
from usipipo_commons.domain.entities.server import Server


@pytest.mark.asyncio
async def test_get_servers_requires_auth(client: AsyncClient):
    """Test that getting servers requires authentication."""
    response = await client.get("/api/v1/vpn/servers?protocol=wireguard")
    assert response.status_code == 401  # Not authenticated


@pytest.mark.asyncio
async def test_get_servers_invalid_protocol(client: AsyncClient, auth_headers: dict):
    """Test that invalid protocol returns 400 error."""
    response = await client.get(
        "/api/v1/vpn/servers?protocol=invalid",
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "Invalid protocol" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_servers_returns_empty_list(client: AsyncClient, auth_headers: dict):
    """Test getting servers when no servers are available."""
    from src.infrastructure.api.v1.routes.vpn import get_server_registry_service

    mock_service = AsyncMock()
    mock_service.get_servers_for_user = AsyncMock(return_value=[])

    # Override dependency
    from src.main import app

    app.dependency_overrides[get_server_registry_service] = lambda: mock_service

    try:
        response = await client.get(
            "/api/v1/vpn/servers?protocol=wireguard",
            headers=auth_headers,
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["servers"] == []
    assert data["recommended"] == []


@pytest.mark.asyncio
async def test_get_servers_returns_servers_list(client: AsyncClient, auth_headers: dict):
    """Test getting list of available servers."""
    from src.infrastructure.api.v1.routes.vpn import get_server_registry_service

    # Create test servers
    server1 = Server(
        id=uuid4(),
        name="USA East",
        country_code="US",
        country_name="United States",
        city="New York",
        status="online",
        max_connections=1000,
        current_connections=100,  # 10% load
    )
    server2 = Server(
        id=uuid4(),
        name="USA West",
        country_code="US",
        country_name="United States",
        city="Los Angeles",
        status="online",
        max_connections=1000,
        current_connections=500,  # 50% load
    )
    server3 = Server(
        id=uuid4(),
        name="UK London",
        country_code="GB",
        country_name="United Kingdom",
        city="London",
        status="online",
        max_connections=1000,
        current_connections=800,  # 80% load
    )

    mock_service = AsyncMock()
    mock_service.get_servers_for_user = AsyncMock(return_value=[server1, server2, server3])

    # Override dependency
    from src.main import app

    app.dependency_overrides[get_server_registry_service] = lambda: mock_service

    try:
        response = await client.get(
            "/api/v1/vpn/servers?protocol=wireguard",
            headers=auth_headers,
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()

    # Check servers list
    assert len(data["servers"]) == 3
    assert data["servers"][0]["name"] == "USA East"
    assert data["servers"][0]["country_code"] == "US"
    assert data["servers"][0]["country_name"] == "United States"
    assert data["servers"][0]["city"] == "New York"
    assert data["servers"][0]["load_percentage"] == 10
    assert data["servers"][0]["load_level"] == "low"
    assert data["servers"][0]["status"] == "online"

    # Check recommended servers (top 5 lowest load, but we only have 3)
    assert len(data["recommended"]) == 3
    # Should be sorted by load (lowest first)
    assert data["recommended"][0]["load_percentage"] == 10
    assert data["recommended"][1]["load_percentage"] == 50
    assert data["recommended"][2]["load_percentage"] == 80


@pytest.mark.asyncio
async def test_get_servers_filters_by_protocol_wireguard(client: AsyncClient, auth_headers: dict):
    """Test that servers are filtered by wireguard protocol."""
    from src.infrastructure.api.v1.routes.vpn import get_server_registry_service

    mock_service = AsyncMock()
    mock_service.get_servers_for_user = AsyncMock(return_value=[])

    # Override dependency
    from src.main import app

    app.dependency_overrides[get_server_registry_service] = lambda: mock_service

    try:
        await client.get(
            "/api/v1/vpn/servers?protocol=wireguard",
            headers=auth_headers,
        )
    finally:
        app.dependency_overrides.clear()

    # Verify service was called with correct protocol
    mock_service.get_servers_for_user.assert_called_once_with("wireguard")


@pytest.mark.asyncio
async def test_get_servers_load_level_calculation(client: AsyncClient, auth_headers: dict):
    """Test load level calculation: low (0-50%), medium (51-80%), high (81-100%)."""
    from src.infrastructure.api.v1.routes.vpn import get_server_registry_service

    # Create servers with different load levels
    low_load_server = Server(
        id=uuid4(),
        name="Low Load Server",
        country_code="US",
        country_name="United States",
        city="New York",
        status="online",
        max_connections=1000,
        current_connections=500,  # 50% - should be "low"
    )

    medium_load_server = Server(
        id=uuid4(),
        name="Medium Load Server",
        country_code="US",
        country_name="United States",
        city="Chicago",
        status="online",
        max_connections=1000,
        current_connections=800,  # 80% - should be "medium"
    )

    high_load_server = Server(
        id=uuid4(),
        name="High Load Server",
        country_code="US",
        country_name="United States",
        city="Miami",
        status="online",
        max_connections=1000,
        current_connections=900,  # 90% - should be "high"
    )

    mock_service = AsyncMock()
    mock_service.get_servers_for_user = AsyncMock(
        return_value=[low_load_server, medium_load_server, high_load_server]
    )

    # Override dependency
    from src.main import app

    app.dependency_overrides[get_server_registry_service] = lambda: mock_service

    try:
        response = await client.get(
            "/api/v1/vpn/servers?protocol=wireguard",
            headers=auth_headers,
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()

    # Find servers by name and check load levels
    servers_by_name = {s["name"]: s for s in data["servers"]}

    assert servers_by_name["Low Load Server"]["load_percentage"] == 50
    assert servers_by_name["Low Load Server"]["load_level"] == "low"

    assert servers_by_name["Medium Load Server"]["load_percentage"] == 80
    assert servers_by_name["Medium Load Server"]["load_level"] == "medium"

    assert servers_by_name["High Load Server"]["load_percentage"] == 90
    assert servers_by_name["High Load Server"]["load_level"] == "high"


@pytest.mark.asyncio
async def test_get_servers_recommended_top_5(client: AsyncClient, auth_headers: dict):
    """Test that recommended servers returns top 5 lowest load."""
    from src.infrastructure.api.v1.routes.vpn import get_server_registry_service

    # Create 10 servers with different loads
    servers = []
    for i in range(10):
        server = Server(
            id=uuid4(),
            name=f"Server {i}",
            country_code="US",
            country_name="United States",
            city=f"City {i}",
            status="online",
            max_connections=1000,
            current_connections=i * 100,  # 0%, 10%, 20%, ..., 90%
        )
        servers.append(server)

    mock_service = AsyncMock()
    mock_service.get_servers_for_user = AsyncMock(return_value=servers)

    # Override dependency
    from src.main import app

    app.dependency_overrides[get_server_registry_service] = lambda: mock_service

    try:
        response = await client.get(
            "/api/v1/vpn/servers?protocol=wireguard",
            headers=auth_headers,
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()

    # All 10 servers should be in the list
    assert len(data["servers"]) == 10

    # Only top 5 lowest load should be in recommended
    assert len(data["recommended"]) == 5

    # Recommended should be sorted by load (lowest first)
    for i in range(len(data["recommended"]) - 1):
        assert (
            data["recommended"][i]["load_percentage"]
            <= data["recommended"][i + 1]["load_percentage"]
        )

    # First recommended should have 0% load, last should have 40% load
    assert data["recommended"][0]["load_percentage"] == 0
    assert data["recommended"][4]["load_percentage"] == 40


@pytest.mark.asyncio
async def test_get_servers_protocol_case_insensitive(client: AsyncClient, auth_headers: dict):
    """Test that protocol validation is case insensitive."""
    from src.infrastructure.api.v1.routes.vpn import get_server_registry_service

    mock_service = AsyncMock()
    mock_service.get_servers_for_user = AsyncMock(return_value=[])

    # Override dependency
    from src.main import app

    app.dependency_overrides[get_server_registry_service] = lambda: mock_service

    try:
        # Test uppercase
        response = await client.get(
            "/api/v1/vpn/servers?protocol=WIREGUARD",
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Test mixed case
        response = await client.get(
            "/api/v1/vpn/servers?protocol=WireGuard",
            headers=auth_headers,
        )
        assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_servers_with_null_city(client: AsyncClient, auth_headers: dict):
    """Test handling servers with null city."""
    from src.infrastructure.api.v1.routes.vpn import get_server_registry_service

    server = Server(
        id=uuid4(),
        name="Server Without City",
        country_code="DE",
        country_name="Germany",
        city=None,
        status="online",
        max_connections=1000,
        current_connections=200,
    )

    mock_service = AsyncMock()
    mock_service.get_servers_for_user = AsyncMock(return_value=[server])

    # Override dependency
    from src.main import app

    app.dependency_overrides[get_server_registry_service] = lambda: mock_service

    try:
        response = await client.get(
            "/api/v1/vpn/servers?protocol=wireguard",
            headers=auth_headers,
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert len(data["servers"]) == 1
    assert data["servers"][0]["city"] is None
