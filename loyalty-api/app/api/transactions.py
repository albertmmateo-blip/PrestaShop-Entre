"""Loyalty transaction endpoints."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.loyalty_service import LoyaltyService
from app.core.logging import logger
from app.middleware.idempotency import check_idempotency, store_idempotency_key, require_idempotency_key
from app.models.schemas import (
    EarnPointsRequest, 
    RedeemPointsRequest, 
    ReverseTransactionRequest,
    TransactionResponse,
    ReversalResponse,
    BalanceResponse,
    ExpiringPoints,
)

router = APIRouter()


@router.post("/transactions/earn", response_model=dict, status_code=201)
async def earn_points(
    request: Request,
    earn_request: EarnPointsRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Award points for a purchase.
    
    Business Rule: Points = Order Amount * 1.5%
    """
    # Require idempotency key
    idempotency_key = require_idempotency_key(request)
    
    # Check idempotency
    cached_response = await check_idempotency(request, idempotency_key, earn_request.model_dump())
    if cached_response:
        logger.info(f"Returning cached earn transaction: {idempotency_key}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=cached_response["status_code"],
            content=cached_response["body"],
            headers=cached_response["headers"],
        )
    
    # Initialize service
    service = LoyaltyService(db)
    
    try:
        # Get customer
        customer = await service.get_customer(earn_request.customer_id)
        
        # Get or create account
        account = await service.get_or_create_account(earn_request.customer_id)
        
        # Calculate points earned
        points_earned, euros_earned = service.calculate_points_earned(earn_request.order_amount_euros)
        
        # Determine channel
        channel = "pos" if earn_request.order_source == "aniwin_pos" else "online"
        
        # Append to ledger
        ledger_entry = await service.append_to_ledger(
            customer_id=earn_request.customer_id,
            account_id=account.account_id,
            transaction_type="earn",
            points_delta=points_earned,
            amount_euros=euros_earned,
            order_id=earn_request.order_id,
            order_amount=earn_request.order_amount_euros,
            source_type="pos_sale" if earn_request.order_source == "aniwin_pos" else "online_order",
            source_reference=earn_request.order_id,
            terminal_id=earn_request.terminal_id,
            channel=channel,
            description=f"Earned {euros_earned} EUR from order {earn_request.order_id}",
            idempotency_key=idempotency_key,
            earn_rate=service.EARN_RATE_PERCENT,
        )
        
        # Commit transaction
        await db.commit()
        
        # Build response
        response_data = {
            "status": "success",
            "data": {
                "transaction_id": str(ledger_entry.ledger_id),
                "customer_id": str(earn_request.customer_id),
                "transaction_type": "earn",
                "amount_euros": float(euros_earned),
                "amount_points": points_earned,
                "order_id": earn_request.order_id,
                "new_balance_euros": float(ledger_entry.balance_after / service.POINTS_PER_EURO),
                "new_balance_points": ledger_entry.balance_after,
                "timestamp": ledger_entry.created_at.isoformat(),
            },
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": idempotency_key,
            }
        }
        
        # Store idempotency key
        await store_idempotency_key(
            idempotency_key=idempotency_key,
            request_body=earn_request.model_dump(),
            endpoint="/transactions/earn",
            http_method="POST",
            response_status=201,
            response_body=response_data,
            terminal_id=earn_request.terminal_id,
        )
        
        logger.info(f"Earn transaction successful: {ledger_entry.ledger_id}")
        return response_data
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error processing earn transaction: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "TRANSACTION_FAILED",
                "error_message": "Failed to process earn transaction",
            }
        )


