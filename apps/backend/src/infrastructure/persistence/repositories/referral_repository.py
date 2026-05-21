"""Implementación del repositorio de referidos con SQLAlchemy."""

import uuid

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session
from usipipo_commons.domain.entities.referral import Referral

from src.core.domain.interfaces.i_referral_repository import IReferralRepository
from src.infrastructure.persistence.models.referral_model import ReferralModel


class ReferralRepository(IReferralRepository):
    """Implementación de repositorio de referidos con SQLAlchemy."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, referral: Referral) -> Referral:
        """Guarda o actualiza una relación de referido."""
        model = ReferralModel.from_entity(referral)
        self.session.merge(model)
        self.session.commit()
        return model.to_entity()

    def get_by_id(self, referral_id: uuid.UUID) -> Referral | None:
        """Obtiene un referido por su ID."""
        result = self.session.execute(
            select(ReferralModel).where(ReferralModel.id == referral_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    def get_by_referred_id(self, referred_id: uuid.UUID) -> Referral | None:
        """Busca quién refirió a un usuario específico."""
        result = self.session.execute(
            select(ReferralModel).where(ReferralModel.referred_id == referred_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    def get_referrals_by_referrer(self, referrer_id: uuid.UUID) -> list[Referral]:
        """Obtiene la lista de usuarios referidos por alguien."""
        result = self.session.execute(
            select(ReferralModel).where(ReferralModel.referrer_id == referrer_id)
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    def count_referrals_by_referrer(self, referrer_id: uuid.UUID) -> int:
        """Cuenta el total de referidos de un usuario."""
        result = self.session.execute(
            select(func.count()).where(ReferralModel.referrer_id == referrer_id)
        )
        return result.scalar() or 0

    def mark_bonus_applied(self, referral_id: uuid.UUID) -> bool:
        """Marca un bono de referido como ya aplicado."""
        try:
            query = (
                update(ReferralModel)
                .where(ReferralModel.id == referral_id)
                .values(bonus_applied=True)
            )
            self.session.execute(query)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False
