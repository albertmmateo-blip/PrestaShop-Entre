"""Database models for loyalty system."""
from datetime import datetime, date
from typing import Optional
import uuid

from sqlalchemy import Column, String, Integer, DateTime, Date, Numeric, Text, Boolean, ForeignKey, CheckConstraint, BigInteger
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.types import GUID


class Customer(Base):
    """Customer entity."""
    
    __tablename__ = "customers"
    
    customer_id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    prestashop_customer_id = Column(Integer, nullable=True, index=True)
    consent_loyalty = Column(Boolean, default=True, nullable=False)
    consent_marketing = Column(Boolean, default=False, nullable=False)
    language = Column(String(10), default="es", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    cards = relationship("LoyaltyCard", back_populates="customer")
    account = relationship("LoyaltyAccount", back_populates="customer", uselist=False)
    transactions = relationship("LoyaltyLedger", back_populates="customer")


class LoyaltyCard(Base):
    """Loyalty card (NFC) entity."""
    
    __tablename__ = "loyalty_cards"
    
    card_id = Column(GUID, primary_key=True, default=uuid.uuid4)
    card_uid = Column(String(20), unique=True, nullable=False, index=True)
    card_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(GUID, ForeignKey("customers.customer_id"), nullable=False)
    status = Column(String(20), default="active", nullable=False, index=True)
    issued_date = Column(Date, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="cards")


class LoyaltyAccount(Base):
    """Loyalty account for balance tracking (cached from ledger)."""
    
    __tablename__ = "loyalty_accounts"
    
    account_id = Column(GUID, primary_key=True, default=uuid.uuid4)
    customer_id = Column(GUID, ForeignKey("customers.customer_id"), nullable=False, unique=True)
    current_balance_points = Column(Integer, default=0, nullable=False)
    current_balance_euros = Column(Numeric(10, 2), default=0.00, nullable=False)
    total_earned_points = Column(Integer, default=0, nullable=False)
    total_redeemed_points = Column(Integer, default=0, nullable=False)
    last_transaction_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="account")


class LoyaltyLedger(Base):
    """
    Immutable loyalty transaction ledger (append-only).
    Single source of truth for all point movements.
    """
    
    __tablename__ = "loyalty_ledger"
    
    ledger_id = Column(GUID, primary_key=True, default=uuid.uuid4)
    ledger_sequence = Column(BigInteger, nullable=False, unique=True, index=True)
    
    # Customer reference
    customer_id = Column(GUID, ForeignKey("customers.customer_id"), nullable=False, index=True)
    account_id = Column(GUID, ForeignKey("loyalty_accounts.account_id"), nullable=False)
    
    # Transaction details
    transaction_type = Column(
        String(20), 
        nullable=False,
        index=True
    )
    transaction_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Point movement
    points_delta = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)
    
    # Amounts in euros
    amount_euros = Column(Numeric(10, 2), nullable=False)
    
    # Source reference
    source_type = Column(String(50), nullable=False)
    source_reference = Column(String(255), nullable=True)
    order_id = Column(String(100), nullable=True, index=True)
    
    # Transaction metadata
    order_amount_eur = Column(Numeric(10, 2), nullable=True)
    earn_rate_percent = Column(Numeric(5, 2), nullable=True)
    redemption_rate_percent = Column(Numeric(5, 2), nullable=True)
    
    # Description
    description = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Expiration tracking
    expiration_date = Column(Date, nullable=True)
    expired_by_ledger_id = Column(GUID, ForeignKey("loyalty_ledger.ledger_id"), nullable=True)
    
    # Idempotency
    idempotency_key = Column(String(255), unique=True, nullable=True, index=True)
    
    # Reversal tracking
    reversed_by_ledger_id = Column(GUID, ForeignKey("loyalty_ledger.ledger_id"), nullable=True)
    reverses_ledger_id = Column(GUID, ForeignKey("loyalty_ledger.ledger_id"), nullable=True)
    
    # Terminal/channel
    terminal_id = Column(String(50), nullable=True)
    channel = Column(String(20), nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(100), nullable=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="transactions")
    
    # Constraints (simplified for database compatibility)
    __table_args__ = (
        CheckConstraint("balance_after >= 0", name="chk_balance_non_negative"),
    )
