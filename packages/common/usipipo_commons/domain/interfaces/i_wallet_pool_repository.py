"""Interfaces de repositorio para gestión de pool de wallets."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from usipipo_commons.domain.entities.wallet import WalletPool


class IWalletPoolRepository(ABC):
    """Contrato para repositorio de pool de wallets."""

    @abstractmethod
    async def get_all(self) -> List[WalletPool]:
        """Obtiene todas las entradas del pool."""
        pass

    @abstractmethod
    async def get_by_id(self, pool_id: UUID) -> Optional[WalletPool]:
        """Obtiene entrada del pool por ID."""
        pass

    @abstractmethod
    async def get_by_address(self, wallet_address: str) -> Optional[WalletPool]:
        """Obtiene entrada del pool por dirección de wallet."""
        pass

    @abstractmethod
    async def get_available_wallets(self) -> List[WalletPool]:
        """Obtiene todas las wallets disponibles en el pool."""
        pass

    @abstractmethod
    async def get_expired_wallets(self) -> List[WalletPool]:
        """Obtiene todas las wallets expiradas del pool."""
        pass

    @abstractmethod
    async def create(self, pool_entry: WalletPool) -> WalletPool:
        """Crea una nueva entrada en el pool."""
        pass

    @abstractmethod
    async def update(self, pool_entry: WalletPool) -> WalletPool:
        """Actualiza entrada del pool existente."""
        pass

    @abstractmethod
    async def delete(self, pool_id: UUID) -> bool:
        """Elimina entrada del pool."""
        pass

    @abstractmethod
    async def get_reusable_for_user(self, user_id: UUID) -> Optional[WalletPool]:
        """
        Obtiene wallet reutilizable de un usuario específico.
        
        Busca wallets expiradas que pertenecieron al usuario.
        """
        pass

    @abstractmethod
    async def get_any_available(self) -> Optional[WalletPool]:
        """
        Obtiene cualquier wallet disponible en el pool.
        
        Busca cualquier wallet expirada no en uso.
        """
        pass

    @abstractmethod
    async def cleanup_expired(self) -> int:
        """
        Limpia wallets expiradas del pool.
        
        Retorna la cantidad de entradas eliminadas.
        """
        pass
