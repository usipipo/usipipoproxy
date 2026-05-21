"""HTTP client for communicating with remote VPN agents."""

import httpx
from loguru import logger


class VpnAgentClientError(Exception):
    """Base exception for VPN agent client errors."""


class VpnAgentClient:
    """HTTP client to communicate with remote VPN agents.

    This client handles communication with VPN agents running on remote VPS servers.
    It supports creating/deleting WireGuard peers.
    """

    # Timeout limits (seconds)
    MIN_TIMEOUT = 1.0
    MAX_TIMEOUT = 60.0
    DEFAULT_TIMEOUT = 10.0
    DEFAULT_RETRIES = 3

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = DEFAULT_TIMEOUT,
        retry_count: int = DEFAULT_RETRIES,
    ):
        """Initialize VPN agent client.

        Args:
            base_url: Base URL of the VPN agent (e.g., https://usipipousa.duckdns.org)
            api_key: API key for authentication
            timeout: Request timeout in seconds (clamped to 1-60s)
            retry_count: Number of retries for failed requests
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

        # Clamp timeout to safe range
        self.timeout = max(self.MIN_TIMEOUT, min(timeout, self.MAX_TIMEOUT))
        self.retry_count = retry_count

        self.client = httpx.AsyncClient(
            headers={"X-API-Key": api_key},
            follow_redirects=True,
            timeout=httpx.Timeout(
                self.timeout, connect=5.0, read=self.timeout, write=self.timeout, pool=self.timeout
            ),
            transport=httpx.AsyncHTTPTransport(
                retries=retry_count,
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=10),
            ),
        )

        logger.info(f"VpnAgentClient initialized for {base_url} (timeout: {self.timeout}s)")

    async def create_wireguard_peer(self, name: str) -> dict:
        """Create a new WireGuard peer on remote server.

        Args:
            name: Name for the peer

        Returns:
            dict with public_key, name, ip_address, config

        Raises:
            VpnAgentClientError: If request fails
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/wireguard/peers",
                json={"name": name},
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to create WireGuard peer: {e}")
            raise VpnAgentClientError(f"Failed to create WireGuard peer: {e}") from e

    async def delete_wireguard_peer(self, name: str) -> bool:
        """Delete a WireGuard peer from remote server.

        Args:
            name: Name of the peer to delete

        Returns:
            True if deleted successfully

        Raises:
            VpnAgentClientError: If request fails
        """
        try:
            response = await self.client.delete(
                f"{self.base_url}/wireguard/peers/{name}",
            )
            return response.status_code == 204
        except httpx.HTTPError as e:
            logger.error(f"Failed to delete WireGuard peer: {e}")
            raise VpnAgentClientError(f"Failed to delete WireGuard peer: {e}") from e

    async def get_wireguard_peer_usage(self, name: str) -> int:
        """Get usage statistics for a WireGuard peer.

        Args:
            name: Name of the peer

        Returns:
            Total bytes transferred (rx + tx)

        Raises:
            VpnAgentClientError: If request fails
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/wireguard/peers/{name}/usage",
            )
            response.raise_for_status()
            data = response.json()
            return data.get("bytes_used", 0)
        except httpx.HTTPError as e:
            logger.error(f"Failed to get WireGuard peer usage: {e}")
            raise VpnAgentClientError(f"Failed to get WireGuard peer usage: {e}") from e

    async def get_status(self) -> dict:
        """Get server status from remote agent.

        Returns:
            dict with status, version

        Raises:
            VpnAgentClientError: If request fails
        """
        try:
            response = await self.client.get(f"{self.base_url}/status")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get server status: {e}")
            raise VpnAgentClientError(f"Failed to get server status: {e}") from e

    async def get_metrics(self) -> dict:
        """Get detailed metrics from remote agent.

        Returns:
            dict with system, vpn, and latency metrics

        Raises:
            VpnAgentClientError: If request fails
        """
        try:
            response = await self.client.get(f"{self.base_url}/metrics")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get metrics: {e}")
            raise VpnAgentClientError(f"Failed to get metrics: {e}") from e

    async def health_check(self) -> bool:
        """Perform health check on remote agent.

        Returns:
            True if agent is healthy

        Raises:
            VpnAgentClientError: If health check fails
        """
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            data = response.json()
            return data.get("status") == "healthy"
        except httpx.HTTPError as e:
            logger.error(f"Health check failed: {e}")
            raise VpnAgentClientError(f"Health check failed: {e}") from e

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info("VpnAgentClient closed")

    async def __aenter__(self) -> "VpnAgentClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
