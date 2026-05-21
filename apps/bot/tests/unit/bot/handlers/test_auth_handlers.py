"""Tests for Auth Handler with referral code support."""

import pytest
from unittest.mock import AsyncMock, MagicMock


class TestAuthHandlerWithReferral:
    """Tests for auth handler with referral code extraction."""

    @pytest.mark.asyncio
    async def test_start_with_referral_code(self):
        """start_handler extracts referral code from context.args."""
        from src.bot.handlers.auth import AuthHandler

        mock_api = AsyncMock()
        mock_tokens = AsyncMock()
        mock_tokens.is_authenticated.return_value = False
        mock_tokens.needs_refresh.return_value = False

        # Mock auto-register response
        mock_api.post.side_effect = [
            {
                "access_token": "test_token",
                "refresh_token": "test_refresh",
                "user_id": "test-user-id",
            },
            {"success": True, "credits_earned": 50},  # Referral response
        ]

        handler = AuthHandler(mock_api, mock_tokens)

        # Create mock update with context.args containing referral code
        mock_update = MagicMock()
        mock_update.effective_user.id = 12345
        mock_update.effective_user.username = "testuser"
        mock_update.effective_user.first_name = "Test"
        mock_update.effective_user.last_name = "User"
        mock_update.message = MagicMock()
        mock_update.message.reply_text = AsyncMock()

        mock_context = MagicMock()
        mock_context.args = ["ref_abc123def456"]

        await handler.start_handler(mock_update, mock_context)

        # Verify auto-register was called first
        assert mock_api.post.call_count == 2
        first_call = mock_api.post.call_args_list[0]
        assert first_call[0][0] == "/auth/telegram/auto-register"
        assert first_call[0][1]["telegram_id"] == 12345
        assert first_call[0][1]["username"] == "testuser"
        assert first_call[0][1]["first_name"] == "Test"
        assert first_call[0][1]["last_name"] == "User"

        # Verify referral endpoint was called second with user_id (UUID)
        second_call = mock_api.post.call_args_list[1]
        assert second_call[0][0] == "/referrals/apply-on-register"
        assert second_call[0][1]["user_id"] == "test-user-id"
        assert second_call[0][1]["referral_code"] == "ref_abc123def456"

    @pytest.mark.asyncio
    async def test_start_without_referral_code(self):
        """start_handler works without referral code."""
        from src.bot.handlers.auth import AuthHandler

        mock_api = AsyncMock()
        mock_tokens = AsyncMock()
        mock_tokens.is_authenticated.return_value = False

        mock_api.post.return_value = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "user_id": "test-user-id",
        }

        handler = AuthHandler(mock_api, mock_tokens)

        mock_update = MagicMock()
        mock_update.effective_user.id = 12345
        mock_update.effective_user.username = None
        mock_update.effective_user.first_name = "Test"
        mock_update.effective_user.last_name = None
        mock_update.message = MagicMock()
        mock_update.message.reply_text = AsyncMock()

        mock_context = MagicMock()
        mock_context.args = []  # No referral code

        await handler.start_handler(mock_update, mock_context)

        # Should still register without referral
        mock_api.post.assert_called()

    @pytest.mark.asyncio
    async def test_start_already_authenticated(self):
        """start_handler shows welcome for authenticated users."""
        from src.bot.handlers.auth import AuthHandler

        mock_api = AsyncMock()
        mock_tokens = AsyncMock()
        mock_tokens.is_authenticated.return_value = True

        handler = AuthHandler(mock_api, mock_tokens)

        mock_update = MagicMock()
        mock_update.effective_user.id = 12345
        mock_update.message = MagicMock()
        mock_update.message.reply_text = AsyncMock()

        mock_context = MagicMock()
        mock_context.args = ["ref_abc123"]  # Even with referral code

        await handler.start_handler(mock_update, mock_context)

        # Should NOT call auto-register
        mock_api.post.assert_not_called()
        # Should show welcome message
        mock_update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_apply_referral_code_retries_on_failure(self):
        """Test that _apply_referral_code retries once on failure."""
        from src.bot.handlers.auth import AuthHandler

        mock_api = AsyncMock()
        mock_tokens = AsyncMock()
        handler = AuthHandler(mock_api, mock_tokens)

        # First call fails, second succeeds
        mock_api.post.side_effect = [
            Exception("Connection timeout"),
            {"success": True, "credits_earned": 50},
        ]

        result = await handler._apply_referral_code("user-123", "ref_abc")

        assert result is True
        assert mock_api.post.call_count == 2
        assert mock_api.post.call_args_list[0][0][0] == "/referrals/apply-on-register"

    @pytest.mark.asyncio
    async def test_apply_referral_code_returns_false_after_retry_exhausted(self):
        """Test that _apply_referral_code returns False after all retries fail."""
        from src.bot.handlers.auth import AuthHandler

        mock_api = AsyncMock()
        mock_tokens = AsyncMock()
        handler = AuthHandler(mock_api, mock_tokens)

        mock_api.post.side_effect = Exception("Connection timeout")

        result = await handler._apply_referral_code("user-123", "ref_abc")

        assert result is False
        assert mock_api.post.call_count == 2
