"""Tests for user profile handlers."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from telegram import Update, CallbackQuery, User
from src.bot.handlers.user_profile import UserProfileHandler


class TestUserProfileHandler:
    """Tests for UserProfileHandler."""

    @pytest.fixture
    def mock_api_client(self):
        """Mock API client."""
        client = AsyncMock()
        return client

    @pytest.fixture
    def mock_token_storage(self):
        """Mock token storage."""
        storage = AsyncMock()
        storage.is_authenticated = AsyncMock(return_value=True)
        storage.get = AsyncMock(return_value={"access_token": "test_token"})
        return storage

    @pytest.fixture
    def handler(self, mock_api_client, mock_token_storage):
        """Create handler with mocked dependencies."""
        return UserProfileHandler(mock_api_client, mock_token_storage)

    @pytest.mark.asyncio
    async def test_show_user_profile_authenticated(self, handler, mock_api_client):
        """Test showing profile for authenticated user."""
        # Mock user data
        mock_api_client.get = AsyncMock(
            return_value={
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
                "balance_gb": 15.5,
                "total_purchased_gb": 50.0,
                "referral_code": "ABC123",
                "referred_users_with_purchase": 5,
                "referral_credits": 2.5,
                "loyalty_bonus_percent": 7,
                "purchase_count": 8,
                "welcome_bonus_used": True,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2025-03-28T14:45:00",
            }
        )

        # Mock update
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.answer = AsyncMock()
        callback_query.edit_message_text = AsyncMock()
        callback_query.from_user = User(id=123456789, is_bot=False, first_name="Test")

        update = MagicMock(spec=Update)
        update.callback_query = callback_query
        update.effective_user = callback_query.from_user

        context = MagicMock()

        # Call handler
        await handler.show_user_profile(update, context)

        # Verify API was called
        mock_api_client.get.assert_called()
        # Verify message was edited
        callback_query.edit_message_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_show_user_profile_not_authenticated(self, handler, mock_token_storage):
        """Test showing profile for unauthenticated user."""
        mock_token_storage.is_authenticated = AsyncMock(return_value=False)

        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.answer = AsyncMock()
        callback_query.edit_message_text = AsyncMock()
        callback_query.from_user = User(id=123456789, is_bot=False, first_name="Test")

        update = MagicMock(spec=Update)
        update.callback_query = callback_query
        update.effective_user = callback_query.from_user

        context = MagicMock()

        await handler.show_user_profile(update, context)

        # Verify error message shown
        callback_query.edit_message_text.assert_called_once()
        call_args = callback_query.edit_message_text.call_args
        assert "No autenticado" in call_args[1]["text"]

    @pytest.mark.asyncio
    async def test_show_user_profile_uses_total_referrals(self, handler, mock_api_client):
        """Test that profile displays total_referrals, not referred_users_with_purchase."""
        mock_api_client.get = AsyncMock(
            side_effect=[
                {
                    "username": "testuser",
                    "first_name": "Test",
                    "last_name": "User",
                    "balance_gb": 5.0,
                    "total_purchased_gb": 0.0,
                    "referral_code": "ref_abc123",
                    "referral_credits": 50,
                    "total_referrals": 3,
                    "referred_users_with_purchase": 1,
                    "loyalty_bonus_percent": 0,
                    "purchase_count": 0,
                    "welcome_bonus_used": False,
                    "created_at": "2026-04-05T00:00:00",
                    "updated_at": "2026-04-05T00:00:00",
                },
                [],  # vpn_keys
            ]
        )

        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.answer = AsyncMock()
        callback_query.edit_message_text = AsyncMock()
        callback_query.from_user = User(id=123456789, is_bot=False, first_name="Test")

        update = MagicMock(spec=Update)
        update.callback_query = callback_query
        update.effective_user = callback_query.from_user

        context = MagicMock()

        await handler.show_user_profile(update, context)

        # Verify message contains total_referrals (3), not referred_users_with_purchase (1)
        edit_call = callback_query.edit_message_text.call_args
        message = edit_call[1]["text"]
        assert "3 usuarios" in message  # total_referrals
        assert "1 usuarios" not in message  # NOT referred_users_with_purchase
