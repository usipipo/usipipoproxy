"""Integration tests for show_keys_by_type with server status summary."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.bot.handlers.keys import KeysHandler


class TestShowKeysByTypeWithServerStatus:
    """Tests for show_keys_by_type handler with server status footer."""

    @pytest.fixture
    def mock_api_client(self):
        return AsyncMock()

    @pytest.fixture
    def mock_token_storage(self):
        storage = AsyncMock()
        storage.get.return_value = {"access_token": "test-token"}
        storage.is_authenticated.return_value = True
        return storage

    @pytest.fixture
    def handler(self, mock_api_client, mock_token_storage):
        return KeysHandler(mock_api_client, mock_token_storage)

    @pytest.fixture
    def mock_update(self):
        update = MagicMock()
        update.callback_query = MagicMock()
        update.callback_query.data = "vpn_keys_wireguard"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        update.effective_user = MagicMock()
        update.effective_user.id = 12345
        return update

    @pytest.fixture
    def mock_context(self):
        return MagicMock()

    async def test_show_keys_by_type_includes_server_status_footer(
        self, handler, mock_update, mock_context, mock_api_client
    ):
        """Test that key list includes server status summary at bottom."""
        mock_api_client.get.side_effect = lambda url, **kwargs: {
            "/vpn/keys": [
                {
                    "id": "key-1",
                    "name": "pigpong",
                    "key_type": "wireguard",
                    "status": "active",
                    "data_used_gb": 0.0,
                    "data_limit_gb": 5.0,
                    "server_id": "server-uuid-456",
                }
            ],
            "/vpn/servers/server-uuid-456/outline": {
                "server_status": "online",
                "active_keys_count": 27,
                "outline_api_reachable": True,
            },
        }.get(url, [])

        await handler.show_keys_by_type(mock_update, mock_context)

        call_args = mock_update.callback_query.edit_message_text.call_args
        message = call_args.kwargs.get("text", "")

        assert "🌐 Servidor:" in message
        assert "🟢 Online" in message
        assert "27" in message

    async def test_show_keys_by_type_shows_warning_for_high_usage(
        self, handler, mock_update, mock_context, mock_api_client
    ):
        """Test that keys with >80% usage show ⚠️ warning emoji."""
        mock_api_client.get.side_effect = lambda url, **kwargs: {
            "/vpn/keys": [
                {
                    "id": "key-1",
                    "name": "Almost Full",
                    "key_type": "wireguard",
                    "status": "active",
                    "data_used_gb": 4.9,
                    "data_limit_gb": 5.0,
                    "server_id": "server-uuid-456",
                }
            ],
            "/vpn/servers/server-uuid-456/outline": {
                "server_status": "online",
                "active_keys_count": 27,
                "outline_api_reachable": True,
            },
        }.get(url, [])

        await handler.show_keys_by_type(mock_update, mock_context)

        call_args = mock_update.callback_query.edit_message_text.call_args
        message = call_args.kwargs.get("text", "")

        assert "⚠️" in message
        assert "Almost Full" in message

    async def test_show_keys_by_type_handles_offline_server(
        self, handler, mock_update, mock_context, mock_api_client
    ):
        """Test display when server is offline."""
        mock_api_client.get.side_effect = lambda url, **kwargs: {
            "/vpn/keys": [
                {
                    "id": "key-1",
                    "name": "Test Key",
                    "key_type": "wireguard",
                    "status": "active",
                    "data_used_gb": 1.0,
                    "data_limit_gb": 5.0,
                    "server_id": "server-uuid-456",
                }
            ],
            "/vpn/servers/server-uuid-456/outline": {
                "server_status": "offline",
                "active_keys_count": 0,
                "outline_api_reachable": False,
            },
        }.get(url, [])

        await handler.show_keys_by_type(mock_update, mock_context)

        call_args = mock_update.callback_query.edit_message_text.call_args
        message = call_args.kwargs.get("text", "")

        assert "🔴 Offline" in message

    async def test_show_keys_by_type_handles_metrics_fetch_failure(
        self, handler, mock_update, mock_context, mock_api_client
    ):
        """Test graceful handling when metrics fetch fails."""
        mock_api_client.get.side_effect = lambda url, **kwargs: (
            {
                "/vpn/keys": [
                    {
                        "id": "key-1",
                        "name": "Test Key",
                        "key_type": "wireguard",
                        "status": "active",
                        "data_used_gb": 1.0,
                        "data_limit_gb": 5.0,
                        "server_id": "server-uuid-456",
                    }
                ],
            }.get(url, {})
            or (_ for _ in ()).throw(Exception("API Error"))
        )

        await handler.show_keys_by_type(mock_update, mock_context)

        call_args = mock_update.callback_query.edit_message_text.call_args
        message = call_args.kwargs.get("text", "")

        # Message should still display keys without server footer
        assert "🔑 *Test Key*" in message

    async def test_show_keys_by_type_no_server_id_skips_metrics(
        self, handler, mock_update, mock_context, mock_api_client
    ):
        """Test that keys without server_id skip metrics fetch."""
        mock_api_client.get.return_value = [
            {
                "id": "key-1",
                "name": "Test Key",
                "key_type": "wireguard",
                "status": "active",
                "data_used_gb": 1.0,
                "data_limit_gb": 5.0,
                "server_id": None,
            }
        ]

        await handler.show_keys_by_type(mock_update, mock_context)

        calls = [call[0][0] for call in mock_api_client.get.call_args_list]
        assert "/vpn/servers/" not in " ".join(calls)

        call_args = mock_update.callback_query.edit_message_text.call_args
        message = call_args.kwargs.get("text", "")
        assert "🔑 *Test Key*" in message
