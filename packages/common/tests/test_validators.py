"""Tests para validadores."""

from usipipo_commons.utils import (
    validate_telegram_id,
    validate_referral_code,
    validate_vpn_key_name,
)


class TestValidateTelegramId:
    """Tests para validate_telegram_id."""

    def test_valid_telegram_id(self):
        """Test con Telegram ID válido."""
        assert validate_telegram_id(123456789) is True
        assert validate_telegram_id(1) is True
        assert validate_telegram_id(2**62) is True

    def test_invalid_telegram_id(self):
        """Test con Telegram ID inválido."""
        assert validate_telegram_id(0) is False
        assert validate_telegram_id(-1) is False
        assert validate_telegram_id(2**64) is False


class TestValidateReferralCode:
    """Tests para validate_referral_code."""

    def test_valid_referral_codes(self):
        """Test con códigos de referido válidos."""
        assert validate_referral_code("REF1") is True
        assert validate_referral_code("ABCD1234") is True
        assert validate_referral_code("abcd1234") is True
        assert validate_referral_code("A1B2C3D4") is True
        assert validate_referral_code(None) is True
        assert validate_referral_code("") is True

    def test_invalid_referral_codes(self):
        """Test con códigos de referido inválidos."""
        assert validate_referral_code("ABC") is False  # Muy corto (3 chars)
        assert validate_referral_code("ABCDEFGHIJ1234567") is False  # Muy largo (17 chars)
        assert validate_referral_code("REF_123") is False  # Carácter especial
        assert validate_referral_code("REF-123") is False  # Guión


class TestValidateVpnKeyName:
    """Tests para validate_vpn_key_name."""

    def test_valid_vpn_key_names(self):
        """Test con nombres de clave VPN válidos."""
        assert validate_vpn_key_name("My VPN") is True
        assert validate_vpn_key_name("work-key") is True
        assert validate_vpn_key_name("personal_1") is True
        assert validate_vpn_key_name("ABC") is True  # Mínimo 3 caracteres
        assert validate_vpn_key_name("A" * 50) is True  # Máximo 50 caracteres

    def test_invalid_vpn_key_names(self):
        """Test con nombres de clave VPN inválidos."""
        assert validate_vpn_key_name("") is False
        assert validate_vpn_key_name("A" * 51) is False  # Muy largo
        assert validate_vpn_key_name("key@123") is False  # Carácter especial
