"""Customer management endpoints."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.logging import logger
from app.middleware.idempotency import require_idempotency_key, check_idempotency, store_idempotency_key
from app.models.loyalty import Customer, LoyaltyCard, LoyaltyAccount, ConsentRecord
from app.models.customer_schemas import (
    CreateCustomerRequest,
    UpdateCustomerRequest,
    CustomerResponse,
    CardInfoResponse,
    ConsentResponse,
)

router = APIRouter()


# Consent text templates
CONSENT_TEXTS = {
    "loyalty_program": "I consent to participate in the Fidelity Points Loyalty Program and agree to the processing of my transaction data to earn and redeem points. I understand that my data will be stored securely and used only for loyalty program purposes as described in the Privacy Policy.",
    "marketing_email": "I consent to receive promotional emails from the company including special offers, discounts, new product announcements, and loyalty program updates. I can unsubscribe at any time.",
}


async def create_consent_record(
    db: AsyncSession,
    customer_id: UUID,
    consent_type: str,
    consent_given: bool,
    consent_method: str = "pos_enrollment",
    ip_address: Optional[str] = None,
) -> ConsentRecord:
    """Create a consent record for a customer."""
    consent = ConsentRecord(
        customer_id=customer_id,
        consent_type=consent_type,
        consent_given=consent_given,
        consent_date=datetime.utcnow(),
        consent_method=consent_method,
        consent_ip_address=ip_address,
        consent_version="v1.0",
        consent_text=CONSENT_TEXTS.get(consent_type, f"Consent to {consent_type}"),
        created_by="api",
    )
    db.add(consent)
    return consent


@router.post("/customers", response_model=dict, status_code=201)
async def create_customer(
    request: Request,
    customer_request: CreateCustomerRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new customer and optionally assign a card.
    
    - Records GDPR consent
    - Creates loyalty account
    - Optionally assigns card if card_uid provided
    """
    # Require idempotency key
    idempotency_key = require_idempotency_key(request)
    
    # Check idempotency
    cached_response = await check_idempotency(request, idempotency_key, customer_request.model_dump(mode='json'))
    if cached_response:
        logger.info(f"Returning cached create customer response: {idempotency_key}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=cached_response["status_code"],
            content=cached_response["body"],
            headers=cached_response["headers"],
        )
    
    try:
        # Check if email already exists
        result = await db.execute(
            select(Customer).where(Customer.email == customer_request.email)
        )
        existing_customer = result.scalar_one_or_none()
        
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error_code": "EMAIL_ALREADY_EXISTS",
                    "error_message": f"Customer with email {customer_request.email} already exists",
                }
            )
        
        # Validate consent_loyalty must be true
        if not customer_request.consent_loyalty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "CONSENT_REQUIRED",
                    "error_message": "Consent to loyalty program terms is required",
                }
            )
        
        # If card_uid provided, check if card exists and is not already assigned
        card = None
        if customer_request.card_uid:
            result = await db.execute(
                select(LoyaltyCard).where(LoyaltyCard.card_uid == customer_request.card_uid)
            )
            card = result.scalar_one_or_none()
            
            if not card:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error_code": "CARD_NOT_FOUND",
                        "error_message": f"Card with UID {customer_request.card_uid} not found",
                    }
                )
            
            if card.customer_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "error_code": "CARD_ALREADY_ASSIGNED",
                        "error_message": f"Card {customer_request.card_uid} is already assigned to another customer",
                    }
                )
        
        # Create customer
        customer = Customer(
            name=customer_request.name,
            email=customer_request.email,
            phone=customer_request.phone,
            prestashop_customer_id=customer_request.prestashop_customer_id,
            consent_loyalty=customer_request.consent_loyalty,
            consent_marketing=customer_request.consent_marketing,
            language=customer_request.language,
        )
        db.add(customer)
        await db.flush()  # Get customer_id
        
        # Create loyalty account
        account = LoyaltyAccount(
            customer_id=customer.customer_id,
            current_balance_points=0,
            current_balance_euros=0.00,
        )
        db.add(account)
        
        # Create consent records
        ip_address = request.client.host if request.client else None
        
        # Loyalty program consent (required)
        await create_consent_record(
            db,
            customer.customer_id,
            "loyalty_program",
            customer_request.consent_loyalty,
            "api",
            ip_address,
        )
        
        # Marketing consent (if provided)
        if customer_request.consent_marketing:
            await create_consent_record(
                db,
                customer.customer_id,
                "marketing_email",
                customer_request.consent_marketing,
                "api",
                ip_address,
            )
        
        # Assign card if provided
        if card:
            card.customer_id = customer.customer_id
            card.status = "active"
            card.assigned_date = datetime.utcnow()
        
        await db.commit()
        await db.refresh(customer)
        
        # Build response
        card_info = None
        if card:
            card_info = {
                "card_id": str(card.card_id),
                "card_uid": card.card_uid,
                "card_number": card.card_number,
                "status": card.status,
                "issued_date": card.issued_date.isoformat(),
                "assigned_date": card.assigned_date.isoformat() if card.assigned_date else None,
            }
        
        response_data = {
            "status": "success",
            "data": {
                "customer_id": str(customer.customer_id),
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
                "prestashop_customer_id": customer.prestashop_customer_id,
                "consent_loyalty": customer.consent_loyalty,
                "consent_marketing": customer.consent_marketing,
                "language": customer.language,
                "created_at": customer.created_at.isoformat(),
                "card": card_info,
                "balance_euros": 0.00,
                "balance_points": 0,
            },
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": idempotency_key,
            }
        }
        
        # Store idempotency key
        await store_idempotency_key(
            idempotency_key=idempotency_key,
            request_body=customer_request.model_dump(mode='json'),
            endpoint="/customers",
            http_method="POST",
            response_status=201,
            response_body=response_data,
        )
        
        logger.info(f"Customer created successfully: {customer.customer_id}")
        return response_data
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating customer: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "CUSTOMER_CREATION_FAILED",
                "error_message": "Failed to create customer",
            }
        )


