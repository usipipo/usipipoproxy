"""Webhook security service for verifying and validating webhook requests."""

import hashlib
import hmac
import logging
import time
from datetime import UTC, datetime, timedelta

from src.core.domain.interfaces.i_crypto_transaction_repository import (
    IWebhookTokenRepository,
)

logger = logging.getLogger(__name__)


class WebhookSecurityService:
    """Service for securing webhook requests with HMAC verification and replay protection."""

    MAX_TIMESTAMP_DRIFT_SECONDS = 300  # 5 minutes
    NONCE_EXPIRY_HOURS = 24

    def __init__(self, webhook_secret: str, token_repo: IWebhookTokenRepository):
        """
        Initializes the webhook security service.

        Args:
            webhook_secret: Secret key for HMAC signature verification.
            token_repo: Repository for managing webhook tokens (nonces).
        """
        self.webhook_secret = webhook_secret
        self.token_repo = token_repo

    def verify_hmac_signature(
        self, payload: bytes, signature: str, timestamp: str | None = None
    ) -> bool:
        """
        Verifies HMAC SHA256 signature.

        If timestamp is provided, the message is: f"{timestamp}." + payload
        Otherwise, just the raw payload is used.

        Args:
            payload: The raw payload bytes.
            signature: The HMAC signature to verify.
            timestamp: Optional timestamp string to include in the message.

        Returns:
            True if signature matches, False otherwise.
        """
        try:
            message = f"{timestamp}.".encode() + payload if timestamp else payload

            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                message,
                hashlib.sha256,
            ).hexdigest()

            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"Error verifying HMAC signature: {e}")
            return False

    def validate_timestamp(self, timestamp_str: str) -> tuple[bool, str | None]:
        """
        Validates timestamp is within acceptable drift (300 seconds).

        Args:
            timestamp_str: Timestamp string to validate (Unix timestamp in seconds).

        Returns:
            (is_valid, error_message)
            - (True, None) if valid
            - (False, "error message") if invalid
        """
        try:
            timestamp = int(timestamp_str)
            current_time = int(time.time())
            drift = abs(current_time - timestamp)

            if drift > self.MAX_TIMESTAMP_DRIFT_SECONDS:
                error_msg = (
                    f"Timestamp drift of {drift} seconds exceeds "
                    f"maximum allowed {self.MAX_TIMESTAMP_DRIFT_SECONDS} seconds"
                )
                logger.warning(error_msg)
                return False, error_msg

            return True, None
        except ValueError as e:
            error_msg = f"Invalid timestamp format: {timestamp_str}. Error: {e}"
            logger.warning(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error validating timestamp: {e}"
            logger.error(error_msg)
            return False, error_msg

    def check_and_register_nonce(self, nonce: str) -> tuple[bool, str | None]:
        """
        Checks if nonce was already used (replay attack detection).
        If not used, registers it in the database.

        Args:
            nonce: Unique nonce string to check and register.

        Returns:
            (is_valid, error_message)
            - (True, None) if nonce is new and registered successfully
            - (False, "error message") if nonce was already used
        """
        try:
            # Create a hash of the nonce for storage
            nonce_hash = hashlib.sha256(nonce.encode()).hexdigest()

            # Check if nonce already exists
            existing_token = self.token_repo.get_by_hash(nonce_hash)

            if existing_token:
                if existing_token.is_used:
                    error_msg = "Nonce already used: replay attack detected"
                    logger.warning(error_msg)
                    return False, error_msg
                elif existing_token.is_expired:
                    # Token expired, but we should still reject it
                    error_msg = "Nonce expired: replay attack detected"
                    logger.warning(error_msg)
                    return False, error_msg
                else:
                    # Token exists but not marked as used yet - race condition
                    # Mark it as used to prevent double processing
                    self.token_repo.mark_used(existing_token.id)
                    logger.info(f"Nonce registered (race condition handled): {nonce[:16]}...")
                    return True, None

            # Create and save new token
            from usipipo_commons.domain.entities.crypto_transaction import WebhookToken

            expires_at = datetime.now(UTC) + timedelta(hours=self.NONCE_EXPIRY_HOURS)
            token = WebhookToken.create(token_hash=nonce_hash, purpose="tron_dealer")
            token.expires_at = expires_at

            self.token_repo.save(token)
            self.token_repo.mark_used(token.id)

            logger.info(f"Nonce registered successfully: {nonce[:16]}...")
            return True, None

        except Exception as e:
            error_msg = f"Error checking/registering nonce: {e}"
            logger.error(error_msg)
            return False, error_msg

    def cleanup_expired_nonces(self) -> int:
        """
        Cleans up expired nonces from database.

        Returns:
            Count of cleaned nonces.
        """
        try:
            count = self.token_repo.cleanup_expired()
            logger.info(f"Cleaned up {count} expired nonces")
            return count
        except Exception as e:
            logger.error(f"Error cleaning up expired nonces: {e}")
            return 0

    def extract_client_ip(self, request_headers: dict) -> str | None:
        """
        Extracts client IP from request headers.

        Checks X-Forwarded-For first, then X-Real-IP.

        Args:
            request_headers: Dictionary of request headers.

        Returns:
            IP address string or None if not found.
        """
        # Check X-Forwarded-For first (can contain multiple IPs)
        forwarded_for = request_headers.get("x-forwarded-for")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs: client, proxy1, proxy2, ...
            # The first one is the original client
            if isinstance(forwarded_for, str):
                ip = forwarded_for.split(",")[0].strip()
                if ip:
                    return ip

        # Check X-Real-IP
        real_ip = request_headers.get("x-real-ip")
        if real_ip and isinstance(real_ip, str):
            return real_ip.strip()

        return None

    def is_suspicious_request(self, payload: dict, headers: dict) -> tuple[bool, str | None]:
        """
        Detects suspicious requests based on payload structure.

        Checks:
        - Payload is not empty
        - Required fields exist: wallet_address, amount, tx_hash
        - Amount is positive
        - Wallet address starts with "0x" and is 42 chars

        Args:
            payload: Request payload dictionary.
            headers: Request headers dictionary.

        Returns:
            (is_suspicious, reason)
            - (False, None) if request appears valid
            - (True, "reason") if request is suspicious
        """
        # Check if payload is empty
        if not payload:
            reason = "Empty payload"
            logger.warning(f"Suspicious request: {reason}")
            return True, reason

        # Check required fields
        required_fields = ["wallet_address", "amount", "tx_hash"]
        for field in required_fields:
            if field not in payload:
                reason = f"Missing required field: {field}"
                logger.warning(f"Suspicious request: {reason}")
                return True, reason

        # Validate amount is positive
        amount = payload.get("amount")
        if not isinstance(amount, (int, float)) or amount <= 0:
            reason = f"Invalid amount: {amount} (must be positive number)"
            logger.warning(f"Suspicious request: {reason}")
            return True, reason

        # Validate wallet address format
        wallet_address = payload.get("wallet_address")
        if not isinstance(wallet_address, str):
            reason = f"Invalid wallet address type: {type(wallet_address)}"
            logger.warning(f"Suspicious request: {reason}")
            return True, reason

        if not wallet_address.startswith("0x"):
            reason = "Invalid wallet address format: must start with '0x'"
            logger.warning(f"Suspicious request: {reason}")
            return True, reason

        if len(wallet_address) != 42:
            reason = f"Invalid wallet address length: {len(wallet_address)} (expected 42)"
            logger.warning(f"Suspicious request: {reason}")
            return True, reason

        return False, None
