"""Tests for /users/me route."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from usipipo_commons.domain.entities.user import User

from src.infrastructure.api.v1.routes.users import get_current_user_profile


@pytest.fixture
def base_user():
    return User(
        id=uuid.uuid4(),
        telegram_id=12345,
        username="testuser",
        first_name="Test",
        last_name="User",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="ref_abc123",
        referred_by=None,
        referral_credits=50,
        purchase_count=0,
        loyalty_bonus_percent=0,
        welcome_bonus_used=False,
    )


@pytest.mark.asyncio
async def test_get_me_returns_total_referrals(base_user):
    """GET /users/me should include total_referrals count."""
    mock_referral_service = AsyncMock()
    mock_referral_service.get_referral_stats.return_value = {
        "total_referrals": 3,
        "referral_credits": 300,
        "referral_code": "ref_abc123",
        "referred_by": None,
    }

    result = await get_current_user_profile(
        current_user=base_user,
        referral_service=mock_referral_service,
    )

    assert "total_referrals" in result
    assert result["total_referrals"] == 3


@pytest.mark.asyncio
async def test_get_me_total_referrals_fallback_on_error(base_user):
    """GET /users/me should fallback to 0 if referral service fails."""
    mock_referral_service = AsyncMock()
    mock_referral_service.get_referral_stats.side_effect = Exception("DB error")

    result = await get_current_user_profile(
        current_user=base_user,
        referral_service=mock_referral_service,
    )

    assert result["total_referrals"] == 0


@pytest.mark.asyncio
async def test_get_me_returns_all_expected_fields(base_user):
    """GET /users/me should return all expected user fields."""
    mock_referral_service = AsyncMock()
    mock_referral_service.get_referral_stats.return_value = {
        "total_referrals": 0,
        "referral_credits": 0,
        "referral_code": "ref_abc123",
        "referred_by": None,
    }

    result = await get_current_user_profile(
        current_user=base_user,
        referral_service=mock_referral_service,
    )

    assert result["username"] == "testuser"
    assert result["first_name"] == "Test"
    assert result["last_name"] == "User"
    assert result["telegram_id"] == 12345
    assert result["balance_gb"] == 5.0
    assert result["referral_code"] == "ref_abc123"
    assert result["referral_credits"] == 50
    assert result["total_referrals"] == 0
