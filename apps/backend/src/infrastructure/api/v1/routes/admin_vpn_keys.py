"""
Admin VPN Keys API routes for uSipipo backend.

These routes provide administrative endpoints for managing VPN keys.
All endpoints require staff privileges (support or admin role).
"""

import logging
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from usipipo_commons.domain.entities.user import User
from usipipo_commons.domain.entities.vpn_key import VpnKey

from src.core.application.services.admin_vpn_key_service import AdminVpnKeyService
from src.infrastructure.api.v1.deps import get_current_user, get_db
from src.infrastructure.persistence.models.staff_role_model import StaffRoleModel
from src.infrastructure.persistence.repositories.audit_log_repository import AuditLogRepository
from src.infrastructure.persistence.repositories.user_repository import UserRepository
from src.infrastructure.persistence.repositories.vpn_key_repository import VpnKeyRepository
from src.shared.schemas.admin_vpn_keys import (
    AdminOperationResult,
    CreateVpnKeyAdminRequest,
    RegenerateConfigRequest,
    ResetUsageRequest,
    UpdateDataLimitRequest,
    VpnKeyDetailResponse,
    VpnKeyListFilters,
    VpnKeyListItemResponse,
    VpnKeyListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/vpn-keys", tags=["Admin VPN Keys"])


# ============================================
# Dependencies
# ============================================


def get_admin_vpn_key_service(
    db: Session = Depends(get_db),
) -> AdminVpnKeyService:
    """Dependency to get AdminVpnKeyService."""
    user_repo = UserRepository(db)
    vpn_key_repo = VpnKeyRepository(db)
    audit_log_repo = AuditLogRepository(db)
    return AdminVpnKeyService(
        session=db,
        user_repo=user_repo,
        vpn_key_repo=vpn_key_repo,
        audit_log_repo=audit_log_repo,
    )


def get_staff_member(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Verify user has staff role (support or admin).

    Returns:
        dict with telegram_id and username
    """
    # Check if user has staff role
    query = select(StaffRoleModel).where(
        StaffRoleModel.telegram_id == current_user.telegram_id,
        StaffRoleModel.is_active,
    )
    result = db.execute(query)
    staff_role = result.scalar_one_or_none()

    if not staff_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff role required",
        )

    return {
        "telegram_id": current_user.telegram_id,
        "username": current_user.username or "",
        "role": staff_role.role,
    }


# ============================================
# Helper Functions
# ============================================


def vpn_key_to_list_item(key: VpnKey, user_id: UUID, user_name: str) -> VpnKeyListItemResponse:
    """Convert VpnKey entity to list item response."""
    data_used_gb = (key.used_bytes or 0) / (1024**3)
    data_limit_gb = (key.data_limit_bytes or 0) / (1024**3)
    usage_percentage = (data_used_gb / data_limit_gb * 100) if data_limit_gb > 0 else 0.0

    return VpnKeyListItemResponse(
        id=key.id,
        user_id=user_id,
        user_name=user_name,
        name=key.name,
        vpn_type=key.key_type.value,
        status=key.status.value,
        country_code="",  # Would need server lookup
        created_at=key.created_at,
        last_used_at=key.last_seen_at,
        data_used_gb=round(data_used_gb, 2),
        data_limit_gb=round(data_limit_gb, 2),
        usage_percentage=round(usage_percentage, 2),
        is_active=key.status.value == "active",
    )


def vpn_key_to_detail(
    key: VpnKey, user_id: UUID, user_name: str, server_name: str = ""
) -> VpnKeyDetailResponse:
    """Convert VpnKey entity to detail response."""
    data_used_gb = (key.used_bytes or 0) / (1024**3)
    data_limit_gb = (key.data_limit_bytes or 0) / (1024**3)
    usage_percentage = (data_used_gb / data_limit_gb * 100) if data_limit_gb > 0 else 0.0

    return VpnKeyDetailResponse(
        id=key.id,
        user_id=user_id,
        user_name=user_name,
        name=key.name,
        vpn_type=key.key_type.value,
        status=key.status.value,
        server_id=key.server_id or UUID("00000000-0000-0000-0000-000000000000"),
        server_name=server_name,
        country_code="",  # Would need server lookup
        config=key.key_data,
        created_at=key.created_at,
        expires_at=key.expires_at,
        last_used_at=key.last_seen_at,
        data_used_gb=round(data_used_gb, 2),
        data_limit_gb=round(data_limit_gb, 2),
        usage_percentage=round(usage_percentage, 2),
        is_active=key.status.value == "active",
    )


# ============================================
# API Endpoints
# ============================================


@router.get(
    "",
    response_model=VpnKeyListResponse,
    summary="List all VPN keys",
    description="List all VPN keys with pagination and filters. Requires staff role.",
)
def list_vpn_keys(
    filters: VpnKeyListFilters = Depends(),
    service: AdminVpnKeyService = Depends(get_admin_vpn_key_service),
    staff: dict = Depends(get_staff_member),
) -> VpnKeyListResponse:
    """List all VPN keys with pagination and filters."""
    try:
        # Convert filters to dict
        filters_dict = filters.model_dump()

        # Call service
        result = service.list_keys(filters_dict, staff["admin_id"])

        # Convert to response format
        keys = []
        for key in result["keys"]:
            # Get user info for each key
            user = service.user_repo.get_by_id(key.user_id)
            user_id = user.id if user else UUID("00000000-0000-0000-0000-000000000000")
            user_name = user.first_name or user.username or "Unknown" if user else "Unknown"

            keys.append(vpn_key_to_list_item(key, user_id, user_name))

        return VpnKeyListResponse(
            keys=keys,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"],
            has_next=result["has_next"],
            has_previous=result["has_previous"],
        )

    except Exception as e:
        logger.error(f"Error listing VPN keys: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing VPN keys: {str(e)}",
        )


@router.get(
    "/{key_id}",
    response_model=VpnKeyDetailResponse,
    summary="Get VPN key details",
    description="Get detailed information about a specific VPN key. Requires staff role.",
)
def get_vpn_key(
    key_id: UUID,
    service: AdminVpnKeyService = Depends(get_admin_vpn_key_service),
    staff: dict = Depends(get_staff_member),
) -> VpnKeyDetailResponse:
    """Get VPN key details."""
    try:
        key = service.get_key_detail(key_id, staff["admin_id"])

        if not key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"VPN key {key_id} not found",
            )

        # Get user info
        user = service.user_repo.get_by_id(key.user_id)
        user_id = user.id if user else UUID("00000000-0000-0000-0000-000000000000")
        user_name = user.first_name or user.username or "Unknown" if user else "Unknown"

        # Get server info if available
        server_name = ""
        if key.server_id:
            from sqlalchemy import select

            from src.infrastructure.persistence.models.vpn_server_model import VpnServerModel

            query = select(VpnServerModel).where(VpnServerModel.id == key.server_id)
            result = service.session.execute(query)
            server = result.scalar_one_or_none()
            if server:
                server_name = server.name

        return vpn_key_to_detail(key, user_id, user_name, server_name)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting VPN key details: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting VPN key details: {str(e)}",
        )


@router.get(
    "/users/{user_id}/keys",
    response_model=list[VpnKeyDetailResponse],
    summary="Get user's VPN keys",
    description="Get all VPN keys for a specific user by Telegram ID. Requires staff role.",
)
def get_user_vpn_keys(
    user_id: UUID,
    service: AdminVpnKeyService = Depends(get_admin_vpn_key_service),
    staff: dict = Depends(get_staff_member),
) -> list[VpnKeyDetailResponse]:
    """Get all VPN keys for a specific user."""
    try:
        keys = service.get_user_keys(user_id, staff["admin_id"])

        # Get user info
        user = service.user_repo.get_by_id(user_id)
        user_name = user.first_name or user.username or "Unknown" if user else "Unknown"

        return [vpn_key_to_detail(key, user_id, user_name) for key in keys]

    except Exception as e:
        logger.error(f"Error getting user's VPN keys: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user's VPN keys: {str(e)}",
        )


@router.post(
    "",
    response_model=VpnKeyDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create VPN key",
    description="Create a new VPN key for a user. Requires admin role.",
)
def create_vpn_key(
    request: CreateVpnKeyAdminRequest,
    service: AdminVpnKeyService = Depends(get_admin_vpn_key_service),
    staff: dict = Depends(get_staff_member),
) -> VpnKeyDetailResponse:
    """Create a new VPN key."""
    try:
        # Check admin role
        if staff["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin role required for creating VPN keys",
            )

        # Call service
        key = service.create_key(request.model_dump(), staff["admin_id"])

        # Get user info
        user = service.user_repo.get_by_id(request.user_id)
        user_name = user.first_name or user.username or "Unknown" if user else "Unknown"

        return vpn_key_to_detail(key, request.user_id, user_name)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error creating VPN key: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating VPN key: {str(e)}",
        )


@router.patch(
    "/{key_id}/toggle",
    response_model=AdminOperationResult,
    summary="Toggle VPN key status",
    description="Toggle VPN key active/inactive status. Requires staff role.",
)
def toggle_vpn_key(
    key_id: UUID,
    service: AdminVpnKeyService = Depends(get_admin_vpn_key_service),
    staff: dict = Depends(get_staff_member),
) -> AdminOperationResult:
    """Toggle VPN key status."""
    try:
        success = service.toggle_key(key_id, staff["admin_id"])

        return AdminOperationResult(
            success=success,
            operation="toggle_key",
            key_id=key_id,
            message=f"VPN key {key_id} status toggled successfully",
            timestamp=datetime.now(UTC),
            admin_telegram_id=staff["admin_id"],
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error toggling VPN key status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling VPN key status: {str(e)}",
        )


@router.patch(
    "/{key_id}/data-limit",
    response_model=AdminOperationResult,
    summary="Update VPN key data limit",
    description="Update data limit for a VPN key. Requires admin role.",
)
def update_vpn_key_data_limit(
    key_id: UUID,
    request: UpdateDataLimitRequest,
    service: AdminVpnKeyService = Depends(get_admin_vpn_key_service),
    staff: dict = Depends(get_staff_member),
) -> AdminOperationResult:
    """Update VPN key data limit."""
    try:
        # Check admin role
        if staff["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin role required for updating data limits",
            )

        success = service.update_data_limit(
            key_id,
            request.data_limit_gb,
            request.reason,
            staff["admin_id"],
        )

        return AdminOperationResult(
            success=success,
            operation="update_data_limit",
            key_id=key_id,
            message=f"VPN key {key_id} data limit updated to {request.data_limit_gb} GB",
            timestamp=datetime.now(UTC),
            admin_telegram_id=staff["admin_id"],
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error updating VPN key data limit: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating VPN key data limit: {str(e)}",
        )


@router.patch(
    "/{key_id}/reset-usage",
    response_model=AdminOperationResult,
    summary="Reset VPN key usage",
    description="Reset data usage for a VPN key. Requires admin role.",
)
def reset_vpn_key_usage(
    key_id: UUID,
    request: ResetUsageRequest,
    service: AdminVpnKeyService = Depends(get_admin_vpn_key_service),
    staff: dict = Depends(get_staff_member),
) -> AdminOperationResult:
    """Reset VPN key usage."""
    try:
        # Check admin role
        if staff["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin role required for resetting usage",
            )

        success = service.reset_usage(key_id, request.reason, staff["admin_id"])

        return AdminOperationResult(
            success=success,
            operation="reset_usage",
            key_id=key_id,
            message=f"VPN key {key_id} usage reset successfully",
            timestamp=datetime.now(UTC),
            admin_telegram_id=staff["admin_id"],
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error resetting VPN key usage: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting VPN key usage: {str(e)}",
        )


@router.post(
    "/{key_id}/regenerate",
    response_model=VpnKeyDetailResponse,
    summary="Regenerate VPN key configuration",
    description="Regenerate configuration for a VPN key. Requires admin role.",
)
def regenerate_vpn_key_config(
    key_id: UUID,
    request: RegenerateConfigRequest,
    service: AdminVpnKeyService = Depends(get_admin_vpn_key_service),
    staff: dict = Depends(get_staff_member),
) -> VpnKeyDetailResponse:
    """Regenerate VPN key configuration."""
    try:
        # Check admin role
        if staff["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin role required for regenerating configuration",
            )

        key = service.regenerate_config(key_id, request.notify_user, staff["admin_id"])

        # Get user info
        user = service.user_repo.get_by_id(key.user_id)
        user_id = user.id if user else UUID("00000000-0000-0000-0000-000000000000")
        user_name = user.first_name or user.username or "Unknown" if user else "Unknown"

        return vpn_key_to_detail(key, user_id, user_name)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error regenerating VPN key configuration: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error regenerating VPN key configuration: {str(e)}",
        )


@router.delete(
    "/{key_id}",
    response_model=AdminOperationResult,
    summary="Delete VPN key",
    description="Delete a VPN key permanently. Requires admin role.",
)
def delete_vpn_key(
    key_id: UUID,
    service: AdminVpnKeyService = Depends(get_admin_vpn_key_service),
    staff: dict = Depends(get_staff_member),
) -> AdminOperationResult:
    """Delete VPN key."""
    try:
        # Check admin role
        if staff["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin role required for deleting VPN keys",
            )

        success = service.delete_key(key_id, staff["admin_id"])

        return AdminOperationResult(
            success=success,
            operation="delete_key",
            key_id=key_id,
            message=f"VPN key {key_id} deleted successfully",
            timestamp=datetime.now(UTC),
            admin_telegram_id=staff["admin_id"],
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error deleting VPN key: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting VPN key: {str(e)}",
        )
