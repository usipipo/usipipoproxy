"""Tests para formateadores."""
from datetime import datetime

from usipipo_commons.utils import (
    format_bytes,
    format_datetime,
    format_duration,
)


class TestFormatBytes:
    """Tests para format_bytes."""

    def test_format_bytes_gb(self):
        """Test formateo de GB."""
        assert format_bytes(5.0) == "5.00 GB"
        assert format_bytes(10.5) == "10.50 GB"
        assert format_bytes(999.99) == "999.99 GB"

    def test_format_bytes_tb(self):
        """Test formateo de TB."""
        assert format_bytes(1000.0) == "1.00 TB"
        assert format_bytes(1500.5) == "1.50 TB"


class TestFormatDatetime:
    """Tests para format_datetime."""

    def test_format_datetime(self):
        """Test formateo de datetime."""
        dt = datetime(2026, 3, 18, 12, 30, 45)
        result = format_datetime(dt)
        assert result == "2026-03-18 12:30:45 UTC"


class TestFormatDuration:
    """Tests para format_duration."""

    def test_format_duration_minutes(self):
        """Test formateo en minutos."""
        assert format_duration(60) == "1m"
        assert format_duration(300) == "5m"
        assert format_duration(3661) == "1h 1m"

    def test_format_duration_hours(self):
        """Test formateo en horas."""
        assert format_duration(3600) == "1h 0m"
        assert format_duration(7200) == "2h 0m"
        assert format_duration(7265) == "2h 1m"
