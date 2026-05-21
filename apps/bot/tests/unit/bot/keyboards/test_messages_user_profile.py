"""Tests for UserProfileMessages."""

from datetime import datetime
from src.bot.keyboards.messages_user_profile import UserProfileMessages


class TestUserProfileMessages:
    """Tests for message formatting."""

    def test_format_personal_info_with_all_data(self):
        """Test formatting with complete user data."""
        result = UserProfileMessages.format_personal_info(
            username="testuser",
            first_name="Test",
            last_name="User",
            telegram_id=123456789,
        )

        assert "@testuser" in result
        assert "Test User" in result
        assert "`123456789`" in result

    def test_format_personal_info_with_missing_username(self):
        """Test formatting when username is None."""
        result = UserProfileMessages.format_personal_info(
            username=None,
            first_name="Test",
            last_name="User",
            telegram_id=123456789,
        )

        assert "No disponible" in result
        assert "Test User" in result

    def test_format_balance_info(self):
        """Test balance formatting."""
        result = UserProfileMessages.format_balance_info(
            balance_gb=15.5,
            total_purchased_gb=50.0,
            vpn_keys_count=3,
        )

        assert "15.50 GB" in result
        assert "50.00 GB" in result
        assert "3" in result

    def test_format_loyalty_info_gold_level(self):
        """Test loyalty level determination for Gold."""
        result = UserProfileMessages.format_loyalty_info(
            loyalty_bonus_percent=7,
            purchase_count=5,
            welcome_bonus_used=True,
        )

        assert "Gold" in result
        assert "7" in result
        assert "✅ Usado" in result

    def test_format_account_info(self):
        """Test account date formatting."""
        created = datetime(2024, 1, 15, 10, 30)
        updated = datetime(2025, 3, 28, 14, 45)

        result = UserProfileMessages.format_account_info(created, updated)

        assert "15 Jan 2024" in result
        assert "28 Mar 2025" in result
