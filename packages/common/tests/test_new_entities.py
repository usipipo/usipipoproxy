"""Tests para las nuevas entidades y campos de la Semana 8."""
from datetime import datetime, timezone
from uuid import uuid4

from usipipo_commons.domain.entities import User, Referral, DataPackage, PackageType


class TestUserBonuses:
    """Tests para los nuevos campos de bonos en la entidad User."""

    def test_user_bonus_fields_default(self):
        """Test que los campos de bonos tengan valores por defecto correctos."""
        user = User(
            id=uuid4(),
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            is_admin=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            balance_gb=5.0,
            total_purchased_gb=0.0,
            referral_code="REF1234",
            referred_by=None,
        )

        assert user.referral_credits == 0
        assert user.purchase_count == 0
        assert user.loyalty_bonus_percent == 0
        assert user.welcome_bonus_used is False
        assert user.referred_users_with_purchase == 0

    def test_user_bonus_fields_custom(self):
        """Test que se puedan asignar valores a los campos de bonos."""
        user = User(
            id=uuid4(),
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            is_admin=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            balance_gb=10.0,
            total_purchased_gb=20.0,
            referral_code="REF1234",
            referred_by=uuid4(),
            referral_credits=500,
            purchase_count=5,
            loyalty_bonus_percent=15,
            welcome_bonus_used=True,
            referred_users_with_purchase=3,
        )

        assert user.referral_credits == 500
        assert user.purchase_count == 5
        assert user.loyalty_bonus_percent == 15
        assert user.welcome_bonus_used is True
        assert user.referred_users_with_purchase == 3

    def test_user_to_dict_includes_bonuses(self):
        """Test que to_dict incluya los nuevos campos de bonos."""
        user = User(
            id=uuid4(),
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            is_admin=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            balance_gb=5.0,
            total_purchased_gb=0.0,
            referral_code="REF1234",
            referred_by=None,
            referral_credits=100,
        )

        user_dict = user.to_dict()
        assert "referral_credits" in user_dict
        assert user_dict["referral_credits"] == 100
        assert "purchase_count" in user_dict
        assert "loyalty_bonus_percent" in user_dict
        assert "welcome_bonus_used" in user_dict
        assert "referred_users_with_purchase" in user_dict


class TestReferral:
    """Tests para la nueva entidad Referral."""

    def test_referral_creation(self):
        """Test para crear una relación de referido válida."""
        referrer_id = uuid4()
        referred_id = uuid4()
        referral = Referral(
            referrer_id=referrer_id,
            referred_id=referred_id,
        )

        assert referral.referrer_id == referrer_id
        assert referral.referred_id == referred_id
        assert referral.id is not None
        assert referral.is_active is True
        assert referral.bonus_applied is False
        assert isinstance(referral.created_at, datetime)

    def test_referral_custom_values(self):
        """Test para crear una relación de referido con valores personalizados."""
        ref_id = uuid4()
        referrer_id = uuid4()
        referred_id = uuid4()
        created_at = datetime.now(timezone.utc)
        
        referral = Referral(
            id=ref_id,
            referrer_id=referrer_id,
            referred_id=referred_id,
            created_at=created_at,
            is_active=False,
            bonus_applied=True,
        )

        assert referral.id == ref_id
        assert referral.is_active is False
        assert referral.bonus_applied is True
        assert referral.created_at == created_at


class TestDataPackageExport:
    """Test para verificar que DataPackage se exporta correctamente."""

    def test_datapackage_creation(self):
        """Test que se puede instanciar DataPackage."""
        pkg_id = uuid4()
        user_id = uuid4()
        expires_at = datetime.now(timezone.utc)

        pkg = DataPackage(
            user_id=user_id,
            package_type=PackageType.BASIC,
            data_limit_bytes=10 * 1024**3,
            stars_paid=250,
            expires_at=expires_at,
            id=pkg_id
        )

        assert pkg.user_id == user_id
        assert pkg.package_type == PackageType.BASIC
        assert pkg.id == pkg_id
        assert pkg.remaining_bytes == 10 * 1024**3
