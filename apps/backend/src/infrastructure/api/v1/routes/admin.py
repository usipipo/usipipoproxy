"""
Admin API routes for uSipipo backend.

These routes provide administrative endpoints for managing users, VPN keys,
and server monitoring. All endpoints require admin privileges.
"""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from usipipo_commons.domain.entities.user import User

from src.core.application.services.admin_key_service import AdminKeyService
from src.core.application.services.admin_server_service import AdminServerService
from src.core.application.services.admin_stats_service import AdminStatsService
from src.core.application.services.admin_user_service import AdminUserService
from src.core.application.services.metrics_service import MetricsService
from src.infrastructure.api.v1.deps import get_db, require_admin
from src.infrastructure.persistence.repositories.payment_repository import PaymentRepository
from src.infrastructure.persistence.repositories.user_repository import UserRepository
from src.infrastructure.persistence.repositories.vpn_repository import VpnRepository
from src.infrastructure.vpn_providers.wireguard_client import WireGuardClient
from src.shared.config import settings
from src.shared.schemas.admin import (
    AdminKeyInfoResponse,
    AdminKeyListResponse,
    AdminOperationResultResponse,
    AdminUserInfoResponse,
    AdminUserListResponse,
    AssignRoleRequest,
    DashboardStatsResponse,
    DeleteKeyResponse,
    ServerStatsResponse,
    ServerStatusListResponse,
    ServerStatusResponse,
    ToggleKeyStatusRequest,
    UpdateUserStatusRequest,
)
from src.shared.schemas.admin import AdminUserListResponse as AdminUserListResponseSchema

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/admin", tags=["Admin"])


# ============================================
# Dependencies
# ============================================


def get_admin_user_service(
    db: Session = Depends(get_db),
) -> AdminUserService:
    """Dependency to get AdminUserService."""
    user_repo = UserRepository(db)
    vpn_repo = VpnRepository(db)
    payment_repo = PaymentRepository(db)
    return AdminUserService(user_repo, vpn_repo, payment_repo)


def get_admin_key_service(
    db: Session = Depends(get_db),
) -> AdminKeyService:
    """Dependency to get AdminKeyService."""
    user_repo = UserRepository(db)
    vpn_repo = VpnRepository(db)
    wireguard_client = WireGuardClient()
    return AdminKeyService(vpn_repo, user_repo, wireguard_client)


def get_admin_stats_service(
    db: Session = Depends(get_db),
) -> AdminStatsService:
    """Dependency to get AdminStatsService."""
    user_repo = UserRepository(db)
    vpn_repo = VpnRepository(db)
    payment_repo = PaymentRepository(db)
    return AdminStatsService(user_repo, vpn_repo, payment_repo)


def get_admin_server_service(
    db: Session = Depends(get_db),
) -> AdminServerService:
    """Dependency to get AdminServerService."""
    user_repo = UserRepository(db)
    vpn_repo = VpnRepository(db)
    wireguard_client = WireGuardClient()
    return AdminServerService(user_repo, vpn_repo, wireguard_client)


# ============================================
# Dashboard Statistics
# ============================================


@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    admin: User = Depends(require_admin),
    stats_service: AdminStatsService = Depends(get_admin_stats_service),
) -> DashboardStatsResponse:
    """
    Get dashboard statistics for admin panel.

    Returns comprehensive statistics including:
    - User metrics (total, active, new today)
    - VPN key metrics (total, active, by type)
    - Usage statistics
    - Revenue metrics

    **Requires admin privileges**
    """
    stats = stats_service.get_dashboard_stats(admin.id)
    return DashboardStatsResponse(**stats)


# ============================================
# User Management
# ============================================


@router.get("/users", response_model=AdminUserListResponseSchema)
def get_all_users(
    admin: User = Depends(require_admin),
    user_service: AdminUserService = Depends(get_admin_user_service),
) -> AdminUserListResponseSchema:
    """
    Get all users with admin information.

    Returns a list of all users with detailed information including:
    - User details (name, username, telegram_id)
    - VPN key counts (total, active)
    - Balance and referral credits
    - Registration and activity dates

    **Requires admin privileges**
    """
    users = user_service.get_all_users(admin.id)
    return AdminUserListResponseSchema(
        users=[
            AdminUserInfoResponse(
                user_id=u.user_id,
                username=u.username,
                first_name=u.first_name,
                last_name=u.last_name,
                total_keys=u.total_keys,
                active_keys=u.active_keys,
                stars_balance=u.stars_balance,
                total_deposited=u.total_deposited,
                referral_credits=u.referral_credits,
                registration_date=u.registration_date,
                last_activity=u.last_activity,
            )
            for u in users
        ],
        total=len(users),
        page=1,
        per_page=len(users),
        total_pages=1,
    )


