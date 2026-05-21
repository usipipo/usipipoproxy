"""Repository for agent API key operations."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.persistence.models.agent_api_key_model import AgentApiKeyModel


class AgentApiKeyRepository:
    """Repository for agent API key database operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        api_key_hash: str,
        description: str | None = None,
        expires_at: datetime | None = None,
        created_by: uuid.UUID | None = None,
    ) -> AgentApiKeyModel:
        """Create a new agent API key.

        Args:
            api_key_hash: Hashed API key value
            description: Optional description for the key
            expires_at: Optional expiration timestamp
            created_by: Optional admin user ID who created the key

        Returns:
            Created AgentApiKeyModel instance
        """
        api_key = AgentApiKeyModel(
            api_key_hash=api_key_hash,
            description=description,
            expires_at=expires_at,
            created_by=created_by,
        )
        self.session.add(api_key)
        self.session.commit()
        self.session.refresh(api_key)
        return api_key

    def get_by_hash(self, api_key_hash: str) -> AgentApiKeyModel | None:
        """Get API key by hash.

        Args:
            api_key_hash: Hash of the API key to retrieve

        Returns:
            AgentApiKeyModel if found, None otherwise
        """
        result = self.session.execute(
            select(AgentApiKeyModel).where(AgentApiKeyModel.api_key_hash == api_key_hash)
        )
        return result.scalar_one_or_none()

    def mark_as_used(
        self,
        api_key: AgentApiKeyModel,
        server_id: uuid.UUID,
    ) -> AgentApiKeyModel:
        """Mark API key as used and link to server.

        Args:
            api_key: The API key model to update
            server_id: UUID of the server this key registered

        Returns:
            Updated AgentApiKeyModel instance
        """
        api_key.status = "used"
        api_key.used_at = datetime.now(UTC)
        api_key.server_id = server_id
        self.session.commit()
        self.session.refresh(api_key)
        return api_key

    def revoke(self, api_key: AgentApiKeyModel) -> AgentApiKeyModel:
        """Revoke an API key.

        Args:
            api_key: The API key model to revoke

        Returns:
            Updated AgentApiKeyModel instance
        """
        api_key.status = "revoked"
        self.session.commit()
        self.session.refresh(api_key)
        return api_key

    def list_keys(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AgentApiKeyModel]:
        """List API keys with optional filtering.

        Args:
            status: Optional status filter (active, used, revoked, expired)
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of AgentApiKeyModel instances
        """
        query = select(AgentApiKeyModel)

        if status:
            query = query.where(AgentApiKeyModel.status == status)

        query = query.order_by(AgentApiKeyModel.created_at.desc())
        query = query.offset(offset).limit(limit)

        result = self.session.execute(query)
        return list(result.scalars().all())
