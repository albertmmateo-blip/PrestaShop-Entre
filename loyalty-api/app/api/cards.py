"""Card management endpoints."""
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.logging import logger
from app.middleware.idempotency import require_idempotency_key, check_idempotency, store_idempotency_key
from app.models.loyalty import Customer, LoyaltyCard
from app.models.customer_schemas import (
    RegisterCardRequest,
    AssignCardRequest,
    CardResponse,
    CardCustomerLookupResponse,
    CustomerInfoResponse,
)

router = APIRouter()


@router.post("/cards", response_model=dict, status_code=201)
async def register_card(
    request: Request,
    card_request: RegisterCardRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new card in the system without assigning to a customer.
    
    - Validates card UID uniqueness
    - Generates card number if not provided
    - Card status is 'inactive' until assigned
    """
    # Require idempotency key
    idempotency_key = require_idempotency_key(request)
    
    # Check idempotency
    cached_response = await check_idempotency(request, idempotency_key, card_request.model_dump(mode='json'))
    if cached_response:
        logger.info(f"Returning cached register card response: {idempotency_key}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=cached_response["status_code"],
            content=cached_response["body"],
            headers=cached_response["headers"],
        )
    
    try:
        # Check if card UID already exists
        result = await db.execute(
            select(LoyaltyCard).where(LoyaltyCard.card_uid == card_request.card_uid)
        )
        existing_card = result.scalar_one_or_none()
        
        if existing_card:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error_code": "CARD_UID_EXISTS",
                    "error_message": f"Card with UID {card_request.card_uid} already exists",
                }
            )
        
        # Check if card number already exists
        result = await db.execute(
            select(LoyaltyCard).where(LoyaltyCard.card_number == card_request.card_number)
        )
        existing_number = result.scalar_one_or_none()
        
        if existing_number:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error_code": "CARD_NUMBER_EXISTS",
                    "error_message": f"Card number {card_request.card_number} already exists",
                }
            )
        
        # Create card
        card = LoyaltyCard(
            card_uid=card_request.card_uid,
            card_number=card_request.card_number,
            status="inactive",  # Inactive until assigned to customer
            customer_id=None,
        )
        db.add(card)
        await db.commit()
        await db.refresh(card)
        
        # Build response
        response_data = {
            "status": "success",
            "data": {
                "card_id": str(card.card_id),
                "card_uid": card.card_uid,
                "card_number": card.card_number,
                "status": card.status,
                "issued_date": card.issued_date.isoformat(),
                "assigned_date": None,
                "customer": None,
            },
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": idempotency_key,
            }
        }
        
        # Store idempotency key
        await store_idempotency_key(
            idempotency_key=idempotency_key,
            request_body=card_request.model_dump(mode='json'),
            endpoint="/cards",
            http_method="POST",
            response_status=201,
            response_body=response_data,
        )
        
        logger.info(f"Card registered successfully: {card.card_uid}")
        return response_data
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error registering card: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "CARD_REGISTRATION_FAILED",
                "error_message": "Failed to register card",
            }
        )


@router.post("/cards/{card_uid}/assign", response_model=dict, status_code=200)
async def assign_card(
    request: Request,
    card_uid: str,
    assign_request: AssignCardRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Assign a card to a customer.
    
    - Validates card exists and is not already assigned
    - Validates customer exists
    - Sets card status to 'active'
    """
    # Require idempotency key
    idempotency_key = require_idempotency_key(request)
    
    # Check idempotency
    cached_response = await check_idempotency(request, idempotency_key, assign_request.model_dump(mode='json'))
    if cached_response:
        logger.info(f"Returning cached assign card response: {idempotency_key}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=cached_response["status_code"],
            content=cached_response["body"],
            headers=cached_response["headers"],
        )
    
    try:
        # Normalize card UID
        card_uid_upper = card_uid.upper()
        
        # Get card
        result = await db.execute(
            select(LoyaltyCard)
            .options(selectinload(LoyaltyCard.customer))
            .where(LoyaltyCard.card_uid == card_uid_upper)
        )
        card = result.scalar_one_or_none()
        
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_code": "CARD_NOT_FOUND",
                    "error_message": f"Card with UID {card_uid} not found",
                }
            )
        
        # Check if card already assigned
        if card.customer_id is not None:
            # Get customer name for error message
            customer_name = card.customer.name if card.customer else "Unknown"
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error_code": "CARD_ALREADY_ASSIGNED",
                    "error_message": f"Card {card_uid} is already assigned to customer {customer_name}",
                }
            )
        
        # Get customer
        result = await db.execute(
            select(Customer).where(Customer.customer_id == assign_request.customer_id)
        )
        customer = result.scalar_one_or_none()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_code": "CUSTOMER_NOT_FOUND",
                    "error_message": f"Customer {assign_request.customer_id} not found",
                }
            )
        
        # Assign card
        card.customer_id = assign_request.customer_id
        card.status = "active"
        card.assigned_date = datetime.utcnow()
        card.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(card)
        await db.refresh(customer)
        
        # Build response
        response_data = {
            "status": "success",
            "data": {
                "card_id": str(card.card_id),
                "card_uid": card.card_uid,
                "card_number": card.card_number,
                "status": card.status,
                "issued_date": card.issued_date.isoformat(),
                "assigned_date": card.assigned_date.isoformat() if card.assigned_date else None,
                "customer": {
                    "customer_id": str(customer.customer_id),
                    "name": customer.name,
                    "email": customer.email,
                    "phone": customer.phone,
                },
            },
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": idempotency_key,
            }
        }
        
        # Store idempotency key
        await store_idempotency_key(
            idempotency_key=idempotency_key,
            request_body=assign_request.model_dump(mode='json'),
            endpoint=f"/cards/{card_uid}/assign",
            http_method="POST",
            response_status=200,
            response_body=response_data,
        )
        
        logger.info(f"Card assigned successfully: {card.card_uid} -> {customer.customer_id}")
        return response_data
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error assigning card: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "CARD_ASSIGNMENT_FAILED",
                "error_message": "Failed to assign card",
            }
        )


