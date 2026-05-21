"""Tests para entidades del dominio."""
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from usipipo_commons.domain.entities import User, VpnKey, Payment, ConsumptionBilling, ConsumptionInvoice, CryptoOrder
from usipipo_commons.domain.enums import KeyType, KeyStatus, PaymentStatus, PaymentMethod, BillingStatus, InvoiceStatus, ConsumptionPaymentMethod, CryptoOrderStatus


class TestUser:
    """Tests para la entidad User."""

    def test_user_creation(self):
        """Test para crear un usuario válido."""
        user = User(
            id=uuid4(),
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            is_admin=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            balance_gb=5.0,
            total_purchased_gb=10.0,
            referral_code="REF1234",
            referred_by=None,
        )

        assert user.telegram_id == 123456789
        assert user.username == "testuser"
        assert user.balance_gb == 5.0
        assert user.is_admin is False

    def test_user_to_dict(self):
        """Test para convertir usuario a diccionario."""
        user_id = uuid4()
        user = User(
            id=user_id,
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            is_admin=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            balance_gb=5.0,
            total_purchased_gb=10.0,
            referral_code="REF1234",
            referred_by=None,
        )

        user_dict = user.to_dict()

        assert user_dict["telegram_id"] == 123456789
        assert user_dict["username"] == "testuser"
        assert user_dict["balance_gb"] == 5.0
        assert isinstance(user_dict["id"], str)


class TestUserConsumptionMethods:
    """Tests para métodos de consumo y deuda de User."""

    def test_mark_as_has_debt(self):
        """Test para marcar usuario con deuda pendiente."""
        user = User(
            id=uuid4(),
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            is_admin=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            balance_gb=5.0,
            total_purchased_gb=10.0,
            referral_code="REF1234",
            referred_by=None,
        )
        user.mark_as_has_debt()
        assert user.has_pending_debt is True

    def test_clear_debt(self):
        """Test para limpiar deuda de usuario."""
        user = User(
            id=uuid4(),
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            is_admin=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            balance_gb=5.0,
            total_purchased_gb=10.0,
            referral_code="REF1234",
            referred_by=None,
        )
        user.mark_as_has_debt()
        user.clear_debt()
        assert user.has_pending_debt is False

    def test_activate_consumption_mode(self):
        """Test para activar modo consumo."""
        user = User(
            id=uuid4(),
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            is_admin=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            balance_gb=5.0,
            total_purchased_gb=10.0,
            referral_code="REF1234",
            referred_by=None,
        )
        user.activate_consumption_mode()
        assert user.consumption_mode_enabled is True

    def test_deactivate_consumption_mode(self):
        """Test para desactivar modo consumo."""
        user = User(
            id=uuid4(),
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            is_admin=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            balance_gb=5.0,
            total_purchased_gb=10.0,
            referral_code="REF1234",
            referred_by=None,
        )
        user.activate_consumption_mode()
        user.deactivate_consumption_mode()
        assert user.consumption_mode_enabled is False


class TestVpnKey:
    """Tests para la entidad VpnKey."""

    def test_vpn_key_creation(self):
        """Test para crear una clave VPN válida."""
        vpn_key = VpnKey(
            id=uuid4(),  # ← Now UUID
            user_id=uuid4(),  # ← Now UUID
            name="My VPN",
            key_type=KeyType.WIREGUARD,
            status=KeyStatus.ACTIVE,  # ← Added status field
            key_data="wireguard-config-placeholder",
            external_id="wg-external-id-123",
            created_at=datetime.now(timezone.utc),
            data_limit_bytes=5 * 1024**3,
        )

        assert vpn_key.name == "My VPN"
        assert vpn_key.key_type == KeyType.WIREGUARD
        assert vpn_key.status == KeyStatus.ACTIVE
        assert vpn_key.is_active is True  # property based on status
        assert vpn_key.data_limit_gb == 5.0

    def test_vpn_key_to_dict(self):
        """Test para convertir clave VPN a diccionario."""
        vpn_key = VpnKey(
            id=uuid4(),  # ← Now UUID, not str
            user_id=uuid4(),  # ← Now UUID, not int
            name="My VPN",
            key_type=KeyType.OUTLINE,
            status=KeyStatus.ACTIVE,  # ← Added status field
            key_data="ss://outline-config-placeholder",
            external_id="outline-external-id-456",
            created_at=datetime.now(timezone.utc),
            data_limit_bytes=10 * 1024**3,
        )

        vpn_dict = vpn_key.to_dict()

        assert vpn_dict["name"] == "My VPN"
        assert vpn_dict["key_type"] == "outline"
        assert vpn_dict["status"] == "active"
        assert vpn_dict["is_active"] is True  # property


