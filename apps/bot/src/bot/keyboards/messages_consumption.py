"""Mensajes para facturación por consumo."""

from src.infrastructure.config import settings

# Precio desde configuración (module-level constant for use in class body)
_CONSUMPTION_PRICE_PER_GB = settings.CONSUMPTION_PRICE_PER_GB_USD


class ConsumptionMessages:
    """Mensajes para el sistema de facturación por consumo."""

    # Precio desde configuración
    PRICE_PER_GB = _CONSUMPTION_PRICE_PER_GB

    class Menu:
        """Mensajes del menú principal de consumo."""

        MAIN_MENU = (
            "⚡ **Tarifa por Consumo**\n\n"
            "📊 **Tu estado:**\n"
            "{status_text}\n\n"
            "💡 *Navega sin límites y paga solo por lo que consumes*"
        )

        INACTIVE_STATE = (
            "⚡ **Tarifa por Consumo**\n\n"
            "📊 **Estado:** Modo consumo INACTIVO\n"
            "📦 Plan actual: 5GB gratuitos mensuales por clave\n\n"
            "💡 ¿Quieres navegar sin límites?\n"
            "Activa la Tarifa por Consumo y paga solo por lo que uses.\n\n"
            "⚡ *Elige una opción:*"
        )

        ACTIVE_STATE = (
            "⚡ **Tarifa por Consumo - ACTIVO**\n\n"
            "📊 **Estado:** Modo consumo ACTIVO\n"
            "📈 Consumo actual: {gb_consumed} GB\n"
            "💰 Costo acumulado: ${cost} USD\n"
            "📅 Días restantes: {days_remaining}\n\n"
            "💡 *Navegas sin límites. Paga solo por lo que consumes.*\n\n"
            "⚡ *Elige una opción:*"
        )

        DEBT_STATE = (
            "🔴 **Tarifa por Consumo - DEUDA PENDIENTE**\n\n"
            "⚠️ **Tienes una deuda pendiente:**\n"
            "💰 Monto: ${debt_amount} USD\n\n"
            "🔒 Tus claves VPN están bloqueadas.\n\n"
            "💳 Genera tu factura para pagar y desbloquear el servicio.\n\n"
            "⚡ *Elige una opción:*"
        )

        STATUS_INACTIVE = "⭕ Modo consumo INACTIVO\n📦 Usando plan gratuito (5GB/clave)"

        STATUS_ACTIVE = "✅ Modo consumo ACTIVO\n📊 Usa `/mi_consumo` para ver detalles"

        STATUS_DEBT = "🔴 TIENES DEUDA PENDIENTE\n💳 Genera factura para pagar"

    class Activation:
        """Mensajes relacionados con la activación del modo consumo."""

        TERMS = (
            "⚠️ **¡ATENCIÓN: MODO CONSUMO LIBRE!** ⚠️\n\n"
            "Estás a punto de activar la **Tarifa por Consumo**. "
            "Lee cuidadosamente los términos antes de continuar.\n\n"
            "📋 **TÉRMINOS Y CONDICIONES**\n\n"
            "1️⃣ **Consumo Ilimitado:**\n"
            "   • Navegarás sin límites de velocidad ni de datos\n"
            "   • Los 5GB gratuitos mensuales se pausan temporalmente\n\n"
            "2️⃣ **Facturación Postpago:**\n"
            "   • En **30 días** recibirás una factura por el consumo total\n"
            f"   • Precio: **${_CONSUMPTION_PRICE_PER_GB:.2f} USD por GB**\n"
            "   • Pagas exactamente lo que consumes, al centavo\n\n"
            "3️⃣ **Consecuencias de No Pagar:**\n"
            "   • Si no pagas la factura, **TODAS tus claves VPN serán bloqueadas**\n"
            "   • Incluye las claves con datos gratuitos\n"
            "   • No podrás usar el servicio hasta pagar la deuda\n\n"
            "4️⃣ **Desactivación Automática:**\n"
            "   • Al pagar, el modo consumo se desactiva automáticamente\n"
            "   • Debes reactivarlo manualmente si deseas otro ciclo\n\n"
            "⚠️ **Este es un sistema de crédito basado en confianza.**\n"
            "Al activar este modo, asumes toda la responsabilidad del consumo.\n\n"
            "💰 **EJEMPLO DE COSTOS**\n\n"
            "Si consumes:\n"
            f"• 1 GB = ${_CONSUMPTION_PRICE_PER_GB:.2f} USD\n"
            f"• 5 GB = ${_CONSUMPTION_PRICE_PER_GB * 5:.2f} USD\n"
            f"• 10 GB = ${_CONSUMPTION_PRICE_PER_GB * 10:.2f} USD\n\n"
            f"💡 *Si usas menos de 10GB, pagas menos. Si usas más, sigues pagando "
            f"solo ${_CONSUMPTION_PRICE_PER_GB:.2f}/GB sin límites.*"
        )

        CONFIRMATION_PROMPT = (
            "❓ **¿Aceptas activar la tarifa por consumo bajo tu propia responsabilidad?**\n\n"
            "Al presionar '✅ Acepto', confirmas que:\n"
            "• Entiendes que pagarás postconsumo\n"
            "• Aceptas que tus claves se bloquearán si no pagas\n"
            "• Has leído y comprendido todos los términos"
        )

        SUCCESS = (
            "✅ **¡Modo Consumo Activado!**\n\n"
            "🚀 Ahora puedes navegar **sin límites**\n"
            "📅 Tu ciclo de 30 días comenzó hoy\n"
            f"💰 Pagas solo por lo que consumes: ${_CONSUMPTION_PRICE_PER_GB:.2f}/GB\n\n"
            "📊 Usa `/mi_consumo` para ver tu consumo actual\n"
            "ℹ️ En 30 días recibirás tu factura"
        )

        FAILED = (
            "❌ **Error al activar modo consumo**\n\n"
            "{reason}\n\n"
            "💡 Intenta nuevamente o contacta al soporte."
        )

        ALREADY_ACTIVE = (
            "ℹ️ **Ya tienes el modo consumo activo**\n\n"
            "📊 Usa `/mi_consumo` para ver tu consumo actual\n"
            "📅 Tu ciclo cierra en {days_remaining} días"
        )

        CANNOT_ACTIVATE = (
            "❌ **No puedes activar el modo consumo**\n\n"
            "{reason}\n\n"
            "💡 Resuelve este problema antes de intentar nuevamente."
        )

    class Cancellation:
        """Mensajes para cancelación del modo consumo."""

        CONFIRMATION_HEADER = (
            "⚠️ **CANCELAR MODO CONSUMO** ⚠️\n\n"
            "Estás a punto de cancelar tu ciclo de consumo anticipadamente."
        )

        SUMMARY_WITH_DEBT = (
            "📊 **Resumen de tu ciclo actual:**\n\n"
            "📅 **Días transcurridos:** {days_active}/30\n"
            "📈 **Consumo acumulado:** {gb_consumed} GB\n"
            "💰 **Costo actual:** ${cost} USD\n\n"
            "⚠️ **Al cancelar:**\n"
            "• Tu ciclo se cerrará inmediatamente\n"
            "• Todas tus claves VPN serán bloqueadas\n"
            f"• Deberás pagar ${_CONSUMPTION_PRICE_PER_GB:.2f}/GB consumido para desbloquear\n\n"
            "¿Deseas proceder con la cancelación?"
        )

        SUMMARY_NO_DEBT = (
            "📊 **Resumen de tu ciclo actual:**\n\n"
            "📅 **Días transcurridos:** {days_active}/30\n"
            "📈 **Consumo acumulado:** 0 GB\n"
            "💰 **Costo actual:** $0.00 USD\n\n"
            "⚠️ **Al cancelar:**\n"
            "• Tu ciclo se cerrará inmediatamente\n"
            "• Volverás al plan gratuito de 5GB\n\n"
            "¿Deseas proceder con la cancelación?"
        )

        SUCCESS_WITH_DEBT = (
            "✅ **Modo Consumo Cancelado**\n\n"
            "🚫 Tu ciclo de consumo ha sido cerrado anticipadamente.\n"
            "🔒 Todas tus claves VPN han sido bloqueadas.\n\n"
            "💳 **Próximo paso:**\n"
            "Genera tu factura y realiza el pago para desbloquear el servicio.\n"
            "💰 **Monto a pagar:** ${cost} USD"
        )

        SUCCESS_NO_DEBT = (
            "✅ **Modo Consumo Cancelado**\n\n"
            "🚫 Tu ciclo de consumo ha sido cerrado.\n"
            "📦 Volverás al plan gratuito de 5GB mensuales.\n\n"
            "💡 No hay deuda pendiente. Tus claves están activas."
        )

        FAILED = (
            "❌ **Error al cancelar modo consumo**\n\n"
            "{reason}\n\n"
            "💡 Intenta nuevamente o contacta al soporte."
        )

        CANNOT_CANCEL = (
            "❌ **No puedes cancelar el modo consumo**\n\n"
            "{reason}\n\n"
            "💡 Resuelve este problema antes de intentar nuevamente."
        )

    class Status:
        """Mensajes para estado de consumo."""

        ACTIVE = (
            "📊 **Tu Consumo Actual**\n\n"
            "🔄 **Estado:** Activo (consumiendo)\n"
            "📅 **Días activo:** {days_active}/30\n"
            "📈 **Consumo:** {gb_consumed} GB ({mb_consumed} MB)\n"
            "💰 **Costo acumulado:** ${cost} USD\n"
            "📅 **Días restantes:** {days_remaining}\n\n"
            "💡 *El ciclo cierra en {days_remaining} días. "
            "Recuerda que pagarás por lo consumido.*"
        )

        INACTIVE = (
            "ℹ️ **No tienes modo consumo activo**\n\n"
            "📦 Tu plan actual:\n"
            "• 5GB gratuitos mensuales por clave\n\n"
            "💡 ¿Quieres navegar sin límites?\n"
            "Activa la Tarifa por Consumo en el menú principal."
        )

        CLOSED_CYCLE = (
            "🔒 **Ciclo Cerrado - Deuda Pendiente**\n\n"
            "📅 **Días totales:** 30/30\n"
            "📈 **Consumo total:** {gb_consumed} GB\n"
            "💰 **Total a pagar:** ${cost} USD\n\n"
            "⚠️ **Tus claves VPN están bloqueadas**\n\n"
            "💳 Presiona 'Generar Factura' para pagar y desbloquear"
        )

    class Invoices:
        """Mensajes para facturación."""

        HEADER = (
            "📜 **Tus Facturas**\n\n"
            "📊 **Resumen:**\n"
            "• Total: {total}\n"
            "• ⏳ Pendientes: {pending}\n"
            "• ✅ Pagadas: {paid}\n"
            "• ❌ Expiradas: {expired}\n\n"
            "📋 **Lista de facturas:**\n\n"
        )

        INVOICE_ITEM = "🔹 {date} - ${amount} USD\n   Estado: {status} ({status_text})\n\n"

        NO_INVOICES = (
            "📜 **Sin facturas**\n\n"
            "Aún no has generado ninguna factura de consumo.\n\n"
            "💡 Cuando actives el modo consumo y completes un ciclo, verás tus facturas aquí."
        )

    class Error:
        """Mensajes de error."""

        GENERIC = (
            "❌ **Error del sistema**\n\n"
            "Ocurrió un error inesperado. Por favor, intenta nuevamente."
        )

        SYSTEM_ERROR = (
            "🚨 **Error del sistema**\n\n💥 Fallo temporal\n\n🔄 Intenta de nuevo en un momento 📡"
        )

        NOT_AUTHENTICATED = (
            "🔒 **No autenticado**\n\n"
            "Debes iniciar sesión para acceder a esta función.\n\n"
            "💡 Usa /start para autenticarte."
        )

        UNAUTHORIZED = "🚫 **Acceso denegado**\n\nNo tienes permisos para realizar esta acción."

        INVOICE_GENERATION = (
            "❌ **Error generando factura**\n\n"
            "{reason}\n\n"
            "💡 Intenta nuevamente o contacta al soporte."
        )

        PAYMENT_PROCESSING = (
            "❌ **Error procesando pago**\n\n"
            "{reason}\n\n"
            "💡 Si el problema persiste, contacta al soporte."
        )

    class Invoice:
        """Mensajes para pagos de facturas."""

        SELECT_PAYMENT_METHOD = (
            "💳 **Selecciona Método de Pago**\n\n"
            "📈 **Consumo total:** {consumption_formatted}\n"
            "💰 **Total a pagar:** {cost_formatted}\n\n"
            "¿Cómo deseas pagar?"
        )

        CRYPTO_PAYMENT = (
            "💰 **Pago con USDT - BSC**\n\n"
            "📈 **Consumo:** {consumption_formatted}\n"
            "💰 **Monto a pagar:** {cost_formatted}\n\n"
            "📋 **Wallet para pago:**\n"
            "`{wallet_address}`\n\n"
            "⏱️ **Tiempo límite:** {time_remaining}\n\n"
            "⚠️ **Importante:**\n"
            "• Envía exactamente el monto indicado\n"
            "• Solo USDT en red BSC (BEP20)\n"
            "• Espera las confirmaciones de la red\n\n"
            "✅ El sistema detectará automáticamente tu pago"
        )

        STARS_PAYMENT = (
            "💫 **Pago con Telegram Stars**\n\n"
            "📈 **Consumo:** {consumption_formatted}\n"
            "💰 **Equivalente:** {cost_formatted}\n"
            "⭐ **Stars a pagar:** {stars_amount} ⭐\n\n"
            "⏱️ **Tiempo límite:** {time_remaining}\n\n"
            "✅ Presiona el botón de pago para completar la transacción"
        )

        PAYMENT_SUCCESS = (
            "🎉 **¡Pago Recibido Exitosamente!**\n\n"
            "💰 **Monto pagado:** {cost_formatted}\n"
            "📈 **Consumo pagado:** {consumption_formatted}\n\n"
            "✅ Tu deuda ha sido liquidada\n"
            "🔓 Todas tus claves VPN han sido desbloqueadas\n"
            "📦 Los 5GB gratuitos mensuales han sido reactivados\n\n"
            "⚠️ **El modo consumo se ha desactivado automáticamente.**\n"
            "Si deseas volver a navegar sin límites, actívalo nuevamente."
        )

        PAYMENT_EXPIRED = (
            "⏱️ **Factura Expirada**\n\n"
            "La factura generada ha expirado (30 minutos).\n\n"
            "💡 Genera una nueva factura para realizar el pago."
        )

        NO_PENDING_DEBT = "ℹ️ **No tienes deudas pendientes**\n\n✅ Estás al día con tus pagos"
