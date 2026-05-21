"""Encryption utilities for sensitive data."""

import base64
from typing import ClassVar

from cryptography.fernet import Fernet
from loguru import logger

from src.shared.config import settings


class EncryptionService:
    """Service for encrypting and decrypting sensitive data.

    Uses Fernet symmetric encryption for API keys and other secrets.
    """

    _instance: ClassVar["EncryptionService | None"] = None
    _fernet: Fernet | None = None

    def __init__(self, encryption_key: bytes | None = None):
        """Initialize encryption service.

        Args:
            encryption_key: 32-byte URL-safe base64-encoded key.
                           If None, loads from settings.ENCRYPTION_KEY.
        """
        if encryption_key is None:
            key_str = settings.ENCRYPTION_KEY
            if not key_str:
                logger.warning(
                    "ENCRYPTION_KEY not set. API keys will NOT be encrypted. "
                    "Generate key with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
                )
                return

            encryption_key = key_str.encode()

        self._fernet = Fernet(encryption_key)
        logger.info("EncryptionService initialized")

    @classmethod
    def get_instance(cls) -> "EncryptionService":
        """Get singleton instance of encryption service."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string.

        Args:
            plaintext: String to encrypt

        Returns:
            Encrypted string (URL-safe base64)

        Raises:
            RuntimeError: If encryption key not configured
        """
        if not self._fernet:
            raise RuntimeError("Encryption not configured. Set ENCRYPTION_KEY env var.")

        encrypted = self._fernet.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a string.

        Args:
            ciphertext: Encrypted string (URL-safe base64)

        Returns:
            Decrypted plaintext

        Raises:
            RuntimeError: If encryption key not configured
            cryptography.fernet.InvalidToken: If decryption fails
        """
        if not self._fernet:
            raise RuntimeError("Encryption not configured. Set ENCRYPTION_KEY env var.")

        try:
            encrypted = base64.urlsafe_b64decode(ciphertext.encode())
            return self._fernet.decrypt(encrypted).decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise

    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key.

        Returns:
            32-byte URL-safe base64-encoded key
        """
        from cryptography.fernet import Fernet

        return Fernet.generate_key().decode()


# Convenience functions
def encrypt_sensitive_data(plaintext: str) -> str:
    """Encrypt sensitive data using the global encryption service."""
    return EncryptionService.get_instance().encrypt(plaintext)


def decrypt_sensitive_data(ciphertext: str) -> str:
    """Decrypt sensitive data using the global encryption service."""
    return EncryptionService.get_instance().decrypt(ciphertext)
