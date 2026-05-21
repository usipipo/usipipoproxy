"""Endpoints para la gestión del sistema de referidos."""

from fastapi import APIRouter, Depends, HTTPException, status
from usipipo_commons.domain.entities.user import User

from src.core.application.services.referral_service import ReferralService
from src.infrastructure.api.v1.deps import get_current_user, get_referral_service
from src.shared.schemas.referral import (
    ReferralApplyOnRegisterRequest,
    ReferralApplyOnRegisterResponse,
    ReferralApplyRequest,
    ReferralOperationResponse,
    ReferralRedeemRequest,
    ReferralStatsResponse,
)

router = APIRouter(prefix="/referrals", tags=["referrals"])


@router.get("/me", response_model=ReferralStatsResponse)
def get_my_referral_stats(
    current_user: User = Depends(get_current_user),
    service: ReferralService = Depends(get_referral_service),
):
    """Obtiene las estadísticas de referidos del usuario actual."""
    try:
        stats = service.get_referral_stats(current_user.id)
        return stats
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/apply", response_model=ReferralOperationResponse)
def apply_referral_code(
    request: ReferralApplyRequest,
    current_user: User = Depends(get_current_user),
    service: ReferralService = Depends(get_referral_service),
):
    """Aplica un código de referido al usuario actual."""
    result = service.register_referral(
        new_user_id=current_user.id, referral_code=request.referral_code
    )

    if not result["success"]:
        error_msg = result.get("error", "Unknown error")
        if error_msg == "invalid_code":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Referral code not found"
            )
        if error_msg == "self_referral":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot refer yourself"
            )
        if error_msg == "already_referred":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="You already have a referrer"
            )

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_msg)

    return {"success": True, "message": "Referral code applied successfully", "data": result}


@router.post("/redeem", response_model=ReferralOperationResponse)
def redeem_credits_for_data(
    request: ReferralRedeemRequest,
    current_user: User = Depends(get_current_user),
    service: ReferralService = Depends(get_referral_service),
):
    """Canjea créditos de referido por datos (GB)."""
    result = service.redeem_credits_for_data(user_id=current_user.id, credits=request.credits)

    if not result["success"]:
        error_msg = result.get("error", "Unknown error")
        if error_msg == "insufficient_credits":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient referral credits"
            )
        if error_msg == "insufficient_credits_for_gb":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough credits to redeem at least 1GB (needs {result.get('required')} credits)",
            )

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_msg)

    return {
        "success": True,
        "message": f"Successfully redeemed {result['credits_spent']} credits for {result['gb_added']}GB",
        "data": result,
    }


@router.post("/apply-on-register", response_model=ReferralApplyOnRegisterResponse)
def apply_referral_on_register(
    request: ReferralApplyOnRegisterRequest,
    service: ReferralService = Depends(get_referral_service),
):
    """
    Aplica un código de referido durante el registro (sin autenticación).

    Usado por clientes (Telegram Bot, Mini App, etc.) después de crear
    un usuario para aplicar un código de referido de forma idempotente.
    """
    result = service.register_referral_by_user_id(
        user_id=request.user_id,
        referral_code=request.referral_code,
    )

    if not result["success"]:
        error_msg = result.get("error", "Unknown error")

        if error_msg == "user_not_found":
            return ReferralApplyOnRegisterResponse(
                success=False,
                message="User not found. Register first.",
                credits_earned=0,
            )

        if error_msg == "invalid_code":
            return ReferralApplyOnRegisterResponse(
                success=False,
                message="Invalid referral code.",
                credits_earned=0,
            )

        if error_msg == "self_referral":
            return ReferralApplyOnRegisterResponse(
                success=False,
                message="Cannot refer yourself.",
                credits_earned=0,
            )

        if error_msg == "already_referred":
            return ReferralApplyOnRegisterResponse(
                success=False,
                message="Already have a referrer.",
                credits_earned=0,
            )

        return ReferralApplyOnRegisterResponse(
            success=False,
            message=f"Error: {error_msg}",
            credits_earned=0,
        )

    return ReferralApplyOnRegisterResponse(
        success=True,
        message="Referral applied successfully",
        referral_code=request.referral_code,
        credits_earned=result["credits_to_new_user"],
    )