class TestPayment:
    """Tests para la entidad Payment."""

    def test_payment_creation(self):
        """Test para crear un pago válido."""
        payment = Payment(
            id=uuid4(),
            user_id=uuid4(),
            amount_usd=5.0,
            gb_purchased=10.0,
            method=PaymentMethod.TELEGRAM_STARS,
            status=PaymentStatus.PENDING,
            crypto_address=None,
            crypto_network=None,
            telegram_star_invoice_id=None,
            created_at=datetime.now(),
            expires_at=None,
            paid_at=None,
            transaction_hash=None,
        )

        assert payment.amount_usd == 5.0
        assert payment.gb_purchased == 10.0
        assert payment.method == PaymentMethod.TELEGRAM_STARS
        assert payment.status == PaymentStatus.PENDING

    def test_payment_to_dict(self):
        """Test para convertir pago a diccionario."""
        payment = Payment(
            id=uuid4(),
            user_id=uuid4(),
            amount_usd=10.0,
            gb_purchased=20.0,
            method=PaymentMethod.CRYPTO_USDT,
            status=PaymentStatus.COMPLETED,
            crypto_address="0x123abc",
            crypto_network="BSC",
            telegram_star_invoice_id=None,
            created_at=datetime.now(),
            expires_at=None,
            paid_at=datetime.now(),
            transaction_hash="0xabc123",
        )

        payment_dict = payment.to_dict()

        assert payment_dict["amount_usd"] == 10.0
        assert payment_dict["method"] == "crypto_usdt"
        assert payment_dict["status"] == "completed"
        assert payment_dict["transaction_hash"] == "0xabc123"


class TestConsumptionBilling:
    """Tests para la entidad ConsumptionBilling."""

    def test_consumption_billing_creation(self):
        """Test para crear un ciclo de facturación por consumo."""
        billing = ConsumptionBilling(
            user_id=uuid4(),
            started_at=datetime.now(timezone.utc),
            status=BillingStatus.ACTIVE,
            mb_consumed=Decimal("1024.00"),
            price_per_mb_usd=Decimal("0.000244140625"),
        )

        assert billing.status == BillingStatus.ACTIVE
        assert billing.mb_consumed == Decimal("1024.00")

    def test_consumption_billing_is_active(self):
        """Test para verificar estado activo."""
        billing = ConsumptionBilling(
            user_id=uuid4(),
            started_at=datetime.now(timezone.utc),
            status=BillingStatus.ACTIVE,
        )

        assert billing.is_active is True
        assert billing.is_closed is False
        assert billing.is_paid is False

    def test_consumption_billing_gb_consumed(self):
        """Test para verificar conversión a GB."""
        billing = ConsumptionBilling(
            user_id=uuid4(),
            started_at=datetime.now(timezone.utc),
            mb_consumed=Decimal("2048.00"),
            price_per_mb_usd=Decimal("0.000244140625"),
        )

        assert billing.gb_consumed == Decimal("2.00")

    def test_consumption_billing_add_consumption(self):
        """Test para agregar consumo."""
        billing = ConsumptionBilling(
            user_id=uuid4(),
            started_at=datetime.now(timezone.utc),
            mb_consumed=Decimal("1024.00"),
            price_per_mb_usd=Decimal("0.000244140625"),
        )

        billing.add_consumption(Decimal("512.00"))

        assert billing.mb_consumed == Decimal("1536.00")
        assert billing.total_cost_usd > Decimal("0")

    def test_consumption_billing_close_cycle(self):
        """Test para cerrar ciclo de facturación."""
        billing = ConsumptionBilling(
            user_id=uuid4(),
            started_at=datetime.now(timezone.utc),
            status=BillingStatus.ACTIVE,
            mb_consumed=Decimal("2048.00"),
            price_per_mb_usd=Decimal("0.000244140625"),
        )

        billing.close_cycle()

        assert billing.status == BillingStatus.CLOSED
        assert billing.ended_at is not None

    def test_consumption_billing_mark_as_paid(self):
        """Test para marcar como pagado."""
        billing = ConsumptionBilling(
            user_id=uuid4(),
            started_at=datetime.now(timezone.utc),
            status=BillingStatus.CLOSED,
            mb_consumed=Decimal("2048.00"),
        )

        billing.mark_as_paid()

        assert billing.status == BillingStatus.PAID


