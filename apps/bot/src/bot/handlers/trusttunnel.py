"""Handlers para gestión de TrustTunnel VPN."""

import io
import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from telegram import InputFile, Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from src.bot.keyboards.messages_trusttunnel import TrustTunnelMessages
from src.bot.keyboards.trusttunnel import TrustTunnelKeyboard
from src.infrastructure.api_client import APIClient
from src.infrastructure.token_storage import TokenStorage

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class TrustTunnelHandler:
    """Handler para gestión de TrustTunnel VPN."""

    def __init__(self, api_client: APIClient, token_storage: TokenStorage):
        self.api = api_client
        self.tokens = token_storage
        logger.info("🛡️ TrustTunnelHandler initialized")

    async def _get_auth_headers(self, telegram_id: int) -> dict[str, str]:
        """Obtiene headers de autenticación."""
        tokens = await self.tokens.get(telegram_id)
        if not tokens:
            raise PermissionError("User not authenticated")
        return {"Authorization": f"Bearer {tokens['access_token']}"}

    async def _fetch_trusttunnel_metrics(
        self, server_id: str, telegram_id: int
    ) -> dict | None:
        """Fetch TrustTunnel metrics for a server."""
        try:
            tokens = await self.tokens.get(telegram_id)
            if not tokens:
                logger.warning(
                    f"No tokens for user {telegram_id} when fetching TrustTunnel metrics"
                )
                return None

            headers = {"Authorization": f"Bearer {tokens['access_token']}"}
            response = await self.api.get(
                f"/vpn/servers/{server_id}/trusttunnel/metrics",
                headers=headers,
            )
            return response
        except Exception as e:
            logger.error(f"Error fetching TrustTunnel metrics for {server_id}: {e}")
            return None

    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human-readable string."""
        if bytes_value == 0:
            return "0.0 B"

        gb = bytes_value / (1024**3)
        if gb >= 1.0:
            return f"{gb:.1f} GB"

        mb = bytes_value / (1024**2)
        if mb >= 1.0:
            return f"{mb:.1f} MB"

        kb = bytes_value / 1024
        return f"{kb:.1f} KB"

    def _format_top_clients(self, client_bytes: dict[str, int], limit: int = 5) -> str:
        """Format top N clients by bandwidth."""
        if not client_bytes:
            return TrustTunnelMessages.METRICS_NO_CLIENTS

        sorted_clients = sorted(client_bytes.items(), key=lambda x: x[1], reverse=True)
        lines = []
        for rank, (name, bytes_val) in enumerate(sorted_clients[:limit], 1):
            lines.append(
                TrustTunnelMessages.METRICS_CLIENT_ROW.format(
                    rank=rank,
                    client_name=name,
                    bandwidth=self._format_bytes(bytes_val),
                )
            )
        return "\n".join(lines)

    def _format_last_seen(self, last_seen_at, now: datetime | None = None) -> str:
        """Format last seen timestamp."""
        if not last_seen_at:
            return "Nunca"

        if now is None:
            now = datetime.now(timezone.utc)

        if last_seen_at.tzinfo is None:
            last_seen_at = last_seen_at.replace(tzinfo=timezone.utc)

        diff = now - last_seen_at
        total_seconds = int(diff.total_seconds())

        if total_seconds < 0:
            return last_seen_at.strftime("%Y-%m-%d %H:%M")

        if total_seconds < 60:
            return "Hace < 1 minuto"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            return f"Hace {minutes} minuto{'s' if minutes > 1 else ''}"
        elif total_seconds < 86400:
            hours = total_seconds // 3600
            return f"Hace {hours} hora{'s' if hours > 1 else ''}"
        else:
            days = total_seconds // 86400
            return f"Hace {days} día{'s' if days > 1 else ''}"

    def _generate_progress_bar(self, percentage: float, width: int = 10) -> str:
        """Generate progress bar string."""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"{bar} {percentage:.0f}%"

    async def show_key_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra detalles de una clave TrustTunnel con métricas."""
        query = update.callback_query
        if query is None or query.data is None:
            return

        await query.answer()

        key_id = query.data.split("_")[-1]
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} viewing TrustTunnel key {key_id}")

        try:
            headers = await self._get_auth_headers(telegram_id)
            response = await self.api.get(f"/vpn/keys/{key_id}", headers=headers)

            key = response
            status = "Activa" if key.get("status", "active") == "active" else "Inactiva"
            status_icon = "🟢" if key.get("status", "active") == "active" else "🔴"

            usage_percentage = (
                (key.get("data_used_gb", 0) / key.get("data_limit_gb", 1)) * 100
                if key.get("data_limit_gb", 0) > 0
                else 0
            )

            usage_bar = self._generate_progress_bar(usage_percentage)

            last_seen_at = key.get("last_used_at")
            if isinstance(last_seen_at, str):
                try:
                    last_seen_at = datetime.fromisoformat(last_seen_at).replace(
                        tzinfo=timezone.utc
                    )
                except (ValueError, TypeError):
                    last_seen_at = None
            last_seen_text = self._format_last_seen(last_seen_at)

            # Fetch TrustTunnel metrics
            server_id = key.get("server_id")
            server_status_line = TrustTunnelMessages.SERVER_METRICS_UNAVAILABLE
            total_bandwidth = "N/A"
            active_clients = "N/A"

            if server_id:
                tt_metrics = await self._fetch_trusttunnel_metrics(server_id, telegram_id)

                if tt_metrics:
                    ac = tt_metrics.get("active_clients", 0)
                    total_bytes = tt_metrics.get("total_bytes_transferred", 0)

                    server_status_line = TrustTunnelMessages.SERVER_ONLINE.format(
                        active_clients=ac
                    )
                    total_bandwidth = self._format_bytes(total_bytes)
                    active_clients = str(ac)

            message = TrustTunnelMessages.KEY_DETAILS.format(
                name=key.get("name", "Unknown"),
                server=key.get("server_name", "N/A"),
                usage=f"{key.get('data_used_gb', 0):.1f}",
                limit=f"{key.get('data_limit_gb', 0):.1f}",
                percentage=f"{usage_percentage:.0f}",
                usage_bar=usage_bar,
                status=status,
                status_icon=status_icon,
                expires=key.get("expires_at", "N/A")[:10] if key.get("expires_at") else "N/A",
                last_seen=last_seen_text,
                server_status_line=server_status_line,
                total_bandwidth=total_bandwidth,
                active_clients=active_clients,
            )

            keyboard = TrustTunnelKeyboard.key_actions(
                key_id,
                key.get("status", "active") == "active",
            )

            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.error(f"Error showing TrustTunnel key details: {e}")
            await query.edit_message_text(
                text=TrustTunnelMessages.Error.KEY_NOT_FOUND,
                reply_markup=TrustTunnelKeyboard.back_to_list(),
                parse_mode="Markdown",
            )

    async def export_config(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Exporta configuración TrustTunnel como archivo TOML."""
        query = update.callback_query
        if query is None or query.data is None:
            return

        await query.answer()

        key_id = query.data.replace("vpn_download_tt_", "")
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} downloading TrustTunnel config for key {key_id}")

        try:
            headers = await self._get_auth_headers(telegram_id)
            response = await self.api.get(f"/vpn/keys/{key_id}/config", headers=headers)

            config_content = response.get("config", "")

            # Get key name for caption
            key_response = await self.api.get(f"/vpn/keys/{key_id}", headers=headers)
            key_name = key_response.get("name", "trusttunnel")

            # Send as file
            file_io = io.BytesIO(config_content.encode("utf-8"))
            file_io.name = f"{key_name}.toml"

            await query.message.reply_document(
                document=InputFile(file_io),
                caption=TrustTunnelMessages.CONFIG_EXPORT_CAPTION.format(key_name=key_name),
                filename=f"{key_name}.toml",
            )

            # Send setup instructions with download buttons
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup

            download_keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📱 Android", url="https://play.google.com/store/apps/details?id=com.adguard.trusttunnel"),
                    InlineKeyboardButton("🍎 iOS", url="https://apps.apple.com/us/app/trusttunnel/id6755807890"),
                ],
                [
                    InlineKeyboardButton("💻 GitHub Releases", url="https://github.com/TrustTunnel/TrustTunnelClient"),
                ],
            ])

            await query.message.reply_text(
                text=TrustTunnelMessages.SETUP_INSTRUCTIONS,
                reply_markup=download_keyboard,
                parse_mode="Markdown",
            )

            await query.edit_message_text(
                text=TrustTunnelMessages.CONFIG_EXPORT_SUCCESS,
                reply_markup=TrustTunnelKeyboard.back_to_list(),
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.error(f"Error exporting TrustTunnel config: {e}")
            await query.edit_message_text(
                text=TrustTunnelMessages.Error.CONFIG_EXPORT_FAILED,
                reply_markup=TrustTunnelKeyboard.back_to_list(),
                parse_mode="Markdown",
            )

    async def copy_deeplink(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Envía el deeplink TrustTunnel como texto para copiar."""
        query = update.callback_query
        if query is None or query.data is None:
            return

        await query.answer()

        key_id = query.data.replace("vpn_copy_deeplink_", "")
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} copying TrustTunnel deeplink for key {key_id}")

        try:
            headers = await self._get_auth_headers(telegram_id)
            response = await self.api.get(f"/vpn/keys/{key_id}", headers=headers)

            deeplink = response.get("deeplink", "")

            if deeplink:
                await query.message.reply_text(
                    text=TrustTunnelMessages.DEEPLINK_COPY_SUCCESS.format(deeplink=deeplink),
                    parse_mode="Markdown",
                    disable_web_page_preview=True,
                )
            else:
                await query.message.reply_text(
                    text=TrustTunnelMessages.DEEPLINK_NOT_AVAILABLE,
                    parse_mode="Markdown",
                )

            await query.edit_message_text(
                text=TrustTunnelMessages.KEY_DETAILS.format(
                    name=response.get("name", "Unknown"),
                    server=response.get("server_name", "N/A"),
                    usage=f"{response.get('data_used_gb', 0):.1f}",
                    limit=f"{response.get('data_limit_gb', 0):.1f}",
                    percentage="0",
                    usage_bar="░░░░░░░░░░ 0%",
                    status="Activa" if response.get("status", "active") == "active" else "Inactiva",
                    status_icon="🟢" if response.get("status", "active") == "active" else "🔴",
                    expires=response.get("expires_at", "N/A")[:10] if response.get("expires_at") else "N/A",
                    last_seen="Nunca",
                    server_status_line=TrustTunnelMessages.SERVER_METRICS_UNAVAILABLE,
                    total_bandwidth="N/A",
                    active_clients="N/A",
                ),
                reply_markup=TrustTunnelKeyboard.key_actions(
                    key_id,
                    response.get("status", "active") == "active",
                ),
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.error(f"Error copying TrustTunnel deeplink: {e}")
            await query.edit_message_text(
                text=TrustTunnelMessages.DEEPLINK_NOT_AVAILABLE,
                reply_markup=TrustTunnelKeyboard.back_to_list(),
                parse_mode="Markdown",
            )

    async def delete_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra confirmación de eliminación."""
        query = update.callback_query
        if query is None or query.data is None:
            return

        await query.answer()
        key_id = query.data.replace("vpn_delete_", "")

        await query.edit_message_text(
            text=(
                "⚠️ ¿Estás seguro de que querés eliminar esta clave TrustTunnel?\n\n"
                "🔌 Todos los dispositivos conectados serán desconectados."
            ),
            reply_markup=TrustTunnelKeyboard.confirm_delete(key_id),
            parse_mode="Markdown",
        )

    async def confirm_delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirma y ejecuta la eliminación."""
        query = update.callback_query
        if query is None or query.data is None:
            return

        await query.answer()
        key_id = query.data.replace("vpn_confirm_delete_", "")
        telegram_id = update.effective_user.id if update.effective_user else 0

        try:
            headers = await self._get_auth_headers(telegram_id)
            await self.api.delete(f"/vpn/keys/{key_id}", headers=headers)

            await query.edit_message_text(
                text=(
                    "🗑️ *Clave TrustTunnel eliminada*\n\n"
                    "💥 Destruida permanentemente\n\n"
                    "🔌 Dispositivos desconectados ⚡"
                ),
                reply_markup=TrustTunnelKeyboard.back_to_list(),
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.error(f"Error deleting TrustTunnel key: {e}")
            await query.edit_message_text(
                text="❌ Error al eliminar la clave. Intenta de nuevo.",
                reply_markup=TrustTunnelKeyboard.back_to_list(),
                parse_mode="Markdown",
            )


def get_trusttunnel_handlers(api_client: APIClient, token_storage: TokenStorage):
    """Retorna los handlers de TrustTunnel."""
    return []


def get_trusttunnel_callback_handlers(api_client: APIClient, token_storage: TokenStorage):
    """Retorna los handlers de callback para TrustTunnel."""
    handler = TrustTunnelHandler(api_client, token_storage)

    return [
        CallbackQueryHandler(handler.show_key_details, pattern="^vpn_key_details_"),
        CallbackQueryHandler(handler.export_config, pattern="^vpn_download_tt_"),
        CallbackQueryHandler(handler.copy_deeplink, pattern="^vpn_copy_deeplink_"),
        CallbackQueryHandler(handler.delete_key, pattern="^vpn_delete_"),
        CallbackQueryHandler(handler.confirm_delete, pattern="^vpn_confirm_delete_"),
    ]
