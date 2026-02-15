"""Integration tests for customer management endpoints."""
import pytest
from datetime import datetime
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy import select

from app.main import app
from app.models.loyalty import Customer, LoyaltyCard, LoyaltyAccount, ConsentRecord


@pytest.mark.asyncio
async def test_create_customer_with_valid_data(db_session):
    """Test creating a customer with valid data."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        request_data = {
            "name": "María García",
            "email": "maria.garcia@example.com",
            "phone": "+34612345678",
            "consent_loyalty": True,
            "consent_marketing": True,
            "language": "es",
        }
        
        response = await client.post(
            "/api/v1/customers",
            json=request_data,
            headers={"X-Idempotency-Key": "test-customer-create-001"}
        )
    
    # Verify response
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["name"] == "María García"
    assert data["data"]["email"] == "maria.garcia@example.com"
    assert data["data"]["phone"] == "+34612345678"
    assert data["data"]["consent_loyalty"] is True
    assert data["data"]["consent_marketing"] is True
    assert data["data"]["balance_euros"] == 0.00
    assert data["data"]["balance_points"] == 0
    
    # Verify customer in database
    customer_id = data["data"]["customer_id"]
    result = await db_session.execute(
        select(Customer).where(Customer.customer_id == customer_id)
    )
    customer = result.scalar_one()
    assert customer.name == "María García"
    assert customer.email == "maria.garcia@example.com"
    
    # Verify loyalty account created
    result = await db_session.execute(
        select(LoyaltyAccount).where(LoyaltyAccount.customer_id == customer_id)
    )
    account = result.scalar_one()
    assert account.current_balance_points == 0
    
    # Verify consent records created
    result = await db_session.execute(
        select(ConsentRecord).where(ConsentRecord.customer_id == customer_id)
    )
    consent_records = result.scalars().all()
    assert len(consent_records) == 2  # loyalty_program and marketing_email
    consent_types = [c.consent_type for c in consent_records]
    assert "loyalty_program" in consent_types
    assert "marketing_email" in consent_types


@pytest.mark.asyncio
async def test_create_customer_invalid_email(db_session):
    """Test creating a customer with invalid email format."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        request_data = {
            "name": "Test User",
            "email": "not-an-email",
            "consent_loyalty": True,
        }
        
        response = await client.post(
            "/api/v1/customers",
            json=request_data,
            headers={"X-Idempotency-Key": "test-customer-invalid-email"}
        )
    
    # Verify validation error
    assert response.status_code == 422
    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_create_customer_invalid_phone(db_session):
    """Test creating a customer with invalid phone format."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        request_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "invalid-phone",
            "consent_loyalty": True,
        }
        
        response = await client.post(
            "/api/v1/customers",
            json=request_data,
            headers={"X-Idempotency-Key": "test-customer-invalid-phone"}
        )
    
    # Verify validation error
    assert response.status_code == 422
    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_create_customer_duplicate_email(db_session):
    """Test creating a customer with an email that already exists."""
    # Create first customer
    customer = Customer(
        customer_id=uuid4(),
        name="Existing Customer",
        email="existing@example.com",
    )
    db_session.add(customer)
    await db_session.commit()
    
    # Try to create second customer with same email
    async with AsyncClient(app=app, base_url="http://test") as client:
        request_data = {
            "name": "New Customer",
            "email": "existing@example.com",
            "consent_loyalty": True,
        }
        
        response = await client.post(
            "/api/v1/customers",
            json=request_data,
            headers={"X-Idempotency-Key": "test-customer-duplicate-email"}
        )
    
    # Verify conflict error
    assert response.status_code == 409
    data = response.json()
    assert "error_code" in data["detail"]
    assert data["detail"]["error_code"] == "EMAIL_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_create_customer_without_consent(db_session):
    """Test creating a customer without loyalty consent."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        request_data = {
            "name": "Test User",
            "email": "test@example.com",
            "consent_loyalty": False,
        }
        
        response = await client.post(
            "/api/v1/customers",
            json=request_data,
            headers={"X-Idempotency-Key": "test-customer-no-consent"}
        )
    
    # Verify error - consent is required
    assert response.status_code == 400
    data = response.json()
    assert "error_code" in data["detail"]
    assert data["detail"]["error_code"] == "CONSENT_REQUIRED"


