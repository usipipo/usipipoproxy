"""TronDealer payment gateway client."""

import hashlib
import hmac
import logging
from typing import Any

import httpx

from src.shared.config import settings

logger = logging.getLogger(__name__)


class TronDealerClient:
    """Client for TronDealer API."""

    BASE_URL = "https://api.trondealer.com"

    def __init__(self):
        self.api_key = settings.TRON_DEALER_API_KEY
        self.webhook_secret = settings.TRON_DEALER_WEBHOOK_SECRET
        self.http = httpx.AsyncClient(base_url=self.BASE_URL)

    async def create_invoice(
        self,
        amount_usd: float,
        network: str,
        external_id: str,
    ) -> dict[str, Any]:
        """Creates an invoice in TronDealer."""
        try:
            response = await self.http.post(
                "/v1/invoice",
                json={
                    "amount": amount_usd,
                    "currency": "USD",
                    "network": network,
                    "external_id": external_id,
                },
                headers={"X-API-Key": self.api_key},
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create TronDealer invoice: {e}")
            raise

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        timestamp: str | None = None,
    ) -> bool:
        """
        Verifies webhook HMAC-SHA256 signature.

        Supports two verification modes:
        - Without timestamp (legacy): verifies signature of payload only
        - With timestamp (enhanced): verifies signature of "{timestamp}." + payload

        Args:
            payload: Raw webhook request body as bytes
            signature: HMAC signature from X-Signature header
            timestamp: Optional Unix timestamp from X-Timestamp header

        Returns:
            bool: True if signature is valid, False otherwise

        Note:
            When timestamp is provided, the message to sign is:
            f"{timestamp}." + payload

            This enhanced mode provides protection against replay attacks
            when combined with timestamp validation.
        """
        try:
            if timestamp:
                # Enhanced verification with timestamp
                message = f"{timestamp}.".encode() + payload
                logger.debug("Verifying webhook signature with timestamp")
            else:
                # Legacy verification without timestamp
                message = payload
                logger.debug("Verifying webhook signature (legacy mode)")

            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                message,
                hashlib.sha256,
            ).hexdigest()

            is_valid = hmac.compare_digest(expected_signature, signature)

            if is_valid:
                logger.info("Webhook signature verification successful")
            else:
                logger.warning("Webhook signature verification failed")

            return is_valid
        except Exception as e:
            logger.error(f"Failed to verify webhook signature: {e}")
            return False

    def verify_webhook_signature_with_timestamp(
        self,
        payload: bytes,
        signature: str,
        timestamp: str,
    ) -> bool:
        """
        Verifies webhook signature with timestamp.

        The message to sign is: f"{timestamp}." + payload

        Args:
            payload: Raw webhook request body as bytes
            signature: HMAC signature from X-Signature header
            timestamp: Unix timestamp from X-Timestamp header

        Returns:
            bool: True if signature is valid, False otherwise

        Note:
            This uses the same HMAC-SHA256 verification as the basic
            verify_webhook_signature method, but includes the timestamp
            in the message for enhanced security.

            This method is provided for explicit clarity when timestamp-based
            verification is required. It is functionally equivalent to calling
            verify_webhook_signature(payload, signature, timestamp).
        """
        try:
            # Construct message with timestamp prefix
            message = f"{timestamp}.".encode() + payload

            # Compute expected HMAC-SHA256 signature
            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                message,
                hashlib.sha256,
            ).hexdigest()

            # Constant-time comparison to prevent timing attacks
            is_valid = hmac.compare_digest(expected_signature, signature)

            if is_valid:
                logger.info(
                    "Webhook signature verification successful with timestamp",
                    extra={"timestamp": timestamp},
                )
            else:
                logger.warning(
                    "Webhook signature verification failed with timestamp",
                    extra={"timestamp": timestamp},
                )

            return is_valid
        except Exception as e:
            logger.error(
                f"Failed to verify webhook signature with timestamp: {e}",
                extra={"timestamp": timestamp},
            )
            return False

    async def close(self) -> None:
        """Closes the HTTP client."""
        await self.http.aclose()
