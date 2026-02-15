"""Rate limiting middleware."""
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

from app.core.config import settings


def get_terminal_id(request: Request) -> str:
    """Extract terminal ID for rate limiting."""
    terminal_id = request.headers.get("x-terminal-id")
    if terminal_id:
        return terminal_id
    # Fallback to IP address if no terminal ID
    return get_remote_address(request)


# Create rate limiter instance
limiter = Limiter(
    key_func=get_terminal_id,
    default_limits=[] if not settings.rate_limit_enabled else None,
    enabled=settings.rate_limit_enabled,
)
