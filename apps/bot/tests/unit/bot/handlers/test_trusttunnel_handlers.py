"""Tests para TrustTunnel handlers."""
import pytest
from unittest.mock import patch, AsyncMock


class TestTrustTunnelHandler:
    """Tests para TrustTunnelHandler."""

    @pytest.mark.asyncio
    async def test_handler_initialization(self):
        """TrustTunnelHandler se inicializa correctamente."""
        with patch("src.bot.handlers.trusttunnel.APIClient"), \
             patch("src.bot.handlers.trusttunnel.TokenStorage"):
            from src.bot.handlers.trusttunnel import TrustTunnelHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = TrustTunnelHandler(mock_api, mock_storage)

            assert handler.api == mock_api
            assert handler.tokens == mock_storage

    @pytest.mark.asyncio
    async def test_fetch_trusttunnel_metrics_success(self):
        """_fetch_trusttunnel_metrics retorna datos correctamente."""
        with patch("src.bot.handlers.trusttunnel.APIClient"), \
             patch("src.bot.handlers.trusttunnel.TokenStorage"):
            from src.bot.handlers.trusttunnel import TrustTunnelHandler

            mock_api = AsyncMock()
            mock_api.get.return_value = {
                "active_clients": 5,
                "total_bytes_transferred": 1073741824,
                "client_bytes": {"user-a": 524288000, "user-b": 268435456},
            }
            mock_storage = AsyncMock()
            mock_storage.get.return_value = {"access_token": "test-token"}

            handler = TrustTunnelHandler(mock_api, mock_storage)
            result = await handler._fetch_trusttunnel_metrics("server-uuid", 123)

            assert result is not None
            assert result["active_clients"] == 5
            assert result["total_bytes_transferred"] == 1073741824

    @pytest.mark.asyncio
    async def test_fetch_trusttunnel_metrics_unauthenticated(self):
        """_fetch_trusttunnel_metrics retorna None si no autenticado."""
        with patch("src.bot.handlers.trusttunnel.APIClient"), \
             patch("src.bot.handlers.trusttunnel.TokenStorage"):
            from src.bot.handlers.trusttunnel import TrustTunnelHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.get.return_value = None

            handler = TrustTunnelHandler(mock_api, mock_storage)
            result = await handler._fetch_trusttunnel_metrics("server-uuid", 123)

            assert result is None

    @pytest.mark.asyncio
    async def test_format_bytes_zero(self):
        """_format_bytes con 0 bytes."""
        with patch("src.bot.handlers.trusttunnel.APIClient"), \
             patch("src.bot.handlers.trusttunnel.TokenStorage"):
            from src.bot.handlers.trusttunnel import TrustTunnelHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = TrustTunnelHandler(mock_api, mock_storage)
            result = handler._format_bytes(0)

            assert result == "0.0 B"

    @pytest.mark.asyncio
    async def test_format_bytes_gb(self):
        """_format_bytes con GB."""
        with patch("src.bot.handlers.trusttunnel.APIClient"), \
             patch("src.bot.handlers.trusttunnel.TokenStorage"):
            from src.bot.handlers.trusttunnel import TrustTunnelHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = TrustTunnelHandler(mock_api, mock_storage)
            result = handler._format_bytes(1073741824)

            assert result == "1.0 GB"

    @pytest.mark.asyncio
    async def test_format_top_clients_empty(self):
        """_format_top_clients con dict vacío."""
        with patch("src.bot.handlers.trusttunnel.APIClient"), \
             patch("src.bot.handlers.trusttunnel.TokenStorage"):
            from src.bot.handlers.trusttunnel import TrustTunnelHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = TrustTunnelHandler(mock_api, mock_storage)
            result = handler._format_top_clients({})

            assert "Sin datos" in result

    @pytest.mark.asyncio
    async def test_format_top_clients_top5(self):
        """_format_top_clients retorna top 5 ordenado."""
        with patch("src.bot.handlers.trusttunnel.APIClient"), \
             patch("src.bot.handlers.trusttunnel.TokenStorage"):
            from src.bot.handlers.trusttunnel import TrustTunnelHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = TrustTunnelHandler(mock_api, mock_storage)
            client_bytes = {
                "a": 100, "b": 200, "c": 300, "d": 400, "e": 500, "f": 600, "g": 700,
            }
            result = handler._format_top_clients(client_bytes)

            lines = result.strip().split("\n")
            assert len(lines) == 5  # Top 5 only
            assert "1. g" in lines[0]  # Highest first

    def test_get_trusttunnel_handlers_returns_list(self):
        """get_trusttunnel_handlers retorna una lista vacía."""
        from src.bot.handlers.trusttunnel import get_trusttunnel_handlers
        from unittest.mock import AsyncMock

        mock_api = AsyncMock()
        mock_storage = AsyncMock()

        handlers = get_trusttunnel_handlers(mock_api, mock_storage)

        assert isinstance(handlers, list)
        assert len(handlers) == 0

    def test_get_trusttunnel_callback_handlers_returns_list(self):
        """get_trusttunnel_callback_handlers retorna una lista."""
        with patch("src.bot.handlers.trusttunnel.APIClient"), \
             patch("src.bot.handlers.trusttunnel.TokenStorage"):
            from src.bot.handlers.trusttunnel import get_trusttunnel_callback_handlers

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handlers = get_trusttunnel_callback_handlers(mock_api, mock_storage)

            assert isinstance(handlers, list)
            assert len(handlers) > 0
