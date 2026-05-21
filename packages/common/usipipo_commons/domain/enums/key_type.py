"""KeyType enum - Define los tipos de VPN que soporta el sistema."""

from enum import Enum


class KeyType(str, Enum):
    """Define los tipos de VPN que soporta el sistema."""

    OUTLINE = "outline"
    WIREGUARD = "wireguard"
    TRUSTTUNNEL = "trusttunnel"
