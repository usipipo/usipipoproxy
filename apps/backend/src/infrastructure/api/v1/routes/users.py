"""Routes para gestión de usuarios."""

import logging

from fastapi import APIRouter, Depends, status
from usipipo_commons.domain.entities.user import User

from src.infrastructure.api.v1.deps import get_current_user, get_referral_service

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(__name__)


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    referral_service=Depends(get_referral_service),
):
    """
    Obtiene el perfil del usuario autenticado.

    Args:
        current_user: Usuario autenticado (inyectado por JWT)
        referral_service: Servicio de referidos

    Returns:
        dict: Perfil del usuario con estadísticas de referidos
    """
    # Get referral stats (graceful fallback on error)
    try:
        referral_stats = referral_service.get_referral_stats(current_user.id)
        total_referrals = referral_stats["total_referrals"]
    except Exception as e:
        logger.warning(f"Failed to get referral stats for user {current_user.id}: {e}")
        total_referrals = 0

    return {
        "id": str(current_user.id),
        "telegram_id": current_user.telegram_id,
        "username": current_user.username,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "is_admin": current_user.is_admin,
        "balance_gb": current_user.balance_gb,
        "total_purchased_gb": current_user.total_purchased_gb,
        "referral_code": current_user.referral_code,
        "referral_credits": current_user.referral_credits,
        "purchase_count": current_user.purchase_count,
        "loyalty_bonus_percent": current_user.loyalty_bonus_percent,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
        "referred_by": str(current_user.referred_by) if current_user.referred_by else None,
        "total_referrals": total_referrals,
    }
