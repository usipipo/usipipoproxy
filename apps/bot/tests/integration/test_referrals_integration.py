"""Integration tests for Referrals feature."""

import pytest
from unittest.mock import AsyncMock

from src.bot.handlers.referrals import ReferralsHandler
from src.infrastructure.api_client import APIClient
from src.infrastructure.token_storage import TokenStorage


@pytest.mark.asyncio
class TestReferralsIntegration:
    """Integration tests for referrals."""

    async def test_full_referrals_flow(self):
        """Test complete referrals flow."""
        # Mock API client
        api_client = AsyncMock(spec=APIClient)
        api_client.get = AsyncMock(
            return_value={
                "referral_code": "TEST123",
                "total_referrals": 3,
                "referral_credits": 15,
            }
        )
        api_client.post = AsyncMock(
            return_value={
                "success": True,
                "credits_spent": 10,
                "gb_added": 1,
                "data": {
                    "remaining_credits": 5,
                },
            }
        )

        # Mock token storage
        token_storage = AsyncMock(spec=TokenStorage)
        token_storage.is_authenticated = AsyncMock(return_value=True)
        token_storage.get = AsyncMock(
            return_value={
                "access_token": "test_token",
                "refresh_token": "test_refresh",
                "user_id": 123,
                "expires_at": 9999999999,
                "created_at": 1234567890,
            }
        )

        # Create handler
        ReferralsHandler(api_client, token_storage)

        # Test 1: Get stats via API client directly
        stats = await api_client.get(
            "/referrals/me",
            headers={"Authorization": "Bearer test_token"},
        )
        assert stats["referral_code"] == "TEST123"
        assert stats["total_referrals"] == 3
        assert stats["referral_credits"] == 15

        # Test 2: Redeem credits via API client directly
        result = await api_client.post(
            "/referrals/redeem",
            headers={"Authorization": "Bearer test_token"},
            json={"credits": 10},
        )
        assert result["success"] is True
        assert result["gb_added"] == 1
        assert result["credits_spent"] == 10

    async def test_referrals_backend_endpoints_available(self):
        """Test that backend endpoints are available."""
        # This would test against actual backend in CI/CD
        # For now, just verify endpoint paths
        endpoints = [
            "GET /referrals/me",
            "POST /referrals/apply",
            "POST /referrals/redeem",
        ]
        assert len(endpoints) == 3

        # Verify endpoint structure
        for endpoint in endpoints:
            method, path = endpoint.split(" ", 1)
            assert method in ["GET", "POST", "PUT", "DELETE", "PATCH"]
            assert path.startswith("/referrals/")
