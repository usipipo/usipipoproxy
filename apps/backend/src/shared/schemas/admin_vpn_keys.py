"""Schemas for admin VPN key management API."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VpnKeyListFilters(BaseModel):
    """Filters for listing VPN keys."""

    page: int = Field(1, ge=1, description="Current page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    user_id: UUID | None = Field(None, description="Filter by user UUID")
    vpn_type: Literal["wireguard"] | None = Field(None, description="Filter by VPN type")
    status: Literal["active", "inactive", "revoked"] | None = Field(
        None, description="Filter by status"
    )
    server_id: UUID | None = Field(None, description="Filter by server ID")
    country: str | None = Field(None, description="Filter by country code")
    search: str | None = Field(None, description="Search by key name")
    sort_by: Literal["created_at", "last_used", "data_used"] = Field(
        "created_at", description="Sort field"
    )
    sort_order: Literal["asc", "desc"] = Field("desc", description="Sort order")
    created_after: datetime | None = Field(None, description="Filter by creation date (after)")
    created_before: datetime | None = Field(None, description="Filter by creation date (before)")


class CreateVpnKeyAdminRequest(BaseModel):
    """Request schema for creating a VPN key."""

    user_id: UUID = Field(..., description="User UUID")
    name: str = Field(..., min_length=3, max_length=50, description="Key name")
    vpn_type: Literal["wireguard"] = Field(..., description="VPN type")
    data_limit_gb: float = Field(5.0, ge=1, le=1000, description="Data limit in GB")
    server_id: UUID | None = Field(None, description="Server ID for key assignment")
    country: str = Field("US", description="Country code for server selection")
    expires_in_days: int = Field(30, ge=1, le=365, description="Expiration in days")


class UpdateDataLimitRequest(BaseModel):
    """Request schema for updating data limit."""

    data_limit_gb: float = Field(..., ge=1, le=1000, description="New data limit in GB")
    reason: str | None = Field(None, max_length=500, description="Optional reason for the change")


class ResetUsageRequest(BaseModel):
    """Request schema for resetting usage."""

    reason: str | None = Field(None, max_length=500, description="Optional reason for the reset")


class RegenerateConfigRequest(BaseModel):
    """Request schema for regenerating configuration."""

    notify_user: bool = Field(False, description="Whether to notify the user")


class VpnKeyListItemResponse(BaseModel):
    """Response schema for VPN key list item."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    server_id: UUID | None = None
    user_name: str
    name: str
    vpn_type: str
    status: str
    country_code: str
    created_at: datetime
    last_used_at: datetime | None
    data_used_gb: float
    data_limit_gb: float
    usage_percentage: float
    is_active: bool


class VpnKeyDetailResponse(BaseModel):
    """Response schema for VPN key details."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    server_id: UUID | None = None
    user_name: str
    name: str
    vpn_type: str
    status: str
    server_name: str | None = None
    country_code: str
    config: str | None
    created_at: datetime
    expires_at: datetime | None
    last_used_at: datetime | None
    data_used_gb: float
    data_limit_gb: float
    usage_percentage: float
    is_active: bool


class VpnKeyListResponse(BaseModel):
    """Response schema for paginated VPN key list."""

    keys: list[VpnKeyListItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


class AdminOperationResult(BaseModel):
    """Response schema for admin operations."""

    success: bool
    operation: str
    key_id: UUID
    message: str
    timestamp: datetime
    admin_telegram_id: int
