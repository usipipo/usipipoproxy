"""Service for handling agent registration."""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.persistence.models.agent_api_key_model import AgentApiKeyModel
from src.infrastructure.persistence.models.vpn_server_model import VpnServerModel
from src.infrastructure.persistence.repositories.agent_api_key_repository import (
    AgentApiKeyRepository,
)
from src.infrastructure.persistence.repositories.vpn_repository import VpnRepository


class AgentRegistrationService:
    """Service for handling agent registration and API key management."""

    def __init__(
        self,
        session: Session,
        api_key_repository: AgentApiKeyRepository,
        vpn_repository: VpnRepository,
    ):
        self.session = session
        self.api_key_repository = api_key_repository
        self.vpn_repository = vpn_repository

    @staticmethod
    def generate_api_key() -> str:
        """Generate a new agent API key.

        Format: agent_<32 hex characters>
        Example: agent_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
        """
        return f"agent_{secrets.token_hex(16)}"

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash API key using SHA-256."""
        return hashlib.sha256(api_key.encode()).hexdigest()

    def create_api_key(
        self,
        description: str | None = None,
        expires_in_days: int | None = None,
        created_by: uuid.UUID | None = None,
    ) -> tuple[str, AgentApiKeyModel]:
        """Generate and store a new API key.

        Returns:
            Tuple of (plain_text_key, api_key_model)
            Store plain_text_key securely - it cannot be recovered!
        """
        # Generate key
        plain_key = self.generate_api_key()
        key_hash = self.hash_api_key(plain_key)

        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        # Store in database
        api_key = self.api_key_repository.create(
            api_key_hash=key_hash,
            description=description,
            expires_at=expires_at,
            created_by=created_by,
        )

        logger.info(f"Created new agent API key: {api_key.id}")

        return plain_key, api_key

    def validate_api_key(self, api_key: str) -> AgentApiKeyModel | None:
        """Validate an API key.

        Returns:
            AgentApiKeyModel if valid, None if invalid/revoked/expired
        """
        key_hash = self.hash_api_key(api_key)
        api_key_model = self.api_key_repository.get_by_hash(key_hash)

        if api_key_model is None:
            logger.warning(f"Invalid API key attempt: {key_hash[:8]}...")
            return None

        # Check status
        if api_key_model.status == "revoked":
            logger.warning(f"Revoked API key used: {api_key_model.id}")
            return None

        # Check expiration
        if api_key_model.expires_at and datetime.utcnow() > api_key_model.expires_at:
            logger.warning(f"Expired API key used: {api_key_model.id}")
            # Mark as expired
            api_key_model.status = "expired"
            self.session.commit()
            return None

        return api_key_model

    def register_agent(
        self,
        api_key: str,
        hostname: str,
        ip_address: str,
        country_code: str,
        country_name: str,
        agent_version: str,
        os_type: str,
        os_arch: str,
        agent_url: str,
        supports_wireguard: bool = True,
        region: str | None = None,
        city: str | None = None,
    ) -> VpnServerModel:
        """Register a new agent and create server record.

        Raises:
            ValueError: If API key is invalid or already used
        """
        # Validate API key
        api_key_model = self.validate_api_key(api_key)
        if api_key_model is None:
            raise ValueError("Invalid or expired API key")

        # Check if already used
        if api_key_model.status == "used":
            raise ValueError("API key already used for registration")

        # Check if server already exists for this key
        if api_key_model.server_id:
            # Return existing server
            result = self.session.execute(
                select(VpnServerModel).where(VpnServerModel.id == api_key_model.server_id)
            )
            server = result.scalar_one_or_none()
            if server:
                return server

        # Create server record
        server_id = uuid.uuid4()

        server = VpnServerModel(
            id=server_id,
            name=f"{country_name} - {hostname}",
            country_code=country_code,
            country_name=country_name,
            city=city,
            region=region,
            agent_url=agent_url,
            agent_api_key=api_key,  # Store for backward compatibility
            supports_wireguard=supports_wireguard,
            status="online",
            agent_version=agent_version,
            os_type=os_type,
            os_arch=os_arch,
            last_registration_ip=ip_address,
        )

        self.session.add(server)
        self.session.flush()  # Get server ID

        # Mark API key as used
        self.api_key_repository.mark_as_used(api_key_model, server_id)

        logger.info(f"Registered new agent: {server_id} ({hostname}) from {ip_address}")

        return server
