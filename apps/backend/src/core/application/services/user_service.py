"""Servicios de aplicación para gestión de usuarios."""

import logging
import uuid
from datetime import datetime

from passlib.context import CryptContext
from usipipo_commons.constants.plans import FREE_GB
from usipipo_commons.domain.entities.user import User

from src.core.application.exceptions import UserNotFoundError
from src.core.domain.interfaces.i_auth_provider_repository import IAuthProviderRepository
from src.core.domain.interfaces.i_user_repository import IUserRepository

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hashea contraseña."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica contraseña."""
    return pwd_context.verify(plain_password, hashed_password)


class UserService:
    """Servicio de aplicación para gestión de usuarios."""

    def __init__(
        self,
        user_repo: IUserRepository,
        auth_provider_repo: IAuthProviderRepository | None = None,
    ):
        self.user_repo = user_repo
        self.auth_provider_repo = auth_provider_repo

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Obtiene usuario por ID."""
        return self.user_repo.get_by_id(user_id)

    def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Obtiene usuario por Telegram ID."""
        return self.user_repo.get_by_telegram_id(telegram_id)

    def get_by_email(self, email: str) -> User | None:
        """Obtiene usuario por email."""
        return self.user_repo.get_by_email(email)

    def create_with_email(
        self,
        email: str,
        password: str,
        display_name: str,
    ) -> User:
        """
        Crea usuario con email/password.

        Args:
            email: Email del usuario
            password: Contraseña (se hashea automáticamente)
            display_name: Nombre para mostrar

        Returns:
            El usuario creado
        """
        # Check if email already exists
        existing = self.get_by_email(email)
        if existing:
            raise ValueError(f"User with email {email} already exists")

        # Generate unique referral code
        referral_code = f"ref_{uuid.uuid4().hex[:16]}"

        # Split display_name into first/last if contains space
        name_parts = display_name.strip().split(maxsplit=1)
        first_name = name_parts[0] if name_parts else None
        last_name = name_parts[1] if len(name_parts) > 1 else None

        new_user = User(
            id=uuid.uuid4(),
            telegram_id=0,  # No Telegram ID for email-only users
            username=email,  # Use email as username
            first_name=first_name,
            last_name=last_name,
            is_admin=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            balance_gb=FREE_GB,
            total_purchased_gb=0.0,
            referral_code=referral_code,
            referred_by=None,
        )

        created_user = self.user_repo.create(new_user)

        # Create auth_provider entry with password_hash
        if self.auth_provider_repo:
            password_hash = hash_password(password)
            self.auth_provider_repo.create(
                user_id=created_user.id,
                provider="email",
                provider_user_id=email,
                password_hash=password_hash,
            )

        return created_user

    def authenticate_email(
        self,
        email: str,
        password: str,
    ) -> User | None:
        """
        Autentica usuario con email/password.

        Args:
            email: Email del usuario
            password: Contraseña a verificar

        Returns:
            El usuario si las credenciales son válidas, None si no
        """
        user = self.get_by_email(email)
        if not user:
            return None

        # Verify password from auth_providers table
        if self.auth_provider_repo:
            auth_provider = self.auth_provider_repo.get_by_provider_and_id(
                provider="email",
                provider_user_id=email,
            )

            if auth_provider and auth_provider.password_hash:
                if verify_password(password, auth_provider.password_hash):
                    # Update last_used_at
                    self.auth_provider_repo.update_last_used(auth_provider.id)
                    return user

        return None

    def get_or_create_by_telegram(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        referral_code: str | None = None,
    ) -> User:
        """
        Obtiene usuario por Telegram ID o crea uno nuevo si no existe.

        Si se proporcionan datos de perfil de Telegram, actualiza el usuario existente
        o usa los datos para crear el nuevo usuario.

        Args:
            telegram_id: El ID de Telegram del usuario
            username: Username de Telegram (actualiza si cambia)
            first_name: Nombre del usuario
            last_name: Apellido del usuario
            referral_code: Código de referido opcional

        Returns:
            El usuario existente o el nuevo usuario creado
        """
        # Intentar obtener usuario existente
        existing_user = self.get_by_telegram_id(telegram_id)
        if existing_user:
            # Actualizar información de perfil si se proporcionó y es diferente
            updated = False
            new_username = username if username is not None else existing_user.username
            new_first_name = first_name if first_name is not None else existing_user.first_name
            new_last_name = last_name if last_name is not None else existing_user.last_name

            # Detectar si hay cambios en el perfil
            if (
                (username is not None and username != existing_user.username)
                or (first_name is not None and first_name != existing_user.first_name)
                or (last_name is not None and last_name != existing_user.last_name)
            ):
                updated = True
                logger.info(
                    f"Updating profile for telegram_id={telegram_id}: "
                    f"username={existing_user.username}->{new_username}, "
                    f"first_name={existing_user.first_name}->{new_first_name}, "
                    f"last_name={existing_user.last_name}->{new_last_name}"
                )

            updated_user = self.user_repo.update(
                User(
                    id=existing_user.id,
                    telegram_id=telegram_id,
                    username=new_username,
                    first_name=new_first_name,
                    last_name=new_last_name,
                    is_admin=existing_user.is_admin,
                    created_at=existing_user.created_at,
                    updated_at=datetime.utcnow() if updated else existing_user.updated_at,
                    balance_gb=existing_user.balance_gb,
                    total_purchased_gb=existing_user.total_purchased_gb,
                    referral_code=existing_user.referral_code,
                    referred_by=existing_user.referred_by,
                )
            )
            return updated_user

        # Generar código de referido único si no se proporciona
        # Formato: ref_ + 16 chars hex (max 20 chars para caber en DB)
        if not referral_code:
            referral_code = f"ref_{uuid.uuid4().hex[:16]}"

        # Crear nuevo usuario con datos de perfil de Telegram
        new_user = User(
            id=uuid.uuid4(),
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_admin=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            balance_gb=FREE_GB,  # 5 GB gratis por defecto
            total_purchased_gb=0.0,
            referral_code=referral_code,
            referred_by=None,
        )

        return self.user_repo.create(new_user)

    def create_user(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        referral_code: str | None = None,
        referred_by: uuid.UUID | None = None,
    ) -> User:
        """
        Crea un nuevo usuario.

        Args:
            telegram_id: El ID de Telegram del usuario
            username: Username de Telegram
            first_name: Nombre del usuario
            last_name: Apellido del usuario
            referral_code: Código de referido opcional
            referred_by: UUID del usuario que refirió (opcional)

        Returns:
            El usuario creado
        """
        # Verificar que no exista
        existing = self.get_by_telegram_id(telegram_id)
        if existing:
            raise ValueError(f"User with telegram_id {telegram_id} already exists")

        # Generar código de referido único si no se proporciona
        # Formato: ref_ + 16 chars hex (max 20 chars para caber en DB)
        if not referral_code:
            referral_code = f"ref_{uuid.uuid4().hex[:16]}"

        new_user = User(
            id=uuid.uuid4(),
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_admin=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            balance_gb=FREE_GB,
            total_purchased_gb=0.0,
            referral_code=referral_code,
            referred_by=referred_by,
        )

        return self.user_repo.create(new_user)

    def update_user(
        self,
        user_id: uuid.UUID,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        balance_gb: float | None = None,
    ) -> User:
        """
        Actualiza información del usuario.

        Args:
            user_id: UUID del usuario
            username: Nuevo username
            first_name: Nuevo nombre
            last_name: Nuevo apellido
            balance_gb: Nuevo saldo en GB

        Returns:
            El usuario actualizado

        Raises:
            UserNotFoundError: Si el usuario no existe
        """
        existing_user = self.get_by_id(user_id)
        if not existing_user:
            raise UserNotFoundError(f"User {user_id} not found")

        updated_user = User(
            id=existing_user.id,
            telegram_id=existing_user.telegram_id,
            username=username if username is not None else existing_user.username,
            first_name=first_name if first_name is not None else existing_user.first_name,
            last_name=last_name if last_name is not None else existing_user.last_name,
            is_admin=existing_user.is_admin,
            created_at=existing_user.created_at,
            updated_at=datetime.utcnow(),
            balance_gb=balance_gb if balance_gb is not None else existing_user.balance_gb,
            total_purchased_gb=existing_user.total_purchased_gb,
            referral_code=existing_user.referral_code,
            referred_by=existing_user.referred_by,
        )

        return self.user_repo.update(updated_user)

    def delete_user(self, user_id: uuid.UUID) -> bool:
        """
        Elimina un usuario.

        Args:
            user_id: UUID del usuario

        Returns:
            True si se eliminó, False si no existía
        """
        return self.user_repo.delete(user_id)

    def add_balance(self, user_id: uuid.UUID, amount_gb: float) -> User:
        """
        Agrega saldo en GB a un usuario.

        Args:
            user_id: UUID del usuario
            amount_gb: Cantidad de GB a agregar

        Returns:
            El usuario actualizado

        Raises:
            UserNotFoundError: Si el usuario no existe
        """
        existing_user = self.get_by_id(user_id)
        if not existing_user:
            raise UserNotFoundError(f"User {user_id} not found")

        updated_user = User(
            id=existing_user.id,
            telegram_id=existing_user.telegram_id,
            username=existing_user.username,
            first_name=existing_user.first_name,
            last_name=existing_user.last_name,
            is_admin=existing_user.is_admin,
            created_at=existing_user.created_at,
            updated_at=datetime.utcnow(),
            balance_gb=existing_user.balance_gb + amount_gb,
            total_purchased_gb=existing_user.total_purchased_gb + amount_gb,
            referral_code=existing_user.referral_code,
            referred_by=existing_user.referred_by,
        )

        return self.user_repo.update(updated_user)

    def apply_referral_bonus(
        self,
        referrer_user_id: uuid.UUID,
        referred_user_id: uuid.UUID,
    ) -> None:
        """
        Aplica bono de referido al usuario que refirió.

        Args:
            referrer_user_id: UUID del usuario que refirió
            referred_user_id: UUID del usuario que fue referido
        """
        # El bono se aplica cuando el referido realiza una compra
        # Esto se maneja en el servicio de pagos
        pass