@router.get("/customers/{customer_id}", response_model=dict)
async def get_customer(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get customer details including cards and balance.
    """
    try:
        # Get customer with relationships
        result = await db.execute(
            select(Customer)
            .options(selectinload(Customer.cards))
            .options(selectinload(Customer.account))
            .where(Customer.customer_id == customer_id)
        )
        customer = result.scalar_one_or_none()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_code": "CUSTOMER_NOT_FOUND",
                    "error_message": f"Customer {customer_id} not found",
                }
            )
        
        # Build cards info
        cards_info = []
        for card in customer.cards:
            cards_info.append({
                "card_id": str(card.card_id),
                "card_uid": card.card_uid,
                "card_number": card.card_number,
                "status": card.status,
                "issued_date": card.issued_date.isoformat(),
                "assigned_date": card.assigned_date.isoformat() if card.assigned_date else None,
            })
        
        # Get balance from account
        balance_euros = 0.00
        balance_points = 0
        if customer.account:
            balance_euros = float(customer.account.current_balance_euros)
            balance_points = customer.account.current_balance_points
        
        response_data = {
            "status": "success",
            "data": {
                "customer_id": str(customer.customer_id),
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
                "prestashop_customer_id": customer.prestashop_customer_id,
                "consent_loyalty": customer.consent_loyalty,
                "consent_marketing": customer.consent_marketing,
                "language": customer.language,
                "created_at": customer.created_at.isoformat(),
                "updated_at": customer.updated_at.isoformat(),
                "cards": cards_info,
                "balance_euros": balance_euros,
                "balance_points": balance_points,
            },
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
            }
        }
        
        logger.info(f"Customer retrieved successfully: {customer_id}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving customer: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "CUSTOMER_RETRIEVAL_FAILED",
                "error_message": "Failed to retrieve customer",
            }
        )


@router.patch("/customers/{customer_id}", response_model=dict)
async def update_customer(
    request: Request,
    customer_id: UUID,
    update_request: UpdateCustomerRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Update customer contact information.
    
    - Records consent changes as new consent records
    - Only updates provided fields
    """
    # Require idempotency key
    idempotency_key = require_idempotency_key(request)
    
    # Check idempotency
    cached_response = await check_idempotency(request, idempotency_key, update_request.model_dump(mode='json'))
    if cached_response:
        logger.info(f"Returning cached update customer response: {idempotency_key}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=cached_response["status_code"],
            content=cached_response["body"],
            headers=cached_response["headers"],
        )
    
    try:
        # Get customer
        result = await db.execute(
            select(Customer)
            .options(selectinload(Customer.cards))
            .options(selectinload(Customer.account))
            .where(Customer.customer_id == customer_id)
        )
        customer = result.scalar_one_or_none()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_code": "CUSTOMER_NOT_FOUND",
                    "error_message": f"Customer {customer_id} not found",
                }
            )
        
        # Track consent change
        consent_changed = False
        if update_request.consent_marketing is not None and update_request.consent_marketing != customer.consent_marketing:
            consent_changed = True
            customer.consent_marketing = update_request.consent_marketing
        
        # Update fields
        if update_request.name is not None:
            customer.name = update_request.name
        if update_request.email is not None:
            # Check if email already used by another customer
            result = await db.execute(
                select(Customer).where(
                    Customer.email == update_request.email,
                    Customer.customer_id != customer_id
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "error_code": "EMAIL_ALREADY_EXISTS",
                        "error_message": f"Email {update_request.email} is already used by another customer",
                    }
                )
            customer.email = update_request.email
        if update_request.phone is not None:
            customer.phone = update_request.phone
        if update_request.language is not None:
            customer.language = update_request.language
        
        customer.updated_at = datetime.utcnow()
        
        # Record consent change
        if consent_changed:
            ip_address = request.client.host if request.client else None
            await create_consent_record(
                db,
                customer.customer_id,
                "marketing_email",
                customer.consent_marketing,
                "account_settings",
                ip_address,
            )
        
        await db.commit()
        await db.refresh(customer)
        
        # Build response
        cards_info = []
        for card in customer.cards:
            cards_info.append({
                "card_id": str(card.card_id),
                "card_uid": card.card_uid,
                "card_number": card.card_number,
                "status": card.status,
                "issued_date": card.issued_date.isoformat(),
                "assigned_date": card.assigned_date.isoformat() if card.assigned_date else None,
            })
        
        balance_euros = 0.00
        balance_points = 0
        if customer.account:
            balance_euros = float(customer.account.current_balance_euros)
            balance_points = customer.account.current_balance_points
        
        response_data = {
            "status": "success",
            "data": {
                "customer_id": str(customer.customer_id),
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
                "prestashop_customer_id": customer.prestashop_customer_id,
                "consent_loyalty": customer.consent_loyalty,
                "consent_marketing": customer.consent_marketing,
                "language": customer.language,
                "created_at": customer.created_at.isoformat(),
                "updated_at": customer.updated_at.isoformat(),
                "cards": cards_info,
                "balance_euros": balance_euros,
                "balance_points": balance_points,
            },
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": idempotency_key,
            }
        }
        
        # Store idempotency key
        await store_idempotency_key(
            idempotency_key=idempotency_key,
            request_body=update_request.model_dump(mode='json'),
            endpoint=f"/customers/{customer_id}",
            http_method="PATCH",
            response_status=200,
            response_body=response_data,
        )
        
        logger.info(f"Customer updated successfully: {customer_id}")
        return response_data
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating customer: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "CUSTOMER_UPDATE_FAILED",
                "error_message": "Failed to update customer",
            }
        )
