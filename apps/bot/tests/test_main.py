"""Tests for Telegram bot handlers."""

import pytest

from src.main import create_application, help_command, start, status


@pytest.fixture
def app():
    """Create test application."""
    return create_application(token="test-token")


def test_create_application():
    """Test application creation."""
    app = create_application(token="test-token")
    assert app is not None


def test_start_command_exists():
    """Test /start command handler exists."""
    assert start is not None


def test_help_command_exists():
    """Test /help command handler exists."""
    assert help_command is not None


def test_status_command_exists():
    """Test /status command handler exists."""
    assert status is not None
