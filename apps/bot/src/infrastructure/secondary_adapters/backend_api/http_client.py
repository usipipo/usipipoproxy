"""HTTP Client for Backend API."""

import httpx
from typing import Optional


class BackendHttpClient:
    """
    Cliente HTTP para comunicar con el backend.

    Wrapper alrededor de httpx.AsyncClient con configuración
    específica para el backend de uSipipo.
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
    ):
        """
        Inicializa el cliente HTTP.

        Args:
            base_url: URL base del backend
            timeout: Timeout en segundos
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        """
        Obtiene o crea el cliente HTTP.

        Returns:
            httpx.AsyncClient configurado
        """
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
        return self._client

    async def close(self) -> None:
        """Cierra el cliente HTTP."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "BackendHttpClient":
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        await self.close()
