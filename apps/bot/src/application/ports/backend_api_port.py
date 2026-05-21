"""Backend API Port - Contract for backend communication."""

from typing import List, Protocol
from uuid import UUID

from usipipo_commons.domain.entities import User, VpnKey, Payment


class BackendApiPort(Protocol):
    """
    Contrato para comunicación con el backend API.

    Define todos los métodos necesarios para interactuar
    con el backend centralizado de uSipipo.
    """

    # Auth endpoints
    async def auto_register(self, telegram_id: int) -> dict:
        """
        Auto-registra usuario y retorna tokens.

        Args:
            telegram_id: ID de Telegram del usuario

        Returns:
            dict con access_token, refresh_token, expires_in
        """

    async def refresh_tokens(self, refresh_token: str) -> dict:
        """
        Renueva tokens con refresh token.

        Args:
            refresh_token: Refresh token actual

        Returns:
            dict con nuevos access_token y refresh_token
        """

    async def get_user_profile(self, access_token: str) -> User:
        """
        Obtiene perfil del usuario.

        Args:
            access_token: JWT access token

        Returns:
            User entity con datos del usuario
        """

    # VPN Keys endpoints
    async def list_vpn_keys(self, access_token: str) -> List[VpnKey]:
        """
        Lista VPN keys del usuario.

        Args:
            access_token: JWT access token

        Returns:
            Lista de VpnKey entities
        """

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
        """

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
        """

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
        """

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
        """

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
        """

    # Referrals endpoints
    async def get_referral_code(self, access_token: str) -> str:
        """
        Obtiene código de referido.

        Args:
            access_token: JWT access token

        Returns:
            Código de referido
        """

    async def get_referral_stats(self, access_token: str) -> dict:
        """
        Obtiene estadísticas de referidos.

        Args:
            access_token: JWT access token

        Returns:
            dict con stats (referrals_count, bonus_earned_gb, etc.)
        """
