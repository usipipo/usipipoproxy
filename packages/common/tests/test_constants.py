"""Tests para constantes."""

from usipipo_commons.constants import (
    FREE_GB,
    FREE_KEYS_LIMIT,
    WELCOME_BONUS_GB,
    LOYALTY_BONUS_GB,
    REFERRAL_BONUS_GB,
    MAX_KEYS_PER_USER,
    MIN_PACKAGE_GB,
    MAX_PACKAGE_GB,
    PRICE_PER_GB,
    BILLING_CYCLE_DAYS,
)


class TestPlansConstants:
    """Tests para constantes de planes."""

    def test_free_gb(self):
        """Test para FREE_GB."""
        assert FREE_GB == 5.0

    def test_free_keys_limit(self):
        """Test para FREE_KEYS_LIMIT."""
        assert FREE_KEYS_LIMIT == 2

    def test_welcome_bonus_gb(self):
        """Test para WELCOME_BONUS_GB."""
        assert WELCOME_BONUS_GB == 2.0

    def test_loyalty_bonus_gb(self):
        """Test para LOYALTY_BONUS_GB."""
        assert LOYALTY_BONUS_GB == 1.0

    def test_referral_bonus_gb(self):
        """Test para REFERRAL_BONUS_GB."""
        assert REFERRAL_BONUS_GB == 5.0

    def test_max_keys_per_user(self):
        """Test para MAX_KEYS_PER_USER."""
        assert MAX_KEYS_PER_USER == 10

    def test_min_package_gb(self):
        """Test para MIN_PACKAGE_GB."""
        assert MIN_PACKAGE_GB == 1.0

    def test_max_package_gb(self):
        """Test para MAX_PACKAGE_GB."""
        assert MAX_PACKAGE_GB == 100.0

    def test_price_per_gb(self):
        """Test para PRICE_PER_GB."""
        assert PRICE_PER_GB == 0.50

    def test_billing_cycle_days(self):
        """Test para BILLING_CYCLE_DAYS."""
        assert BILLING_CYCLE_DAYS == 30
