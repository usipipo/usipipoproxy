"""Plan type enum for subscriptions."""

from enum import Enum


class PlanType(str, Enum):
    """Tipos de plan de suscripción."""

    ONE_MONTH = "one_month"
    THREE_MONTHS = "three_months"
    SIX_MONTHS = "six_months"
