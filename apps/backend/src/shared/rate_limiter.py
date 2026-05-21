"""Rate limiter configuration for the application."""

from datetime import UTC, datetime, timedelta

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


def get_user_id_or_ip(request: Request) -> str:
    """
    Extract user ID from JWT token or fall back to IP address.

    This function is used as the key_func for rate limiting.
    It prioritizes user identification via JWT token for per-user limits,
    and falls back to IP address for unauthenticated requests.

    Args:
        request: FastAPI request object

    Returns:
        str: User ID (UUID) if authenticated, otherwise IP address
    """
    # Try to get user_id from request state (set by authentication middleware)
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return str(user_id)

    # Fall back to IP address
    return get_remote_address(request)


async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom rate limit exceeded handler with detailed JSON response.

    Returns a structured error response with:
    - detail: Error message
    - retry_after: Seconds until rate limit resets
    - limit: The rate limit that was exceeded
    - reset_time: ISO 8601 timestamp when the limit resets

    Also sets the Retry-After HTTP header.

    Args:
        request: FastAPI request object
        exc: RateLimitExceeded exception

    Returns:
        JSONResponse: Structured error response
    """
    # Calculate retry_after from the exception header
    retry_after = int(exc.detail.split(" ")[-1]) if " " in exc.detail else 60

    # Calculate reset time
    reset_time = datetime.now(UTC).replace(microsecond=0)
    reset_time = reset_time + timedelta(seconds=retry_after)

    # Extract limit from exception message
    limit_str = str(exc.limit) if hasattr(exc, "limit") else "unknown"

    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded",
            "retry_after": retry_after,
            "limit": limit_str,
            "reset_time": reset_time.isoformat().replace("+00:00", "Z"),
        },
        headers={"Retry-After": str(retry_after)},
    )


# Rate limiter setup with custom key function
limiter = Limiter(key_func=get_user_id_or_ip)
