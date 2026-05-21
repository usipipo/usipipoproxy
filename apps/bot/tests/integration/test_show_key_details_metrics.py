"""Integration tests for show_key_details with server metrics."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.bot.handlers.keys import KeysHandler


class TestShowKeyDetailsWithMetrics:
    """Tests for show_key_details handler with server metrics integration."""

    @pytest.fixture
    def mock_api_client(self):
        """Create mock API client."""
        return AsyncMock()

    @pytest.fixture
    def mock_token_storage(self):
        """Create mock token storage."""
        storage = AsyncMock()
        storage.get.return_value = {"access_token": "test-token"}
        storage.is_authenticated.return_value = True
        return storage

    @pytest.fixture
    def handler(self, mock_api_client, mock_token_storage):
        """Create KeysHandler with mocked dependencies."""
        return KeysHandler(mock_api_client, mock_token_storage)

    @pytest.fixture
    def mock_update(self):
        """Create mock update with callback query."""
        update = MagicMock()
        update.callback_query = MagicMock()
        update.callback_query.data = "vpn_key_details_key-123"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 12345
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        return MagicMock()

    async def test_show_key_details_fetches_server_metrics(
        self, handler, mock_update, mock_context, mock_api_client
    ):
        """Test that show_key_details fetches server metrics when server_id exists."""
        # Mock key data with server_id
        mock_api_client.get.side_effect = lambda url, **kwargs: {
            "/vpn/keys/key-123": {
                "id": "key-123",
                "name": "pigpong",
                "key_type": "wireguard",
                "status": "active",
                "data_used_gb": 0.0,
                "data_limit_gb": 5.0,
                "expires_at": "2026-05-04T00:00:00",
                "server": "USA East 1",
                "server_id": "server-uuid-456",
                "last_used_at": "2026-04-04T10:00:00",
            },
            "/vpn/servers/server-uuid-456/outline": {
                "server_status": "online",
                "active_keys_count": 27,
                "total_bytes_transferred": 20347013889,
                "outline_api_reachable": True,
            },
        }.get(url, {})

        await handler.show_key_details(mock_update, mock_context)

        # Verify server metrics endpoint was called
        calls = [call[0][0] for call in mock_api_client.get.call_args_list]
        assert "/vpn/servers/server-uuid-456/outline" in calls

    async def test_show_key_details_includes_server_metrics_in_message(
        self, handler, mock_update, mock_context, mock_api_client
    ):
        """Test that formatted message includes server metrics section."""
        mock_api_client.get.side_effect = lambda url, **kwargs: {
            "/vpn/keys/key-123": {
                "id": "key-123",
                "name": "pigpong",
                "key_type": "wireguard",
                "status": "active",
                "data_used_gb": 0.0,
                "data_limit_gb": 5.0,
                "expires_at": "2026-05-04T00:00:00",
                "server": "USA East 1",
                "server_id": "server-uuid-456",
                "last_used_at": "2026-04-04T10:00:00",
            },
            "/vpn/servers/server-uuid-456/outline": {
                "server_status": "online",
                "active_keys_count": 27,
                "total_bytes_transferred": 20347013889,
                "outline_api_reachable": True,
            },
        }.get(url, {})

        await handler.show_key_details(mock_update, mock_context)

        # Verify message includes server metrics
        call_args = mock_update.callback_query.edit_message_text.call_args
        message = call_args.kwargs.get("text", "")

        assert "🌐 Estado del Servidor" in message
        assert "🟢 Online" in message
        assert "27" in message  # active keys count
        assert "GB" in message  # bandwidth

    async def test_show_key_details_handles_missing_server_id(
        self, handler, mock_update, mock_context, mock_api_client
    ):
        """Test graceful handling when key has no server_id."""
        mock_api_client.get.return_value = {
            "id": "key-123",
            "name": "Test Key",
            "key_type": "outline",
            "status": "active",
            "data_used_gb": 1.5,
            "data_limit_gb": 5.0,
            "expires_at": "2026-05-04T00:00:00",
            "server": "N/A",
            "server_id": None,
            "last_used_at": None,
        }

        await handler.show_key_details(mock_update, mock_context)

        # Verify metrics endpoint was NOT called
        calls = [call[0][0] for call in mock_api_client.get.call_args_list]
        assert "/vpn/servers/" not in " ".join(calls)

        # Verify message still displays with fallback
        call_args = mock_update.callback_query.edit_message_text.call_args
        message = call_args.kwargs.get("text", "")
        assert "💎 *Test Key*" in message

    async def test_show_key_details_handles_metrics_fetch_failure(
        self, handler, mock_update, mock_context, mock_api_client
    ):
        """Test graceful handling when metrics fetch fails."""
        mock_api_client.get.side_effect = lambda url, **kwargs: (
            {
                "/vpn/keys/key-123": {
                    "id": "key-123",
                    "name": "pigpong",
                    "key_type": "wireguard",
                    "status": "active",
                    "data_used_gb": 0.0,
                    "data_limit_gb": 5.0,
                    "expires_at": "2026-05-04T00:00:00",
                    "server": "USA East 1",
                    "server_id": "server-uuid-456",
                    "last_used_at": "2026-04-04T10:00:00",
                },
            }.get(url, {})
            or (_ for _ in ()).throw(Exception("API Error"))
        )

        await handler.show_key_details(mock_update, mock_context)

        # Verify message still displays with fallback
        call_args = mock_update.callback_query.edit_message_text.call_args
        message = call_args.kwargs.get("text", "")
        assert "📡 Métricas no disponibles" in message or "N/A" in message

    async def test_show_key_details_handles_offline_server(
        self, handler, mock_update, mock_context, mock_api_client
    ):
        """Test display when server is offline."""
        mock_api_client.get.side_effect = lambda url, **kwargs: {
            "/vpn/keys/key-123": {
                "id": "key-123",
                "name": "pigpong",
                "key_type": "wireguard",
                "status": "active",
                "data_used_gb": 0.0,
                "data_limit_gb": 5.0,
                "expires_at": "2026-05-04T00:00:00",
                "server": "USA East 1",
                "server_id": "server-uuid-456",
                "last_used_at": "2026-04-04T10:00:00",
            },
            "/vpn/servers/server-uuid-456/outline": {
                "server_status": "offline",
                "active_keys_count": 0,
                "total_bytes_transferred": 0,
                "outline_api_reachable": False,
            },
        }.get(url, {})

        await handler.show_key_details(mock_update, mock_context)

        # Verify offline message
        call_args = mock_update.callback_query.edit_message_text.call_args
        message = call_args.kwargs.get("text", "")
        assert "🔴 Offline" in message
