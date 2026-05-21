"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest

from .infrastructure.api.v1.routes.admin import router as admin_router
from .infrastructure.api.v1.routes.admin_agent_keys import router as admin_agent_keys_router
from .infrastructure.api.v1.routes.admin_vpn_keys import router as admin_vpn_keys_router
from .infrastructure.api.v1.routes.agent_registration import router as agent_registration_router
from .infrastructure.api.v1.routes.auth import router as auth_router
from .infrastructure.api.v1.routes.billing import router as billing_router
from .infrastructure.api.v1.routes.consumption_invoices import (
    router as consumption_invoices_router,
)
from .infrastructure.api.v1.routes.data_packages import router as data_packages_router
from .infrastructure.api.v1.routes.devices import router as devices_router
from .infrastructure.api.v1.routes.metrics import router as metrics_router
from .infrastructure.api.v1.routes.payments import router as payments_router
from .infrastructure.api.v1.routes.referrals import router as referrals_router
from .infrastructure.api.v1.routes.subscriptions import router as subscriptions_router
from .infrastructure.api.v1.routes.tickets import router as tickets_router
from .infrastructure.api.v1.routes.users import router as users_router
from .infrastructure.api.v1.routes.vpn import router as vpn_router
from .infrastructure.api.v1.routes.wallets import router as wallets_router
from .infrastructure.api.v1.webhooks.crypto import router as crypto_webhook_router
from .infrastructure.api.v1.webhooks.telegram_stars import router as telegram_stars_webhook_router
from .infrastructure.persistence.database import close_db, init_db
from .infrastructure.redis import RedisPool
from .shared.config import settings

logger = logging.getLogger(__name__)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación.

    Args:
        app: Instancia de FastAPI
    """
    # Startup
    init_db()
    logger.info("Database connection initialized")

    # Initialize Redis connection pool
    await RedisPool.get_instance()
    logger.info("Redis connection pool initialized")

    yield

    # Shutdown
    await RedisPool.close()
    logger.info("Redis connection pool closed")
    close_db()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="uSipipo Backend API",
    description="Backend API principal del ecosistema uSipipo",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

# Set up rate limiter
app.state.limiter = limiter
if settings.RATE_LIMIT_ENABLED:

    async def _rate_limit_handler(request: Request, exc: Exception) -> JSONResponse:
        """Wrap slowapi's handler for FastAPI compatibility."""
        return _rate_limit_exceeded_handler(request, exc)  # type: ignore[arg-type,return-value]

    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)


# Incluir routers de API v1
api_prefix = f"{settings.API_PREFIX}"
app.include_router(auth_router, prefix=api_prefix)
app.include_router(vpn_router, prefix=api_prefix)
app.include_router(payments_router, prefix=api_prefix)
app.include_router(billing_router, prefix=api_prefix)
app.include_router(subscriptions_router, prefix=api_prefix)
app.include_router(consumption_invoices_router, prefix=api_prefix)
app.include_router(data_packages_router, prefix=api_prefix)
app.include_router(devices_router, prefix=api_prefix)
app.include_router(referrals_router, prefix=api_prefix)
app.include_router(tickets_router, prefix=api_prefix)
app.include_router(wallets_router, prefix=api_prefix)
app.include_router(users_router, prefix=api_prefix)
app.include_router(admin_router, prefix=api_prefix)
app.include_router(metrics_router, prefix=api_prefix)  # Metrics ingestion
app.include_router(agent_registration_router, prefix=api_prefix)  # Agent registration
app.include_router(admin_agent_keys_router, prefix=api_prefix)  # Admin API keys
app.include_router(admin_vpn_keys_router, prefix=api_prefix)  # Admin VPN keys CRUD

# Incluir webhooks (sin prefijo de API)
app.include_router(crypto_webhook_router, prefix=api_prefix)
app.include_router(telegram_stars_webhook_router, prefix=api_prefix)


# TrustedHost middleware - solo permitir hosts configurados
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# CORS middleware - solo orígenes autorizados
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Añade headers de seguridad HTTP a todas las respuestas."""

    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


app.add_middleware(SecurityHeadersMiddleware)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to uSipipo Backend API",
        "docs": "/docs",
        "health": "/health",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler - logs error and returns safe response in production."""
    logger.exception(f"Unhandled exception on {request.method} {request.url}")

    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
                "type": type(exc).__name__,
            },
        )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
