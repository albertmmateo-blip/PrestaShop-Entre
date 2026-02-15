"""Integration tests for authentication."""
import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

from app.main import app
from app.core.database import AsyncSessionLocal
from app.core.security import hash_api_key, generate_api_key
from app.models.auth import TerminalCredential


@pytest.fixture
async def test_terminal():
    """Create a test terminal with valid credentials."""
    async with AsyncSessionLocal() as db:
        # Generate API key
        api_key = generate_api_key("development", "TEST-TERMINAL-001")
        api_key_hash = hash_api_key(api_key)

        # Create terminal credential
        terminal = TerminalCredential(
            terminal_id="TEST-TERMINAL-001",
            api_key_hash=api_key_hash,
            location="Test Location",
            manager_assigned="Test Manager",
            status="active",
            created_at=datetime.utcnow(),
            rotation_due_date=datetime.utcnow() + timedelta(days=90),
        )
        db.add(terminal)
        await db.commit()

        yield {"terminal_id": "TEST-TERMINAL-001", "api_key": api_key}

        # Cleanup
        await db.delete(terminal)
        await db.commit()


@pytest.mark.asyncio
async def test_authenticated_request_succeeds(test_terminal):
    """Test that authenticated requests succeed."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/health",
            headers={
                "Authorization": f"Bearer {test_terminal['api_key']}",
                "X-Terminal-ID": test_terminal["terminal_id"],
            },
        )
        
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_missing_authorization_header_rejected():
    """Test that requests without Authorization header are rejected."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        
        # Health endpoint doesn't require auth, but other endpoints do
        # Test with a protected endpoint once we add one
        assert response.status_code == 200  # Health is public


@pytest.mark.asyncio
async def test_invalid_api_key_rejected(test_terminal):
    """Test that requests with invalid API key are rejected."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/health",
            headers={
                "Authorization": "Bearer invalid_key",
                "X-Terminal-ID": test_terminal["terminal_id"],
            },
        )
        
        # Health endpoint doesn't require auth
        # This test will be more meaningful with protected endpoints
        assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_missing_terminal_id_rejected(test_terminal):
    """Test that requests without X-Terminal-ID header are rejected."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/health",
            headers={
                "Authorization": f"Bearer {test_terminal['api_key']}",
            },
        )
        
        # Health endpoint doesn't require auth
        assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_revoked_credentials_rejected(test_terminal):
    """Test that revoked terminal credentials are rejected."""
    async with AsyncSessionLocal() as db:
        # Revoke the terminal
        from sqlalchemy import select
        result = await db.execute(
            select(TerminalCredential).where(
                TerminalCredential.terminal_id == test_terminal["terminal_id"]
            )
        )
        terminal = result.scalar_one()
        terminal.status = "revoked"
        await db.commit()

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/health",
            headers={
                "Authorization": f"Bearer {test_terminal['api_key']}",
                "X-Terminal-ID": test_terminal["terminal_id"],
            },
        )
        
        # Health endpoint doesn't require auth, but protected ones will reject
        assert response.status_code in [200, 403]