@router.get("/users/paginated", response_model=AdminUserListResponse)
@limiter.limit(settings.RATE_LIMIT_ADMIN)
def get_users_paginated(
    request: Request,
    page: int = 1,
    per_page: int = 20,
    admin: User = Depends(require_admin),
    user_service: AdminUserService = Depends(get_admin_user_service),
) -> AdminUserListResponse:
    """
    Get paginated list of users.

    **Requires admin privileges**
    """
    result = user_service.get_users_paginated(page, per_page, admin.id)
    return AdminUserListResponse(**result)


@router.post("/users/{user_id}/status", response_model=AdminOperationResultResponse)
def update_user_status(
    user_id: UUID,
    request: UpdateUserStatusRequest,
    admin: User = Depends(require_admin),
    user_service: AdminUserService = Depends(get_admin_user_service),
) -> AdminOperationResultResponse:
    """
    Update user status (ACTIVE, SUSPENDED, BLOCKED).

    **Requires admin privileges**
    """
    result = user_service.update_user_status(user_id, request.status)
    return AdminOperationResultResponse(
        success=result.success,
        operation=result.operation,
        target_id=result.target_id,
        message=result.message,
        details=result.details,
        timestamp=result.timestamp,
    )


@router.post("/users/{user_id}/role", response_model=AdminOperationResultResponse)
def assign_role_to_user(
    user_id: UUID,
    request: AssignRoleRequest,
    admin: User = Depends(require_admin),
    user_service: AdminUserService = Depends(get_admin_user_service),
) -> AdminOperationResultResponse:
    """
    Assign role to a user (ADMIN, USER).

    **Requires admin privileges**
    """
    result = user_service.assign_role_to_user(user_id, request.role, request.duration_days)
    return AdminOperationResultResponse(
        success=result.success,
        operation=result.operation,
        target_id=result.target_id,
        message=result.message,
        details=result.details,
        timestamp=result.timestamp,
    )


@router.post("/users/{user_id}/block", response_model=AdminOperationResultResponse)
def block_user(
    user_id: UUID,
    admin: User = Depends(require_admin),
    user_service: AdminUserService = Depends(get_admin_user_service),
) -> AdminOperationResultResponse:
    """
    Block a user.

    **Requires admin privileges**
    """
    result = user_service.block_user(user_id)
    return AdminOperationResultResponse(
        success=result.success,
        operation=result.operation,
        target_id=result.target_id,
        message=result.message,
        details=result.details,
        timestamp=result.timestamp,
    )


@router.post("/users/{user_id}/unblock", response_model=AdminOperationResultResponse)
def unblock_user(
    user_id: UUID,
    admin: User = Depends(require_admin),
    user_service: AdminUserService = Depends(get_admin_user_service),
) -> AdminOperationResultResponse:
    """
    Unblock a user.

    **Requires admin privileges**
    """
    result = user_service.unblock_user(user_id)
    return AdminOperationResultResponse(
        success=result.success,
        operation=result.operation,
        target_id=result.target_id,
        message=result.message,
        details=result.details,
        timestamp=result.timestamp,
    )


@router.delete("/users/{user_id}", response_model=AdminOperationResultResponse)
def delete_user(
    user_id: UUID,
    admin: User = Depends(require_admin),
    user_service: AdminUserService = Depends(get_admin_user_service),
) -> AdminOperationResultResponse:
    """
    Delete a user and all associated VPN keys.

    **Requires admin privileges**
    """
    result = user_service.delete_user(user_id)
    return AdminOperationResultResponse(
        success=result.success,
        operation=result.operation,
        target_id=result.target_id,
        message=result.message,
        details=result.details,
        timestamp=result.timestamp,
    )


# ============================================
# VPN Key Management
# ============================================


@router.get("/keys", response_model=AdminKeyListResponse)
def get_all_keys(
    admin: User = Depends(require_admin),
    key_service: AdminKeyService = Depends(get_admin_key_service),
) -> AdminKeyListResponse:
    """
    Get all VPN keys from all users.

    Returns detailed information about each key including:
    - Key details (ID, name, type, access URL)
    - User information
    - Usage statistics
    - Server status

    **Requires admin privileges**
    """
    keys = key_service.get_all_keys(admin.id)
    return AdminKeyListResponse(
        keys=[
            AdminKeyInfoResponse(
                key_id=k.key_id,
                user_id=k.user_id,
                user_name=k.user_name,
                key_type=k.key_type,
                key_name=k.key_name,
                access_url=k.access_url,
                created_at=k.created_at,
                last_used=k.last_used,
                data_limit=k.data_limit,
                data_used=k.data_used,
                is_active=k.is_active,
                server_status=k.server_status,
            )
            for k in keys
        ],
        total=len(keys),
    )


