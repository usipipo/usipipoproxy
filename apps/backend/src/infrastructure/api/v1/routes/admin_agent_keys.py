"""Admin routes for managing agent API keys."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.core.application.services.agent_registration_service import (
    AgentRegistrationService,
)
from src.infrastructure.persistence.database import get_db
from src.infrastructure.persistence.repositories.agent_api_key_repository import (
    AgentApiKeyRepository,
)
from src.infrastructure.persistence.repositories.vpn_repository import VpnRepository
from src.shared.schemas.agent_registration import (
    ApiKeyListResponse,
    GenerateApiKeyRequest,
    GenerateApiKeyResponse,
)

router = APIRouter(prefix="/admin/agent-api-keys", tags=["Admin - Agent Keys"])


def get_service(db: Session = Depends(get_db)) -> AgentRegistrationService:
    """Get registration service."""
    return AgentRegistrationService(
        session=db,
        api_key_repository=AgentApiKeyRepository(db),
        vpn_repository=VpnRepository(db),
    )


@router.post("", response_model=GenerateApiKeyResponse, status_code=status.HTTP_201_CREATED)
def generate_api_key(
    request: GenerateApiKeyRequest,
    service: AgentRegistrationService = Depends(get_service),
):
    """Generate a new agent API key.

    **Authentication:** Requires admin JWT token

    **Security:** Generated key is only shown once - store it securely!
    """
    plain_key, api_key_model = service.create_api_key(
        description=request.description,
        expires_in_days=request.expires_in_days,
    )

    return GenerateApiKeyResponse(
        id=str(api_key_model.id),
        api_key=plain_key,
        status=api_key_model.status,
        created_at=api_key_model.created_at.isoformat(),
        expires_at=api_key_model.expires_at.isoformat() if api_key_model.expires_at else None,
    )


@router.get("", response_model=ApiKeyListResponse)
def list_api_keys(
    status_filter: str | None = Query(
        None, alias="status", pattern="^(active|used|revoked|expired)$"
    ),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: AgentRegistrationService = Depends(get_service),
):
    """List agent API keys with optional filtering.

    **Authentication:** Requires admin JWT token
    """
    keys = service.api_key_repository.list_keys(
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    return ApiKeyListResponse(
        keys=[
            {
                "id": str(k.id),
                "status": k.status,
                "description": k.description,
                "created_at": k.created_at.isoformat(),
                "used_at": k.used_at.isoformat() if k.used_at else None,
                "server_id": str(k.server_id) if k.server_id else None,
            }
            for k in keys
        ],
        total=len(keys),
    )
