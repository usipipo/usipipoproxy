"""
Admin Key Info entity for uSipipo Commons.

This module contains the AdminKeyInfo dataclass for administrative key information.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AdminKeyInfo:
    """
    Administrative key information.

    This entity contains VPN key data displayed in admin panels
    and used for administrative operations.
    """

    key_id: str
    user_id: uuid.UUID
    user_name: str
    key_type: str
    key_name: str
    access_url: Optional[str]
    created_at: datetime
    last_used: Optional[datetime]
    data_limit: int
    data_used: int
    is_active: bool
    server_status: str
