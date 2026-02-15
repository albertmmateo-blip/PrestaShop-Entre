"""Integration tests for card management endpoints."""
import pytest
from datetime import datetime
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy import select

from app.main import app
from app.models.loyalty import Customer, LoyaltyCard, LoyaltyAccount


@pytest.mark.asyncio
async def test_register_card_successfully(db_session):
    """Test registering a new card."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        request_data = {
            "card_uid": "04A1B2C3D4E5F6",
            "card_number": "LC-00000001",
        }
        
        response = await client.post(
            "/api/v1/cards",
            json=request_data,
            headers={"X-Idempotency-Key": "test-card-register-001"}
        )
    
    # Verify response
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["card_uid"] == "04A1B2C3D4E5F6"
    assert data["data"]["card_number"] == "LC-00000001"
    assert data["data"]["status"] == "inactive"
    assert data["data"]["customer"] is None
    
    # Verify card in database
    card_id = data["data"]["card_id"]
    result = await db_session.execute(
        select(LoyaltyCard).where(LoyaltyCard.card_id == card_id)
    )
    card = result.scalar_one()
    assert card.card_uid == "04A1B2C3D4E5F6"
    assert card.status == "inactive"
    assert card.customer_id is None


@pytest.mark.asyncio
async def test_register_card_duplicate_uid(db_session):
    """Test registering a card with a UID that already exists."""
    # Create existing card
    card = LoyaltyCard(
        card_uid="04A1B2C3D4E5F6",
        card_number="LC-00000001",
        status="inactive",
    )
    db_session.add(card)
    await db_session.commit()
    
    # Try to register another card with same UID
    async with AsyncClient(app=app, base_url="http://test") as client:
        request_data = {
            "card_uid": "04A1B2C3D4E5F6",
            "card_number": "LC-00000002",
        }
        
        response = await client.post(
            "/api/v1/cards",
            json=request_data,
            headers={"X-Idempotency-Key": "test-card-duplicate-uid"}
        )
    
    # Verify conflict error
    assert response.status_code == 409
    data = response.json()
    assert "error_code" in data["detail"]
    assert data["detail"]["error_code"] == "CARD_UID_EXISTS"


@pytest.mark.asyncio
async def test_register_card_invalid_uid(db_session):
    """Test registering a card with invalid UID format."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        request_data = {
            "card_uid": "invalid",  # Too short
            "card_number": "LC-00000001",
        }
        
        response = await client.post(
            "/api/v1/cards",
            json=request_data,
            headers={"X-Idempotency-Key": "test-card-invalid-uid"}
        )
    
    # Verify validation error
    assert response.status_code == 422
    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_assign_card_to_customer(db_session):
    """Test assigning a card to a customer."""
    # Create customer
    customer = Customer(
        customer_id=uuid4(),
        name="Test Customer",
        email="test@example.com",
    )
    db_session.add(customer)
    
    # Create card
    card = LoyaltyCard(
        card_uid="04A1B2C3D4E5F6",
        card_number="LC-00000001",
        status="inactive",
    )
    db_session.add(card)
    await db_session.commit()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        request_data = {
            "customer_id": str(customer.customer_id),
        }
        
        response = await client.post(
            f"/api/v1/cards/{card.card_uid}/assign",
            json=request_data,
            headers={"X-Idempotency-Key": "test-card-assign-001"}
        )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["card_uid"] == "04A1B2C3D4E5F6"
    assert data["data"]["status"] == "active"
    assert data["data"]["customer"]["customer_id"] == str(customer.customer_id)
    assert data["data"]["customer"]["name"] == "Test Customer"
    assert data["data"]["assigned_date"] is not None
    
    # Verify card in database
    await db_session.refresh(card)
    assert card.customer_id == customer.customer_id
    assert card.status == "active"
    assert card.assigned_date is not None


@pytest.mark.asyncio
async def test_assign_card_already_assigned(db_session):
    """Test assigning a card that is already assigned to another customer."""
    # Create two customers
    customer1 = Customer(
        customer_id=uuid4(),
        name="Customer 1",
        email="customer1@example.com",
    )
    customer2 = Customer(
        customer_id=uuid4(),
        name="Customer 2",
        email="customer2@example.com",
    )
    db_session.add_all([customer1, customer2])
    
    # Create card assigned to customer1
    card = LoyaltyCard(
        card_uid="04A1B2C3D4E5F6",
        card_number="LC-00000001",
        customer_id=customer1.customer_id,
        status="active",
        assigned_date=datetime.utcnow(),
    )
    db_session.add(card)
    await db_session.commit()
    
    # Try to assign to customer2
    async with AsyncClient(app=app, base_url="http://test") as client:
        request_data = {
            "customer_id": str(customer2.customer_id),
        }
        
        response = await client.post(
            f"/api/v1/cards/{card.card_uid}/assign",
            json=request_data,
            headers={"X-Idempotency-Key": "test-card-reassign"}
        )
    
    # Verify conflict error
    assert response.status_code == 409
    data = response.json()
    assert "error_code" in data["detail"]
    assert data["detail"]["error_code"] == "CARD_ALREADY_ASSIGNED"


