# Data Model: PostgreSQL Database Schema

## Purpose

Define the complete PostgreSQL database schema for the loyalty points system, including all tables, relationships, constraints, indexes, and data types to ensure data integrity, performance, and ACID compliance for multi-channel loyalty operations.

## Scope

### In Scope
- All database tables for loyalty system (customers, cards, transactions, consents, mappings)
- Foreign key relationships and referential integrity
- Primary and composite indexes for query optimization
- Check constraints and data validation rules
- SQL DDL statements for table creation
- Migration scripts for schema updates
- Performance indexes for high-traffic queries
- Audit fields (created_at, updated_at) on all tables

### Out of Scope
- PrestaShop core tables (ps_customer, ps_orders) - managed by PrestaShop
- Aniwin POS database schema (separate system)
- Application-level caching layer (Redis/Memcached)
- Data warehouse or analytics tables (separate OLAP database)
- Archive tables for historical data (future consideration)

## Database Overview

**DBMS**: PostgreSQL 14+  
**Character Set**: UTF-8  
**Collation**: en_US.UTF-8  
**Timezone**: UTC (all timestamps stored in UTC)

### Database Configuration
```sql
-- Database creation
CREATE DATABASE loyalty_system
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

## Core Tables

### 1. customers

Stores customer profiles with PrestaShop linking and contact information.

```sql
CREATE TABLE customers (
    -- Primary identifier
    customer_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- PrestaShop integration
    prestashop_customer_id INTEGER UNIQUE,
    prestashop_email VARCHAR(255) NOT NULL,
    
    -- Personal information
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20),
    language_preference VARCHAR(5) DEFAULT 'es' CHECK (language_preference IN ('es', 'ca', 'en')),
    
    -- Address (optional, synced from PrestaShop)
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    country_code VARCHAR(2) DEFAULT 'ES',
    
    -- Loyalty status
    enrollment_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    account_status VARCHAR(20) NOT NULL DEFAULT 'active' 
        CHECK (account_status IN ('active', 'inactive', 'suspended', 'deleted')),
    
    -- GDPR and consent
    gdpr_consent_date TIMESTAMP WITH TIME ZONE,
    marketing_consent BOOLEAN DEFAULT FALSE,
    whatsapp_consent BOOLEAN DEFAULT FALSE,
    
    -- Duplicate prevention
    email_hash VARCHAR(64) NOT NULL UNIQUE,
    phone_hash VARCHAR(64),
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    
    -- Soft delete
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by VARCHAR(100)
);

