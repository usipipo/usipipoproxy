"""
VPN Key factory for creating test keys.
"""

import uuid

from src.core.domain.entities.vpn_key import KeyType, VpnKey


class VpnKeyFactory:
    """Factory for creating test VPN keys."""

    @staticmethod
    def create(
        user_id: uuid.UUID,
        server_id: uuid.UUID,
        name: str = None,
        key_type: KeyType = KeyType.WIREGUARD,
        data_limit_gb: float = 10.0,
        external_id: str = None,
    ) -> VpnKey:
        """Create a test VPN key."""
        return VpnKey(
            id=uuid.uuid4(),
            user_id=user_id,
            server_id=server_id,
            name=name or f"Test Key {uuid.uuid4().hex[:8]}",
            key_type=key_type,
            data_limit_gb=data_limit_gb,
            external_id=external_id or f"test-ext-{uuid.uuid4().hex[:8]}",
            is_active=True,
        )
