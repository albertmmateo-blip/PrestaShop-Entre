"""Security utilities for authentication and authorization."""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_api_key(api_key: str) -> str:
    """Hash an API key using SHA-256."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, stored_hash: str) -> bool:
    """Verify an API key against stored hash."""
    return hash_api_key(api_key) == stored_hash


def hash_request_body(body: dict) -> str:
    """Hash request body for idempotency checking."""
    import json
    from uuid import UUID
    from datetime import datetime, date
    from decimal import Decimal
    
    # Custom JSON encoder for special types
    def json_encoder(obj):
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f"Type {type(obj)} not serializable")
    
    # Sort keys for deterministic hash
    canonical_json = json.dumps(body, sort_keys=True, separators=(",", ":"), default=json_encoder)
    return hashlib.sha256(canonical_json.encode()).hexdigest()


def generate_api_key(environment: str, terminal_id: str) -> str:
    """Generate a secure API key for a terminal."""
    # Generate 32-character random string
    random_part = "".join(
        secrets.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(32)
    )
    return f"loyalty_{environment}_{terminal_id}_{random_part}"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT access token."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None