@pytest.mark.asyncio
async def test_assign_card_not_found(db_session):
    """Test assigning a card that doesn't exist."""
    # Create customer
    customer = Customer(
        customer_id=uuid4(),
        name="Test Customer",
        email="test@example.com",
    )
    db_session.add(customer)
    await db_session.commit()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        request_data = {
            "customer_id": str(customer.customer_id),
        }
        
        response = await client.post(
            "/api/v1/cards/04A1B2C3D4E5F6/assign",
            json=request_data,
            headers={"X-Idempotency-Key": "test-card-assign-not-found"}
        )
    
    # Verify not found error
    assert response.status_code == 404
    data = response.json()
    assert "error_code" in data["detail"]
    assert data["detail"]["error_code"] == "CARD_NOT_FOUND"


@pytest.mark.asyncio
async def test_assign_card_customer_not_found(db_session):
    """Test assigning a card to a customer that doesn't exist."""
    # Create card
    card = LoyaltyCard(
        card_uid="04A1B2C3D4E5F6",
        card_number="LC-00000001",
        status="inactive",
    )
    db_session.add(card)
    await db_session.commit()
    
    fake_customer_id = uuid4()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        request_data = {
            "customer_id": str(fake_customer_id),
        }
        
        response = await client.post(
            f"/api/v1/cards/{card.card_uid}/assign",
            json=request_data,
            headers={"X-Idempotency-Key": "test-card-assign-customer-not-found"}
        )
    
    # Verify not found error
    assert response.status_code == 404
    data = response.json()
    assert "error_code" in data["detail"]
    assert data["detail"]["error_code"] == "CUSTOMER_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_card_customer(db_session):
    """Test looking up customer by card UID."""
    # Create customer
    customer = Customer(
        customer_id=uuid4(),
        name="Test Customer",
        email="test@example.com",
        phone="+34612345678",
    )
    db_session.add(customer)
    
    # Create card assigned to customer
    card = LoyaltyCard(
        card_uid="04A1B2C3D4E5F6",
        card_number="LC-00000001",
        customer_id=customer.customer_id,
        status="active",
        assigned_date=datetime.utcnow(),
    )
    db_session.add(card)
    await db_session.commit()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/api/v1/cards/{card.card_uid}/customer")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["card_uid"] == "04A1B2C3D4E5F6"
    assert data["data"]["status"] == "active"
    assert data["data"]["customer"]["customer_id"] == str(customer.customer_id)
    assert data["data"]["customer"]["name"] == "Test Customer"
    assert data["data"]["customer"]["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_card_customer_card_not_found(db_session):
    """Test looking up customer for a card that doesn't exist."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/cards/04A1B2C3D4E5F6/customer")
    
    # Verify not found error
    assert response.status_code == 404
    data = response.json()
    assert "error_code" in data["detail"]
    assert data["detail"]["error_code"] == "CARD_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_card_customer_card_inactive(db_session):
    """Test looking up customer for an inactive card."""
    # Create customer
    customer = Customer(
        customer_id=uuid4(),
        name="Test Customer",
        email="test@example.com",
    )
    db_session.add(customer)
    
    # Create inactive card
    card = LoyaltyCard(
        card_uid="04A1B2C3D4E5F6",
        card_number="LC-00000001",
        customer_id=customer.customer_id,
        status="lost",  # Inactive status
        assigned_date=datetime.utcnow(),
    )
    db_session.add(card)
    await db_session.commit()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/api/v1/cards/{card.card_uid}/customer")
    
    # Verify forbidden error
    assert response.status_code == 403
    data = response.json()
    assert "error_code" in data["detail"]
    assert data["detail"]["error_code"] == "CARD_INACTIVE"


@pytest.mark.asyncio
async def test_get_card_customer_card_not_assigned(db_session):
    """Test looking up customer for a card that is not assigned."""
    # Create unassigned card
    card = LoyaltyCard(
        card_uid="04A1B2C3D4E5F6",
        card_number="LC-00000001",
        status="active",  # Active but not assigned
    )
    db_session.add(card)
    await db_session.commit()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/api/v1/cards/{card.card_uid}/customer")
    
    # Verify not found error
    assert response.status_code == 404
    data = response.json()
    assert "error_code" in data["detail"]
    assert data["detail"]["error_code"] == "CARD_NOT_ASSIGNED"


@pytest.mark.asyncio
async def test_card_uid_case_insensitive(db_session):
    """Test that card UID lookups are case-insensitive."""
    # Create customer
    customer = Customer(
        customer_id=uuid4(),
        name="Test Customer",
        email="test@example.com",
    )
    db_session.add(customer)
    
    # Create card with uppercase UID
    card = LoyaltyCard(
        card_uid="04A1B2C3D4E5F6",
        card_number="LC-00000001",
        customer_id=customer.customer_id,
        status="active",
        assigned_date=datetime.utcnow(),
    )
    db_session.add(card)
    await db_session.commit()
    
    # Lookup with lowercase UID
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/cards/04a1b2c3d4e5f6/customer")
    
    # Verify response (should find the card)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["card_uid"] == "04A1B2C3D4E5F6"
