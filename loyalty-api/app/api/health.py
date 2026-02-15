"""Health check endpoint."""
import time
from datetime import datetime

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import check_db_health

router = APIRouter()

# Track application start time
start_time = time.time()


class HealthCheckResponse(BaseModel):
    """Health check response model."""

    status: str
    checks: dict
    version: str
    uptime_seconds: int


@router.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns system health status including:
    - Database connectivity
    - Application version
    - Uptime
    """
    # Check database
    db_healthy = await check_db_health()

    # Calculate uptime
    uptime = int(time.time() - start_time)

    # Determine overall status
    overall_status = "healthy" if db_healthy else "unhealthy"

    # Build response
    response = HealthCheckResponse(
        status=overall_status,
        checks={
            "database": "ok" if db_healthy else "error",
        },
        version=settings.app_version,
        uptime_seconds=uptime,
    )

    # Return appropriate status code
    status_code = status.HTTP_200_OK if db_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    return response
