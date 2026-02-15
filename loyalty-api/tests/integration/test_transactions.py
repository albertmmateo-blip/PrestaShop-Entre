"""Integration tests for loyalty transaction endpoints."""
import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy import select

from app.main import app
from app.models.loyalty import Customer, LoyaltyAccount, LoyaltyLedger


@pytest.mark.asyncio
async def test_earn_points_transaction(db_session):
    """Test earning points from a purchase."""
    # Create test customer
    customer = Customer(
        customer_id=uuid4(),
        name="Test Customer",
        phone="+34612345678",
        email="test@example.com",
    )
    db_session.add(customer)
    await db_session.commit()
    
    # Create account
    account = LoyaltyAccount(
        customer_id=customer.customer_id,
        current_balance_points=0,
        current_balance_euros=Decimal("0.00"),
    )
    db_session.add(account)
    await db_session.commit()
    
    # Make earn request
    async with AsyncClient(app=app, base_url="http://test") as client:
        request_data = {
            "customer_id": str(customer.customer_id),
            "order_id": "TEST-ORDER-001",
            "order_source": "aniwin_pos",
            "terminal_id": "TEST-TERMINAL-001",
            "order_amount_euros": 100.00,
            "order_timestamp": datetime.utcnow().isoformat(),
        }
        
        response = await client.post(
            "/api/v1/transactions/earn",
            json=request_data,
            headers={"X-Idempotency-Key": "test-earn-001"}
        )
    
    # Verify response
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["transaction_type"] == "earn"
    assert data["data"]["amount_euros"] == 1.50  # 100 * 1.5%
    assert data["data"]["amount_points"] == 15000
    assert data["data"]["new_balance_points"] == 15000
    assert data["data"]["new_balance_euros"] == 1.50
    
    # Verify ledger entry
    result = await db_session.execute(
        select(LoyaltyLedger).where(LoyaltyLedger.customer_id == customer.customer_id)
    )
    ledger_entry = result.scalar_one()
    assert ledger_entry.transaction_type == "earn"
    assert ledger_entry.points_delta == 15000
    assert ledger_entry.balance_after == 15000
    
    # Verify account balance updated
    await db_session.refresh(account)
    assert account.current_balance_points == 15000
    assert account.current_balance_euros == Decimal("1.50")


@pytest.mark.asyncio
async def test_redeem_points_transaction(db_session):
    """Test redeeming points for discount."""
    # Create test customer with balance
    customer = Customer(
        customer_id=uuid4(),
        name="Test Customer",
        phone="+34612345678",
        email="test@example.com",
    )
    db_session.add(customer)
    await db_session.commit()
    
    # Create account with balance
    account = LoyaltyAccount(
        customer_id=customer.customer_id,
        current_balance_points=200000,  # 20 EUR
        current_balance_euros=Decimal("20.00"),
    )
    db_session.add(account)
    await db_session.commit()
    
    # Create initial earn ledger entry
    initial_entry = LoyaltyLedger(
        customer_id=customer.customer_id,
        account_id=account.account_id,
        transaction_type="earn",
        points_delta=200000,
        balance_after=200000,
        amount_euros=Decimal("20.00"),
        source_type="pos_sale",
        order_id="INITIAL-ORDER",
        description="Initial balance",
        idempotency_key="initial-earn",
        channel="pos",
        created_by="test",
    )
    db_session.add(initial_entry)
    await db_session.commit()
    
    # Make redeem request
    async with AsyncClient(app=app, base_url="http://test") as client:
        request_data = {
            "customer_id": str(customer.customer_id),
            "redemption_amount_euros": 10.00,
            "order_id": "TEST-ORDER-002",
            "order_source": "aniwin_pos",
            "terminal_id": "TEST-TERMINAL-001",
            "order_timestamp": datetime.utcnow().isoformat(),
        }
        
        response = await client.post(
            "/api/v1/transactions/redeem",
            json=request_data,
            headers={"X-Idempotency-Key": "test-redeem-001"}
        )
    
    # Verify response
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["transaction_type"] == "redeem"
    assert data["data"]["amount_euros"] == -10.00
    assert data["data"]["amount_points"] == -100000
    assert data["data"]["new_balance_points"] == 100000
    assert data["data"]["new_balance_euros"] == 10.00
    assert "voucher_code" in data["data"]