@router.get("/cards/{card_uid}/customer", response_model=dict)
async def get_card_customer(
    card_uid: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Lookup customer by card UID.
    
    - Used by POS terminals to identify customer when card is tapped
    - Returns customer info if card is assigned
    """
    try:
        # Normalize card UID
        card_uid_upper = card_uid.upper()
        
        # Get card with customer
        result = await db.execute(
            select(LoyaltyCard)
            .options(selectinload(LoyaltyCard.customer))
            .where(LoyaltyCard.card_uid == card_uid_upper)
        )
        card = result.scalar_one_or_none()
        
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_code": "CARD_NOT_FOUND",
                    "error_message": f"Card with UID {card_uid} not found",
                }
            )
        
        # Check card status
        if card.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error_code": "CARD_INACTIVE",
                    "error_message": f"Card {card_uid} is {card.status}",
                }
            )
        
        # Check if card is assigned
        if card.customer_id is None or card.customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_code": "CARD_NOT_ASSIGNED",
                    "error_message": f"Card {card_uid} is not assigned to any customer",
                }
            )
        
        customer = card.customer
        
        # Build response
        response_data = {
            "status": "success",
            "data": {
                "card_id": str(card.card_id),
                "card_uid": card.card_uid,
                "card_number": card.card_number,
                "status": card.status,
                "customer": {
                    "customer_id": str(customer.customer_id),
                    "name": customer.name,
                    "email": customer.email,
                    "phone": customer.phone,
                },
            },
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
            }
        }
        
        logger.info(f"Card customer lookup successful: {card.card_uid} -> {customer.customer_id}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error looking up card customer: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "CARD_LOOKUP_FAILED",
                "error_message": "Failed to lookup card customer",
            }
        )