class TestConsumptionInvoice:
    """Tests para la entidad ConsumptionInvoice."""

    def test_consumption_invoice_creation(self):
        """Test para crear una factura de consumo."""
        billing_id = uuid4()
        invoice = ConsumptionInvoice(
            billing_id=billing_id,
            user_id=uuid4(),
            amount_usd=Decimal("5.00"),
            wallet_address="0x1234567890abcdef",
            payment_method=ConsumptionPaymentMethod.CRYPTO,
        )

        assert invoice.amount_usd == Decimal("5.00")
        assert invoice.status == InvoiceStatus.PENDING

    def test_consumption_invoice_is_pending(self):
        """Test para verificar estado pendiente."""
        billing_id = uuid4()
        invoice = ConsumptionInvoice(
            billing_id=billing_id,
            user_id=uuid4(),
            amount_usd=Decimal("5.00"),
            wallet_address="0x1234567890abcdef",
        )

        assert invoice.is_pending is True
        assert invoice.is_paid is False
        assert invoice.is_expired is False

    def test_consumption_invoice_mark_as_paid_crypto(self):
        """Test para marcar como pagada con crypto."""
        billing_id = uuid4()
        invoice = ConsumptionInvoice(
            billing_id=billing_id,
            user_id=uuid4(),
            amount_usd=Decimal("5.00"),
            wallet_address="0x1234567890abcdef",
            payment_method=ConsumptionPaymentMethod.CRYPTO,
        )

        invoice.mark_as_paid(transaction_hash="0xabc123")

        assert invoice.status == InvoiceStatus.PAID
        assert invoice.transaction_hash == "0xabc123"
        assert invoice.paid_at is not None

    def test_consumption_invoice_mark_as_paid_stars(self):
        """Test para marcar como pagada con Stars."""
        billing_id = uuid4()
        invoice = ConsumptionInvoice(
            billing_id=billing_id,
            user_id=uuid4(),
            amount_usd=Decimal("5.00"),
            wallet_address="N/A",
            payment_method=ConsumptionPaymentMethod.STARS,
        )

        invoice.mark_as_paid(telegram_payment_id="stars_123")

        assert invoice.status == InvoiceStatus.PAID
        assert invoice.telegram_payment_id == "stars_123"

    def test_consumption_invoice_mark_as_expired(self):
        """Test para marcar como expirada."""
        billing_id = uuid4()
        invoice = ConsumptionInvoice(
            billing_id=billing_id,
            user_id=uuid4(),
            amount_usd=Decimal("5.00"),
            wallet_address="0x1234567890abcdef",
            status=InvoiceStatus.PENDING,
        )

        invoice.mark_as_expired()

        assert invoice.status == InvoiceStatus.EXPIRED

    def test_consumption_invoice_stars_amount(self):
        """Test para calcular monto en Stars."""
        billing_id = uuid4()
        invoice = ConsumptionInvoice(
            billing_id=billing_id,
            user_id=uuid4(),
            amount_usd=Decimal("5.00"),
            wallet_address="0x1234567890abcdef",
            payment_method=ConsumptionPaymentMethod.STARS,
        )

        # 5 USD * 120 Stars/USD = 600 Stars
        assert invoice.get_stars_amount() == 600

    def test_consumption_invoice_mask_wallet(self):
        """Test para enmascarar wallet."""
        billing_id = uuid4()
        invoice = ConsumptionInvoice(
            billing_id=billing_id,
            user_id=uuid4(),
            amount_usd=Decimal("5.00"),
            wallet_address="0x1234567890abcdef12345678",
            payment_method=ConsumptionPaymentMethod.CRYPTO,
        )

        masked = invoice._mask_wallet_address()

        assert masked == "0x1234...5678"


