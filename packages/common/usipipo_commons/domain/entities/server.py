"""Server entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class Server:
    """VPN Server entity."""
    
    id: UUID
    name: str
    country_code: str
    country_name: str
    city: str | None = None
    region: str | None = None
    agent_url: str = ""
    agent_api_key: str = ""
    supports_outline: bool = True
    supports_wireguard: bool = True
    supports_trust_tunnel: bool = False
    status: str = "online"
    max_connections: int = 1000
    current_connections: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_heartbeat_at: datetime | None = None
