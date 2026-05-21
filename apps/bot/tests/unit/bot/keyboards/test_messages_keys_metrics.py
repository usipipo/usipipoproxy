"""Tests for VPN key message templates with server metrics."""

from src.bot.keyboards.messages_keys import KeysMessages


class TestKeyDetailsTemplate:
    """Tests for KEY_DETAILS template with server metrics section."""

    def test_key_details_template_has_all_placeholders(self):
        """Test KEY_DETAILS includes all required placeholders."""
        template = KeysMessages.KEY_DETAILS

        # Verify all placeholders are present
        required_placeholders = [
            "{name}",
            "{type}",
            "{server}",
            "{usage_bar}",
            "{usage}",
            "{limit}",
            "{percentage}",
            "{status_icon}",
            "{status}",
            "{expires}",
            "{last_seen}",
            "{server_status_line}",
            "{server_bandwidth}",
            "{server_uptime}",
        ]

        for placeholder in required_placeholders:
            assert placeholder in template, f"Missing placeholder: {placeholder}"

    def test_key_details_template_has_server_metrics_section(self):
        """Test KEY_DETAILS includes server metrics section header."""
        assert "🌐 Estado del Servidor" in KeysMessages.KEY_DETAILS

    def test_key_details_template_has_separator_lines(self):
        """Test KEY_DETAILS has visual separator lines."""
        assert "━" * 13 in KeysMessages.KEY_DETAILS

    def test_key_details_template_formatting(self):
        """Test KEY_DETAILS can be formatted with valid data."""
        message = KeysMessages.KEY_DETAILS.format(
            name="Test Key",
            type="WIREGUARD",
            server="USA East 1",
            usage_bar="░" * 20 + " 0%",
            usage="0.0",
            limit="5.0",
            percentage="0",
            status="Activa",
            status_icon="🟢",
            expires="2026-05-04",
            last_seen="Hace 2 horas",
            server_status_line="🟢 Online • 27 claves activas",
            server_bandwidth="18.9 GB",
            server_uptime="99%+ uptime (30 días)",
        )

        # Verify key sections (Markdown formatting adds asterisks)
        assert "💎 *Test Key*" in message
        assert "📡 WIREGUARD" in message
        assert "🖥️ USA East 1" in message
        assert "🌐 Estado del Servidor" in message
        assert "🟢 Online • 27 claves activas" in message
        assert "18.9 GB" in message
        assert "⚡ *Acciones:*" in message


class TestServerMetricsConstants:
    """Tests for server metrics message constants."""

    def test_server_metrics_online_constant(self):
        """Test SERVER_METRICS_ONLINE has active_keys placeholder."""
        assert "{active_keys}" in KeysMessages.SERVER_METRICS_ONLINE
        assert "🟢 Online" in KeysMessages.SERVER_METRICS_ONLINE

    def test_server_metrics_offline_constant(self):
        """Test SERVER_METRICS_OFFLINE constant exists."""
        assert "🔴 Offline" in KeysMessages.SERVER_METRICS_OFFLINE

    def test_server_metrics_unavailable_constant(self):
        """Test SERVER_METRICS_UNAVAILABLE constant exists."""
        assert "📡" in KeysMessages.SERVER_METRICS_UNAVAILABLE

    def test_server_uptime_good_constant(self):
        """Test SERVER_UPTIME_GOOD constant exists."""
        assert "99%" in KeysMessages.SERVER_UPTIME_GOOD

    def test_server_uptime_unknown_constant(self):
        """Test SERVER_UPTIME_UNKNOWN constant exists."""
        assert (
            "desconocido" in KeysMessages.SERVER_UPTIME_UNKNOWN.lower()
            or "N/A" in KeysMessages.SERVER_UPTIME_UNKNOWN
        )

    def test_server_metrics_online_formatting(self):
        """Test SERVER_METRICS_ONLINE can be formatted."""
        message = KeysMessages.SERVER_METRICS_ONLINE.format(active_keys=27)
        assert "27" in message
        assert "claves activas" in message


class TestKeysListHeader:
    """Tests for KEYS_LIST_HEADER template."""

    def test_keys_list_header_has_type_placeholder(self):
        """Test KEYS_LIST_HEADER includes {type} placeholder."""
        assert "{type}" in KeysMessages.KEYS_LIST_HEADER

    def test_keys_list_header_formatting(self):
        """Test KEYS_LIST_HEADER can be formatted."""
        message = KeysMessages.KEYS_LIST_HEADER.format(type="WIREGUARD")
        assert "WIREGUARD" in message
