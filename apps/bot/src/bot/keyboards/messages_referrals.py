"""Messages for Referrals feature."""


class ReferralsMessages:
    """Messages for referral system."""

    class Menu:
        """Menu messages."""

        REFERRAL_STATS = (
            "🎯 *Tu Programa de Referidos*\n\n"
            "📊 *Estadísticas:*\n"
            "• Código: `{referral_code}`\n"
            "• Total referidos: `{total_referrals}`\n"
            "• Créditos disponibles: `{referral_credits}`\n\n"
            "🔗 *Tu enlace:*\n"
            "[{referral_link}]({referral_link})\n\n"
            "💡 *Beneficios:*\n"
            "• 1 crédito por cada amigo invitado\n"
            "• 5 créditos si tu amigo compra un paquete\n\n"
            "Comparte tu enlace y gana créditos!"
        )

        INVITE_LINK = (
            "🔗 *Tu Link de Invitación*\n\n"
            "[{referral_link}]({referral_link})\n\n"
            "Comparte este link con tus amigos y gana créditos cuando se unan.\n\n"
            "💰 *Recompensas:*\n"
            "• 1 crédito por cada referido\n"
            "• 10 créditos = 1 GB de datos"
        )

        REDEEM_CONFIRMATION = (
            "✅ *Canje Exitoso!*\n\n"
            "Has canjeado `{credits}` créditos por `{gb}` GB de datos.\n\n"
            "Tus créditos restantes: `{remaining_credits}`"
        )

        APPLY_SUCCESS = (
            "✅ *Código Aplicado!*\n\n"
            "Has aplicado el código de referido `{referral_code}`.\n"
            "¡Bienvenido al programa de referidos!"
        )

    class Error:
        """Error messages."""

        NOT_AUTHENTICATED = "❌ Debes estar autenticado para usar esta función."
        INVALID_CODE = "❌ Código de referido inválido o no encontrado."
        SELF_REFERRAL = "❌ No puedes usar tu propio código de referido."
        ALREADY_REFERRED = "❌ Ya tienes un código de referido aplicado."
        INSUFFICIENT_CREDITS = "❌ No tienes suficientes créditos para canjear."
        SYSTEM_ERROR = "❌ Error del sistema. Por favor intenta de nuevo más tarde."
