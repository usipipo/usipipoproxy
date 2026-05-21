"""Mensajes para perfil de usuario."""

from datetime import datetime


class UserProfileMessages:
    """Mensajes para mostrar el perfil del usuario."""

    class Profile:
        """Mensajes del perfil de usuario."""

        HEADER = "👤 **Tu Perfil uSipipo**\n\n"

        PERSONAL_INFO = (
            "📋 **Información Personal**\n"
            "├─ Usuario: @{username}\n"
            "├─ Nombre: {full_name}\n"
            "└─ ID Telegram: `{telegram_id}`\n\n"
        )

        BALANCE_INFO = (
            "💰 **Balance y Datos**\n"
            "├─ Saldo Actual: {balance_gb} GB\n"
            "├─ Total Comprado: {total_purchased_gb} GB\n"
            "└─ Claves VPN Activas: {vpn_keys_count}\n\n"
        )

        REFERRAL_INFO = (
            "🎁 **Programa de Referidos**\n"
            "├─ Código: `{referral_code}`\n"
            "├─ Referidos: {referrals_count} usuarios\n"
            "└─ Créditos Ganados: {referral_credits} GB\n\n"
        )

        LOYALTY_INFO = (
            "⭐ **Programa de Lealtad**\n"
            "├─ Nivel: {loyalty_level} ({loyalty_bonus}% bonus)\n"
            "├─ Compras Realizadas: {purchase_count}\n"
            "└─ Bonus Bienvenida: {welcome_bonus_status}\n\n"
        )

        ACCOUNT_INFO = (
            "📅 **Información de Cuenta**\n"
            "├─ Creada: {created_at}\n"
            "└─ Última Actualización: {updated_at}\n\n"
        )

        TIP = "💡 *Consejo: Invita más amigos para aumentar tu bonus de lealtad*"

        FULL_PROFILE = (
            HEADER
            + PERSONAL_INFO
            + BALANCE_INFO
            + REFERRAL_INFO
            + LOYALTY_INFO
            + ACCOUNT_INFO
            + TIP
        )

    class Error:
        """Mensajes de error."""

        NOT_AUTHENTICATED = (
            "🔒 **No autenticado**\n\n"
            "Debes iniciar sesión para ver tu perfil.\n\n"
            "💡 Usa /start para autenticarte."
        )

        API_ERROR = (
            "❌ **Error al cargar perfil**\n\n"
            "No se pudo obtener tu información.\n\n"
            "🔄 Intenta nuevamente en un momento."
        )

        GENERIC_ERROR = (
            "❌ **Error del sistema**\n\n"
            "Ocurrió un error inesperado.\n\n"
            "💡 Intenta nuevamente o contacta al soporte."
        )

    @staticmethod
    def format_personal_info(
        username: str | None, first_name: str | None, last_name: str | None, telegram_id: int
    ) -> str:
        """Formatea información personal manejando valores nulos."""
        username_str = username if username else "No disponible"
        full_name = " ".join(filter(None, [first_name or "", last_name or ""])) or "No disponible"

        return UserProfileMessages.Profile.PERSONAL_INFO.format(
            username=username_str,
            full_name=full_name,
            telegram_id=telegram_id,
        )

    @staticmethod
    def format_balance_info(
        balance_gb: float, total_purchased_gb: float, vpn_keys_count: int
    ) -> str:
        """Formatea información de balance."""
        return UserProfileMessages.Profile.BALANCE_INFO.format(
            balance_gb=f"{balance_gb:.2f}",
            total_purchased_gb=f"{total_purchased_gb:.2f}",
            vpn_keys_count=vpn_keys_count,
        )

    @staticmethod
    def format_referral_info(
        referral_code: str, referrals_count: int, referral_credits: float
    ) -> str:
        """Formatea información de referidos."""
        return UserProfileMessages.Profile.REFERRAL_INFO.format(
            referral_code=referral_code,
            referrals_count=referrals_count,
            referral_credits=f"{referral_credits:.1f}",
        )

    @staticmethod
    def format_loyalty_info(
        loyalty_bonus_percent: int, purchase_count: int, welcome_bonus_used: bool
    ) -> str:
        """Formatea información de lealtad."""
        # Determine loyalty level based on bonus percent
        if loyalty_bonus_percent >= 10:
            level = "Platinum"
        elif loyalty_bonus_percent >= 7:
            level = "Gold"
        elif loyalty_bonus_percent >= 5:
            level = "Silver"
        elif loyalty_bonus_percent >= 3:
            level = "Bronze"
        else:
            level = "Standard"

        welcome_status = "✅ Usado" if welcome_bonus_used else "⏳ Disponible"

        return UserProfileMessages.Profile.LOYALTY_INFO.format(
            loyalty_level=level,
            loyalty_bonus=loyalty_bonus_percent,
            purchase_count=purchase_count,
            welcome_bonus_status=welcome_status,
        )

    @staticmethod
    def format_account_info(created_at: datetime, updated_at: datetime) -> str:
        """Formatea información de cuenta."""
        created_str = created_at.strftime("%d %b %Y")
        updated_str = updated_at.strftime("%d %b %Y")

        return UserProfileMessages.Profile.ACCOUNT_INFO.format(
            created_at=created_str,
            updated_at=updated_str,
        )
