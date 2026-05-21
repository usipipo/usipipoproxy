"""Tests para TrustTunnel messages."""


class TestTrustTunnelMessages:
    """Tests para TrustTunnelMessages."""

    def test_key_details_exists(self):
        """TrustTunnelMessages.KEY_DETAILS existe con placeholders."""
        from src.bot.keyboards.messages_trusttunnel import TrustTunnelMessages

        assert "{name}" in TrustTunnelMessages.KEY_DETAILS
        assert "{active_clients}" in TrustTunnelMessages.KEY_DETAILS
        assert "{total_bandwidth}" in TrustTunnelMessages.KEY_DETAILS

    def test_metrics_display_exists(self):
        """TrustTunnelMessages.METRICS_DISPLAY existe."""
        from src.bot.keyboards.messages_trusttunnel import TrustTunnelMessages

        assert hasattr(TrustTunnelMessages, "METRICS_DISPLAY")
        assert "{active_clients}" in TrustTunnelMessages.METRICS_DISPLAY

    def test_config_export_success_exists(self):
        """TrustTunnelMessages.CONFIG_EXPORT_SUCCESS existe."""
        from src.bot.keyboards.messages_trusttunnel import TrustTunnelMessages

        assert hasattr(TrustTunnelMessages, "CONFIG_EXPORT_SUCCESS")

    def test_error_messages_exist(self):
        """TrustTunnelMessages.Error tiene mensajes de error."""
        from src.bot.keyboards.messages_trusttunnel import TrustTunnelMessages

        assert hasattr(TrustTunnelMessages.Error, "SERVICE_UNAVAILABLE")
        assert hasattr(TrustTunnelMessages.Error, "CONFIG_EXPORT_FAILED")
