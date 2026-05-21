"""Tests for _generate_progress_bar helper method."""

import pytest
from unittest.mock import AsyncMock

from src.bot.handlers.keys import KeysHandler


class TestGenerateProgressBar:
    """Tests for _generate_progress_bar helper."""

    @pytest.fixture
    def handler(self):
        """Create KeysHandler instance."""
        api_client = AsyncMock()
        token_storage = AsyncMock()
        return KeysHandler(api_client, token_storage)

    async def test_progress_bar_zero_percent(self, handler):
        """Test 0% shows empty bar."""
        result = handler._generate_progress_bar(0)
        assert result == "░░░░░░░░░░░░░░░░░░░░ 0%"

    async def test_progress_bar_full(self, handler):
        """Test 100% shows filled bar."""
        result = handler._generate_progress_bar(100)
        assert result == "████████████████████ 100%"

    async def test_progress_bar_half(self, handler):
        """Test 50% shows half-filled bar."""
        result = handler._generate_progress_bar(50)
        assert result == "██████████░░░░░░░░░░ 50%"

    async def test_progress_bar_over_100_shows_100_percent_bar(self, handler):
        """Test >100% caps bar at 100% but shows actual percentage."""
        result = handler._generate_progress_bar(150)
        assert "150%" in result
        assert result.startswith("████████████████████")  # 20 filled blocks

    async def test_progress_bar_custom_width(self, handler):
        """Test custom width parameter."""
        result = handler._generate_progress_bar(50, width=10)
        assert result == "█████░░░░░ 50%"

    async def test_progress_bar_quarter(self, handler):
        """Test 25% shows quarter-filled bar."""
        result = handler._generate_progress_bar(25)
        expected_filled = 5  # 20 * 0.25 = 5
        expected_empty = 15
        assert result == "█" * expected_filled + "░" * expected_empty + " 25%"

    async def test_progress_bar_small_percentage(self, handler):
        """Test small percentage rounds correctly."""
        result = handler._generate_progress_bar(5)
        expected_filled = 1  # 20 * 0.05 = 1
        expected_empty = 19
        assert result == "█" * expected_filled + "░" * expected_empty + " 5%"

    async def test_progress_bar_uses_block_characters(self, handler):
        """Test progress bar uses █ and ░ characters."""
        result = handler._generate_progress_bar(50)
        assert "█" in result
        assert "░" in result
