"""Interfaces de repositorio para la capa de dominio."""

from abc import ABC, abstractmethod
from uuid import UUID

from usipipo_commons.domain.entities.user import User


class IUserRepository(ABC):
    """Contrato para repositorio de usuarios."""

    @abstractmethod
    def get_all(self) -> list[User]:
        """Obtiene todos los usuarios."""
        pass

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None:
        """Obtiene usuario por ID."""
        pass

    @abstractmethod
    def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Obtiene usuario por Telegram ID."""
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        """Obtiene usuario por email."""
        pass

    @abstractmethod
    def get_by_referral_code(self, referral_code: str) -> User | None:
        """Obtiene usuario por código de referido."""
        pass

    @abstractmethod
    def update_referral_credits(self, user_id: UUID, credits: int) -> bool:
        """Actualiza los créditos de referido de un usuario."""
        pass

    @abstractmethod
    def create(self, user: User) -> User:
        """Crea un nuevo usuario."""
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        """Actualiza usuario existente."""
        pass

    @abstractmethod
    def delete(self, user_id: UUID) -> bool:
        """Elimina usuario."""
        pass