@router.post("/transactions/redeem", response_model=dict, status_code=201)
async def redeem_points(
    request: Request,
    redeem_request: RedeemPointsRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Redeem points for discount.
    
    Validates that customer has sufficient balance.
    """
    # Require idempotency key
    idempotency_key = require_idempotency_key(request)
    
    # Check idempotency
    cached_response = await check_idempotency(request, idempotency_key, redeem_request.model_dump())
    if cached_response:
        logger.info(f"Returning cached redeem transaction: {idempotency_key}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=cached_response["status_code"],
            content=cached_response["body"],
            headers=cached_response["headers"],
        )
    
    # Initialize service
    service = LoyaltyService(db)
    
    try:
        # Get customer
        customer = await service.get_customer(redeem_request.customer_id)
        
        # Get or create account
        account = await service.get_or_create_account(redeem_request.customer_id)
        
        # Calculate points to redeem
        points_to_redeem = service.euros_to_points(redeem_request.redemption_amount_euros)
        
        # Validate redemption amount
        if redeem_request.redemption_amount_euros <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "INVALID_REDEMPTION_AMOUNT",
                    "error_message": "Redemption amount must be positive",
                }
            )
        
        # Determine channel
        channel = "pos" if redeem_request.order_source == "aniwin_pos" else "online"
        
        # Append to ledger (negative points)
        ledger_entry = await service.append_to_ledger(
            customer_id=redeem_request.customer_id,
            account_id=account.account_id,
            transaction_type="redeem",
            points_delta=-points_to_redeem,
            amount_euros=-redeem_request.redemption_amount_euros,
            order_id=redeem_request.order_id,
            order_amount=None,
            source_type="pos_sale" if redeem_request.order_source == "aniwin_pos" else "online_order",
            source_reference=redeem_request.order_id,
            terminal_id=redeem_request.terminal_id,
            channel=channel,
            description=f"Redeemed {redeem_request.redemption_amount_euros} EUR discount",
            idempotency_key=idempotency_key,
        )
        
        # Commit transaction
        await db.commit()
        
        # Build response
        response_data = {
            "status": "success",
            "data": {
                "transaction_id": str(ledger_entry.ledger_id),
                "customer_id": str(redeem_request.customer_id),
                "transaction_type": "redeem",
                "amount_euros": float(-redeem_request.redemption_amount_euros),
                "amount_points": -points_to_redeem,
                "order_id": redeem_request.order_id,
                "new_balance_euros": float(ledger_entry.balance_after / service.POINTS_PER_EURO),
                "new_balance_points": ledger_entry.balance_after,
                "voucher_code": f"LOYALTY-{ledger_entry.ledger_id.hex[:8].upper()}",
                "timestamp": ledger_entry.created_at.isoformat(),
            },
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": idempotency_key,
            }
        }
        
        # Store idempotency key
        await store_idempotency_key(
            idempotency_key=idempotency_key,
            request_body=redeem_request.model_dump(),
            endpoint="/transactions/redeem",
            http_method="POST",
            response_status=201,
            response_body=response_data,
            terminal_id=redeem_request.terminal_id,
        )
        
        logger.info(f"Redeem transaction successful: {ledger_entry.ledger_id}")
        return response_data
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error processing redeem transaction: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "TRANSACTION_FAILED",
                "error_message": "Failed to process redeem transaction",
            }
        )


@router.post("/transactions/reverse", response_model=dict, status_code=201)
async def reverse_transaction(
    request: Request,
    reverse_request: ReverseTransactionRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Reverse transactions for a refunded order.
    
    Finds all transactions (earn/redeem) for the order and creates
    compensating reversal transactions.
    """
    # Require idempotency key
    idempotency_key = require_idempotency_key(request)
    
    # Check idempotency
    cached_response = await check_idempotency(request, idempotency_key, reverse_request.model_dump())
    if cached_response:
        logger.info(f"Returning cached reverse transaction: {idempotency_key}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=cached_response["status_code"],
            content=cached_response["body"],
            headers=cached_response["headers"],
        )
    
    # Initialize service
    service = LoyaltyService(db)
    
    try:
        # Find original transactions
        original_transactions = await service.find_transactions_by_order_id(
            reverse_request.original_order_id
        )
        
        if not original_transactions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_code": "ORDER_NOT_FOUND",
                    "error_message": f"Order {reverse_request.original_order_id} not found",
                }
            )
        
        # Check if already refunded
        # (This is handled by the reversed_by_ledger_id check in find_transactions_by_order_id)
        
        reversal_entries = []
        
        # Create reversal for each original transaction
        for idx, original in enumerate(original_transactions):
            # Calculate reversal amounts (opposite sign)
            reversal_points = -original.points_delta
            reversal_euros = -original.amount_euros
            
            # Append reversal to ledger
            reversal_entry = await service.append_to_ledger(
                customer_id=original.customer_id,
                account_id=original.account_id,
                transaction_type="refund",
                points_delta=reversal_points,
                amount_euros=reversal_euros,
                order_id=reverse_request.original_order_id,
                order_amount=None,
                source_type="refund_reversal",
                source_reference=f"REFUND-{reverse_request.original_order_id}",
                terminal_id=reverse_request.terminal_id,
                channel="system",
                description=f"Refund: Reversed {original.transaction_type} from order {reverse_request.original_order_id}",
                idempotency_key=f"{idempotency_key}-{idx}",
                reverses_ledger_id=original.ledger_id,
            )
            
            reversal_entries.append(reversal_entry)
        
        # Commit all reversals
        await db.commit()
        
        # Get new balance
        final_balance_points, final_balance_euros = await service.get_latest_balance_after(
            original_transactions[0].customer_id
        )
        
        # Build response
        response_data = {
            "status": "success",
            "data": {
                "reversal_transactions": [
                    {
                        "transaction_id": str(entry.ledger_id),
                        "customer_id": str(entry.customer_id),
                        "transaction_type": entry.transaction_type,
                        "amount_euros": float(entry.amount_euros),
                        "amount_points": entry.points_delta,
                        "original_transaction_id": str(entry.reverses_ledger_id),
                        "timestamp": entry.created_at.isoformat(),
                    }
                    for entry in reversal_entries
                ],
                "new_balance_euros": float(final_balance_euros),
                "new_balance_points": final_balance_points,
            },
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": idempotency_key,
            }
        }
        
        # Store idempotency key
        await store_idempotency_key(
            idempotency_key=idempotency_key,
            request_body=reverse_request.model_dump(),
            endpoint="/transactions/reverse",
            http_method="POST",
            response_status=201,
            response_body=response_data,
            terminal_id=reverse_request.terminal_id,
        )
        
        logger.info(f"Reverse transaction successful for order: {reverse_request.original_order_id}")
        return response_data
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error processing reverse transaction: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "TRANSACTION_FAILED",
                "error_message": "Failed to process reverse transaction",
            }
        )


