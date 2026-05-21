"""Referral entity for uSipipo ecosystem."""

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Referral:
    """Entidad que representa una relación de referido."""

    referrer_id: uuid.UUID
    referred_id: uuid.UUID
    id: Optional[uuid.UUID] = None
    created_at: Optional[datetime] = None
    is_active: bool = True
    bonus_applied: bool = False

    def __post_init__(self):
        if self.id is None:
            self.id = uuid.uuid4()
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
