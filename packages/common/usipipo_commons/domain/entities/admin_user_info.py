"""
Admin User Info entity for uSipipo Commons.

This module contains the AdminUserInfo dataclass for administrative user information.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AdminUserInfo:
    """
    Administrative user information.

    This entity contains user data displayed in admin panels
    and used for administrative operations.
    """

    user_id: uuid.UUID
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    total_keys: int
    active_keys: int
    stars_balance: int = 0  # Deprecated - kept for compatibility
    total_deposited: int = 0  # Now represents referral_credits
    referral_credits: int = 0
    registration_date: Optional[datetime] = None
    last_activity: Optional[datetime] = None
