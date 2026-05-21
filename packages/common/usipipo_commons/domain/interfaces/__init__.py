"""Interfaces de repositorio para el dominio."""

from .i_wallet_repository import IWalletRepository
from .i_wallet_pool_repository import IWalletPoolRepository

__all__ = [
    "IWalletRepository",
    "IWalletPoolRepository",
]
