"""Tests for VPN server response schemas."""

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError
from usipipo_commons.domain.enums.key_status import KeyStatus
from usipipo_commons.domain.enums.key_type import KeyType

from src.shared.schemas.vpn import (
    VpnKeyResponse,
    VpnServerResponse,
    VpnServersListResponse,
)

# ---------------------------------------------------------------------------
# VpnKeyResponse Tests
# ---------------------------------------------------------------------------


class TestVpnKeyResponse:
    """Tests for VpnKeyResponse schema."""

    def test_vpn_key_response_with_server_name(self):
        """Test VpnKeyResponse with server_name field populated."""
        data = {
            "id": uuid.uuid4(),
            "user_id": uuid.uuid4(),
            "server_id": uuid.uuid4(),
            "server_name": "USA East 1",
            "name": "test-key",
            "key_type": KeyType.WIREGUARD,
            "data_limit_gb": 5.0,
            "created_at": "2026-04-04T00:00:00",
        }
        response = VpnKeyResponse(**data)
        assert response.server_name == "USA East 1"
        assert response.server_id is not None

    def test_vpn_key_response_with_null_server_name(self):
        """Test VpnKeyResponse with server_name as None."""
        data = {
            "id": uuid.uuid4(),
            "user_id": uuid.uuid4(),
            "server_id": None,
            "name": "test-key",
            "key_type": KeyType.WIREGUARD,
            "data_limit_gb": 10.0,
            "created_at": "2026-04-04T00:00:00",
        }
        response = VpnKeyResponse(**data)
        assert response.server_name is None
        assert response.server_id is None

    def test_vpn_key_response_with_server_id_but_no_name(self):
        """Test VpnKeyResponse with server_id but server_name is None (server lookup failed)."""
        data = {
            "id": uuid.uuid4(),
            "user_id": uuid.uuid4(),
            "server_id": uuid.uuid4(),
            "server_name": None,
            "name": "orphan-key",
            "key_type": KeyType.WIREGUARD,
            "data_limit_gb": 3.0,
            "created_at": "2026-04-04T00:00:00",
        }
        response = VpnKeyResponse(**data)
        assert response.server_id is not None
        assert response.server_name is None

    def test_vpn_key_response_full_fields(self):
        """Test VpnKeyResponse with all fields populated."""
        now = datetime.now(UTC)
        data = {
            "id": uuid.uuid4(),
            "user_id": uuid.uuid4(),
            "server_id": uuid.uuid4(),
            "server_name": "Europe West",
            "name": "my-key",
            "key_type": KeyType.WIREGUARD,
            "status": KeyStatus.ACTIVE,
            "config": "[Interface]\nPrivateKey = test",
            "created_at": now,
            "expires_at": now,
            "last_used_at": now,
            "data_used_gb": 2.5,
            "data_limit_gb": 5.0,
        }
        response = VpnKeyResponse(**data)
        assert response.server_name == "Europe West"
        assert response.key_type == KeyType.WIREGUARD
        assert response.status == KeyStatus.ACTIVE
        assert response.data_used_gb == 2.5
        assert response.data_limit_gb == 5.0
        assert response.vpn_type == KeyType.WIREGUARD  # computed_field alias


def create_server_data(
    load_percentage: int = 50,
    status: str = "online",
    city: str | None = None,
) -> dict:
    """Helper to create valid server data."""
    return {
        "id": uuid.uuid4(),
        "name": "Test Server",
        "country_code": "US",
        "country_name": "United States",
        "city": city,
        "load_percentage": load_percentage,
        "status": status,
    }


