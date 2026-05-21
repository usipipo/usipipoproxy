"""Tests para schemas Pydantic."""
import pytest

from usipipo_commons.schemas import (
    UserCreateRequest,
    CreateVpnKeyRequest,
    CreatePaymentRequest,
)
from usipipo_commons.domain.enums import KeyType, PaymentMethod


class TestUserCreateRequest:
    """Tests para UserCreateRequest."""

    def test_valid_request(self):
        """Test con solicitud válida."""
        request = UserCreateRequest(
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
        )

        assert request.telegram_id == 123456789
        assert request.username == "testuser"

    def test_minimal_request(self):
        """Test con solicitud mínima."""
        request = UserCreateRequest(telegram_id=123456789)

        assert request.telegram_id == 123456789
        assert request.username is None


class TestCreateVpnKeyRequest:
    """Tests para CreateVpnKeyRequest."""

    def test_valid_request(self):
        """Test con solicitud válida."""
        request = CreateVpnKeyRequest(
            name="My VPN",
            key_type=KeyType.WIREGUARD,
            data_limit_gb=10.0,
        )

        assert request.name == "My VPN"
        assert request.key_type == KeyType.WIREGUARD
        assert request.data_limit_gb == 10.0

    def test_default_data_limit(self):
        """Test con límite de datos por defecto."""
        request = CreateVpnKeyRequest(
            name="My VPN",
            key_type=KeyType.OUTLINE,
        )

        assert request.data_limit_gb == 5.0


class TestCreatePaymentRequest:
    """Tests para CreatePaymentRequest."""

    def test_valid_request(self):
        """Test con solicitud válida."""
        request = CreatePaymentRequest(
            amount_usd=5.0,
            method=PaymentMethod.TELEGRAM_STARS,
            gb_purchased=10.0,
        )

        assert request.amount_usd == 5.0
        assert request.method == PaymentMethod.TELEGRAM_STARS

    def test_invalid_amount(self):
        """Test con monto inválido."""
        with pytest.raises(ValueError):
            CreatePaymentRequest(
                amount_usd=0,
                method=PaymentMethod.TELEGRAM_STARS,
                gb_purchased=10.0,
            )
