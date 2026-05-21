"""Subscription transaction domain entity."""

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional


class SubscriptionTransactionStatus(str, Enum):
    """Subscription transaction statuses."""

    PENDING = "pending"
    COMPLETED = "completed"
    EXPIRED = "expired"
    FAILED = "failed"


@dataclass
class SubscriptionTransaction:
    """Represents a subscription transaction for tracking and idempotency."""

    transaction_id: str
    user_id: uuid.UUID  # ← Changed from int to UUID
    plan_type: str
    amount_stars: int
    payload: str
    status: SubscriptionTransactionStatus = SubscriptionTransactionStatus.PENDING
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    id: Optional[uuid.UUID] = None

    def __post_init__(self):
        if self.id is None:
            self.id = uuid.uuid4()
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        # Transactions expire after 30 minutes
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(minutes=30)

    @property
    def is_pending(self) -> bool:
        """True if transaction is still pending."""
        return self.status == SubscriptionTransactionStatus.PENDING

    @property
    def is_completed(self) -> bool:
        """True if transaction has been completed."""
        return self.status == SubscriptionTransactionStatus.COMPLETED

    @property
    def is_expired(self) -> bool:
        """True if transaction has expired."""
        return self.status == SubscriptionTransactionStatus.EXPIRED or (
            self.status == SubscriptionTransactionStatus.PENDING
            and self.expires_at is not None
            and datetime.now(timezone.utc) > self.expires_at
        )

    def mark_completed(self) -> None:
        """Mark transaction as completed."""
        self.status = SubscriptionTransactionStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)

    def mark_failed(self) -> None:
        """Mark transaction as failed."""
        self.status = SubscriptionTransactionStatus.FAILED

    def mark_expired(self) -> None:
        """Mark transaction as expired."""
        self.status = SubscriptionTransactionStatus.EXPIRED
