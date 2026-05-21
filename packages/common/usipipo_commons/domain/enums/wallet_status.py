from enum import Enum


class WalletStatus(str, Enum):
    """Estado de una wallet BSC."""
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    AVAILABLE = "available"
    IN_USE = "in_use"
