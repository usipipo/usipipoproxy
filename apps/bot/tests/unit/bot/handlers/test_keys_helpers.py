"""Tests for KeysHandler helper methods."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest

from src.bot.handlers.keys import KeysHandler


class TestFormatLastSeen:
    """Tests for _format_last_seen helper."""

    @pytest.fixture
    def handler(self):
        """Create KeysHandler instance (mock dependencies)."""
        api_client = AsyncMock()
        token_storage = AsyncMock()
        return KeysHandler(api_client, token_storage)

    async def test_recent_last_seen(self, handler):
        """Test 'Hace X minutos' format."""
        now = datetime(2026, 4, 4, 12, 0, 0, tzinfo=timezone.utc)
        five_min_ago = now - timedelta(minutes=5)

        result = handler._format_last_seen(five_min_ago, now)
        assert result == "Hace 5 minutos"

    async def test_single_minute(self, handler):
        """Test 'Hace 1 minuto' (singular)."""
        now = datetime(2026, 4, 4, 12, 0, 0, tzinfo=timezone.utc)
        one_min_ago = now - timedelta(minutes=1)

        result = handler._format_last_seen(one_min_ago, now)
        assert result == "Hace 1 minuto"

    async def test_hours_ago_last_seen(self, handler):
        """Test hours format."""
        now = datetime(2026, 4, 4, 12, 0, 0, tzinfo=timezone.utc)
        two_hours_ago = now - timedelta(hours=2)

        result = handler._format_last_seen(two_hours_ago, now)
        assert result == "Hace 2 horas"

    async def test_single_hour(self, handler):
        """Test 'Hace 1 hora' (singular)."""
        now = datetime(2026, 4, 4, 12, 0, 0, tzinfo=timezone.utc)
        one_hour_ago = now - timedelta(hours=1)

        result = handler._format_last_seen(one_hour_ago, now)
        assert result == "Hace 1 hora"

    async def test_days_ago_last_seen(self, handler):
        """Test days format."""
        now = datetime(2026, 4, 4, 12, 0, 0, tzinfo=timezone.utc)
        three_days_ago = now - timedelta(days=3)

        result = handler._format_last_seen(three_days_ago, now)
        assert result == "Hace 3 días"

    async def test_single_day(self, handler):
        """Test 'Hace 1 día' (singular)."""
        now = datetime(2026, 4, 4, 12, 0, 0, tzinfo=timezone.utc)
        one_day_ago = now - timedelta(days=1)

        result = handler._format_last_seen(one_day_ago, now)
        assert result == "Hace 1 día"

    async def test_none_last_seen(self, handler):
        """Test None returns 'Nunca'."""
        now = datetime(2026, 4, 4, 12, 0, 0, tzinfo=timezone.utc)
        result = handler._format_last_seen(None, now)
        assert result == "Nunca"

    async def test_future_date(self, handler):
        """Test future date shows date string."""
        now = datetime(2026, 4, 4, 12, 0, 0, tzinfo=timezone.utc)
        future = now + timedelta(hours=1)
        result = handler._format_last_seen(future, now)
        assert "2026-04-04" in result


class TestFormatBytes:
    """Tests for _format_bytes helper."""

    @pytest.fixture
    def handler(self):
        api_client = AsyncMock()
        token_storage = AsyncMock()
        return KeysHandler(api_client, token_storage)

    async def test_bytes_to_gb(self, handler):
        """Test bytes to GB conversion."""
        result = handler._format_bytes(1073741824)  # 1 GB
        assert result == "1.0 GB"

    async def test_bytes_to_mb(self, handler):
        """Test bytes to MB conversion."""
        result = handler._format_bytes(524288000)  # ~500 MB
        assert "MB" in result

    async def test_zero_bytes(self, handler):
        """Test zero bytes."""
        result = handler._format_bytes(0)
        assert result == "0.0 B"

    async def test_large_bytes(self, handler):
        """Test large bytes (20 GB)."""
        result = handler._format_bytes(21474836480)  # 20 GB
        assert "20.0 GB" in result


class TestFetchServerMetrics:
    """Tests for _fetch_server_metrics helper."""

    @pytest.fixture
    def handler(self):
        api_client = AsyncMock()
        token_storage = AsyncMock()
        return KeysHandler(api_client, token_storage)

    async def test_successful_metrics_fetch(self, handler):
        """Test successful API call to outline endpoint."""
        mock_response = {
            "server_status": "online",
            "active_keys_count": 27,
            "total_bytes_transferred": 20347013889,
            "outline_api_reachable": True,
        }
        handler.api.get = AsyncMock(return_value=mock_response)
        handler.tokens.get = AsyncMock(return_value={"access_token": "test"})

        result = await handler._fetch_server_metrics(server_id="test-uuid", telegram_id=12345)

        assert result == mock_response
        handler.api.get.assert_called_once()

    async def test_metrics_fetch_failure_returns_none(self, handler):
        """Test that API errors return None gracefully."""
        handler.api.get = AsyncMock(side_effect=Exception("API error"))

        result = await handler._fetch_server_metrics(server_id="test-uuid", telegram_id=12345)

        assert result is None

    async def test_metrics_fetch_no_tokens_returns_none(self, handler):
        """Test that missing tokens returns None."""
        handler.tokens.get = AsyncMock(return_value=None)

        result = await handler._fetch_server_metrics(server_id="test-uuid", telegram_id=12345)

        assert result is None
