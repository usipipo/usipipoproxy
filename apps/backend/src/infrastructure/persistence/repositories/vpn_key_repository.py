"""VPN Key repository implementation with SQLAlchemy."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from usipipo_commons.domain.entities.vpn_key import VpnKey

from src.core.domain.interfaces.i_vpn_key_repository import IVpnKeyRepository
from src.infrastructure.persistence.models.vpn_key_model import VpnKeyModel


class VpnKeyRepository(IVpnKeyRepository):
    """SQLAlchemy implementation of VPN key repository."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, key_id: UUID) -> VpnKey | None:
        """Gets VPN key by ID."""
        result = self.session.execute(select(VpnKeyModel).where(VpnKeyModel.id == key_id))
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    def get_by_user_id(self, user_id: UUID) -> list[VpnKey]:
        """Gets all VPN keys for a user."""
        result = self.session.execute(
            select(VpnKeyModel)
            .where(VpnKeyModel.user_id == user_id)
            .order_by(VpnKeyModel.created_at.desc())
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    def create(self, vpn_key: VpnKey) -> VpnKey:
        """Creates a new VPN key."""
        model = VpnKeyModel.from_entity(vpn_key)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model.to_entity()

    def update(self, vpn_key: VpnKey) -> VpnKey:
        """
        Updates an existing VPN key.

        Note: server_id is intentionally NOT updated after creation.
        The server association is immutable - if a key needs to be moved
        to a different server, it should be deleted and recreated.
        """
        # Fetch existing model first to ensure it's attached to this session
        result = self.session.execute(select(VpnKeyModel).where(VpnKeyModel.id == vpn_key.id))
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"VPN key {vpn_key.id} not found")

        # Update fields from entity
        model.user_id = vpn_key.user_id
        model.name = vpn_key.name
        model.key_type = vpn_key.key_type
        model.status = vpn_key.status
        model.key_data = vpn_key.key_data
        model.external_id = vpn_key.external_id
        model.is_active = vpn_key.is_active
        model.expires_at = vpn_key.expires_at
        model.last_seen_at = vpn_key.last_seen_at
        model.used_bytes = vpn_key.used_bytes
        model.data_limit_bytes = vpn_key.data_limit_bytes
        model.billing_reset_at = vpn_key.billing_reset_at

        self.session.commit()
        self.session.refresh(model)
        return model.to_entity()

    def delete(self, key_id: UUID) -> bool:
        """Deletes a VPN key."""
        result = self.session.execute(select(VpnKeyModel).where(VpnKeyModel.id == key_id))
        model = result.scalar_one_or_none()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

    def update_usage(self, key_id: UUID, data_used_gb: float) -> bool:
        """Updates data usage for a VPN key."""
        result = self.session.execute(select(VpnKeyModel).where(VpnKeyModel.id == key_id))
        model = result.scalar_one_or_none()
        if model:
            model.used_bytes = int(data_used_gb * 1024**3)  # Convert GB to bytes
            model.last_seen_at = datetime.now(UTC)
            self.session.commit()
            return True
        return False

    def reset_data_usage(self, key_id: UUID) -> bool:
        """Resets data usage for a VPN key (new billing cycle)."""
        result = self.session.execute(select(VpnKeyModel).where(VpnKeyModel.id == key_id))
        model = result.scalar_one_or_none()
        if model:
            model.used_bytes = 0
            model.billing_reset_at = datetime.now(UTC)
            self.session.commit()
            return True
        return False

    def update_data_limit(self, key_id: UUID, data_limit_gb: float) -> bool:
        """Updates data limit for a VPN key."""
        result = self.session.execute(select(VpnKeyModel).where(VpnKeyModel.id == key_id))
        model = result.scalar_one_or_none()
        if model:
            model.data_limit_bytes = int(data_limit_gb * 1024**3)  # Convert GB to bytes
            self.session.commit()
            return True
        return False

    def get_keys_needing_reset(self) -> list[VpnKey]:
        """Gets keys that need billing cycle reset."""
        now = datetime.now(UTC)
        result = self.session.execute(
            select(VpnKeyModel).where(
                VpnKeyModel.billing_reset_at < now,
                VpnKeyModel.is_active,
            )
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    def get_all_active(self) -> list[VpnKey]:
        """Gets all active VPN keys in the system."""
        result = self.session.execute(select(VpnKeyModel).where(VpnKeyModel.is_active))
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    def get_all_keys(self) -> list[VpnKey]:
        """Gets all VPN keys in the system (active and inactive)."""
        result = self.session.execute(select(VpnKeyModel))
        models = result.scalars().all()
        return [model.to_entity() for model in models]
