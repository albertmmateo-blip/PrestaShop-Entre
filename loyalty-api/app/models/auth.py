"""Database models for authentication and idempotency."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base


class TerminalCredential(Base):
    """Terminal API credentials."""

    __tablename__ = "terminal_credentials"

    id = Column(Integer, primary_key=True, index=True)
    terminal_id = Column(String(50), unique=True, nullable=False, index=True)
    api_key_hash = Column(String(64), nullable=False)
    location = Column(String(200))
    manager_assigned = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime)
    rotation_due_date = Column(DateTime)
    status = Column(String(20), default="active", nullable=False, index=True)
    created_by = Column(String(100))
    # Use JSON for database compatibility
    ip_whitelist = Column(JSON, nullable=True)


class IdempotencyKey(Base):
    """Idempotency keys for duplicate request prevention."""

    __tablename__ = "idempotency_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idempotency_key = Column(String(255), unique=True, nullable=False, index=True)
    request_hash = Column(String(64), nullable=False)
    endpoint = Column(String(100), nullable=False)
    http_method = Column(String(10), nullable=False)
    response_status = Column(Integer, nullable=False)
    response_body = Column(Text, nullable=False)
    terminal_id = Column(String(50))
    card_uid = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    request_metadata = Column(JSON)
