"""API routes for agent registration."""

from fastapi import APIRouter, Depends, HTTPException, status
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
    AgentRegistrationRequest,
    AgentRegistrationResponse,
)

router = APIRouter(prefix="/servers", tags=["Agent Registration"])


def get_registration_service(db: Session = Depends(get_db)) -> AgentRegistrationService:
    """Get agent registration service instance."""
    return AgentRegistrationService(
        session=db,
        api_key_repository=AgentApiKeyRepository(db),
        vpn_repository=VpnRepository(db),
    )


@router.post(
    "/register-agent",
    response_model=AgentRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_agent(
    request: AgentRegistrationRequest,
    service: AgentRegistrationService = Depends(get_registration_service),
):
    """Register a new VPN agent.

    **Authentication:** Requires X-API-Key header (agent API key)

    **Process:**
    1. Validate API key
    2. Create server record with metadata
    3. Mark API key as used
    4. Return server UUID

    **Idempotency:** Same API key returns existing server (409 if different metadata)
    """
    try:
        server = service.register_agent(
            api_key=request.agent_api_key,
            hostname=request.hostname,
            ip_address=request.ip_address,
            country_code=request.country_code,
            country_name=request.country_name,
            agent_version=request.agent_version,
            os_type=request.os_type,
            os_arch=request.os_arch,
            agent_url=request.agent_url,
            supports_wireguard=request.supports_wireguard,
            region=request.region,
            city=request.city,
        )

        return AgentRegistrationResponse(
            server_id=str(server.id),
            status="registered",
            message="Server registered successfully",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/register-agent",
    response_model=AgentRegistrationResponse,
)
def check_agent_registration(
    api_key: str,
    service: AgentRegistrationService = Depends(get_registration_service),
):
    """Check if an API key has been used for registration.

    Returns existing server_id if registered, or error if not yet registered.
    """
    api_key_model = service.validate_api_key(api_key)

    if api_key_model is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    if api_key_model.status == "active":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not yet used for registration",
        )

    if api_key_model.server_id:
        return AgentRegistrationResponse(
            server_id=str(api_key_model.server_id),
            status="registered",
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Server ID not found",
    )
