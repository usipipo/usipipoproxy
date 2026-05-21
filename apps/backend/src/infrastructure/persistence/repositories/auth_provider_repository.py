"""Repositorio de proveedores de autenticación con SQLAlchemy."""

import uuid
from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from src.core.domain.interfaces.i_auth_provider_repository import IAuthProviderRepository
from src.infrastructure.persistence.database import get_execute_rowcount
from src.infrastructure.persistence.models.auth_provider_model import AuthProviderModel


class AuthProviderRepository(IAuthProviderRepository):
    """Implementación de repositorio de auth providers con SQLAlchemy."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_provider_and_id(
        self,
        provider: str,
        provider_user_id: str,
    ) -> AuthProviderModel | None:
        """
        Obtiene auth provider por provider y provider_user_id.

        Args:
            provider: Tipo de provider (telegram, email, google, etc.)
            provider_user_id: ID único dentro del provider

        Returns:
            AuthProviderModel o None si no existe
        """
        result = self.session.execute(
            select(AuthProviderModel).where(
                AuthProviderModel.provider == provider,
                AuthProviderModel.provider_user_id == provider_user_id,
            )
        )
        return result.scalar_one_or_none()

    def get_by_user_id(self, user_id: uuid.UUID) -> list[AuthProviderModel]:
        """
        Obtiene todos los auth providers de un usuario.

        Args:
            user_id: UUID del usuario

        Returns:
            Lista de auth providers
        """
        result = self.session.execute(
            select(AuthProviderModel).where(AuthProviderModel.user_id == user_id)
        )
        return list(result.scalars().all())

    def create(
        self,
        user_id: uuid.UUID,
        provider: str,
        provider_user_id: str,
        password_hash: str | None = None,
    ) -> AuthProviderModel:
        """
        Crea un nuevo auth provider.

        Args:
            user_id: UUID del usuario
            provider: Tipo de provider
            provider_user_id: ID único dentro del provider
            password_hash: Hash de contraseña (solo para email)

        Returns:
            AuthProviderModel creado
        """
        auth_provider = AuthProviderModel(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            password_hash=password_hash,
        )
        self.session.add(auth_provider)
        self.session.commit()
        self.session.refresh(auth_provider)
        return auth_provider

    def update_password_hash(
        self,
        user_id: uuid.UUID,
        provider: str,
        password_hash: str,
    ) -> bool:
        """
        Actualiza hash de contraseña.

        Args:
            user_id: UUID del usuario
            provider: Tipo de provider
            password_hash: Nuevo hash de contraseña

        Returns:
            True si se actualizó, False si no existe
        """
        result = self.session.execute(
            update(AuthProviderModel)
            .where(
                AuthProviderModel.user_id == user_id,
                AuthProviderModel.provider == provider,
            )
            .values(password_hash=password_hash)
        )
        self.session.commit()
        return get_execute_rowcount(result) > 0

    def update_last_used(self, auth_provider_id: uuid.UUID) -> bool:
        """
        Actualiza last_used_at del auth provider.

        Args:
            auth_provider_id: UUID del auth provider

        Returns:
            True si se actualizó, False si no existe
        """
        result = self.session.execute(
            update(AuthProviderModel)
            .where(AuthProviderModel.id == auth_provider_id)
            .values(last_used_at=datetime.utcnow())
        )
        self.session.commit()
        return get_execute_rowcount(result) > 0

    def delete(self, auth_provider_id: uuid.UUID) -> bool:
        """
        Elimina auth provider.

        Args:
            auth_provider_id: UUID del auth provider

        Returns:
            True si se eliminó, False si no existe
        """
        result = self.session.execute(
            delete(AuthProviderModel).where(AuthProviderModel.id == auth_provider_id)
        )
        self.session.commit()
        return get_execute_rowcount(result) > 0

    def delete_by_user_id(self, user_id: uuid.UUID) -> int:
        """
        Elimina todos los auth providers de un usuario.

        Args:
            user_id: UUID del usuario

        Returns:
            Cantidad de providers eliminados
        """
        result = self.session.execute(
            delete(AuthProviderModel).where(AuthProviderModel.user_id == user_id)
        )
        self.session.commit()
        return get_execute_rowcount(result)
