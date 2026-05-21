"""Unit tests for WebhookSecurityService."""

import hashlib
import hmac
import time
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from usipipo_commons.domain.entities.crypto_transaction import WebhookToken

from src.core.application.services.webhook_security_service import WebhookSecurityService


@pytest.fixture
def mock_token_repo():
    """Creates a mock webhook token repository."""
    repo = AsyncMock()
    repo.get_by_hash = AsyncMock()
    repo.save = AsyncMock()
    repo.mark_used = AsyncMock()
    repo.cleanup_expired = AsyncMock()
    return repo


@pytest.fixture
def webhook_secret():
    """Returns a test webhook secret."""
    return "test-secret-key-for-webhook-verification"


@pytest.fixture
def security_service(mock_token_repo, webhook_secret):
    """Creates a WebhookSecurityService instance with mock dependencies."""
    return WebhookSecurityService(
        webhook_secret=webhook_secret,
        token_repo=mock_token_repo,
    )


class TestVerifyHmacSignature:
    """Tests for HMAC signature verification."""

    def test_valid_signature_without_timestamp(self, security_service, webhook_secret):
        """Verifies valid signature without timestamp."""
        payload = b'{"wallet_address": "0x123", "amount": 100}'
        expected_signature = hmac.new(
            webhook_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

        result = security_service.verify_hmac_signature(payload, expected_signature)

        assert result is True

    def test_valid_signature_with_timestamp(self, security_service, webhook_secret):
        """Verifies valid signature with timestamp."""
        payload = b'{"wallet_address": "0x123", "amount": 100}'
        timestamp = "1234567890"
        message = f"{timestamp}.".encode() + payload
        expected_signature = hmac.new(
            webhook_secret.encode(),
            message,
            hashlib.sha256,
        ).hexdigest()

        result = security_service.verify_hmac_signature(payload, expected_signature, timestamp)

        assert result is True

    def test_invalid_signature(self, security_service):
        """Verifies invalid signature returns False."""
        payload = b'{"wallet_address": "0x123", "amount": 100}'
        invalid_signature = "invalid_signature_12345"

        result = security_service.verify_hmac_signature(payload, invalid_signature)

        assert result is False

    def test_invalid_signature_with_timestamp(self, security_service):
        """Verifies invalid signature with timestamp returns False."""
        payload = b'{"wallet_address": "0x123", "amount": 100}'
        timestamp = "1234567890"
        invalid_signature = "invalid_signature_12345"

        result = security_service.verify_hmac_signature(payload, invalid_signature, timestamp)

        assert result is False

    def test_signature_with_tampered_payload(self, security_service, webhook_secret):
        """Verifies tampered payload fails signature verification."""
        original_payload = b'{"wallet_address": "0x123", "amount": 100}'
        tampered_payload = b'{"wallet_address": "0x123", "amount": 999}'

        expected_signature = hmac.new(
            webhook_secret.encode(),
            original_payload,
            hashlib.sha256,
        ).hexdigest()

        result = security_service.verify_hmac_signature(tampered_payload, expected_signature)

        assert result is False

    def test_empty_payload(self, security_service, webhook_secret):
        """Verifies empty payload signature."""
        payload = b""
        expected_signature = hmac.new(
            webhook_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

        result = security_service.verify_hmac_signature(payload, expected_signature)

        assert result is True

    def test_signature_with_different_timestamps(self, security_service, webhook_secret):
        """Verifies different timestamps produce different signatures."""
        payload = b'{"wallet_address": "0x123", "amount": 100}'
        timestamp1 = "1234567890"
        timestamp2 = "1234567891"

        message1 = f"{timestamp1}.".encode() + payload
        message2 = f"{timestamp2}.".encode() + payload

        signature1 = hmac.new(
            webhook_secret.encode(),
            message1,
            hashlib.sha256,
        ).hexdigest()

        signature2 = hmac.new(
            webhook_secret.encode(),
            message2,
            hashlib.sha256,
        ).hexdigest()

        assert signature1 != signature2
        # Signature with timestamp1 should not verify with timestamp2
        result = security_service.verify_hmac_signature(payload, signature1, timestamp2)
        assert result is False


class TestValidateTimestamp:
    """Tests for timestamp validation."""

    def test_valid_timestamp(self, security_service):
        """Verifies valid timestamp within drift window."""
        current_time = str(int(time.time()))

        is_valid, error_msg = security_service.validate_timestamp(current_time)

        assert is_valid is True
        assert error_msg is None

    def test_expired_timestamp(self, security_service):
        """Verifies expired timestamp is rejected."""
        # Create timestamp 10 minutes ago (beyond 5 minute drift)
        expired_time = str(int(time.time()) - 600)

        is_valid, error_msg = security_service.validate_timestamp(expired_time)

        assert is_valid is False
        assert error_msg is not None
        assert "exceeds maximum allowed" in error_msg

    def test_future_timestamp(self, security_service):
        """Verifies future timestamp beyond drift is rejected."""
        # Create timestamp 10 minutes in the future
        future_time = str(int(time.time()) + 600)

        is_valid, error_msg = security_service.validate_timestamp(future_time)

        assert is_valid is False
        assert error_msg is not None
        assert "exceeds maximum allowed" in error_msg

    def test_timestamp_at_drift_boundary(self, security_service):
        """Verifies timestamp at exact drift boundary is accepted."""
        # Create timestamp exactly at 5 minute boundary
        boundary_time = str(int(time.time()) - 300)

        is_valid, error_msg = security_service.validate_timestamp(boundary_time)

        assert is_valid is True
        assert error_msg is None

    def test_timestamp_just_beyond_drift_boundary(self, security_service):
        """Verifies timestamp just beyond drift boundary is rejected."""
        # Create timestamp 1 second beyond 5 minute boundary
        beyond_boundary = str(int(time.time()) - 301)

        is_valid, error_msg = security_service.validate_timestamp(beyond_boundary)

        assert is_valid is False
        assert error_msg is not None

    def test_invalid_timestamp_format(self, security_service):
        """Verifies invalid timestamp format is rejected."""
        invalid_timestamp = "not-a-number"

        is_valid, error_msg = security_service.validate_timestamp(invalid_timestamp)

        assert is_valid is False
        assert error_msg is not None
        assert "Invalid timestamp format" in error_msg

    def test_empty_timestamp(self, security_service):
        """Verifies empty timestamp is rejected."""
        empty_timestamp = ""

        is_valid, error_msg = security_service.validate_timestamp(empty_timestamp)

        assert is_valid is False
        assert error_msg is not None


class TestCheckAndRegisterNonce:
    """Tests for nonce replay protection."""

    @pytest.mark.asyncio
    async def test_new_nonce_registered_successfully(self, security_service, mock_token_repo):
        """Verifies new nonce is registered successfully."""
        mock_token_repo.get_by_hash.return_value = None
        mock_token_repo.save.return_value = MagicMock()
        mock_token_repo.mark_used.return_value = True

        nonce = "unique-nonce-12345"
        is_valid, error_msg = await security_service.check_and_register_nonce(nonce)

        assert is_valid is True
        assert error_msg is None
        mock_token_repo.get_by_hash.assert_called_once()
        mock_token_repo.save.assert_called_once()
        mock_token_repo.mark_used.assert_called()

    @pytest.mark.asyncio
    async def test_reused_nonce_rejected(self, security_service, mock_token_repo):
        """Verifies reused nonce is rejected."""
        # Create a mock token that was already used
        used_token = WebhookToken.create(
            token_hash=hashlib.sha256(b"reused-nonce").hexdigest(),
            purpose="tron_dealer",
        )
        used_token.used_at = datetime.now(UTC) - timedelta(hours=1)

        mock_token_repo.get_by_hash.return_value = used_token

        nonce = "reused-nonce"
        is_valid, error_msg = await security_service.check_and_register_nonce(nonce)

        assert is_valid is False
        assert error_msg is not None
        assert "already used" in error_msg

    @pytest.mark.asyncio
    async def test_expired_nonce_rejected(self, security_service, mock_token_repo):
        """Verifies expired nonce is rejected."""
        # Create a mock token that is expired
        expired_token = WebhookToken.create(
            token_hash=hashlib.sha256(b"expired-nonce").hexdigest(),
            purpose="tron_dealer",
        )
        expired_token.expires_at = datetime.now(UTC) - timedelta(hours=25)
        expired_token.used_at = None

        mock_token_repo.get_by_hash.return_value = expired_token

        nonce = "expired-nonce"
        is_valid, error_msg = await security_service.check_and_register_nonce(nonce)

        assert is_valid is False
        assert error_msg is not None
        assert "expired" in error_msg

    @pytest.mark.asyncio
    async def test_nonce_hash_is_sha256(self, security_service, mock_token_repo):
        """Verifies nonce is hashed with SHA256 before storage."""
        mock_token_repo.get_by_hash.return_value = None
        mock_token_repo.save.return_value = MagicMock()
        mock_token_repo.mark_used.return_value = True

        nonce = "test-nonce"
        expected_hash = hashlib.sha256(nonce.encode()).hexdigest()

        await security_service.check_and_register_nonce(nonce)

        mock_token_repo.get_by_hash.assert_called_with(expected_hash)


class TestCleanupExpiredNonces:
    """Tests for expired nonce cleanup."""

    @pytest.mark.asyncio
    async def test_cleanup_returns_count(self, security_service, mock_token_repo):
        """Verifies cleanup returns count of cleaned nonces."""
        mock_token_repo.cleanup_expired.return_value = 42

        count = await security_service.cleanup_expired_nonces()

        assert count == 42
        mock_token_repo.cleanup_expired.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_handles_zero_count(self, security_service, mock_token_repo):
        """Verifies cleanup handles zero count."""
        mock_token_repo.cleanup_expired.return_value = 0

        count = await security_service.cleanup_expired_nonces()

        assert count == 0

    @pytest.mark.asyncio
    async def test_cleanup_handles_error(self, security_service, mock_token_repo):
        """Verifies cleanup handles errors gracefully."""
        mock_token_repo.cleanup_expired.side_effect = Exception("Database error")

        count = await security_service.cleanup_expired_nonces()

        assert count == 0


class TestExtractClientIp:
    """Tests for client IP extraction."""

    def test_extract_from_x_forwarded_for_single(self, security_service):
        """Verifies IP extraction from X-Forwarded-For with single IP."""
        headers = {"x-forwarded-for": "192.168.1.1"}

        ip = security_service.extract_client_ip(headers)

        assert ip == "192.168.1.1"

    def test_extract_from_x_forwarded_for_multiple(self, security_service):
        """Verifies first IP is extracted from X-Forwarded-For with multiple IPs."""
        headers = {"x-forwarded-for": "192.168.1.1, 10.0.0.1, 172.16.0.1"}

        ip = security_service.extract_client_ip(headers)

        assert ip == "192.168.1.1"

    def test_extract_from_x_real_ip(self, security_service):
        """Verifies IP extraction from X-Real-IP."""
        headers = {"x-real-ip": "192.168.1.100"}

        ip = security_service.extract_client_ip(headers)

        assert ip == "192.168.1.100"

    def test_x_forwarded_for_takes_precedence(self, security_service):
        """Verifies X-Forwarded-For takes precedence over X-Real-IP."""
        headers = {
            "x-forwarded-for": "192.168.1.1",
            "x-real-ip": "10.0.0.1",
        }

        ip = security_service.extract_client_ip(headers)

        assert ip == "192.168.1.1"

    def test_returns_none_when_no_ip_headers(self, security_service):
        """Verifies None is returned when no IP headers present."""
        headers = {"content-type": "application/json", "user-agent": "Test"}

        ip = security_service.extract_client_ip(headers)

        assert ip is None

    def test_returns_none_when_empty_headers(self, security_service):
        """Verifies None is returned with empty headers."""
        headers = {}

        ip = security_service.extract_client_ip(headers)

        assert ip is None

    def test_handles_whitespace_in_x_forwarded_for(self, security_service):
        """Verifies whitespace is handled in X-Forwarded-For."""
        headers = {"x-forwarded-for": "  192.168.1.1  , 10.0.0.1"}

        ip = security_service.extract_client_ip(headers)

        assert ip == "192.168.1.1"


class TestIsSuspiciousRequest:
    """Tests for suspicious request detection."""

    def test_valid_request(self, security_service):
        """Verifies valid request is not flagged as suspicious."""
        payload = {
            "wallet_address": "0x1234567890123456789012345678901234567890",
            "amount": 100.50,
            "tx_hash": "0xabcdef1234567890",
        }
        headers = {"content-type": "application/json"}

        is_suspicious, reason = security_service.is_suspicious_request(payload, headers)

        assert is_suspicious is False
        assert reason is None

    def test_empty_payload(self, security_service):
        """Verifies empty payload is flagged as suspicious."""
        payload = {}
        headers = {"content-type": "application/json"}

        is_suspicious, reason = security_service.is_suspicious_request(payload, headers)

        assert is_suspicious is True
        assert "Empty payload" in reason

    def test_none_payload(self, security_service):
        """Verifies None payload is flagged as suspicious."""
        payload = None
        headers = {"content-type": "application/json"}

        is_suspicious, reason = security_service.is_suspicious_request(payload, headers)

        assert is_suspicious is True

    def test_missing_wallet_address(self, security_service):
        """Verifies missing wallet_address is flagged as suspicious."""
        payload = {
            "amount": 100.50,
            "tx_hash": "0xabcdef1234567890",
        }
        headers = {"content-type": "application/json"}

        is_suspicious, reason = security_service.is_suspicious_request(payload, headers)

        assert is_suspicious is True
        assert "Missing required field: wallet_address" in reason

    def test_missing_amount(self, security_service):
        """Verifies missing amount is flagged as suspicious."""
        payload = {
            "wallet_address": "0x1234567890123456789012345678901234567890",
            "tx_hash": "0xabcdef1234567890",
        }
        headers = {"content-type": "application/json"}

        is_suspicious, reason = security_service.is_suspicious_request(payload, headers)

        assert is_suspicious is True
        assert "Missing required field: amount" in reason

    def test_missing_tx_hash(self, security_service):
        """Verifies missing tx_hash is flagged as suspicious."""
        payload = {
            "wallet_address": "0x1234567890123456789012345678901234567890",
            "amount": 100.50,
        }
        headers = {"content-type": "application/json"}

        is_suspicious, reason = security_service.is_suspicious_request(payload, headers)

        assert is_suspicious is True
        assert "Missing required field: tx_hash" in reason

    def test_negative_amount(self, security_service):
        """Verifies negative amount is flagged as suspicious."""
        payload = {
            "wallet_address": "0x1234567890123456789012345678901234567890",
            "amount": -100.50,
            "tx_hash": "0xabcdef1234567890",
        }
        headers = {"content-type": "application/json"}

        is_suspicious, reason = security_service.is_suspicious_request(payload, headers)

        assert is_suspicious is True
        assert "Invalid amount" in reason

    def test_zero_amount(self, security_service):
        """Verifies zero amount is flagged as suspicious."""
        payload = {
            "wallet_address": "0x1234567890123456789012345678901234567890",
            "amount": 0,
            "tx_hash": "0xabcdef1234567890",
        }
        headers = {"content-type": "application/json"}

        is_suspicious, reason = security_service.is_suspicious_request(payload, headers)

        assert is_suspicious is True
        assert "Invalid amount" in reason

    def test_wallet_address_without_0x_prefix(self, security_service):
        """Verifies wallet address without 0x prefix is flagged as suspicious."""
        payload = {
            "wallet_address": "1234567890123456789012345678901234567890",
            "amount": 100.50,
            "tx_hash": "0xabcdef1234567890",
        }
        headers = {"content-type": "application/json"}

        is_suspicious, reason = security_service.is_suspicious_request(payload, headers)

        assert is_suspicious is True
        assert "must start with '0x'" in reason

    def test_wallet_address_wrong_length(self, security_service):
        """Verifies wallet address with wrong length is flagged as suspicious."""
        payload = {
            "wallet_address": "0x123456789012345678901234567890123456789",  # 41 chars
            "amount": 100.50,
            "tx_hash": "0xabcdef1234567890",
        }
        headers = {"content-type": "application/json"}

        is_suspicious, reason = security_service.is_suspicious_request(payload, headers)

        assert is_suspicious is True
        assert "Invalid wallet address length" in reason

    def test_wallet_address_too_long(self, security_service):
        """Verifies wallet address that is too long is flagged as suspicious."""
        payload = {
            "wallet_address": "0x12345678901234567890123456789012345678901",  # 43 chars
            "amount": 100.50,
            "tx_hash": "0xabcdef1234567890",
        }
        headers = {"content-type": "application/json"}

        is_suspicious, reason = security_service.is_suspicious_request(payload, headers)

        assert is_suspicious is True
        assert "Invalid wallet address length" in reason

    def test_wallet_address_not_string(self, security_service):
        """Verifies non-string wallet address is flagged as suspicious."""
        payload = {
            "wallet_address": 12345,
            "amount": 100.50,
            "tx_hash": "0xabcdef1234567890",
        }
        headers = {"content-type": "application/json"}

        is_suspicious, reason = security_service.is_suspicious_request(payload, headers)

        assert is_suspicious is True
        assert "Invalid wallet address type" in reason

    def test_amount_as_string(self, security_service):
        """Verifies string amount is flagged as suspicious."""
        payload = {
            "wallet_address": "0x1234567890123456789012345678901234567890",
            "amount": "100.50",
            "tx_hash": "0xabcdef1234567890",
        }
        headers = {"content-type": "application/json"}

        is_suspicious, reason = security_service.is_suspicious_request(payload, headers)

        assert is_suspicious is True
        assert "Invalid amount" in reason


class TestWebhookSecurityServiceConstants:
    """Tests for WebhookSecurityService constants."""

    def test_max_timestamp_drift_seconds(self):
        """Verifies MAX_TIMESTAMP_DRIFT_SECONDS constant."""
        assert WebhookSecurityService.MAX_TIMESTAMP_DRIFT_SECONDS == 300

    def test_nonce_expiry_hours(self):
        """Verifies NONCE_EXPIRY_HOURS constant."""
        assert WebhookSecurityService.NONCE_EXPIRY_HOURS == 24
