"""Implementación de WebhookTokenRepository con SQLAlchemy."""

from datetime import UTC
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session
from usipipo_commons.domain.entities.crypto_transaction import WebhookToken

from src.core.domain.interfaces.i_crypto_transaction_repository import (
    IWebhookTokenRepository,
)
from src.infrastructure.persistence.database import get_execute_rowcount
from src.infrastructure.persistence.models.webhook_token_model import (
    WebhookTokenModel,
)


class WebhookTokenRepository(IWebhookTokenRepository):
    """Implementación de repositorio de webhook tokens con SQLAlchemy."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, token: WebhookToken) -> WebhookToken:
        """Guarda un webhook token."""
        model = WebhookTokenModel.from_entity(token)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model.to_entity()

    def get_by_hash(self, token_hash: str) -> WebhookToken | None:
        """Obtiene un token por hash."""
        result = self.session.execute(
            select(WebhookTokenModel).where(WebhookTokenModel.token_hash == token_hash)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    def mark_used(self, token_id: UUID) -> bool:
        """Marca un token como usado."""
        from datetime import datetime

        result = self.session.execute(
            update(WebhookTokenModel)
            .where(WebhookTokenModel.id == token_id)
            .values(used_at=datetime.now(UTC))
        )
        self.session.commit()
        rowcount = get_execute_rowcount(result)
        return rowcount > 0

    def cleanup_expired(self) -> int:
        """Limpia tokens expirados."""
        from datetime import datetime

        result = self.session.execute(
            update(WebhookTokenModel)
            .where(WebhookTokenModel.expires_at < datetime.now(UTC))
            .where(WebhookTokenModel.used_at.is_(None))
        )
        self.session.commit()
        return get_execute_rowcount(result)
