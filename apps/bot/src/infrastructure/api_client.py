"""
Cliente HTTP para comunicación con el backend API.

Author: uSipipo Team
Version: 1.0.0
"""

import os
from typing import Any, Optional

import httpx

from src.infrastructure.logger import get_logger

logger = get_logger("api_client")

DEFAULT_BACKEND_URL = "https://usipipo.duckdns.org"
DEFAULT_API_PREFIX = "/api/v1"


class APIClient:
    """Cliente HTTP para el backend API de uSipipo."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_prefix: Optional[str] = None,
    ):
        self.base_url = (base_url or os.getenv("BACKEND_URL") or DEFAULT_BACKEND_URL).rstrip("/")
        self.api_prefix = api_prefix or os.getenv("API_PREFIX") or DEFAULT_API_PREFIX
        self._client: Optional[httpx.AsyncClient] = None
        logger.info(f"APIClient initialized: {self.base_url}{self.api_prefix}")

    # Retry configuration for transient failures
    MAX_RETRIES = 2
    RETRY_DELAY = 0.5  # seconds

    async def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Execute HTTP request with retry on 401 and network errors.

        Uses exponential backoff: 0.5s, 1.0s between retries.
        """
        import asyncio

        last_response: httpx.Response | None = None

        for attempt in range(self.MAX_RETRIES + 1):
            try:
                client = await self._get_client()
                response = await client.request(method, endpoint, **kwargs)
                last_response = response

                # If 401 and we have retries left, wait and retry
                if response.status_code == 401 and attempt < self.MAX_RETRIES:
                    delay = self.RETRY_DELAY * (2**attempt)  # 0.5s, 1.0s
                    logger.warning(
                        f"401 on attempt {attempt + 1}, retrying in {delay}s: {method} {endpoint}"
                    )
                    await asyncio.sleep(delay)
                    continue

                return response
            except httpx.RequestError as e:
                if attempt < self.MAX_RETRIES:
                    delay = self.RETRY_DELAY * (2**attempt)
                    logger.warning(f"Request error, retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                    continue
                raise

        # All retries exhaust, return last response
        if last_response is None:
            raise RuntimeError("Request failed without response")
        return last_response

    async def _get_client(self) -> httpx.AsyncClient:
        """Retorna o crea el cliente HTTP async."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=f"{self.base_url}{self.api_prefix}",
                timeout=30.0,
                headers={"Content-Type": "application/json"},
            )
        return self._client

    async def get(
        self, endpoint: str, params: Optional[dict] = None, headers: Optional[dict] = None
    ) -> dict[str, Any]:
        """Realiza una petición GET al backend con retry logic."""
        response = await self._request_with_retry(
            "GET",
            endpoint,
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    async def post(
        self, endpoint: str, data: Optional[dict] = None, headers: Optional[dict] = None
    ) -> dict[str, Any]:
        """Realiza una petición POST al backend con retry logic."""
        response = await self._request_with_retry(
            "POST",
            endpoint,
            json=data,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    async def delete(self, endpoint: str, headers: Optional[dict] = None) -> dict[str, Any]:
        """
        Realiza una petición DELETE al backend con retry logic.

        Args:
            endpoint: Endpoint de la API (sin base_url)
            headers: Headers opcionales (ej: Authorization)

        Returns:
            dict: {"success": True} si la operación fue exitosa
        """
        response = await self._request_with_retry(
            "DELETE",
            endpoint,
            headers=headers,
        )
        response.raise_for_status()
        return {"success": True}

    async def put(
        self, endpoint: str, data: Optional[dict] = None, headers: Optional[dict] = None
    ) -> dict[str, Any]:
        """Realiza una petición PUT al backend con retry logic."""
        response = await self._request_with_retry(
            "PUT",
            endpoint,
            json=data,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        """Cierra el cliente HTTP."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            logger.info("APIClient closed")
