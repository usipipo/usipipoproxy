"""Backend API Adapter - Implementation of BackendApiPort."""

import logging
from typing import List
from uuid import UUID

import httpx
from usipipo_commons.domain.entities import User, VpnKey, Payment

from .error_translator import ErrorTranslator
from .http_client import BackendHttpClient
from ....application.ports.backend_api_port import BackendApiPort


logger = logging.getLogger(__name__)


class BackendApiAdapter(BackendApiPort):
    """
    Adaptador secundario para comunicación con el backend API.

    Implementa el contrato BackendApiPort usando httpx.
    """

    def __init__(self, base_url: str, timeout: float = 30.0):
        """
        Inicializa el adaptador.

        Args:
            base_url: URL base del backend
            timeout: Timeout en segundos
        """
        self.http_client = BackendHttpClient(base_url, timeout)

    async def close(self) -> None:
        """Cierra el cliente HTTP."""
        await self.http_client.close()

    # Auth endpoints

    async def auto_register(self, telegram_id: int) -> dict:
        """
        Auto-registra usuario y retorna tokens.

        Args:
            telegram_id: ID de Telegram del usuario

        Returns:
            dict con access_token, refresh_token, expires_in

        Raises:
            BackendConnectionError: Si no se puede conectar
        """
        try:
            client = await self.http_client.get_client()
            response = await client.post(
                "/api/v1/auth/telegram/auto-register",
                json={"telegram_id": telegram_id},
            )
            response.raise_for_status()
            data = response.json()
            return {
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "expires_in": data["expires_in"],
                "user_id": data.get("user_id"),
            }
        except httpx.HTTPStatusError as e:
            raise ErrorTranslator.translate(
                e.response.status_code,
                detail=e.response.text,
                original_exception=e,
            ) from e
        except httpx.ConnectError as e:
            raise ErrorTranslator.translate_connection_error(e) from e

    async def refresh_tokens(self, refresh_token: str) -> dict:
        """
        Renueva tokens con refresh token.

        Args:
            refresh_token: Refresh token actual

        Returns:
            dict con nuevos access_token y refresh_token

        Raises:
            AuthenticationError: Si el refresh token es inválido
        """
        try:
            client = await self.http_client.get_client()
            response = await client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": refresh_token},
            )
            response.raise_for_status()
            data = response.json()
            return {
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "expires_in": data["expires_in"],
            }
        except httpx.HTTPStatusError as e:
            raise ErrorTranslator.translate(
                e.response.status_code,
                detail=e.response.text,
                original_exception=e,
            ) from e
        except httpx.ConnectError as e:
            raise ErrorTranslator.translate_connection_error(e) from e

    async def get_user_profile(self, access_token: str) -> User:
        """
        Obtiene perfil del usuario.

        Args:
            access_token: JWT access token

        Returns:
            User entity con datos del usuario

        Raises:
            AuthenticationError: Si el token es inválido
        """
        try:
            client = await self.http_client.get_client()
            response = await client.get(
                "/api/v1/users/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            data = response.json()
            return User(**data)
        except httpx.HTTPStatusError as e:
            raise ErrorTranslator.translate(
                e.response.status_code,
                detail=e.response.text,
                original_exception=e,
            ) from e
        except httpx.ConnectError as e:
            raise ErrorTranslator.translate_connection_error(e) from e

    # VPN Keys endpoints

    async def list_vpn_keys(self, access_token: str) -> List[VpnKey]:
        """
        Lista VPN keys del usuario.

        Args:
            access_token: JWT access token

        Returns:
            Lista de VpnKey entities

        Raises:
            AuthenticationError: Si el token es inválido
        """
        try:
            client = await self.http_client.get_client()
            response = await client.get(
                "/api/v1/vpn/keys",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            data = response.json()
            return [VpnKey(**item) for item in data]
        except httpx.HTTPStatusError as e:
            raise ErrorTranslator.translate(
                e.response.status_code,
                detail=e.response.text,
                original_exception=e,
            ) from e
        except httpx.ConnectError as e:
            raise ErrorTranslator.translate_connection_error(e) from e

    async def create_vpn_key(
        self,
        access_token: str,
        name: str,
        key_type: str,
        data_limit_gb: float = 5.0,
    ) -> VpnKey:
        """
        Crea nueva VPN key.

        Args:
            access_token: JWT access token
            name: Nombre de la key
            key_type: Tipo de VPN (wireguard, outline)
            data_limit_gb: Límite de datos en GB

        Returns:
            VpnKey entity creada

        Raises:
            ValidationError: Si los datos son inválidos
        """
        try:
            client = await self.http_client.get_client()
            response = await client.post(
                "/api/v1/vpn/keys",
                json={
                    "name": name,
                    "key_type": key_type,
                    "data_limit_gb": data_limit_gb,
                },
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            data = response.json()
            return VpnKey(**data)
        except httpx.HTTPStatusError as e:
            raise ErrorTranslator.translate(
                e.response.status_code,
                detail=e.response.text,
                original_exception=e,
            ) from e
        except httpx.ConnectError as e:
            raise ErrorTranslator.translate_connection_error(e) from e

    async def delete_vpn_key(
        self,
        access_token: str,
        key_id: UUID,
    ) -> bool:
        """
        Elimina VPN key.

        Args:
            access_token: JWT access token
            key_id: ID de la key a eliminar

        Returns:
            True si se eliminó correctamente

        Raises:
            NotFoundError: Si la key no existe
        """
        try:
            client = await self.http_client.get_client()
            response = await client.delete(
                f"/api/v1/vpn/keys/{key_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            raise ErrorTranslator.translate(
                e.response.status_code,
                detail=e.response.text,
                original_exception=e,
            ) from e
        except httpx.ConnectError as e:
            raise ErrorTranslator.translate_connection_error(e) from e

    async def get_key_config(
        self,
        access_token: str,
        key_id: UUID,
    ) -> str:
        """
        Obtiene configuración de VPN key.

        Args:
            access_token: JWT access token
            key_id: ID de la key

        Returns:
            Configuración (WireGuard config o ss:// URL)

        Raises:
            NotFoundError: Si la key no existe
        """
        try:
            client = await self.http_client.get_client()
            response = await client.get(
                f"/api/v1/vpn/keys/{key_id}/config",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            data = response.json()
            return data["config"]
        except httpx.HTTPStatusError as e:
            raise ErrorTranslator.translate(
                e.response.status_code,
                detail=e.response.text,
                original_exception=e,
            ) from e
        except httpx.ConnectError as e:
            raise ErrorTranslator.translate_connection_error(e) from e

    # Payments endpoints

    async def create_crypto_payment(
        self,
        access_token: str,
        amount_usd: float,
        gb_purchased: float,
    ) -> Payment:
        """
        Crea pago con criptomoneda.

        Args:
            access_token: JWT access token
            amount_usd: Monto en USD
            gb_purchased: GB comprados

        Returns:
            Payment entity creada

        Raises:
            ValidationError: Si los datos son inválidos
        """
        try:
            client = await self.http_client.get_client()
            response = await client.post(
                "/api/v1/payments/crypto",
                json={
                    "amount_usd": amount_usd,
                    "gb_purchased": gb_purchased,
                },
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            data = response.json()
            return Payment(**data)
        except httpx.HTTPStatusError as e:
            raise ErrorTranslator.translate(
                e.response.status_code,
                detail=e.response.text,
                original_exception=e,
            ) from e
        except httpx.ConnectError as e:
            raise ErrorTranslator.translate_connection_error(e) from e

    async def create_stars_payment(
        self,
        access_token: str,
        amount_usd: float,
        gb_purchased: float,
    ) -> Payment:
        """
        Crea pago con Telegram Stars.

        Args:
            access_token: JWT access token
            amount_usd: Monto en USD
            gb_purchased: GB comprados

        Returns:
            Payment entity creada

        Raises:
            ValidationError: Si los datos son inválidos
        """
        try:
            client = await self.http_client.get_client()
            response = await client.post(
                "/api/v1/payments/stars",
                json={
                    "amount_usd": amount_usd,
                    "gb_purchased": gb_purchased,
                },
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            data = response.json()
            return Payment(**data)
        except httpx.HTTPStatusError as e:
            raise ErrorTranslator.translate(
                e.response.status_code,
                detail=e.response.text,
                original_exception=e,
            ) from e
        except httpx.ConnectError as e:
            raise ErrorTranslator.translate_connection_error(e) from e

    # Referrals endpoints

    async def get_referral_code(self, access_token: str) -> str:
        """
        Obtiene código de referido.

        Args:
            access_token: JWT access token

        Returns:
            Código de referido

        Raises:
            AuthenticationError: Si el token es inválido
        """
        try:
            client = await self.http_client.get_client()
            response = await client.get(
                "/api/v1/referrals/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            data = response.json()
            return data["referral_code"]
        except httpx.HTTPStatusError as e:
            raise ErrorTranslator.translate(
                e.response.status_code,
                detail=e.response.text,
                original_exception=e,
            ) from e
        except httpx.ConnectError as e:
            raise ErrorTranslator.translate_connection_error(e) from e

    async def get_referral_stats(self, access_token: str) -> dict:
        """
        Obtiene estadísticas de referidos.

        Args:
            access_token: JWT access token

        Returns:
            dict con stats (referrals_count, bonus_earned_gb, etc.)

        Raises:
            AuthenticationError: Si el token es inválido
        """
        try:
            client = await self.http_client.get_client()
            response = await client.get(
                "/api/v1/referrals/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise ErrorTranslator.translate(
                e.response.status_code,
                detail=e.response.text,
                original_exception=e,
            ) from e
        except httpx.ConnectError as e:
            raise ErrorTranslator.translate_connection_error(e) from e
