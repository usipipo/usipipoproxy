"""Dependencias para autenticación y autorización."""

import logging
from uuid import UUID

import redis.asyncio as redis
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from usipipo_commons.domain.entities.user import User

from src.core.application.services.data_package_service import DataPackageService
from src.core.application.services.referral_service import ReferralService
from src.core.application.services.server_registry_service import ServerRegistryService
from src.core.application.services.subscription_service import SubscriptionService
from src.core.application.services.ticket_service import TicketService
from src.core.application.services.user_service import UserService
from src.core.application.services.vpn_service import VpnService
from src.core.application.services.wallet_management_service import WalletManagementService
from src.core.application.services.wallet_pool_service import WalletPoolService
from src.infrastructure.api_clients.client_tron_dealer import TronDealerClient
from src.infrastructure.persistence.database import get_db
from src.infrastructure.persistence.repositories.auth_provider_repository import (
    AuthProviderRepository,
)
from src.infrastructure.persistence.repositories.crypto_order_repository import (
    CryptoOrderRepository,
)
from src.infrastructure.persistence.repositories.data_package_repository import (
    DataPackageRepository,
)
from src.infrastructure.persistence.repositories.referral_repository import ReferralRepository
from src.infrastructure.persistence.repositories.subscription_repository import (
    SubscriptionRepository,
)
from src.infrastructure.persistence.repositories.ticket_repository import TicketRepository
from src.infrastructure.persistence.repositories.user_repository import UserRepository
from src.infrastructure.persistence.repositories.vpn_repository import VpnRepository
from src.infrastructure.persistence.repositories.wallet_pool_repository import WalletPoolRepository
from src.infrastructure.persistence.repositories.wallet_repository import WalletRepository
from src.infrastructure.redis import RedisPool
from src.infrastructure.vpn_providers.wireguard_client import WireGuardClient
from src.shared.security.jwt import decode_jwt_token, is_token_revoked

logger = logging.getLogger(__name__)
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials

    if is_token_revoked(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_jwt_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = UUID(payload["sub"])

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Requiere que el usuario sea admin.

    Args:
        current_user: Usuario actual

    Returns:
        User: Usuario admin

    Raises:
        HTTPException: 403 si el usuario no es admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user


def get_user_service(
    db: Session = Depends(get_db),
) -> UserService:
    """
    Dependency para obtener UserService.

    Args:
        db: Sesión de base de datos

    Returns:
        UserService: Servicio de usuarios
    """
    user_repo = UserRepository(db)
    auth_provider_repo = AuthProviderRepository(db)
    return UserService(user_repo, auth_provider_repo)


def get_vpn_service(
    db: Session = Depends(get_db),
) -> VpnService:
    """
    Dependency para obtener VpnService.

    Args:
        db: Sesión de base de datos

    Returns:
        VpnService: Servicio de VPN
    """
    user_repo = UserRepository(db)
    vpn_repo = VpnRepository(db)
    server_registry_service = ServerRegistryService(db)
    wireguard_client = WireGuardClient()
    return VpnService(user_repo, vpn_repo, server_registry_service, wireguard_client)


def get_subscription_service(
    db: Session = Depends(get_db),
) -> SubscriptionService:
    """
    Dependency para obtener SubscriptionService.

    Args:
        db: Sesión de base de datos

    Returns:
        SubscriptionService: Servicio de suscripciones
    """
    subscription_repo = SubscriptionRepository(db)
    user_repo = UserRepository(db)
    return SubscriptionService(subscription_repo, user_repo)


def get_ticket_service(
    db: Session = Depends(get_db),
) -> TicketService:
    """
    Dependency para obtener TicketService.

    Args:
        db: Sesión de base de datos

    Returns:
        TicketService: Servicio de tickets
    """
    ticket_repo = TicketRepository(db)
    return TicketService(ticket_repo)


def get_data_package_service(
    db: Session = Depends(get_db),
) -> DataPackageService:
    """
    Dependency para obtener DataPackageService.

    Args:
        db: Sesión de base de datos

    Returns:
        DataPackageService: Servicio de paquetes de datos
    """
    package_repo = DataPackageRepository(db)
    user_repo = UserRepository(db)
    return DataPackageService(package_repo, user_repo)


def get_referral_service(
    db: Session = Depends(get_db),
) -> ReferralService:
    """
    Dependency para obtener ReferralService.

    Args:
        db: Sesión de base de datos

    Returns:
        ReferralService: Servicio de referidos
    """
    user_repo = UserRepository(db)
    referral_repo = ReferralRepository(db)
    return ReferralService(user_repo, referral_repo)


def get_wallet_management_service(
    db: Session = Depends(get_db),
) -> WalletManagementService:
    """
    Dependency para obtener WalletManagementService.

    Args:
        db: Sesión de base de datos

    Returns:
        WalletManagementService: Servicio de gestión de wallets
    """
    wallet_repo = WalletRepository(db)
    user_repo = UserRepository(db)
    tron_dealer = TronDealerClient()
    return WalletManagementService(tron_dealer, wallet_repo, user_repo)


def get_wallet_pool_service(
    db: Session = Depends(get_db),
) -> WalletPoolService:
    """
    Dependency para obtener WalletPoolService.

    Args:
        db: Sesión de base de datos

    Returns:
        WalletPoolService: Servicio de pool de wallets
    """
    wallet_pool_repo = WalletPoolRepository(db)
    crypto_order_repo = CryptoOrderRepository(db)
    tron_dealer = TronDealerClient()
    return WalletPoolService(tron_dealer, wallet_pool_repo, crypto_order_repo)


async def get_redis() -> redis.Redis:
    """
    Dependency para obtener cliente Redis.

    Returns:
        redis.Redis: Cliente Redis conectado al pool

    Raises:
        HTTPException: 503 si Redis no está disponible
    """
    try:
        client = await RedisPool.get_client()
        return client
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis service unavailable",
        )
