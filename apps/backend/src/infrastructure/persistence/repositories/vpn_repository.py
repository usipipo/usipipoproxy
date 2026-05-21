"""Repositorio de claves VPN con SQLAlchemy."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from usipipo_commons.domain.entities.vpn_key import VpnKey

from src.core.domain.interfaces.i_vpn_repository import IVPNRepository
from src.infrastructure.persistence.models.vpn_key_model import VpnKeyModel


class VpnRepository(IVPNRepository):
    """Implementación de repositorio de claves VPN con SQLAlchemy."""

    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[VpnKey]:
        """
        Obtiene todas las claves VPN.

        Returns:
            Lista de todas las claves VPN
        """
        result = self.session.execute(select(VpnKeyModel))
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    def get_by_id(self, key_id: UUID) -> VpnKey | None:
        """
        Obtiene clave VPN por ID.

        Args:
            key_id: UUID de la clave

        Returns:
            VpnKey o None si no existe
        """
        result = self.session.execute(
            select(VpnKeyModel).where(VpnKeyModel.id == str(key_id))
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    def get_by_user_id(self, user_id: UUID) -> list[VpnKey]:
        """
        Obtiene todas las claves VPN de un usuario.

        Args:
            user_id: UUID del usuario

        Returns:
            Lista de claves VPN
        """
        result = self.session.execute(
            select(VpnKeyModel).where(VpnKeyModel.user_id == user_id)
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    def create(self, vpn_key: VpnKey) -> VpnKey:
        """
        Crea una nueva clave VPN.

        Args:
            vpn_key: Clave VPN a crear

        Returns:
            Clave VPN creada
        """
        model = VpnKeyModel.from_entity(vpn_key)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model.to_entity()

    def update(self, vpn_key: VpnKey) -> VpnKey:
        """
        Actualiza clave VPN existente.

        Args:
            vpn_key: Clave VPN con datos actualizados

        Returns:
            Clave VPN actualizada
        """
        model = VpnKeyModel.from_entity(vpn_key)
        self.session.merge(model)
        self.session.commit()
        self.session.refresh(model)
        return model.to_entity()

    def delete(self, key_id: UUID) -> bool:
        """
        Elimina clave VPN.

        Args:
            key_id: UUID de la clave

        Returns:
            True si se eliminó, False si no existía
        """
        result = self.session.execute(
            select(VpnKeyModel).where(VpnKeyModel.id == str(key_id))
        )
        model = result.scalar_one_or_none()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False
