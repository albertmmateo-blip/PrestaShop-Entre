"""Add loyalty system tables

Revision ID: 002
Revises: 001
Create Date: 2026-02-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create loyalty system tables."""
    
    # Create customers table
    op.create_table(
        'customers',
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('prestashop_customer_id', sa.Integer(), nullable=True),
        sa.Column('consent_loyalty', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('consent_marketing', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('language', sa.String(length=10), nullable=False, server_default='es'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('customer_id')
    )
    op.create_index('ix_customers_prestashop_customer_id', 'customers', ['prestashop_customer_id'])
    
    # Create loyalty_accounts table
    op.create_table(
        'loyalty_accounts',
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('current_balance_points', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('current_balance_euros', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('total_earned_points', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_redeemed_points', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_transaction_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('account_id'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.customer_id'], ondelete='CASCADE'),
        sa.UniqueConstraint('customer_id')
    )
    
    # Create loyalty_cards table
    op.create_table(
        'loyalty_cards',
        sa.Column('card_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('card_uid', sa.String(length=20), nullable=False),
        sa.Column('card_number', sa.String(length=50), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('issued_date', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('card_id'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.customer_id'], ondelete='CASCADE'),
        sa.UniqueConstraint('card_uid'),
        sa.UniqueConstraint('card_number')
    )
    op.create_index('ix_loyalty_cards_card_uid', 'loyalty_cards', ['card_uid'], unique=True)
    op.create_index('ix_loyalty_cards_status', 'loyalty_cards', ['status'])
    
    # Create loyalty_ledger table (immutable)
    op.create_table(
        'loyalty_ledger',
        sa.Column('ledger_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ledger_sequence', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_type', sa.String(length=20), nullable=False),
        sa.Column('transaction_date', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('points_delta', sa.Integer(), nullable=False),
        sa.Column('balance_after', sa.Integer(), nullable=False),
        sa.Column('amount_euros', sa.Numeric(10, 2), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('source_reference', sa.String(length=255), nullable=True),
        sa.Column('order_id', sa.String(length=100), nullable=True),
        sa.Column('order_amount_eur', sa.Numeric(10, 2), nullable=True),
        sa.Column('earn_rate_percent', sa.Numeric(5, 2), nullable=True),
        sa.Column('redemption_rate_percent', sa.Numeric(5, 2), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('expiration_date', sa.Date(), nullable=True),
        sa.Column('expired_by_ledger_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('idempotency_key', sa.String(length=255), nullable=True),
        sa.Column('reversed_by_ledger_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reverses_ledger_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('terminal_id', sa.String(length=50), nullable=True),
        sa.Column('channel', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('ledger_id'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.customer_id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['account_id'], ['loyalty_accounts.account_id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['expired_by_ledger_id'], ['loyalty_ledger.ledger_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['reversed_by_ledger_id'], ['loyalty_ledger.ledger_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['reverses_ledger_id'], ['loyalty_ledger.ledger_id'], ondelete='SET NULL'),
        sa.CheckConstraint(
            """
            (transaction_type IN ('earn', 'adjustment') AND points_delta > 0) OR
            (transaction_type IN ('redeem', 'refund', 'expiration', 'reversal') AND points_delta <= 0)
            """,
            name='chk_ledger_points_delta'
        ),
        sa.CheckConstraint('balance_after >= 0', name='chk_balance_non_negative'),
        sa.CheckConstraint(
            "transaction_type IN ('earn', 'redeem', 'refund', 'adjustment', 'expiration', 'reversal')",
            name='chk_transaction_type'
        ),
        sa.CheckConstraint(
            "source_type IN ('pos_sale', 'online_order', 'manual_adjustment', 'expiration_policy', 'refund_reversal', 'migration')",
            name='chk_source_type'
        ),
        sa.CheckConstraint(
            "channel IN ('pos', 'online', 'manual', 'system')",
            name='chk_channel'
        )
    )
    
    # Indexes for loyalty_ledger
    op.create_index('ix_loyalty_ledger_ledger_sequence', 'loyalty_ledger', ['ledger_sequence'], unique=True)
    op.create_index('ix_loyalty_ledger_customer_id', 'loyalty_ledger', ['customer_id'])
    op.create_index('ix_loyalty_ledger_transaction_type', 'loyalty_ledger', ['transaction_type'])
    op.create_index('ix_loyalty_ledger_order_id', 'loyalty_ledger', ['order_id'])
    op.create_index('ix_loyalty_ledger_idempotency_key', 'loyalty_ledger', ['idempotency_key'], unique=True)
    op.create_index('ix_loyalty_ledger_customer_sequence', 'loyalty_ledger', ['customer_id', 'ledger_sequence'])
    
    # Create trigger to prevent UPDATE/DELETE on loyalty_ledger (immutability)
    op.execute("""
        CREATE OR REPLACE FUNCTION prevent_ledger_modification()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_OP = 'DELETE' THEN
                RAISE EXCEPTION 'DELETE not allowed on loyalty_ledger (immutable ledger)';
            ELSIF TG_OP = 'UPDATE' THEN
                -- Allow updates only to expired_by_ledger_id and reversed_by_ledger_id (for linking)
                IF (OLD.expired_by_ledger_id IS DISTINCT FROM NEW.expired_by_ledger_id) OR
                   (OLD.reversed_by_ledger_id IS DISTINCT FROM NEW.reversed_by_ledger_id) THEN
                    RETURN NEW;
                ELSE
                    RAISE EXCEPTION 'UPDATE not allowed on loyalty_ledger except for expired_by and reversed_by fields';
                END IF;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        CREATE TRIGGER prevent_ledger_update 
        BEFORE UPDATE ON loyalty_ledger
        FOR EACH ROW EXECUTE FUNCTION prevent_ledger_modification();
    """)
    
    op.execute("""
        CREATE TRIGGER prevent_ledger_delete 
        BEFORE DELETE ON loyalty_ledger
        FOR EACH ROW EXECUTE FUNCTION prevent_ledger_modification();
    """)


def downgrade() -> None:
    """Drop loyalty system tables."""
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS prevent_ledger_delete ON loyalty_ledger;")
    op.execute("DROP TRIGGER IF EXISTS prevent_ledger_update ON loyalty_ledger;")
    op.execute("DROP FUNCTION IF EXISTS prevent_ledger_modification();")
    
    # Drop tables (in reverse order due to foreign keys)
    op.drop_table('loyalty_ledger')
    op.drop_table('loyalty_cards')
    op.drop_table('loyalty_accounts')
    op.drop_table('customers')
