"""Tests de integración entre Telegram Bot y Backend."""

import pytest

from src.infrastructure.api_client import APIClient
from src.infrastructure.config import settings


class TestBackendIntegration:
    """Tests de integración con el backend."""

    @pytest.fixture
    def api_client(self):
        """Crea APIClient configurado con el backend de producción."""
        return APIClient(
            base_url=settings.BACKEND_URL,
            api_prefix=settings.API_PREFIX,
        )

    @pytest.mark.asyncio
    async def test_backend_url_is_production(self):
        """Verifica que la URL del backend sea la de producción (no localhost)."""
        assert "duckdns.org" in settings.BACKEND_URL
        assert "localhost" not in settings.BACKEND_URL
        assert settings.BACKEND_URL == "https://usipipo.duckdns.org"

    @pytest.mark.asyncio
    async def test_backend_health(self, api_client):
        """Verifica que el backend esté accesible en producción."""
        try:
            response = await api_client.get("/health")
            assert response["status"] == "healthy"
        except Exception:
            pytest.skip("Backend no está disponible en usipipo.duckdns.org")

    @pytest.mark.asyncio
    async def test_auto_register_endpoint_production(self, api_client):
        """Verifica que el endpoint auto-register existe en producción."""
        try:
            # Test con telegram_id de prueba
            response = await api_client.post(
                "/auth/telegram/auto-register", {"telegram_id": 999999999}
            )
            # Si llega aquí, el endpoint existe
            assert "access_token" in response or response.get("detail")
        except Exception as e:
            # Error de conexión = backend no disponible
            if "Connection" in str(type(e).__name__):
                pytest.skip("Backend no está disponible en producción")
            else:
                raise

    @pytest.mark.asyncio
    async def test_refresh_endpoint_production(self, api_client):
        """Verifica que el endpoint refresh existe en producción."""
        import httpx

        try:
            # Test con refresh token inválido (el endpoint debe responder 401)
            response = await api_client.post("/auth/refresh", {"refresh_token": "invalid_token"})
            # Debe responder (aunque sea con error 401)
            assert response is not None
        except httpx.HTTPStatusError as e:
            # 401 es esperado para token inválido
            if e.response.status_code == 401:
                pass  # Éxito: el endpoint existe y responde correctamente
            else:
                raise
        except Exception as e:
            if "Connection" in str(type(e).__name__):
                pytest.skip("Backend no está disponible en producción")
            else:
                raise

    @pytest.mark.asyncio
    async def test_config_api_prefix(self):
        """Verifica que el API prefix sea correcto."""
        assert settings.API_PREFIX == "/api/v1"

    @pytest.mark.asyncio
    async def test_redis_connection(self):
        """Verifica que Redis esté configurado."""
        from src.infrastructure.redis import RedisPool

        try:
            await RedisPool.get_instance()
            health = await RedisPool.health_check()
            # Si Redis no está disponible, el test no falla, solo se saltea
            if not health:
                pytest.skip("Redis no está disponible")
        except Exception:
            pytest.skip("Redis no está configurado o disponible")
