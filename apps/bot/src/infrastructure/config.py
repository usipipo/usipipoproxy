"""Configuración del bot usando pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Configuración del bot de Telegram uSipipo."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==================================================================
    # TELEGRAM BOT CONFIGURATION
    # ==================================================================
    TELEGRAM_TOKEN: str = ""
    ADMIN_ID: int = 0
    BOT_USERNAME: str = "usipipobot"

    # ==================================================================
    # BACKEND API CONFIGURATION
    # ==================================================================
    BACKEND_URL: str = "https://usipipo.duckdns.org"
    API_PREFIX: str = "/api/v1"

    # ==================================================================
    # REDIS CONFIGURATION
    # ==================================================================
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_MAX_CONNECTIONS: int = 10
    REDIS_SOCKET_TIMEOUT: float = 5.0
    REDIS_RETRY_ON_TIMEOUT: bool = True

    # ==================================================================
    # LOGGING
    # ==================================================================
    LOG_LEVEL: str = "INFO"

    # ==================================================================
    # TOKEN CONFIGURATION
    # ==================================================================
    TOKEN_REFRESH_THRESHOLD_SECONDS: int = 300  # 5 minutos antes de expirar

    # ==================================================================
    # CONSUMPTION BILLING (Pay-as-you-go)
    # ==================================================================
    CONSUMPTION_PRICE_PER_GB_USD: float = 0.25
    CONSUMPTION_PRICE_PER_MB_USD: float = 0.000244140625  # 0.25 / 1024

    # ==================================================================
    # PAYMENT CONVERSION RATE (from legacy bot)
    # ==================================================================
    STARS_PER_USDT: int = 120  # 1 USDT = 120 Telegram Stars

    # ==================================================================
    # HELPER PROPERTIES
    # ==================================================================
    @property
    def backend_base_url(self) -> str:
        """Obtiene la URL base completa del backend."""
        return f"{self.BACKEND_URL.rstrip('/')}{self.API_PREFIX}"


@lru_cache
def get_settings() -> BotSettings:
    """
    Obtiene la configuración del bot (cached).

    Returns:
        BotSettings: Configuración cargada
    """
    return BotSettings()


settings = get_settings()
