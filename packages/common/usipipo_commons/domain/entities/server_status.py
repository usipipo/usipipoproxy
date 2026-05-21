"""
Server Status entity for uSipipo Commons.

This module contains the ServerStatus dataclass for VPN server status information.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ServerStatus:
    """
    VPN server status information.
    
    This entity contains server health and status data
    used for monitoring and administrative operations.
    """

    server_type: str
    is_healthy: bool
    total_keys: int
    active_keys: int
    version: Optional[str]
    uptime: Optional[str]
    error_message: Optional[str] = None