@pytest.mark.asyncio
async def test_redeem_insufficient_balance(db_session):
    """Test redeeming more points than available."""
    # Create test customer with low balance
    customer = Customer(
        customer_id=uuid4(),
        name="Test Customer",
        phone="+34612345678",
        email="test@example.com",
    )
    db_session.add(customer)
    await db_session.commit()
    
    # Create account with low balance
    account = LoyaltyAccount(
        customer_id=customer.customer_id,
        current_balance_points=50000,  # 5 EUR
        current_balance_euros=Decimal("5.00"),
    )
    db_session.add(account)
    await db_session.commit()
    
    # Create initial ledger entry
    initial_entry = LoyaltyLedger(
        customer_id=customer.customer_id,
        account_id=account.account_id,
        transaction_type="earn",
        points_delta=50000,
        balance_after=50000,
        amount_euros=Decimal("5.00"),
        source_type="pos_sale",
        order_id="INITIAL-ORDER",
        description="Initial balance",
        idempotency_key="initial-earn-3",
        channel="pos",
        created_by="test",
    )
    db_session.add(initial_entry)
    await db_session.commit()
    
    # Try to redeem more than available
    async with AsyncClient(app=app, base_url="http://test") as client:
        request_data = {
            "customer_id": str(customer.customer_id),
            "redemption_amount_euros": 10.00,  # More than 5 EUR available
            "order_id": "TEST-ORDER-003",
            "order_source": "aniwin_pos",
            "terminal_id": "TEST-TERMINAL-001",
            "order_timestamp": datetime.utcnow().isoformat(),
        }
        
        response = await client.post(
            "/api/v1/transactions/redeem",
            json=request_data,
            headers={"X-Idempotency-Key": "test-redeem-insufficient"}
        )
    
    # Verify error response
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["error_code"] == "INSUFFICIENT_BALANCE"


@pytest.mark.asyncio
async def test_reverse_transaction(db_session):
    """Test reversing a transaction for refund."""
    # Create test customer with transactions
    customer = Customer(
        customer_id=uuid4(),
        name="Test Customer",
        phone="+34612345678",
        email="test@example.com",
    )
    db_session.add(customer)
    await db_session.commit()
    
    # Create account
    account = LoyaltyAccount(
        customer_id=customer.customer_id,
        current_balance_points=150000,
        current_balance_euros=Decimal("15.00"),
    )
    db_session.add(account)
    await db_session.commit()
    
    # Create earn transaction to reverse
    order_id = "ORDER-TO-REFUND-001"
    earn_entry = LoyaltyLedger(
        customer_id=customer.customer_id,
        account_id=account.account_id,
        transaction_type="earn",
        points_delta=150000,
        balance_after=150000,
        amount_euros=Decimal("15.00"),
        source_type="pos_sale",
        order_id=order_id,
        description="Earn to be reversed",
        idempotency_key="earn-to-reverse",
        channel="pos",
        created_by="test",
    )
    db_session.add(earn_entry)
    await db_session.commit()
    
    # Reverse the transaction
    async with AsyncClient(app=app, base_url="http://test") as client:
        request_data = {
            "original_order_id": order_id,
            "refund_timestamp": datetime.utcnow().isoformat(),
            "reason": "Customer return",
            "terminal_id": "TEST-TERMINAL-001",
        }
        
        response = await client.post(
            "/api/v1/transactions/reverse",
            json=request_data,
            headers={"X-Idempotency-Key": "test-reverse-001"}
        )
    
    # Verify response
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]["reversal_transactions"]) == 1
    reversal = data["data"]["reversal_transactions"][0]
    assert reversal["transaction_type"] == "refund"
    assert reversal["amount_points"] == -150000
    assert data["data"]["new_balance_points"] == 0


@pytest.mark.asyncio
async def test_get_balance(db_session):
    """Test getting customer balance."""
    # Create test customer with transactions
    customer = Customer(
        customer_id=uuid4(),
        name="Test Customer",
        phone="+34612345678",
        email="test@example.com",
    )
    db_session.add(customer)
    await db_session.commit()
    
    # Create account
    account = LoyaltyAccount(
        customer_id=customer.customer_id,
        current_balance_points=250000,
        current_balance_euros=Decimal("25.00"),
    )
    db_session.add(account)
    await db_session.commit()
    
    # Create transactions
    earn_entry1 = LoyaltyLedger(
        customer_id=customer.customer_id,
        account_id=account.account_id,
        transaction_type="earn",
        points_delta=150000,
        balance_after=150000,
        amount_euros=Decimal("15.00"),
        source_type="pos_sale",
        order_id="ORDER-001",
        description="First earn",
        idempotency_key="balance-test-1",
        channel="pos",
        created_by="test",
    )
    db_session.add(earn_entry1)
    
    earn_entry2 = LoyaltyLedger(
        customer_id=customer.customer_id,
        account_id=account.account_id,
        transaction_type="earn",
        points_delta=100000,
        balance_after=250000,
        amount_euros=Decimal("10.00"),
        source_type="pos_sale",
        order_id="ORDER-002",
        description="Second earn",
        idempotency_key="balance-test-2",
        channel="pos",
        created_by="test",
    )
    db_session.add(earn_entry2)
    await db_session.commit()
    
    # Get balance
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/customers/{customer.customer_id}/balance"
        )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["balance_points"] == 250000
    assert data["data"]["balance_euros"] == 25.00
    assert data["data"]["transactions_count"] == 2


