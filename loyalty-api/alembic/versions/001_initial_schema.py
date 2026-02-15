"""Initial schema: terminal credentials and idempotency keys

Revision ID: 001
Revises: 
Create Date: 2026-02-15 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial tables for authentication and idempotency."""
    # Create terminal_credentials table
    op.create_table(
        'terminal_credentials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('terminal_id', sa.String(length=50), nullable=False),
        sa.Column('api_key_hash', sa.String(length=64), nullable=False),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('manager_assigned', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('rotation_due_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('ip_whitelist', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_terminal_credentials_terminal_id', 'terminal_credentials', ['terminal_id'], unique=True)
    op.create_index('ix_terminal_credentials_status', 'terminal_credentials', ['status'])

    # Create idempotency_keys table
    op.create_table(
        'idempotency_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('idempotency_key', sa.String(length=255), nullable=False),
        sa.Column('request_hash', sa.String(length=64), nullable=False),
        sa.Column('endpoint', sa.String(length=100), nullable=False),
        sa.Column('http_method', sa.String(length=10), nullable=False),
        sa.Column('response_status', sa.Integer(), nullable=False),
        sa.Column('response_body', sa.Text(), nullable=False),
        sa.Column('terminal_id', sa.String(length=50), nullable=True),
        sa.Column('card_uid', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('request_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_idempotency_keys_idempotency_key', 'idempotency_keys', ['idempotency_key'], unique=True)
    op.create_index('ix_idempotency_keys_expires_at', 'idempotency_keys', ['expires_at'])


def downgrade() -> None:
    """Drop tables."""
    op.drop_table('idempotency_keys')
    op.drop_table('terminal_credentials')