@router.get("/users/{user_id}/keys", response_model=AdminKeyListResponse)
def get_user_keys(
    user_id: UUID,
    admin: User = Depends(require_admin),
    key_service: AdminKeyService = Depends(get_admin_key_service),
) -> AdminKeyListResponse:
    """
    Get all VPN keys for a specific user.

    **Requires admin privileges**
    """
    keys = key_service.get_user_keys(user_id)
    key_responses = []
    for k in keys:
        user = key_service.user_repository.get_by_id(k.user_id)
        key_responses.append(
            AdminKeyInfoResponse(
                key_id=str(k.id),
                user_id=user.id if user else UUID("00000000-0000-0000-0000-000000000000"),
                user_name=user.first_name or "" if user else "",
                key_type=k.key_type.value if hasattr(k.key_type, "value") else str(k.key_type),
                key_name=k.name,
                access_url=k.key_data,
                created_at=k.created_at,
                last_used=k.last_seen_at,
                data_limit=k.data_limit_bytes,
                data_used=k.used_bytes,
                is_active=k.is_active,
                server_status="unknown",
            )
        )
    return AdminKeyListResponse(
        keys=key_responses,
        total=len(keys),
    )


@router.post("/keys/{key_id}/toggle", response_model=AdminOperationResultResponse)
def toggle_key_status(
    key_id: str,
    request: ToggleKeyStatusRequest,
    admin: User = Depends(require_admin),
    key_service: AdminKeyService = Depends(get_admin_key_service),
) -> AdminOperationResultResponse:
    """
    Activate or deactivate a VPN key.

    **Requires admin privileges**
    """
    result = key_service.toggle_key_status(key_id, request.active)
    return AdminOperationResultResponse(
        success=result["success"],
        operation="toggle_key_status",
        target_id=key_id,
        message=result["message"],
        details={"is_active": result.get("is_active")},
        timestamp=datetime.now(UTC),
    )


@router.delete("/keys/{key_id}", response_model=DeleteKeyResponse)
def delete_key(
    key_id: str,
    admin: User = Depends(require_admin),
    key_service: AdminKeyService = Depends(get_admin_key_service),
) -> DeleteKeyResponse:
    """
    Delete a VPN key completely (from servers and database).

    **Requires admin privileges**
    """
    result = key_service.delete_user_key_complete(key_id)
    return DeleteKeyResponse(
        success=result["success"],
        message=result["message"],
        key_id=key_id,
        server_deleted=result.get("server_deleted"),
        db_deleted=result.get("db_deleted"),
    )


# ============================================
# Server Management
# ============================================


@router.get("/servers/status", response_model=ServerStatusListResponse)
def get_server_status(
    admin: User = Depends(require_admin),
    server_service: AdminServerService = Depends(get_admin_server_service),
) -> ServerStatusListResponse:
    """
    Get status of all VPN servers.

    Returns health status for:
    - WireGuard server

    **Requires admin privileges**
    """
    status = server_service.get_server_status()

    def _to_response(s) -> ServerStatusResponse | None:
        if s is None:
            return None
        return ServerStatusResponse(
            server_type=s.server_type,
            is_healthy=s.is_healthy,
            total_keys=s.total_keys,
            active_keys=s.active_keys,
            version=s.version,
            uptime=s.uptime,
            error_message=s.error_message,
        )

    return ServerStatusListResponse(
        wireguard=_to_response(status.get("wireguard")),
    )


@router.get("/servers/stats", response_model=ServerStatsResponse)
def get_server_stats(
    admin: User = Depends(require_admin),
    server_service: AdminServerService = Depends(get_admin_server_service),
) -> ServerStatsResponse:
    """
    Get comprehensive server statistics.

    Returns:
    - User statistics
    - Key statistics
    - Data usage
    - Server health status

    **Requires admin privileges**
    """
    stats = server_service.get_server_stats(admin.id)
    return ServerStatsResponse(**stats)


# ---------------------------------------------------------------------------
# Metrics Management Endpoints
# ---------------------------------------------------------------------------


def get_metrics_service(
    db: Session = Depends(get_db),
) -> MetricsService:
    """Dependency to get MetricsService instance."""
    return MetricsService(db)


@router.post("/metrics/cleanup")
def cleanup_old_metrics(
    admin: User = Depends(require_admin),
    metrics_service: "MetricsService" = Depends(get_metrics_service),
    retention_days: int = 30,
):
    """
    Clean up old metrics beyond retention period.

    This endpoint removes metrics older than the specified retention period
    from WireGuard and Server metrics tables.

    Args:
        admin: Admin user (required)
        metrics_service: Metrics service
        retention_days: Number of days to retain metrics (default: 30)

    Returns:
        Dictionary with counts of deleted metrics

    **Requires admin privileges**
    """
    result = metrics_service.cleanup_old_metrics(retention_days=retention_days)
    return result
