"""Authentication middleware."""
from datetime import datetime
from typing import Optional

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.logging import logger
from app.core.security import verify_api_key
from app.models.auth import TerminalCredential

security = HTTPBearer()


async def get_current_terminal(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = None
) -> dict:
    """Authenticate terminal using API key."""
    # Extract API key from Authorization header
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("Missing or invalid Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "UNAUTHORIZED",
                "error_message": "Missing or invalid Authorization header",
            },
        )

    api_key = auth_header.replace("Bearer ", "")

    # Extract terminal ID from header
    terminal_id = request.headers.get("x-terminal-id")
    if not terminal_id:
        logger.warning("Missing X-Terminal-ID header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "MISSING_TERMINAL_ID",
                "error_message": "X-Terminal-ID header required",
            },
        )

    # Validate API key format
    if not api_key.startswith("loyalty_"):
        logger.warning(f"Invalid API key format for terminal {terminal_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "INVALID_CREDENTIALS",
                "error_message": "Invalid API key format",
            },
        )

    # Parse API key components
    parts = api_key.split("_")
    if len(parts) != 4:
        logger.warning(f"Invalid API key structure for terminal {terminal_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "INVALID_CREDENTIALS",
                "error_message": "Invalid API key structure",
            },
        )

    _, environment, key_terminal_id, _ = parts

    # Verify terminal ID matches
    if key_terminal_id != terminal_id:
        logger.warning(
            f"Terminal ID mismatch: key={key_terminal_id}, header={terminal_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "TERMINAL_ID_MISMATCH",
                "error_message": "Terminal ID in key does not match header",
            },
        )

    # Lookup terminal credentials in database
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(TerminalCredential).where(
                TerminalCredential.terminal_id == terminal_id
            )
        )
        credential = result.scalar_one_or_none()

        if not credential:
            logger.warning(f"Terminal not found: {terminal_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error_code": "TERMINAL_NOT_FOUND",
                    "error_message": "Terminal not registered",
                },
            )

        # Check status
        if credential.status != "active":
            logger.warning(f"Terminal {terminal_id} status: {credential.status}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error_code": "CREDENTIALS_REVOKED",
                    "error_message": f"Terminal status: {credential.status}",
                },
            )

        # Verify API key hash
        if not verify_api_key(api_key, credential.api_key_hash):
            logger.warning(f"Invalid API key for terminal {terminal_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error_code": "INVALID_CREDENTIALS",
                    "error_message": "Invalid API key",
                },
            )

        # Check IP whitelist if configured
        if credential.ip_whitelist:
            client_ip = request.client.host if request.client else None
            if client_ip not in credential.ip_whitelist:
                logger.warning(
                    f"IP {client_ip} not whitelisted for terminal {terminal_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error_code": "IP_NOT_WHITELISTED",
                        "error_message": f"IP {client_ip} not authorized",
                    },
                )

        # Update last used timestamp
        credential.last_used_at = datetime.utcnow()
        await db.commit()

        logger.info(f"Terminal {terminal_id} authenticated successfully")

        return {
            "terminal_id": terminal_id,
            "location": credential.location,
            "manager": credential.manager_assigned,
        }
