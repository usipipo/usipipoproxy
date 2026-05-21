from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class User:
    """Entidad de usuario compartida."""
    id: UUID
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    balance_gb: float
    total_purchased_gb: float
    referral_code: str
    referred_by: Optional[UUID]
    referral_credits: int = 0
    purchase_count: int = 0
    loyalty_bonus_percent: int = 0
    welcome_bonus_used: bool = False
    referred_users_with_purchase: int = 0
    current_billing_id: Optional[UUID] = None
    has_pending_debt: bool = False
    consumption_mode_enabled: bool = False

    def mark_as_has_debt(self) -> None:
        """Mark user as having pending debt."""
        self.has_pending_debt = True

    def clear_debt(self) -> None:
        """Clear user debt."""
        self.has_pending_debt = False

    def activate_consumption_mode(self, billing_id: UUID | None = None) -> None:
        """Enable consumption mode and optionally link to a billing cycle."""
        self.consumption_mode_enabled = True
        if billing_id is not None:
            self.current_billing_id = billing_id

    def deactivate_consumption_mode(self) -> None:
        """Disable consumption mode."""
        self.consumption_mode_enabled = False

    def to_dict(self) -> dict:
        """Convierte a diccionario para serialización."""
        return {
            "id": str(self.id),
            "telegram_id": self.telegram_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "balance_gb": self.balance_gb,
            "total_purchased_gb": self.total_purchased_gb,
            "referral_code": self.referral_code,
            "referred_by": str(self.referred_by) if self.referred_by else None,
            "referral_credits": self.referral_credits,
            "purchase_count": self.purchase_count,
            "loyalty_bonus_percent": self.loyalty_bonus_percent,
            "welcome_bonus_used": self.welcome_bonus_used,
            "referred_users_with_purchase": self.referred_users_with_purchase,
        }
