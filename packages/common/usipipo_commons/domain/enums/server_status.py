"""Server status enum."""

from enum import Enum


class ServerStatus(str, Enum):
    """Server status."""
    
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
