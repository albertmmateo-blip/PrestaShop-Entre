"""Pydantic schemas for customer and card management API."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator
import re


# Validation patterns
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PHONE_PATTERN = re.compile(r'^\+?[1-9]\d{1,14}$')  # E.164 format


# Request Schemas - Customers

class CreateCustomerRequest(BaseModel):
    """Request schema for creating a new customer."""
    name: str = Field(..., min_length=1, max_length=200, description="Customer full name")
    email: str = Field(..., max_length=255, description="Customer email address")
    phone: Optional[str] = Field(None, max_length=20, description="Customer phone number")
    prestashop_customer_id: Optional[int] = Field(None, description="PrestaShop customer ID if linking")
    consent_loyalty: bool = Field(True, description="Consent to loyalty program terms")
    consent_marketing: bool = Field(False, description="Consent to marketing communications")
    language: str = Field("es", pattern="^(es|ca|en)$", description="Preferred language")
    card_uid: Optional[str] = Field(None, min_length=14, max_length=14, description="Card UID to assign during enrollment")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if not EMAIL_PATTERN.match(v):
            raise ValueError('Invalid email format')
        return v.lower().strip()
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format (E.164)."""
        if v is None:
            return v
        # Remove spaces and dashes for validation
        phone_clean = v.replace(' ', '').replace('-', '')
        if not PHONE_PATTERN.match(phone_clean):
            raise ValueError('Invalid phone number format. Use E.164 format (e.g., +34612345678)')
        return phone_clean
    
    @field_validator('card_uid')
    @classmethod
    def validate_card_uid(cls, v: Optional[str]) -> Optional[str]:
        """Validate card UID format (14 hex characters)."""
        if v is None:
            return v
        if not re.match(r'^[0-9A-Fa-f]{14}$', v):
            raise ValueError('Invalid card UID format. Must be 14 hexadecimal characters')
        return v.upper()


class UpdateCustomerRequest(BaseModel):
    """Request schema for updating customer contact information."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    consent_marketing: Optional[bool] = None
    language: Optional[str] = Field(None, pattern="^(es|ca|en)$")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validate email format."""
        if v is None:
            return v
        if not EMAIL_PATTERN.match(v):
            raise ValueError('Invalid email format')
        return v.lower().strip()
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format (E.164)."""
        if v is None:
            return v
        phone_clean = v.replace(' ', '').replace('-', '')
        if not PHONE_PATTERN.match(phone_clean):
            raise ValueError('Invalid phone number format. Use E.164 format (e.g., +34612345678)')
        return phone_clean


# Request Schemas - Cards

class RegisterCardRequest(BaseModel):
    """Request schema for registering a new card."""
    card_uid: str = Field(..., min_length=14, max_length=14, description="Card NFC UID (14 hex characters)")
    card_number: str = Field(..., min_length=1, max_length=50, description="Human-readable card number")
    
    @field_validator('card_uid')
    @classmethod
    def validate_card_uid(cls, v: str) -> str:
        """Validate card UID format (14 hex characters)."""
        if not re.match(r'^[0-9A-Fa-f]{14}$', v):
            raise ValueError('Invalid card UID format. Must be 14 hexadecimal characters')
        return v.upper()


class AssignCardRequest(BaseModel):
    """Request schema for assigning a card to a customer."""
    customer_id: UUID = Field(..., description="Customer ID to assign card to")


# Response Schemas - Customers

class ConsentResponse(BaseModel):
    """Response schema for consent record."""
    model_config = ConfigDict(from_attributes=True)
    
    consent_id: UUID
    consent_type: str
    consent_given: bool
    consent_date: datetime
    consent_method: str


class CardInfoResponse(BaseModel):
    """Response schema for card information in customer response."""
    model_config = ConfigDict(from_attributes=True)
    
    card_id: UUID
    card_uid: str
    card_number: str
    status: str
    issued_date: str  # ISO date string
    assigned_date: Optional[datetime] = None


class CustomerResponse(BaseModel):
    """Response schema for customer operations."""
    model_config = ConfigDict(from_attributes=True)
    
    customer_id: UUID
    name: str
    email: str
    phone: Optional[str] = None
    prestashop_customer_id: Optional[int] = None
    consent_loyalty: bool
    consent_marketing: bool
    language: str
    created_at: datetime
    updated_at: datetime
    cards: Optional[list[CardInfoResponse]] = None
    balance_euros: Optional[float] = None
    balance_points: Optional[int] = None


# Response Schemas - Cards

class CustomerInfoResponse(BaseModel):
    """Response schema for customer information in card response."""
    model_config = ConfigDict(from_attributes=True)
    
    customer_id: UUID
    name: str
    phone: Optional[str] = None
    email: str


class CardResponse(BaseModel):
    """Response schema for card operations."""
    model_config = ConfigDict(from_attributes=True)
    
    card_id: UUID
    card_uid: str
    card_number: str
    status: str
    issued_date: str
    assigned_date: Optional[datetime] = None
    customer: Optional[CustomerInfoResponse] = None


class CardCustomerLookupResponse(BaseModel):
    """Response schema for card-to-customer lookup."""
    model_config = ConfigDict(from_attributes=True)
    
    card_id: UUID
    card_uid: str
    card_number: str
    status: str
    customer: CustomerInfoResponse


# Standard Response Wrapper

class StandardResponse(BaseModel):
    """Standard API response wrapper."""
    status: str  # "success" or "error"
    data: Optional[dict] = None
    error: Optional[dict] = None
    meta: dict = Field(default_factory=dict)
