"""Mensajes para gestión de TrustTunnel VPN."""


class TrustTunnelMessages:
    """Mensajes para gestión de TrustTunnel VPN."""

    # ============================================
    # KEY CREATED WITH DEEPLINK
    # ============================================

    KEY_CREATED_WITH_DEEPLINK = (
        "✅ *Clave {vpn_type} Creada*\n\n"
        "🔑 Nombre: *{name}*\n"
        "💾 Límite: *{limit}GB*\n\n"
        "📱 *Configuración rápida:*\n"
        "Tocá el enlace para configurar automáticamente en tu dispositivo:\n\n"
        "{deeplink}\n\n"
        "💾 *¿Preferís manual?*\n"
        "Descargá el archivo .toml abajo e importalo en la app."
    )

    # ============================================
    # KEY DETAILS
    # ============================================

    KEY_DETAILS = (
        "🛡️ *{name}*\n\n"
        "📡 TrustTunnel • 🖥️ {server}\n"
        "━━━━━━━━━━━━━\n\n"
        "📊 Tu Consumo: {usage}/{limit}GB ({percentage}%)\n"
        "{usage_bar}\n\n"
        "{status_icon} Estado: *{status}*\n"
        "📅 Expira: {expires}\n"
        "🕐 Última vez: {last_seen}\n\n"
        "━━━━━━━━━━━━━\n"
        "🛡️ TrustTunnel Server Status\n"
        "{server_status_line}\n"
        "📈 {total_bandwidth} transferidos (total)\n"
        "👥 {active_clients} clientes activos\n"
        "━━━━━━━━━━━━━\n\n"
        "⚡ *Acciones:*"
    )

    # ============================================
    # METRICS DISPLAY
    # ============================================

    METRICS_DISPLAY = (
        "🛡️ *TrustTunnel Metrics*\n\n"
        "👥 Clientes activos: {active_clients}\n"
        "📈 Total transferido: {total_bandwidth}\n\n"
        "{client_breakdown}"
    )

    METRICS_CLIENT_ROW = "  {rank}. {client_name} — {bandwidth}"
    METRICS_NO_CLIENTS = "  Sin datos de clientes"

    # ============================================
    # CONFIG EXPORT
    # ============================================

    CONFIG_EXPORT_SUCCESS = "📥 *Configuración lista*\n\n📄 Archivo TOML generado\n\n⬇️ Descargalo abajo:"
    CONFIG_EXPORT_CAPTION = "🛡️ TrustTunnel config — {key_name}"

    # ============================================
    # DEEPLINK COPY
    # ============================================

    DEEPLINK_COPY_SUCCESS = (
        "📋 *Deeplink copiado*\n\n"
        "Tocá el enlace para configurar tu dispositivo:\n\n"
        "{deeplink}\n\n"
        "💡 _Enviado como texto para que puedas copiarlo y pegarlo en la app._"
    )

    DEEPLINK_NOT_AVAILABLE = (
        "⚠️ *Deeplink no disponible*\n\n"
        "No se pudo generar el deeplink para esta clave.\n\n"
        "💡 Usá el archivo .toml para configurar manualmente."
    )

    # ============================================
    # SETUP INSTRUCTIONS
    # ============================================

    SETUP_INSTRUCTIONS = (
        "📖 *Cómo configurar TrustTunnel*\n\n"
        "1️⃣ *Descargá la app:*\n"
        "   📱 Android: Play Store → buscá \"TrustTunnel\"\n"
        "   🍎 iOS: App Store → buscá \"TrustTunnel\"\n"
        "   💻 Desktop: github.com/trusttunnel/trusttunnel\n\n"
        "2️⃣ *Importá la configuración:*\n"
        "   📱 En la app, tocá \"Importar configuración\"\n"
        "   📂 Seleccioná el archivo .toml que descargaste\n\n"
        "3️⃣ *Conectate:*\n"
        "   ▶️ Tocá el botón de conectar\n"
        "   🟢 Cuando veas el ícono verde, estás protegido\n\n"
        "💡 *¿Necesitás ayuda?*\n"
        "   Usá /soporte para hablar con nuestro equipo"
    )

    # ============================================
    # SERVER STATUS
    # ============================================

    SERVER_ONLINE = "🟢 Online • {active_clients} clientes activos"
    SERVER_OFFLINE = "🔴 Offline • Sin conexión"
    SERVER_METRICS_UNAVAILABLE = "📡 Métricas no disponibles"

    # ============================================
    # CREATE KEY
    # ============================================

    KEY_CREATED = (
        "✅ *Clave TrustTunnel creada*\n\n"
        "🔑 Nombre: {name}\n"
        "🛡️ Tipo: TrustTunnel\n"
        "💾 Límite: {limit}GB\n\n"
        "🚀 ¡Lista para usar! Descargá la configuración ⬇️"
    )

    # ============================================
    # ERRORS
    # ============================================

    class Error:
        """Mensajes de error."""

        SERVICE_UNAVAILABLE = (
            "🔴 *Servicio no disponible*\n\n"
            "💥 TrustTunnel no responde en el servidor\n\n"
            "🔄 Intenta de nuevo en unos minutos 📡"
        )

        CONFIG_EXPORT_FAILED = (
            "❌ *Error al generar config*\n\n"
            "💥 No se pudo crear el archivo TOML\n\n"
            "🔄 Intenta de nuevo 📡"
        )

        NO_SERVERS = (
            "⚠️ *Sin servidores*\n\n"
            "🛡️ No hay servidores TrustTunnel disponibles\n\n"
            "💡 Probá otro protocolo ⚡"
        )

        KEY_NOT_FOUND = (
            "❌ *Clave no encontrada*\n\n"
            "🔒 No existe o no te pertenece 🔐"
        )