class TestVpnServerResponse:
    """Tests for VpnServerResponse schema."""

    def test_valid_response_with_low_load(self):
        """Test valid response with low load level (0-50%)."""
        data = create_server_data(load_percentage=30)
        server = VpnServerResponse(**data)

        assert server.id is not None
        assert server.name == "Test Server"
        assert server.country_code == "US"
        assert server.country_name == "United States"
        assert server.load_percentage == 30
        assert server.status == "online"
        assert server.load_level == "low"

    def test_valid_response_with_medium_load(self):
        """Test valid response with medium load level (51-80%)."""
        data = create_server_data(load_percentage=65)
        server = VpnServerResponse(**data)

        assert server.load_percentage == 65
        assert server.load_level == "medium"

    def test_valid_response_with_high_load(self):
        """Test valid response with high load level (81-100%)."""
        data = create_server_data(load_percentage=90)
        server = VpnServerResponse(**data)

        assert server.load_percentage == 90
        assert server.load_level == "high"

    def test_boundary_condition_50_percent(self):
        """Test boundary: 50% should be 'low'."""
        data = create_server_data(load_percentage=50)
        server = VpnServerResponse(**data)

        assert server.load_percentage == 50
        assert server.load_level == "low"

    def test_boundary_condition_51_percent(self):
        """Test boundary: 51% should be 'medium'."""
        data = create_server_data(load_percentage=51)
        server = VpnServerResponse(**data)

        assert server.load_percentage == 51
        assert server.load_level == "medium"

    def test_boundary_condition_80_percent(self):
        """Test boundary: 80% should be 'medium'."""
        data = create_server_data(load_percentage=80)
        server = VpnServerResponse(**data)

        assert server.load_percentage == 80
        assert server.load_level == "medium"

    def test_boundary_condition_81_percent(self):
        """Test boundary: 81% should be 'high'."""
        data = create_server_data(load_percentage=81)
        server = VpnServerResponse(**data)

        assert server.load_percentage == 81
        assert server.load_level == "high"

    def test_boundary_condition_0_percent(self):
        """Test boundary: 0% should be 'low'."""
        data = create_server_data(load_percentage=0)
        server = VpnServerResponse(**data)

        assert server.load_percentage == 0
        assert server.load_level == "low"

    def test_boundary_condition_100_percent(self):
        """Test boundary: 100% should be 'high'."""
        data = create_server_data(load_percentage=100)
        server = VpnServerResponse(**data)

        assert server.load_percentage == 100
        assert server.load_level == "high"

    def test_optional_city_field(self):
        """Test that city field is optional."""
        data = create_server_data(city=None)
        server = VpnServerResponse(**data)

        assert server.city is None

    def test_with_city_value(self):
        """Test with city value provided."""
        data = create_server_data(city="New York")
        server = VpnServerResponse(**data)

        assert server.city == "New York"

    def test_different_status_values(self):
        """Test different status values."""
        for status in ["online", "offline", "maintenance"]:
            data = create_server_data(status=status)
            server = VpnServerResponse(**data)
            assert server.status == status

    def test_validation_error_load_below_zero(self):
        """Test validation error for load below 0."""
        data = create_server_data(load_percentage=-1)

        with pytest.raises(ValidationError) as exc_info:
            VpnServerResponse(**data)

        assert "load_percentage" in str(exc_info.value)
        assert (
            "ge=0" in str(exc_info.value).lower()
            or "greater than or equal to 0" in str(exc_info.value).lower()
        )

    def test_validation_error_load_above_100(self):
        """Test validation error for load above 100."""
        data = create_server_data(load_percentage=101)

        with pytest.raises(ValidationError) as exc_info:
            VpnServerResponse(**data)

        assert "load_percentage" in str(exc_info.value)
        assert (
            "le=100" in str(exc_info.value).lower()
            or "less than or equal to 100" in str(exc_info.value).lower()
        )

    def test_uuid_type_validation(self):
        """Test that id must be a valid UUID."""
        data = create_server_data()
        data["id"] = "not-a-uuid"

        with pytest.raises(ValidationError) as exc_info:
            VpnServerResponse(**data)

        assert "id" in str(exc_info.value)


class TestVpnServersListResponse:
    """Tests for VpnServersListResponse schema."""

    def test_valid_list_response(self):
        """Test valid list response with servers."""
        servers_data = [
            create_server_data(load_percentage=30),
            create_server_data(load_percentage=50),
            create_server_data(load_percentage=70),
        ]

        servers = [VpnServerResponse(**data) for data in servers_data]
        recommended = servers[:2]  # Top 2 lowest load

        response = VpnServersListResponse(servers=servers, recommended=recommended)

        assert len(response.servers) == 3
        assert len(response.recommended) == 2
        assert all(s.load_level in ["low", "medium"] for s in response.recommended)

    def test_empty_servers_list(self):
        """Test response with empty servers list."""
        response = VpnServersListResponse(servers=[], recommended=[])

        assert len(response.servers) == 0
        assert len(response.recommended) == 0

    def test_recommended_subset(self):
        """Test that recommended can be a subset of servers."""
        servers_data = [
            create_server_data(load_percentage=20),
            create_server_data(load_percentage=40),
            create_server_data(load_percentage=60),
            create_server_data(load_percentage=80),
            create_server_data(load_percentage=95),
        ]

        servers = [VpnServerResponse(**data) for data in servers_data]
        # Recommended: top 3 lowest load
        recommended = servers[:3]

        response = VpnServersListResponse(servers=servers, recommended=recommended)

        assert len(response.servers) == 5
        assert len(response.recommended) == 3
        assert all(s.load_percentage <= 60 for s in response.recommended)

    def test_recommended_sorted_by_load(self):
        """Test that recommended servers are sorted by load."""
        servers_data = [
            create_server_data(load_percentage=50),
            create_server_data(load_percentage=10),
            create_server_data(load_percentage=30),
        ]

        servers = [VpnServerResponse(**data) for data in servers_data]
        # Recommended should be sorted by load (lowest first)
        recommended = sorted(servers, key=lambda s: s.load_percentage)[:2]

        response = VpnServersListResponse(servers=servers, recommended=recommended)

        assert response.recommended[0].load_percentage == 10
        assert response.recommended[1].load_percentage == 30