@pytest.mark.asyncio
async def test_idempotency_duplicate_request(db_session):
    """Test idempotency - duplicate request returns same result."""
    # Create test customer
    customer = Customer(
        customer_id=uuid4(),
        name="Test Customer",
        phone="+34612345678",
        email="test@example.com",
    )
    db_session.add(customer)
    await db_session.commit()
    
    # Create account
    account = LoyaltyAccount(
        customer_id=customer.customer_id,
        current_balance_points=0,
        current_balance_euros=Decimal("0.00"),
    )
    db_session.add(account)
    await db_session.commit()
    
    idempotency_key = f"idempotency-test-{uuid4()}"
    request_data = {
        "customer_id": str(customer.customer_id),
        "order_id": "IDEMPOTENCY-TEST-001",
        "order_source": "aniwin_pos",
        "terminal_id": "TEST-TERMINAL-001",
        "order_amount_euros": 100.00,
        "order_timestamp": datetime.utcnow().isoformat(),
    }
    
    # First request
    async with AsyncClient(app=app, base_url="http://test") as client:
        response1 = await client.post(
            "/api/v1/transactions/earn",
            json=request_data,
            headers={"X-Idempotency-Key": idempotency_key}
        )
    
    assert response1.status_code == 201
    data1 = response1.json()
    transaction_id_1 = data1["data"]["transaction_id"]
    
    # Duplicate request (same idempotency key)
    async with AsyncClient(app=app, base_url="http://test") as client:
        response2 = await client.post(
            "/api/v1/transactions/earn",
            json=request_data,
            headers={"X-Idempotency-Key": idempotency_key}
        )
    
    # Should return cached response
    assert response2.status_code == 200  # Note: cached responses return 200
    assert response2.headers.get("X-Idempotency-Replay") == "true"
    data2 = response2.json()
    transaction_id_2 = data2["data"]["transaction_id"]
    
    # Same transaction ID
    assert transaction_id_1 == transaction_id_2
    
    # Verify only one ledger entry was created
    result = await db_session.execute(
        select(LoyaltyLedger).where(LoyaltyLedger.order_id == "IDEMPOTENCY-TEST-001")
    )
    entries = list(result.scalars().all())
    assert len(entries) == 1


@pytest.mark.asyncio
async def test_customer_not_found(db_session):
    """Test error when customer doesn't exist."""
    non_existent_customer_id = uuid4()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        request_data = {
            "customer_id": str(non_existent_customer_id),
            "order_id": "TEST-ORDER-999",
            "order_source": "aniwin_pos",
            "terminal_id": "TEST-TERMINAL-001",
            "order_amount_euros": 100.00,
            "order_timestamp": datetime.utcnow().isoformat(),
        }
        
        response = await client.post(
            "/api/v1/transactions/earn",
            json=request_data,
            headers={"X-Idempotency-Key": "test-not-found"}
        )
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["error_code"] == "CUSTOMER_NOT_FOUND"


@pytest.mark.asyncio
async def test_missing_idempotency_key(db_session):
    """Test error when idempotency key is missing."""
    customer = Customer(
        customer_id=uuid4(),
        name="Test Customer",
    )
    db_session.add(customer)
    await db_session.commit()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        request_data = {
            "customer_id": str(customer.customer_id),
            "order_id": "TEST-ORDER-888",
            "order_source": "aniwin_pos",
            "order_amount_euros": 100.00,
            "order_timestamp": datetime.utcnow().isoformat(),
        }
        
        # No idempotency key header
        response = await client.post(
            "/api/v1/transactions/earn",
            json=request_data,
        )
    
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["error_code"] == "MISSING_IDEMPOTENCY_KEY"