-- Indexes for performance
CREATE INDEX idx_customers_prestashop_id ON customers(prestashop_customer_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_customers_email ON customers(prestashop_email) WHERE deleted_at IS NULL;
CREATE INDEX idx_customers_phone ON customers(phone_number) WHERE deleted_at IS NULL;
CREATE INDEX idx_customers_status ON customers(account_status) WHERE deleted_at IS NULL;
CREATE INDEX idx_customers_email_hash ON customers(email_hash);
CREATE INDEX idx_customers_enrollment_date ON customers(enrollment_date DESC);

-- Comments
COMMENT ON TABLE customers IS 'Customer profiles with PrestaShop linking and loyalty enrollment';
COMMENT ON COLUMN customers.email_hash IS 'SHA-256 hash of lowercase email for duplicate detection';
COMMENT ON COLUMN customers.phone_hash IS 'SHA-256 hash of normalized phone for duplicate detection';
```

### 2. cards

Stores NFC loyalty cards with unique identifiers and status tracking.

```sql
CREATE TABLE cards (
    -- Primary identifier
    card_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Card identifiers
    card_uid VARCHAR(14) NOT NULL UNIQUE,
    card_number VARCHAR(20) NOT NULL UNIQUE,
    
    -- QR code for non-NFC devices
    qr_code_url TEXT,
    qr_code_data VARCHAR(255),
    
    -- Card status
    card_status VARCHAR(20) NOT NULL DEFAULT 'inactive' 
        CHECK (card_status IN ('active', 'inactive', 'lost', 'stolen', 'expired', 'replaced')),
    
    -- Customer association
    customer_id UUID REFERENCES customers(customer_id) ON DELETE SET NULL,
    assigned_date TIMESTAMP WITH TIME ZONE,
    unassigned_date TIMESTAMP WITH TIME ZONE,
    
    -- Physical card info
    printing_batch VARCHAR(50),
    printing_date DATE,
    printed_by VARCHAR(100),
    
    -- Card lifecycle
    activated_date TIMESTAMP WITH TIME ZONE,
    expiration_date DATE,
    replacement_card_id UUID REFERENCES cards(card_id) ON DELETE SET NULL,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    
    -- Soft delete
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by VARCHAR(100),
    
    -- Constraints
    CONSTRAINT chk_card_assigned CHECK (
        (customer_id IS NULL AND assigned_date IS NULL) OR
        (customer_id IS NOT NULL AND assigned_date IS NOT NULL)
    )
);

-- Indexes for performance
CREATE INDEX idx_cards_uid ON cards(card_uid) WHERE deleted_at IS NULL;
CREATE INDEX idx_cards_number ON cards(card_number) WHERE deleted_at IS NULL;
CREATE INDEX idx_cards_customer ON cards(customer_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_cards_status ON cards(card_status) WHERE deleted_at IS NULL;
CREATE INDEX idx_cards_printing_batch ON cards(printing_batch);

-- Comments
COMMENT ON TABLE cards IS 'NFC loyalty cards with UID tracking and customer assignment';
COMMENT ON COLUMN cards.card_uid IS 'Unique 7-byte NFC UID in hex format (e.g., 04A1B2C3D4E5F6)';
COMMENT ON COLUMN cards.card_number IS 'Human-readable card number format: LC-XXXXXXXX';
```

### 3. loyalty_accounts

Stores customer loyalty account metadata and cached balance.

```sql
CREATE TABLE loyalty_accounts (
    -- Primary identifier
    account_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Customer linkage
    customer_id UUID NOT NULL UNIQUE REFERENCES customers(customer_id) ON DELETE CASCADE,
    
    -- Balance cache (computed from ledger)
    current_balance_points INTEGER NOT NULL DEFAULT 0 CHECK (current_balance_points >= 0),
    current_balance_eur DECIMAL(10,2) GENERATED ALWAYS AS (current_balance_points / 10000.0) STORED,
    
    -- Lifetime statistics
    lifetime_earned_points INTEGER NOT NULL DEFAULT 0,
    lifetime_redeemed_points INTEGER NOT NULL DEFAULT 0,
    lifetime_expired_points INTEGER NOT NULL DEFAULT 0,
    lifetime_adjusted_points INTEGER NOT NULL DEFAULT 0,
    
    -- Transaction counts
    total_earn_transactions INTEGER NOT NULL DEFAULT 0,
    total_redeem_transactions INTEGER NOT NULL DEFAULT 0,
    
    -- Last activity
    last_earn_date TIMESTAMP WITH TIME ZONE,
    last_redeem_date TIMESTAMP WITH TIME ZONE,
    last_transaction_date TIMESTAMP WITH TIME ZONE,
    
    -- Account metadata
    account_tier VARCHAR(20) DEFAULT 'standard' CHECK (account_tier IN ('standard', 'silver', 'gold', 'platinum')),
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    balance_last_computed_at TIMESTAMP WITH TIME ZONE,
    
    -- Soft delete
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX idx_loyalty_accounts_customer ON loyalty_accounts(customer_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_loyalty_accounts_balance ON loyalty_accounts(current_balance_points DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_loyalty_accounts_last_activity ON loyalty_accounts(last_transaction_date DESC);

-- Comments
COMMENT ON TABLE loyalty_accounts IS 'Loyalty account with cached balance and statistics';
COMMENT ON COLUMN loyalty_accounts.current_balance_points IS 'Cached balance in points (1 point = 0.0001 EUR)';
COMMENT ON COLUMN loyalty_accounts.current_balance_eur IS 'Auto-computed balance in EUR from points';
```

### 4. loyalty_ledger

Immutable append-only ledger of all loyalty point transactions.

```sql
CREATE TABLE loyalty_ledger (
    -- Primary identifier
    ledger_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Sequence for ordering
    ledger_sequence BIGSERIAL NOT NULL UNIQUE,
    
    -- Customer reference
    customer_id UUID NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
    account_id UUID NOT NULL REFERENCES loyalty_accounts(account_id) ON DELETE RESTRICT,
    
    -- Transaction details
    transaction_type VARCHAR(20) NOT NULL 
        CHECK (transaction_type IN ('earn', 'redeem', 'refund', 'adjustment', 'expiration', 'reversal')),
    transaction_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Point movement
    points_delta INTEGER NOT NULL,
    balance_after INTEGER NOT NULL CHECK (balance_after >= 0),
    
    -- Source reference
    source_type VARCHAR(50) NOT NULL 
        CHECK (source_type IN ('pos_sale', 'online_order', 'manual_adjustment', 'expiration_policy', 'refund_reversal', 'migration')),
    source_reference VARCHAR(255),
    order_id VARCHAR(100),
    
    -- Transaction metadata
    order_amount_eur DECIMAL(10,2),
    earn_rate_percent DECIMAL(5,2),
    redemption_rate_percent DECIMAL(5,2),
    
    -- Description and notes
    description TEXT NOT NULL,
    notes TEXT,
    
    -- Expiration tracking
    expiration_date DATE,
    expired_by_ledger_id UUID REFERENCES loyalty_ledger(ledger_id) ON DELETE SET NULL,
    
    -- Idempotency
    idempotency_key VARCHAR(255) UNIQUE,
    
    -- Reversal tracking
    reversed_by_ledger_id UUID REFERENCES loyalty_ledger(ledger_id) ON DELETE SET NULL,
    reverses_ledger_id UUID REFERENCES loyalty_ledger(ledger_id) ON DELETE SET NULL,
    
    -- Terminal/channel
    terminal_id VARCHAR(50),
    channel VARCHAR(20) CHECK (channel IN ('pos', 'online', 'manual', 'system')),
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_by VARCHAR(100) NOT NULL,
    
    -- NO UPDATE/DELETE ALLOWED (immutable ledger)
    -- deleted_at intentionally omitted - entries are never deleted
    
    -- Constraints
    CONSTRAINT chk_ledger_points_delta CHECK (
        (transaction_type IN ('earn', 'refund', 'adjustment') AND points_delta > 0) OR
        (transaction_type IN ('redeem', 'expiration', 'reversal') AND points_delta < 0)
    )
);

-- Indexes for performance
CREATE INDEX idx_loyalty_ledger_customer ON loyalty_ledger(customer_id, ledger_sequence DESC);
CREATE INDEX idx_loyalty_ledger_account ON loyalty_ledger(account_id, transaction_date DESC);
CREATE INDEX idx_loyalty_ledger_transaction_date ON loyalty_ledger(transaction_date DESC);
CREATE INDEX idx_loyalty_ledger_transaction_type ON loyalty_ledger(transaction_type, transaction_date DESC);
CREATE INDEX idx_loyalty_ledger_source_reference ON loyalty_ledger(source_reference) WHERE source_reference IS NOT NULL;
CREATE INDEX idx_loyalty_ledger_order_id ON loyalty_ledger(order_id) WHERE order_id IS NOT NULL;
CREATE INDEX idx_loyalty_ledger_expiration ON loyalty_ledger(expiration_date) WHERE expiration_date IS NOT NULL AND expired_by_ledger_id IS NULL;
CREATE INDEX idx_loyalty_ledger_idempotency ON loyalty_ledger(idempotency_key) WHERE idempotency_key IS NOT NULL;

-- Comments
COMMENT ON TABLE loyalty_ledger IS 'Immutable append-only ledger of all loyalty point transactions';
COMMENT ON COLUMN loyalty_ledger.ledger_sequence IS 'Auto-incrementing sequence for strict ordering';
COMMENT ON COLUMN loyalty_ledger.points_delta IS 'Point change: positive for earn/refund, negative for redeem/expire';
COMMENT ON COLUMN loyalty_ledger.balance_after IS 'Customer balance after this transaction (computed from ledger)';
```

### 5. order_mapping

Maps POS and PrestaShop orders to loyalty transactions for cross-channel tracking.

```sql
CREATE TABLE order_mapping (
    -- Primary identifier
    mapping_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Order identifiers
    order_type VARCHAR(20) NOT NULL CHECK (order_type IN ('pos', 'prestashop')),
    pos_order_id VARCHAR(100),
    prestashop_order_id INTEGER,
    
    -- Order details
    order_date TIMESTAMP WITH TIME ZONE NOT NULL,
    order_total_eur DECIMAL(10,2) NOT NULL,
    order_status VARCHAR(50) NOT NULL,
    
    -- Customer reference
    customer_id UUID REFERENCES customers(customer_id) ON DELETE SET NULL,
    
    -- Loyalty transaction linkage
    earn_ledger_id UUID REFERENCES loyalty_ledger(ledger_id) ON DELETE SET NULL,
    redeem_ledger_id UUID REFERENCES loyalty_ledger(ledger_id) ON DELETE SET NULL,
    refund_ledger_id UUID REFERENCES loyalty_ledger(ledger_id) ON DELETE SET NULL,
    
    -- Points earned/redeemed
    points_earned INTEGER DEFAULT 0,
    points_redeemed INTEGER DEFAULT 0,
    points_refunded INTEGER DEFAULT 0,
    
    -- Channel info
    terminal_id VARCHAR(50),
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('pos', 'online')),
    
    -- Sync status
    sync_status VARCHAR(20) DEFAULT 'pending' 
        CHECK (sync_status IN ('pending', 'synced', 'failed', 'reconciled')),
    last_sync_at TIMESTAMP WITH TIME ZONE,
    sync_error TEXT,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_order_id CHECK (
        (order_type = 'pos' AND pos_order_id IS NOT NULL) OR
        (order_type = 'prestashop' AND prestashop_order_id IS NOT NULL)
    ),
    CONSTRAINT uk_pos_order UNIQUE (pos_order_id),
    CONSTRAINT uk_prestashop_order UNIQUE (prestashop_order_id)
);

-- Indexes for performance
CREATE INDEX idx_order_mapping_customer ON order_mapping(customer_id, order_date DESC);
CREATE INDEX idx_order_mapping_pos_order ON order_mapping(pos_order_id) WHERE pos_order_id IS NOT NULL;
CREATE INDEX idx_order_mapping_prestashop_order ON order_mapping(prestashop_order_id) WHERE prestashop_order_id IS NOT NULL;
CREATE INDEX idx_order_mapping_earn_ledger ON order_mapping(earn_ledger_id) WHERE earn_ledger_id IS NOT NULL;
CREATE INDEX idx_order_mapping_order_date ON order_mapping(order_date DESC);
CREATE INDEX idx_order_mapping_sync_status ON order_mapping(sync_status) WHERE sync_status != 'synced';

-- Comments
COMMENT ON TABLE order_mapping IS 'Mapping between POS/PrestaShop orders and loyalty transactions';
COMMENT ON COLUMN order_mapping.pos_order_id IS 'Aniwin POS order reference (e.g., POS-2025-02-15-0042)';
COMMENT ON COLUMN order_mapping.prestashop_order_id IS 'PrestaShop order ID from ps_orders table';
```

### 6. consent_records

GDPR consent tracking for loyalty program and marketing communications.

```sql
CREATE TABLE consent_records (
    -- Primary identifier
    consent_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Customer reference
    customer_id UUID NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    
    -- Consent type
    consent_type VARCHAR(50) NOT NULL 
        CHECK (consent_type IN ('loyalty_program', 'marketing_email', 'marketing_sms', 'marketing_whatsapp', 'data_processing')),
    
    -- Consent status
    consent_given BOOLEAN NOT NULL,
    consent_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Consent metadata
    consent_method VARCHAR(50) NOT NULL 
        CHECK (consent_method IN ('pos_enrollment', 'online_signup', 'email_link', 'account_settings', 'customer_service')),
    consent_ip_address INET,
    consent_user_agent TEXT,
    
    -- Withdrawal tracking
    withdrawn BOOLEAN NOT NULL DEFAULT FALSE,
    withdrawal_date TIMESTAMP WITH TIME ZONE,
    withdrawal_method VARCHAR(50) CHECK (withdrawal_method IN ('account_settings', 'email_link', 'customer_service', 'right_to_be_forgotten')),
    
    -- Audit trail
    consent_version VARCHAR(20) NOT NULL,
    consent_text TEXT NOT NULL,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_by VARCHAR(100),
    
    -- NO UPDATE - audit trail is immutable
    -- NO DELETE - consent records must be retained for GDPR compliance
    
    -- Constraints
    CONSTRAINT chk_consent_withdrawal CHECK (
        (withdrawn = FALSE AND withdrawal_date IS NULL) OR
        (withdrawn = TRUE AND withdrawal_date IS NOT NULL)
    )
);

-- Indexes for performance
CREATE INDEX idx_consent_customer ON consent_records(customer_id, consent_date DESC);
CREATE INDEX idx_consent_type_status ON consent_records(consent_type, consent_given, withdrawn);
CREATE INDEX idx_consent_withdrawal ON consent_records(withdrawal_date DESC) WHERE withdrawn = TRUE;

-- Comments
COMMENT ON TABLE consent_records IS 'GDPR consent audit trail for loyalty and marketing';
COMMENT ON COLUMN consent_records.consent_version IS 'Version of consent form/policy (e.g., v1.0, v2.1)';
COMMENT ON COLUMN consent_records.consent_text IS 'Full text of consent given (for audit purposes)';
```

### 7. idempotency_keys

Ensures exactly-once processing of duplicate requests.

```sql
CREATE TABLE idempotency_keys (
    -- Primary identifier
    key_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Idempotency key
    idempotency_key VARCHAR(255) NOT NULL UNIQUE,
    
    -- Request metadata
    request_type VARCHAR(50) NOT NULL 
        CHECK (request_type IN ('earn_points', 'redeem_points', 'refund_transaction', 'manual_adjustment')),
    customer_id UUID REFERENCES customers(customer_id) ON DELETE CASCADE,
    
    -- Response caching
    request_payload JSONB NOT NULL,
    response_status INTEGER NOT NULL,
    response_payload JSONB,
    
    -- Processing state
    processing_status VARCHAR(20) NOT NULL DEFAULT 'processing' 
        CHECK (processing_status IN ('processing', 'completed', 'failed')),
    
    -- Result reference
    ledger_id UUID REFERENCES loyalty_ledger(ledger_id) ON DELETE SET NULL,
    
    -- Expiration (keys expire after 24 hours)
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() + INTERVAL '24 hours'),
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_idempotency_key ON idempotency_keys(idempotency_key) WHERE processing_status = 'completed';
CREATE INDEX idx_idempotency_expires ON idempotency_keys(expires_at) WHERE expires_at < NOW();
CREATE INDEX idx_idempotency_customer ON idempotency_keys(customer_id, created_at DESC);

-- Comments
COMMENT ON TABLE idempotency_keys IS 'Ensures exactly-once processing of duplicate requests';
COMMENT ON COLUMN idempotency_keys.idempotency_key IS 'Client-provided or system-generated unique key';
```

## Database Functions and Triggers

### Auto-update timestamp trigger

```sql
-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cards_updated_at BEFORE UPDATE ON cards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_loyalty_accounts_updated_at BEFORE UPDATE ON loyalty_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_order_mapping_updated_at BEFORE UPDATE ON order_mapping
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_idempotency_keys_updated_at BEFORE UPDATE ON idempotency_keys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Email hash generation trigger

```sql
-- Function to generate email hash
CREATE OR REPLACE FUNCTION generate_email_hash()
RETURNS TRIGGER AS $$
BEGIN
    NEW.email_hash = encode(digest(lower(trim(NEW.prestashop_email)), 'sha256'), 'hex');
    IF NEW.phone_number IS NOT NULL THEN
        NEW.phone_hash = encode(digest(regexp_replace(NEW.phone_number, '[^0-9]', '', 'g'), 'sha256'), 'hex');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to customers table
CREATE TRIGGER generate_customer_hashes BEFORE INSERT OR UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION generate_email_hash();
```

### Prevent ledger UPDATE/DELETE

```sql
-- Function to prevent ledger modification
CREATE OR REPLACE FUNCTION prevent_ledger_modification()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'DELETE not allowed on loyalty_ledger (immutable ledger)';
    ELSIF TG_OP = 'UPDATE' THEN
        RAISE EXCEPTION 'UPDATE not allowed on loyalty_ledger (immutable ledger)';
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to ledger
CREATE TRIGGER prevent_ledger_update BEFORE UPDATE ON loyalty_ledger
    FOR EACH ROW EXECUTE FUNCTION prevent_ledger_modification();

CREATE TRIGGER prevent_ledger_delete BEFORE DELETE ON loyalty_ledger
    FOR EACH ROW EXECUTE FUNCTION prevent_ledger_modification();
```

## Migration Scripts

### Migration 001: Initial schema

```sql
-- migrations/001_initial_schema.sql
BEGIN;

-- Create all tables in order (dependencies first)
\i create_customers.sql
\i create_cards.sql
\i create_loyalty_accounts.sql
\i create_loyalty_ledger.sql
\i create_order_mapping.sql
\i create_consent_records.sql
\i create_idempotency_keys.sql

-- Create indexes
\i create_indexes.sql

-- Create triggers
\i create_triggers.sql

-- Insert migration record
INSERT INTO schema_migrations (version, applied_at) VALUES ('001', NOW());

COMMIT;
```

### Migration 002: Add card QR code support

```sql
-- migrations/002_add_card_qr_code.sql
BEGIN;

ALTER TABLE cards
    ADD COLUMN IF NOT EXISTS qr_code_url TEXT,
    ADD COLUMN IF NOT EXISTS qr_code_data VARCHAR(255);

CREATE INDEX idx_cards_qr_code ON cards(qr_code_data) WHERE qr_code_data IS NOT NULL;

INSERT INTO schema_migrations (version, applied_at) VALUES ('002', NOW());

COMMIT;
```

## Common Queries

### Query 1: Get customer balance

```sql
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    la.current_balance_points,
    la.current_balance_eur,
    la.last_transaction_date
FROM customers c
JOIN loyalty_accounts la ON la.customer_id = c.customer_id
WHERE c.prestashop_customer_id = $1
    AND c.deleted_at IS NULL;
```

### Query 2: Get transaction history

```sql
SELECT 
    ll.ledger_id,
    ll.transaction_date,
    ll.transaction_type,
    ll.points_delta,
    ll.balance_after,
    ll.description,
    ll.order_amount_eur,
    ll.source_reference
FROM loyalty_ledger ll
WHERE ll.customer_id = $1
ORDER BY ll.ledger_sequence DESC
LIMIT 50;
```

### Query 3: Find customer by card UID

```sql
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    c.prestashop_email,
    c.phone_number,
    card.card_number,
    la.current_balance_points
FROM cards card
JOIN customers c ON c.customer_id = card.customer_id
JOIN loyalty_accounts la ON la.customer_id = c.customer_id
WHERE card.card_uid = $1
    AND card.card_status = 'active'
    AND c.deleted_at IS NULL;
```

### Query 4: Get expiring points

```sql
SELECT 
    ll.customer_id,
    c.first_name,
    c.last_name,
    SUM(ll.points_delta) AS points_expiring,
    ll.expiration_date
FROM loyalty_ledger ll
JOIN customers c ON c.customer_id = ll.customer_id
WHERE ll.expiration_date BETWEEN NOW() AND NOW() + INTERVAL '30 days'
    AND ll.expired_by_ledger_id IS NULL
    AND ll.transaction_type = 'earn'
GROUP BY ll.customer_id, c.first_name, c.last_name, ll.expiration_date
ORDER BY ll.expiration_date ASC;
```

### Query 5: Compute balance from ledger

```sql
SELECT 
    customer_id,
    SUM(points_delta) AS computed_balance
FROM loyalty_ledger
WHERE customer_id = $1
GROUP BY customer_id;
```

### Query 6: Get orders with loyalty activity

```sql
SELECT 
    om.order_type,
    COALESCE(om.pos_order_id, om.prestashop_order_id::TEXT) AS order_reference,
    om.order_date,
    om.order_total_eur,
    om.points_earned,
    om.points_redeemed,
    ll_earn.transaction_date AS earn_transaction_date,
    ll_redeem.transaction_date AS redeem_transaction_date
FROM order_mapping om
LEFT JOIN loyalty_ledger ll_earn ON ll_earn.ledger_id = om.earn_ledger_id
LEFT JOIN loyalty_ledger ll_redeem ON ll_redeem.ledger_id = om.redeem_ledger_id
WHERE om.customer_id = $1
ORDER BY om.order_date DESC
LIMIT 20;
```

## Performance Optimization

### Partition loyalty_ledger by date

```sql
-- Partition ledger by month for performance
CREATE TABLE loyalty_ledger_partitioned (
    LIKE loyalty_ledger INCLUDING ALL
) PARTITION BY RANGE (transaction_date);

-- Create monthly partitions
CREATE TABLE loyalty_ledger_2025_01 PARTITION OF loyalty_ledger_partitioned
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE loyalty_ledger_2025_02 PARTITION OF loyalty_ledger_partitioned
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- Add partitions automatically
CREATE OR REPLACE FUNCTION create_monthly_partition()
RETURNS void AS $$
DECLARE
    partition_date DATE;
    partition_name TEXT;
    start_date TEXT;
    end_date TEXT;
BEGIN
    partition_date := DATE_TRUNC('month', NOW() + INTERVAL '1 month');
    partition_name := 'loyalty_ledger_' || TO_CHAR(partition_date, 'YYYY_MM');
    start_date := partition_date::TEXT;
    end_date := (partition_date + INTERVAL '1 month')::TEXT;
    
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF loyalty_ledger_partitioned FOR VALUES FROM (%L) TO (%L)',
        partition_name, start_date, end_date
    );
END;
$$ LANGUAGE plpgsql;
```

## Data Integrity Rules

### Rule 1: No orphaned cards
All active cards must be assigned to a customer.

### Rule 2: Balance consistency
The `loyalty_accounts.current_balance_points` must equal `SUM(loyalty_ledger.points_delta)` for that customer.

### Rule 3: No negative balances
Customer balance can never go negative (enforced by CHECK constraint).

### Rule 4: Immutable ledger
No UPDATE or DELETE on `loyalty_ledger` (enforced by trigger).

### Rule 5: Idempotency
All point-changing operations must use idempotency keys to prevent duplicates.

### Rule 6: GDPR retention
Consent records are never deleted (retained for legal compliance).

## Backup and Recovery

### Daily backup script

```bash
#!/bin/bash
# backup_loyalty_db.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/loyalty"
DB_NAME="loyalty_system"

# Full database backup
pg_dump -U postgres -d $DB_NAME -F c -f "$BACKUP_DIR/loyalty_full_$TIMESTAMP.dump"

# Compressed SQL backup
pg_dump -U postgres -d $DB_NAME | gzip > "$BACKUP_DIR/loyalty_sql_$TIMESTAMP.sql.gz"

# Retention: keep last 30 days
find $BACKUP_DIR -name "loyalty_*.dump" -mtime +30 -delete
find $BACKUP_DIR -name "loyalty_*.sql.gz" -mtime +30 -delete
```

### Point-in-time recovery

```sql
-- Enable WAL archiving in postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /archive/%f'
```

## Related Documents

### Dependencies
- `02_architecture/CLOUD_BACKEND.md` - Backend database access layer
- `02_architecture/DATABASE_DESIGN.md` - Database architecture and scaling
- `06_security/DATA_ENCRYPTION.md` - Encryption at rest and in transit
- `06_security/GDPR_COMPLIANCE.md` - GDPR data handling requirements

### Dependents
- `05_data/LOYALTY_LEDGER.md` - Detailed ledger transaction rules
- `05_data/CUSTOMER_MODEL.md` - Customer entity details
- `05_data/CARD_MODEL.md` - Card entity details
- `05_data/ORDER_MAPPING.md` - Order mapping details
- `05_data/CONSENT_RECORDS.md` - Consent tracking details

### Related Features
- `03_features/EARN_POINTS_POS.md` - Inserts into loyalty_ledger
- `03_features/REDEEM_POINTS_POS.md` - Inserts into loyalty_ledger
- `03_features/CARD_ENROLLMENT.md` - Creates customer and card records
- `03_features/BALANCE_QUERY.md` - Queries loyalty_accounts and loyalty_ledger
- `03_features/MANUAL_ADJUSTMENTS.md` - Inserts adjustment transactions

### Integration Points
- `04_integrations/PRESTASHOP_MODULE.md` - Syncs customer data from ps_customer
- `04_integrations/POS_WINDOWS_AGENT.md` - Local SQLite mirrors subset of schema
- `07_operations/MONITORING.md` - Database performance monitoring

## Open Questions / TODOs

### TODO: Archive old transactions
**Status**: Not implemented  
**Required by**: When ledger exceeds 10M rows  
**Description**: Archive transactions older than 5 years to separate table

### TODO: Multi-region replication
**Status**: Future consideration  
**Required by**: If expanding to multiple countries  
**Description**: PostgreSQL streaming replication for disaster recovery

### Open Question: Partition strategy
**Question**: Should we partition loyalty_ledger by customer_id or transaction_date?  
**Context**: Customer_id gives better isolation, date gives easier archival  
**Decision Required By**: Before reaching 5M transactions
