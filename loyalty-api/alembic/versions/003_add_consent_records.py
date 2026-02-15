"""Add consent records and update card model

Revision ID: 003
Revises: 002
Create Date: 2026-02-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create consent_records table
    op.create_table(
        'consent_records',
        sa.Column('consent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('consent_type', sa.String(length=50), nullable=False),
        sa.Column('consent_given', sa.Boolean(), nullable=False),
        sa.Column('consent_date', sa.DateTime(), nullable=False),
        sa.Column('consent_method', sa.String(length=50), nullable=False),
        sa.Column('consent_ip_address', sa.String(length=45), nullable=True),
        sa.Column('consent_user_agent', sa.Text(), nullable=True),
        sa.Column('withdrawn', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('withdrawal_date', sa.DateTime(), nullable=True),
        sa.Column('withdrawal_method', sa.String(length=50), nullable=True),
        sa.Column('consent_version', sa.String(length=20), nullable=False, server_default='v1.0'),
        sa.Column('consent_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.CheckConstraint(
            "(withdrawn = false AND withdrawal_date IS NULL AND withdrawal_method IS NULL) OR "
            "(withdrawn = true AND withdrawal_date IS NOT NULL AND withdrawal_method IS NOT NULL)",
            name='chk_consent_withdrawal'
        ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.customer_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('consent_id')
    )
    op.create_index(op.f('ix_consent_records_customer_id'), 'consent_records', ['customer_id'], unique=False)
    op.create_index(op.f('ix_consent_records_consent_type'), 'consent_records', ['consent_type'], unique=False)
    
    # Add assigned_date column to loyalty_cards
    op.add_column('loyalty_cards', sa.Column('assigned_date', sa.DateTime(), nullable=True))
    
    # Make customer_id nullable for unassigned cards
    # Note: This requires handling existing data
    # First, ensure all existing cards have a customer_id or set status to inactive
    op.execute("""
        UPDATE loyalty_cards 
        SET status = 'inactive' 
        WHERE customer_id IS NULL
    """)
    
    # Now we can alter the column
    op.alter_column('loyalty_cards', 'customer_id',
                    existing_type=postgresql.UUID(),
                    nullable=True)
    
    # Update default status for new cards
    op.alter_column('loyalty_cards', 'status',
                    existing_type=sa.VARCHAR(length=20),
                    server_default='inactive')


def downgrade() -> None:
    # Revert loyalty_cards changes
    op.alter_column('loyalty_cards', 'status',
                    existing_type=sa.VARCHAR(length=20),
                    server_default='active')
    
    op.alter_column('loyalty_cards', 'customer_id',
                    existing_type=postgresql.UUID(),
                    nullable=False)
    
    op.drop_column('loyalty_cards', 'assigned_date')
    
    # Drop consent_records table
    op.drop_index(op.f('ix_consent_records_consent_type'), table_name='consent_records')
    op.drop_index(op.f('ix_consent_records_customer_id'), table_name='consent_records')
    op.drop_table('consent_records')
