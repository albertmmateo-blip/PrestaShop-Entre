"""Integration tests for idempotency."""
import pytest
from httpx import AsyncClient
from datetime import datetime

from app.main import app
from app.middleware.idempotency import store_idempotency_key, check_idempotency


@pytest.mark.asyncio
async def test_idempotency_prevents_duplicates():
    """Test that idempotency keys prevent duplicate processing."""
    idempotency_key = "test_earn_04A1B2C3_1234567890_TEST-TERM-001"
    request_body = {
        "card_uid": "04A1B2C3",
        "order_amount": 50.00,
        "order_id": "TEST-ORDER-001",
    }

    # Store initial response
    await store_idempotency_key(
        idempotency_key=idempotency_key,
        request_body=request_body,
        endpoint="/transactions/earn",
        http_method="POST",
        response_status=201,
        response_body={"transaction_id": "txn_123", "success": True},
        terminal_id="TEST-TERM-001",
        card_uid="04A1B2C3",
    )

    # Create mock request
    from fastapi import Request
    from unittest.mock import MagicMock
    
    mock_request = MagicMock(spec=Request)
    mock_request.headers.get.return_value = idempotency_key

    # Check idempotency (should return cached response)
    result = await check_idempotency(
        request=mock_request,
        idempotency_key=idempotency_key,
        request_body=request_body,
    )

    assert result is not None
    assert result["status_code"] == 201
    assert result["body"]["transaction_id"] == "txn_123"
    assert "X-Idempotency-Replay" in result["headers"]


@pytest.mark.asyncio
async def test_idempotency_detects_conflicts():
    """Test that idempotency detects conflicts (same key, different params)."""
    idempotency_key = "test_earn_04A1B2C3_1234567891_TEST-TERM-001"
    original_body = {
        "card_uid": "04A1B2C3",
        "order_amount": 50.00,
        "order_id": "TEST-ORDER-002",
    }

    # Store original request
    await store_idempotency_key(
        idempotency_key=idempotency_key,
        request_body=original_body,
        endpoint="/transactions/earn",
        http_method="POST",
        response_status=201,
        response_body={"transaction_id": "txn_124", "success": True},
        terminal_id="TEST-TERM-001",
        card_uid="04A1B2C3",
    )

    # Try with different parameters
    different_body = {
        "card_uid": "04A1B2C3",
        "order_amount": 75.00,  # Different amount
        "order_id": "TEST-ORDER-002",
    }

    from fastapi import Request, HTTPException
    from unittest.mock import MagicMock
    
    mock_request = MagicMock(spec=Request)
    mock_request.headers.get.return_value = idempotency_key

    # Should raise conflict exception
    with pytest.raises(HTTPException) as exc_info:
        await check_idempotency(
            request=mock_request,
            idempotency_key=idempotency_key,
            request_body=different_body,
        )

    assert exc_info.value.status_code == 409
    assert "IDEMPOTENCY_CONFLICT" in str(exc_info.value.detail)
