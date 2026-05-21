"""Telegram Stars payment gateway client."""

import ipaddress
import logging
from typing import Any

import httpx

from src.shared.config import settings

logger = logging.getLogger(__name__)

# Telegram's official IP ranges for webhook verification
TELEGRAM_IP_RANGES = [
    "149.154.160.0/20",
    "91.108.4.0/22",
    "91.108.8.0/22",
    "91.108.12.0/22",
    "91.108.16.0/22",
    "91.108.56.0/22",
    "5.28.192.0/18",
]


def verify_telegram_ip(client_ip: str) -> bool:
    """
    Verifica si una IP pertenece a los rangos oficiales de Telegram.

    Args:
        client_ip: IP del cliente a verificar

    Returns:
        bool: True si es una IP de Telegram, False si no
    """
    try:
        ip = ipaddress.ip_address(client_ip)
        for cidr in TELEGRAM_IP_RANGES:
            if ip in ipaddress.ip_network(cidr):
                return True
    except ValueError:
        logger.warning(f"Invalid IP address format: {client_ip}")
    return False


class TelegramStarsClient:
    """Client for Telegram Stars payments."""

    def __init__(self):
        self.bot_token = settings.TELEGRAM_TOKEN
        self.base_url = "https://api.telegram.org"
        self.http = httpx.AsyncClient(base_url=self.base_url)

    async def create_invoice(
        self,
        amount_usd: float,
        user_telegram_id: int,
    ) -> dict[str, Any]:
        """Creates a Telegram Stars invoice."""
        try:
            stars_amount = int(amount_usd / 0.02)  # 1 Star ≈ $0.02

            response = await self.http.post(
                f"/bot{self.bot_token}/createInvoiceLink",
                json={
                    "title": "uSipipo VPN - GB Package",
                    "description": f"Purchase of {amount_usd} USD in VPN data",
                    "payload": f"user_{user_telegram_id}",
                    "provider_token": "",  # Empty for Telegram Stars
                    "currency": "XTR",  # Telegram Stars currency code
                    "prices": [{"label": "VPN Data", "amount": stars_amount}],
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create Telegram Stars invoice: {e}")
            raise

    async def answer_pre_checkout_query(
        self,
        query_id: str,
        ok: bool,
        error_message: str | None = None,
    ) -> bool:
        """Answers a pre-checkout query from Telegram."""
        try:
            payload = {
                "pre_checkout_query_id": query_id,
                "ok": ok,
            }
            if not ok and error_message:
                payload["error_message"] = error_message

            response = await self.http.post(
                f"/bot{self.bot_token}/answerPreCheckoutQuery",
                json=payload,
                timeout=10.0,
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to answer pre-checkout query: {e}")
            return False

    def verify_webhook_data(self, data: dict[str, Any]) -> bool:
        """Verifies pre-checkout query data from Telegram."""
        payload = data.get("invoice_payload", "")
        return payload.startswith("user_")

    async def close(self) -> None:
        """Closes the HTTP client."""
        await self.http.aclose()