class TestCryptoOrder:
    """Tests para la entidad CryptoOrder."""

    def test_crypto_order_creation(self):
        """Test para crear una orden crypto."""
        user_id = uuid4()
        order = CryptoOrder(
            id=uuid4(),
            user_id=user_id,
            package_type="basic",
            amount_usdt=10.0,
            wallet_address="TXm4M8z5VrX9z2Y1wP6sK3nR8jL9hT7",
            tron_dealer_order_id="TRO-12345",
            status=CryptoOrderStatus.PENDING,
            created_at=datetime.now(),
            expires_at=datetime.now(),
            tx_hash=None,
            confirmed_at=None,
        )

        assert order.user_id == user_id
        assert order.amount_usdt == 10.0
        assert order.status == CryptoOrderStatus.PENDING

    def test_crypto_order_create_factory(self):
        """Test para crear orden usando factory method."""
        user_id = uuid4()
        order = CryptoOrder.create(
            user_id=user_id,
            package_type="premium",
            amount_usdt=25.0,
            wallet_address="TXm4M8z5VrX9z2Y1wP6sK3nR8jL9hT7",
        )

        assert order.user_id == user_id
        assert order.package_type == "premium"
        assert order.amount_usdt == 25.0
        assert order.status == CryptoOrderStatus.PENDING
        assert order.id is not None
        assert order.created_at is not None
        assert order.tx_hash is None
        assert order.confirmed_at is None

    def test_crypto_order_to_dict(self):
        """Test para convertir orden crypto a diccionario."""
        order = CryptoOrder.create(
            user_id=uuid4(),
            package_type="basic",
            amount_usdt=10.0,
            wallet_address="TXm4M8z5VrX9z2Y1wP6sK3nR8jL9hT7",
        )

        order_dict = order.to_dict()

        assert "id" in order_dict
        assert order_dict["amount_usdt"] == 10.0
        assert order_dict["package_type"] == "basic"
        assert order_dict["status"] == "pending"
        assert isinstance(order_dict["created_at"], str)

    def test_crypto_order_status_values(self):
        """Test para verificar valores del enum."""
        assert CryptoOrderStatus.PENDING.value == "pending"
        assert CryptoOrderStatus.COMPLETED.value == "completed"
        assert CryptoOrderStatus.FAILED.value == "failed"
        assert CryptoOrderStatus.EXPIRED.value == "expired"


class TestKeyType:
    """Tests para el enum KeyType."""

    def test_trusttunnel_key_type_exists(self):
        """Test para verificar que TRUSTTUNNEL existe en KeyType."""
        assert KeyType.TRUSTTUNNEL == "trusttunnel"
        assert KeyType.TRUSTTUNNEL.value == "trusttunnel"

    def test_all_key_types(self):
        """Test para verificar todos los tipos de VPN."""
        assert len(KeyType) == 3
        assert KeyType.OUTLINE == "outline"
        assert KeyType.WIREGUARD == "wireguard"
        assert KeyType.TRUSTTUNNEL == "trusttunnel"