@router.get("/customers/{customer_id}/balance", response_model=dict)
async def get_balance(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get current loyalty balance for customer.
    
    Computes balance from ledger and includes expiring points info.
    """
    service = LoyaltyService(db)
    
    try:
        # Get customer
        customer = await service.get_customer(customer_id)
        
        # Get current balance
        balance_points, balance_euros = await service.get_current_balance(customer_id)
        
        # Get transaction count
        tx_count = await service.get_transaction_count(customer_id)
        
        # Get last transaction date
        account = await service.get_or_create_account(customer_id)
        last_transaction = account.last_transaction_date
        
        # Get expiring points (within 30 days)
        expiring_info = await service.get_expiring_points(customer_id, days_ahead=30)
        
        expiring_soon = None
        if expiring_info:
            exp_points, exp_euros, exp_date = expiring_info
            expiring_soon = {
                "amount_euros": float(exp_euros),
                "amount_points": exp_points,
                "expiry_date": exp_date,
            }
        
        response_data = {
            "status": "success",
            "data": {
                "customer_id": str(customer_id),
                "balance_euros": float(balance_euros),
                "balance_points": balance_points,
                "transactions_count": tx_count,
                "last_transaction": last_transaction.isoformat() if last_transaction else None,
                "expiring_soon": expiring_soon,
            },
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
            }
        }
        
        logger.info(f"Balance query successful for customer: {customer_id}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying balance: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "BALANCE_QUERY_FAILED",
                "error_message": "Failed to retrieve balance",
            }
        )
