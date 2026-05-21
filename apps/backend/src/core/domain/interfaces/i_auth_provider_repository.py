"""Interfaz de repositorio para auth providers."""

import uuid
from abc import ABC, abstractmethod

from src.infrastructure.persistence.models.auth_provider_model import AuthProviderModel


class IAuthProviderRepository(ABC):
    """Contrato para repositorio de auth providers."""

    @abstractmethod
    def get_by_provider_and_id(
        self,
        provider: str,
        provider_user_id: str,
    ) -> AuthProviderModel | None:
        """Obtiene auth provider por provider y provider_user_id."""
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: uuid.UUID) -> list[AuthProviderModel]:
        """Obtiene todos los auth providers de un usuario."""
        pass

    @abstractmethod
    def create(
        self,
        user_id: uuid.UUID,
        provider: str,
        provider_user_id: str,
        password_hash: str | None = None,
    ) -> AuthProviderModel:
        """Crea un nuevo auth provider."""
        pass

    @abstractmethod
    def update_password_hash(
        self,
        user_id: uuid.UUID,
        provider: str,
        password_hash: str,
    ) -> bool:
        """Actualiza hash de contraseña."""
        pass

    @abstractmethod
    def update_last_used(self, auth_provider_id: uuid.UUID) -> bool:
        """Actualiza last_used_at del auth provider."""
        pass

    @abstractmethod
    def delete(self, auth_provider_id: uuid.UUID) -> bool:
        """Elimina auth provider."""
        pass

    @abstractmethod
    def delete_by_user_id(self, user_id: uuid.UUID) -> int:
        """Elimina todos los auth providers de un usuario."""
        pass
