"""Idempotency middleware."""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Request, HTTPException, status, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.logging import logger
from app.core.security import hash_request_body
from app.models.auth import IdempotencyKey


async def check_idempotency(
    request: Request,
    idempotency_key: str,
    request_body: dict,
) -> Optional[dict]:
    """
    Check idempotency key and return cached response if duplicate.
    
    Returns:
        - None if new request (should process)
        - dict with cached response if duplicate
        - Raises HTTPException if conflict detected
    """
    async with AsyncSessionLocal() as db:
        # Lookup existing key
        result = await db.execute(
            select(IdempotencyKey).where(
                IdempotencyKey.idempotency_key == idempotency_key
            )
        )
        existing = result.scalar_one_or_none()

        if not existing:
            # New request - should process
            logger.debug(f"New idempotency key: {idempotency_key}")
            return None

        # Check if expired
        if existing.expires_at < datetime.utcnow():
            # Key expired - treat as new request
            logger.debug(f"Idempotency key expired: {idempotency_key}")
            await db.delete(existing)
            await db.commit()
            return None

        # Calculate hash of current request
        current_hash = hash_request_body(request_body)

        # Compare hashes
        if current_hash == existing.request_hash:
            # Exact duplicate - return cached response
            logger.info(f"Idempotency key replay: {idempotency_key}")
            import json
            return {
                "status_code": existing.response_status,
                "body": json.loads(existing.response_body),
                "headers": {"X-Idempotency-Replay": "true"},
            }
        else:
            # Conflict - same key, different parameters
            logger.warning(f"Idempotency key conflict: {idempotency_key}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error_code": "IDEMPOTENCY_CONFLICT",
                    "error_message": "Same key with different request parameters",
                    "original_hash": existing.request_hash,
                    "current_hash": current_hash,
                },
            )


async def store_idempotency_key(
    idempotency_key: str,
    request_body: dict,
    endpoint: str,
    http_method: str,
    response_status: int,
    response_body: dict,
    terminal_id: Optional[str] = None,
    card_uid: Optional[str] = None,
) -> None:
    """Store idempotency key with response for future deduplication."""
    import json

    async with AsyncSessionLocal() as db:
        # Calculate request hash
        request_hash = hash_request_body(request_body)

        # Create idempotency record (expires in 48 hours)
        idempotency_record = IdempotencyKey(
            idempotency_key=idempotency_key,
            request_hash=request_hash,
            endpoint=endpoint,
            http_method=http_method,
            response_status=response_status,
            response_body=json.dumps(response_body),
            terminal_id=terminal_id,
            card_uid=card_uid,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=48),
            request_metadata=request_body,
        )

        db.add(idempotency_record)
        await db.commit()

        logger.debug(f"Stored idempotency key: {idempotency_key}")


def require_idempotency_key(request: Request) -> str:
    """Extract and validate idempotency key from request headers."""
    idempotency_key = request.headers.get("x-idempotency-key")

    if not idempotency_key:
        logger.warning("Missing idempotency key")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "MISSING_IDEMPOTENCY_KEY",
                "error_message": "X-Idempotency-Key header required for this endpoint",
            },
        )

    return idempotency_key
