"""Esquemas Pydantic para el sistema de referidos."""

from uuid import UUID

from pydantic import BaseModel, Field


class ReferralStatsResponse(BaseModel):
    """Respuesta con estadísticas de referidos."""

    referral_code: str
    total_referrals: int
    referral_credits: int
    referred_by: UUID | None = None


class ReferralApplyRequest(BaseModel):
    """Solicitud para aplicar un código de referido."""

    referral_code: str = Field(..., min_length=4, max_length=20)


class ReferralRedeemRequest(BaseModel):
    """Solicitud para canjear créditos por datos."""

    credits: int = Field(..., gt=0)


class ReferralOperationResponse(BaseModel):
    """Respuesta genérica para operaciones de referidos."""

    success: bool
    message: str | None = None
    data: dict | None = None


class ReferralApplyOnRegisterRequest(BaseModel):
    """Solicitud para aplicar código de referido durante registro."""

    user_id: UUID = Field(..., description="UUID del usuario")
    referral_code: str = Field(..., min_length=4, max_length=20, description="Código de referido")


class ReferralApplyOnRegisterResponse(BaseModel):
    """Respuesta para aplicación de código de referido durante registro."""

    success: bool
    message: str
    referral_code: str | None = None
    credits_earned: int = 0