@pytest.mark.asyncio
async def test_create_customer_with_card(db_session):
    """Test creating a customer and assigning a card in one request."""
    # Create a card first
    card = LoyaltyCard(
        card_id=uuid4(),
        card_uid="04A1B2C3D4E5F6",
        card_number="LC-00000001",
        status="inactive",
    )
    db_session.add(card)
    await db_session.commit()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        request_data = {
            "name": "Card User",
            "email": "carduser@example.com",
            "phone": "+34612345678",
            "consent_loyalty": True,
            "card_uid": "04A1B2C3D4E5F6",
        }
        
        response = await client.post(
            "/api/v1/customers",
            json=request_data,
            headers={"X-Idempotency-Key": "test-customer-with-card"}
        )
    
    # Verify response
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["card"] is not None
    assert data["data"]["card"]["card_uid"] == "04A1B2C3D4E5F6"
    assert data["data"]["card"]["status"] == "active"
    
    # Verify card is assigned
    await db_session.refresh(card)
    assert card.customer_id is not None
    assert card.status == "active"
    assert card.assigned_date is not None


@pytest.mark.asyncio
async def test_get_customer(db_session):
    """Test retrieving customer details."""
    # Create customer
    customer = Customer(
        customer_id=uuid4(),
        name="Test Customer",
        email="test@example.com",
        phone="+34612345678",
    )
    db_session.add(customer)
    
    # Create account
    account = LoyaltyAccount(
        customer_id=customer.customer_id,
        current_balance_points=50000,
        current_balance_euros=5.00,
    )
    db_session.add(account)
    
    # Create card
    card = LoyaltyCard(
        card_uid="04A1B2C3D4E5F7",
        card_number="LC-00000002",
        customer_id=customer.customer_id,
        status="active",
        assigned_date=datetime.utcnow(),
    )
    db_session.add(card)
    await db_session.commit()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/api/v1/customers/{customer.customer_id}")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["customer_id"] == str(customer.customer_id)
    assert data["data"]["name"] == "Test Customer"
    assert data["data"]["email"] == "test@example.com"
    assert data["data"]["balance_euros"] == 5.00
    assert data["data"]["balance_points"] == 50000
    assert len(data["data"]["cards"]) == 1
    assert data["data"]["cards"][0]["card_uid"] == "04A1B2C3D4E5F7"


@pytest.mark.asyncio
async def test_get_customer_not_found(db_session):
    """Test retrieving a non-existent customer."""
    fake_customer_id = uuid4()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/api/v1/customers/{fake_customer_id}")
    
    # Verify 404 error
    assert response.status_code == 404
    data = response.json()
    assert "error_code" in data["detail"]
    assert data["detail"]["error_code"] == "CUSTOMER_NOT_FOUND"


@pytest.mark.asyncio
async def test_update_customer(db_session):
    """Test updating customer contact information."""
    # Create customer
    customer = Customer(
        customer_id=uuid4(),
        name="Original Name",
        email="original@example.com",
        phone="+34612345678",
        consent_marketing=False,
    )
    db_session.add(customer)
    await db_session.commit()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        update_data = {
            "name": "Updated Name",
            "phone": "+34698765432",
            "consent_marketing": True,
        }
        
        response = await client.patch(
            f"/api/v1/customers/{customer.customer_id}",
            json=update_data,
            headers={"X-Idempotency-Key": "test-customer-update-001"}
        )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["name"] == "Updated Name"
    assert data["data"]["phone"] == "+34698765432"
    assert data["data"]["consent_marketing"] is True
    assert data["data"]["email"] == "original@example.com"  # Unchanged
    
    # Verify customer in database
    await db_session.refresh(customer)
    assert customer.name == "Updated Name"
    assert customer.phone == "+34698765432"
    assert customer.consent_marketing is True
    
    # Verify consent record created for marketing consent change
    result = await db_session.execute(
        select(ConsentRecord).where(
            ConsentRecord.customer_id == customer.customer_id,
            ConsentRecord.consent_type == "marketing_email",
        )
    )
    consent_record = result.scalar_one()
    assert consent_record.consent_given is True
    assert consent_record.consent_method == "account_settings"


@pytest.mark.asyncio
async def test_update_customer_duplicate_email(db_session):
    """Test updating customer with an email that belongs to another customer."""
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
    await db_session.commit()
    
    # Try to update customer2 with customer1's email
    async with AsyncClient(app=app, base_url="http://test") as client:
        update_data = {
            "email": "customer1@example.com",
        }
        
        response = await client.patch(
            f"/api/v1/customers/{customer2.customer_id}",
            json=update_data,
            headers={"X-Idempotency-Key": "test-customer-update-duplicate"}
        )
    
    # Verify conflict error
    assert response.status_code == 409
    data = response.json()
    assert "error_code" in data["detail"]
    assert data["detail"]["error_code"] == "EMAIL_ALREADY_EXISTS"
