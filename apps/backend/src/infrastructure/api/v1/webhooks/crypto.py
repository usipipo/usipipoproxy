"""Crypto payment webhook routes."""

import logging
import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.core.application.services.notification_service import NotificationService
from src.core.application.services.payment_service import PaymentService
from src.core.application.services.webhook_security_service import WebhookSecurityService
from src.infrastructure.persistence.database import get_db
from src.infrastructure.persistence.repositories.payment_repository import (
    PaymentRepository,
)
from src.infrastructure.persistence.repositories.user_repository import UserRepository
from src.infrastructure.persistence.repositories.webhook_token_repository import (
    WebhookTokenRepository,
)
from src.shared.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


# =============================================================================
# Pydantic Models
# =============================================================================


class TronDealerWebhookPayload(BaseModel):
    """Schema for TronDealer webhook payload."""

    wallet_address: str = Field(..., min_length=42, max_length=42)
    amount: float = Field(..., gt=0)
    tx_hash: str = Field(..., min_length=66, max_length=66)
    token_symbol: str = Field(default="USDT")
    confirmations: int = Field(default=0, ge=0)
    timestamp: str | None = None
    nonce: str | None = None


# =============================================================================
# Dependencies
# =============================================================================


def get_webhook_security_service(db: Session = Depends(get_db)) -> WebhookSecurityService:
    """Gets WebhookSecurityService instance."""
    # Use the session from dependency injection for proper testability
    token_repo = WebhookTokenRepository(db)
    return WebhookSecurityService(
        webhook_secret=settings.TRON_DEALER_WEBHOOK_SECRET,
        token_repo=token_repo,
    )


# =============================================================================
# Webhook Routes
# =============================================================================


@router.post("/crypto")
async def tron_dealer_webhook(
    request: Request,
    x_signature: str = Header(..., description="Webhook signature"),
    x_timestamp: str = Header(..., description="Webhook timestamp"),
    x_nonce: str = Header(..., description="Webhook nonce for replay protection"),
    security_service: WebhookSecurityService = Depends(get_webhook_security_service),
    db: Session = Depends(get_db),
):
    """
    Webhook from TronDealer for payment confirmation.

    TronDealer sends POST when a payment is confirmed.

    Security:
    - HMAC SHA256 signature verification
    - Timestamp validation (max drift: 300 seconds)
    - Nonce-based replay attack protection
    - Suspicious payload detection
    - Client IP logging
    - Request ID tracing

    Headers Required:
    - X-Signature: HMAC SHA256 signature
    - X-Timestamp: Unix timestamp in seconds
    - X-Nonce: Unique nonce for replay protection

    Returns:
    - 200: Successfully processed
    - 401: Invalid signature
    - 400: Expired timestamp, replayed nonce, or suspicious payload
    """
    # Generate request ID for tracing
    request_id = str(uuid.uuid4())[:8]

    # Extract raw body
    raw_body = await request.body()

    # Step 1: Verify HMAC signature (with timestamp)
    if not security_service.verify_hmac_signature(
        payload=raw_body, signature=x_signature, timestamp=x_timestamp
    ):
        logger.warning(f"[{request_id}] Invalid webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Step 2: Validate timestamp (drift < 300s)
    is_timestamp_valid, timestamp_error = security_service.validate_timestamp(x_timestamp)
    if not is_timestamp_valid:
        logger.warning(f"[{request_id}] {timestamp_error}")
        raise HTTPException(status_code=400, detail=timestamp_error)

    # Step 3: Check and register nonce (replay protection)
    is_nonce_valid, nonce_error = security_service.check_and_register_nonce(x_nonce)
    if not is_nonce_valid:
        logger.warning(f"[{request_id}] {nonce_error}")
        raise HTTPException(status_code=400, detail=nonce_error)

    # Parse JSON payload
    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"[{request_id}] Failed to parse JSON payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Step 4: Check for suspicious request
    headers_dict = dict(request.headers)
    is_suspicious, suspicious_reason = security_service.is_suspicious_request(data, headers_dict)
    if is_suspicious:
        logger.warning(f"[{request_id}] Suspicious request: {suspicious_reason}")
        raise HTTPException(status_code=400, detail=suspicious_reason)

    # Step 5: Extract client IP for logging
    client_ip = security_service.extract_client_ip(headers_dict)
    if not client_ip:
        client_ip = request.client.host if request.client else "unknown"

    # Step 6: Log request with client IP and request_id
    logger.info(f"[{request_id}] Webhook received from IP: {client_ip}")

    # Validate payload structure using Pydantic model
    try:
        payload = TronDealerWebhookPayload(
            wallet_address=data.get("wallet_address"),
            amount=data.get("amount"),
            tx_hash=data.get("tx_hash"),
            token_symbol=data.get("token_symbol", "USDT"),
            confirmations=data.get("confirmations", 0),
            timestamp=data.get("timestamp"),
            nonce=data.get("nonce"),
        )
    except Exception as e:
        logger.error(f"[{request_id}] Invalid payload structure: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")

    # Log payment details
    logger.info(
        f"[{request_id}] Processing payment: {payload.amount} {payload.token_symbol} "
        f"to wallet {payload.wallet_address}"
    )

    # Step 7: Process payment
    payment_id_str = data.get("external_id")
    transaction_hash = data.get("transaction_hash") or payload.tx_hash
    amount_usd = data.get("amount") or payload.amount
    payment_status = data.get("status", "completed")

    if payment_status != "completed":
        logger.info(f"[{request_id}] Ignoring webhook: payment status is '{payment_status}'")
        return {"status": "ignored", "reason": f"Payment status: {payment_status}"}

    try:
        payment_id = UUID(payment_id_str)
    except (ValueError, TypeError):
        logger.error(f"[{request_id}] Invalid payment_id in webhook: {payment_id_str}")
        raise HTTPException(status_code=400, detail="Invalid payment_id")

    try:
        payment_repo = PaymentRepository(db)
        user_repo = UserRepository(db)
        payment_service = PaymentService(payment_repo, user_repo)
        notification_service = NotificationService(user_repo)

        payment_service.complete_payment(
            payment_id=payment_id,
            transaction_hash=transaction_hash,
        )

        notification_service.notify_payment_completed(
            user_id=payment_id,
            amount_usd=amount_usd,
            gb_purchased=data.get("gb_purchased", 0),
        )

        notification_service.close()

    except Exception as e:
        logger.error(f"[{request_id}] Failed to complete payment {payment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process payment: {e}")

    # Step 8: Return success
    logger.info(f"[{request_id}] Webhook processed successfully")
    return {"status": "success"}
