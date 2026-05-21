"""encrypt_existing_agent_api_keys

Revision ID: encrypt_existing_agent_api_keys
Revises: 176f92841904
Create Date: 2026-04-01 00:00:00.000000

This migration encrypts all existing plaintext agent API keys in the vpn_servers table.
It requires the ENCRYPTION_KEY environment variable to be set.

"""

import os
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from cryptography.fernet import Fernet
from loguru import logger

# revision identifiers, used by Alembic.
revision: str = "encrypt_existing_agent_api_keys"
down_revision: str | Sequence[str] | None = "176f92841904"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _get_encryption_key() -> bytes:
    """Get encryption key from environment.

    Raises:
        ValueError: If ENCRYPTION_KEY is not set
    """
    key_str = os.getenv("ENCRYPTION_KEY")
    if not key_str:
        raise ValueError(
            "ENCRYPTION_KEY environment variable is not set. "
            "Cannot encrypt existing API keys. "
            "Generate a key with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
        )
    return key_str.encode()


def _is_already_encrypted(value: str) -> bool:
    """Check if a value appears to be encrypted.

    Encrypted values are base64-encoded and typically longer than plaintext.
    This is a heuristic check - encrypted values are URL-safe base64 with 2+ dots.
    """
    if not value:
        return False

    # Encrypted values are typically longer (base64 encoded Fernet tokens)
    # and contain only URL-safe base64 characters
    if len(value) < 50:  # Plaintext keys are typically shorter
        return False

    # Check if it looks like base64 (alphanumeric + - and _)
    import re

    return bool(re.match(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$", value))


def upgrade() -> None:
    """Encrypt all existing plaintext agent API keys.

    This migration:
    1. Reads all existing API keys from vpn_servers table
    2. Checks if each key is already encrypted (skip if yes)
    3. Encrypts plaintext keys using Fernet encryption
    4. Updates the database with encrypted values

    IMPORTANT: This migration will FAIL if ENCRYPTION_KEY is not set.
    """
    # Validate encryption key is available
    encryption_key = _get_encryption_key()
    fernet = Fernet(encryption_key)

    logger.info("Starting encryption migration for agent API keys")

    # Use op.get_bind() for read-only SELECT (returns Result).
    # Use op.execute() for DML (UPDATE) to stay within alembic's transaction.
    # Never call conn.commit() — breaks alembic's atomic version tracking.

    conn = op.get_bind()
    servers = conn.execute(
        sa.text("SELECT id, agent_api_key FROM vpn_servers WHERE agent_api_key IS NOT NULL")
    ).fetchall()

    encrypted_count = 0
    skipped_count = 0
    failed_count = 0

    for server_id, api_key in servers:
        try:
            if _is_already_encrypted(api_key):
                logger.info(f"Server {server_id}: API key already encrypted, skipping")
                skipped_count += 1
                continue

            encrypted_key = fernet.encrypt(api_key.encode()).decode()

            op.execute(
                sa.text(
                    "UPDATE vpn_servers SET agent_api_key = :encrypted_key WHERE id = :server_id"
                ),
                params={"encrypted_key": encrypted_key, "server_id": server_id},
            )

            encrypted_count += 1
            logger.info(f"Server {server_id}: API key encrypted successfully")

        except Exception as e:
            failed_count += 1
            logger.error(f"Server {server_id}: Failed to encrypt API key: {e}")

    # No explicit commit — alembic manages transaction atomically.
    # Do NOT call conn.commit() — breaks alembic version tracking.

    logger.info(
        f"Encryption migration complete: "
        f"{encrypted_count} encrypted, {skipped_count} skipped (already encrypted), "
        f"{failed_count} failed"
    )

    if failed_count > 0:
        logger.warning(f"{failed_count} servers failed encryption. Review logs for details.")


def downgrade() -> None:
    """Downgrade: Cannot decrypt without the encryption key.

    This is a one-way migration for security reasons.
    If you need to downgrade, you must:
    1. Have the ENCRYPTION_KEY available
    2. Manually decrypt each key using the encryption service
    """
    logger.warning(
        "Downgrade of encryption migration is not automatically supported. "
        "API keys will remain encrypted. "
        "To decrypt keys, use the EncryptionService.decrypt() method with the ENCRYPTION_KEY."
    )

    # Note: We intentionally do NOT decrypt the keys in downgrade
    # This is a security measure - once encrypted, keys should stay encrypted
