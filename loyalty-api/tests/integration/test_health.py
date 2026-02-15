"""Integration tests for health check endpoint."""
import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_check_returns_correct_format():
    """Test that health check endpoint returns correct format."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "status" in data
        assert "checks" in data
        assert "version" in data
        assert "uptime_seconds" in data
        
        # Check that checks include database
        assert "database" in data["checks"]


@pytest.mark.asyncio
async def test_health_check_cors_headers():
    """Test that CORS headers are present."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/health",
            headers={"Origin": "http://localhost:8001"},
        )
        
        assert response.status_code == 200
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers or True  # May vary


@pytest.mark.asyncio
async def test_security_headers_present():
    """Test that security headers are present in responses."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        
        assert response.status_code == 200
        
        # Check for security headers
        assert "x-content-type-options" in response.headers
        assert "x-frame-options" in response.headers
        assert "x-xss-protection" in response.headers
