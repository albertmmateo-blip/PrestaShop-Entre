"""Pydantic schemas for loyalty transactions API."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# Request Schemas

class EarnPointsRequest(BaseModel):
    """Request schema for earning points."""
    customer_id: UUID
    order_id: str = Field(..., min_length=1, max_length=100)
    order_source: str = Field(..., pattern="^(aniwin_pos|prestashop|manual)$")
    terminal_id: Optional[str] = Field(None, max_length=50)
    order_amount_euros: Decimal = Field(..., gt=0, decimal_places=2)
    order_timestamp: datetime
    metadata: Optional[dict] = None


class RedeemPointsRequest(BaseModel):
    """Request schema for redeeming points."""
    customer_id: UUID
    redemption_amount_euros: Decimal = Field(..., gt=0, decimal_places=2)
    order_id: str = Field(..., min_length=1, max_length=100)
    order_source: str = Field(..., pattern="^(aniwin_pos|prestashop|manual)$")
    terminal_id: Optional[str] = Field(None, max_length=50)
    order_timestamp: datetime


class ReverseTransactionRequest(BaseModel):
    """Request schema for reversing/refunding a transaction."""
    original_order_id: str = Field(..., min_length=1, max_length=100)
    refund_timestamp: datetime
    reason: Optional[str] = Field(None, max_length=500)
    terminal_id: Optional[str] = Field(None, max_length=50)


# Response Schemas

class TransactionResponse(BaseModel):
    """Response schema for transaction operations."""
    model_config = ConfigDict(from_attributes=True)
    
    transaction_id: UUID
    customer_id: UUID
    transaction_type: str
    amount_euros: Decimal
    amount_points: int
    order_id: Optional[str] = None
    new_balance_euros: Decimal
    new_balance_points: int
    timestamp: datetime
    voucher_code: Optional[str] = None


class ReversalResponse(BaseModel):
    """Response schema for reversal operations."""
    model_config = ConfigDict(from_attributes=True)
    
    reversal_transactions: list[TransactionResponse]
    new_balance_euros: Decimal
    new_balance_points: int


class ExpiringPoints(BaseModel):
    """Expiring points information."""
    amount_euros: Decimal
    amount_points: int
    expiry_date: str  # ISO date string


class BalanceResponse(BaseModel):
    """Response schema for balance query."""
    model_config = ConfigDict(from_attributes=True)
    
    customer_id: UUID
    balance_euros: Decimal
    balance_points: int
    transactions_count: int
    last_transaction: Optional[datetime] = None
    expiring_soon: Optional[ExpiringPoints] = None


class ErrorDetail(BaseModel):
    """Error detail in responses."""
    error_code: str
    error_message: str
    details: Optional[dict] = None


class StandardResponse(BaseModel):
    """Standard API response wrapper."""
    status: str  # "success" or "error"
    data: Optional[dict] = None
    error: Optional[ErrorDetail] = None
    meta: dict = Field(default_factory=dict)
