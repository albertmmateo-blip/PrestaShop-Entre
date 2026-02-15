"""Custom SQLAlchemy types for database compatibility."""
from sqlalchemy import TypeDecorator, String
from sqlalchemy.dialects import postgresql
import uuid as uuid_lib


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.
    
    Uses PostgreSQL's UUID type, otherwise uses String(36) storing as stringified UUIDs.
    """
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(postgresql.UUID())
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value) if not isinstance(value, uuid_lib.UUID) else value
        else:
            if not isinstance(value, uuid_lib.UUID):
                return str(value)
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid_lib.UUID):
            return uuid_lib.UUID(value)
        else:
            return value
