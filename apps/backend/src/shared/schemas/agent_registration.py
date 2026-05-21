"""Pydantic schemas for agent registration."""

from pydantic import BaseModel, Field


class AgentRegistrationRequest(BaseModel):
    """Request schema for agent registration."""

    hostname: str = Field(..., description="Server hostname", max_length=255)
    ip_address: str = Field(..., description="Public IP address", max_length=45)
    country_code: str = Field(
        ..., description="ISO 3166-1 alpha-2 country code", min_length=2, max_length=2
    )
    country_name: str = Field(..., description="Country name", max_length=100)
    region: str | None = Field(None, description="Region/state", max_length=100)
    city: str | None = Field(None, description="City", max_length=100)
    agent_version: str = Field(..., description="Agent version", max_length=20)
    os_type: str = Field(..., description="Operating system", max_length=50)
    os_arch: str = Field(..., description="Architecture", max_length=20)
    agent_url: str = Field(..., description="Agent API URL", max_length=500)
    supports_wireguard: bool = Field(True, description="Supports WireGuard")
    agent_api_key: str = Field(..., description="Agent API key", max_length=255)


class AgentRegistrationResponse(BaseModel):
    """Response schema for agent registration."""

    server_id: str
    status: str
    message: str | None = None


class GenerateApiKeyRequest(BaseModel):
    """Request schema for generating API keys."""

    description: str | None = Field(None, max_length=255)
    expires_in_days: int | None = Field(None, ge=1, le=3650)


class GenerateApiKeyResponse(BaseModel):
    """Response schema for generated API key."""

    id: str
    api_key: str
    status: str
    created_at: str
    expires_at: str | None = None


class ApiKeyListResponse(BaseModel):
    """Response schema for API key list."""

    keys: list[dict]
    total: int
