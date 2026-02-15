# Database Migrations - Loyalty System

This directory contains PostgreSQL database migrations for the Fidelity Points loyalty system. Migrations are versioned SQL scripts that create and modify the database schema in a controlled, reproducible manner.

## Overview

The loyalty system uses PostgreSQL 14+ as its database management system. The schema includes:
- **customers**: Customer profiles with PrestaShop linking
- **cards**: NFC loyalty cards with UID tracking
- **loyalty_accounts**: Account metadata and cached balances
- **loyalty_ledger**: Immutable transaction ledger (append-only, audit-compliant)
- **order_mapping**: Links between POS/PrestaShop orders and loyalty transactions
- **consent_records**: GDPR consent tracking and audit trail
- **idempotency_keys**: Duplicate request prevention
- **schema_migrations**: Migration version tracking

## Directory Structure

```
database/
├── README.md                       # This file
├── run_migrations.sh               # Automated migration runner script
├── test_data.sql                   # Sample test data for validation
└── migrations/
    ├── 001_initial_schema.sql      # Initial database schema
    └── 001_rollback.sql            # Rollback for migration 001
```

## Requirements

- PostgreSQL 14 or higher
- PostgreSQL client tools (`psql`, `pg_dump`)
- Extensions: `uuid-ossp`, `pgcrypto`
- Database user with CREATE/DROP privileges

## Quick Start

### 1. Set Environment Variables

```bash
export LOYALTY_DB_HOST=localhost          # Database host (default: localhost)
export LOYALTY_DB_PORT=5432               # Database port (default: 5432)
export LOYALTY_DB_NAME=loyalty_system     # Database name
export LOYALTY_DB_USER=postgres           # Database user
export LOYALTY_DB_PASSWORD=your_password  # Database password
```

### 2. Run Migrations (Recommended)

The migration script automatically creates the database if it doesn't exist:

```bash
cd "Points System/07_operations/database"
chmod +x run_migrations.sh
./run_migrations.sh
```

For test database:
```bash
./run_migrations.sh --test  # Uses ${LOYALTY_DB_NAME}_test
```

### 3. Load Test Data (Optional)

```bash
psql -h $LOYALTY_DB_HOST -p $LOYALTY_DB_PORT -U $LOYALTY_DB_USER -d $LOYALTY_DB_NAME \
    -f test_data.sql
```

## Migration Files

- **001_initial_schema.sql**: Initial database schema with all core tables, indexes, triggers, and functions
- **001_rollback.sql**: Rollback script to undo migration 001 (drops all tables)
- **test_data.sql**: Sample test data (3 customers, 4 cards, 6 transactions)

## Schema Features

### Core Tables (8 total)

1. **customers** - Customer profiles with PrestaShop linking (UUID primary key)
2. **cards** - NFC loyalty cards with 7-byte UID tracking
3. **loyalty_accounts** - Customer loyalty account with cached balance
4. **loyalty_ledger** - Immutable append-only transaction log (34+ fields)
5. **order_mapping** - Links POS/PrestaShop orders to loyalty transactions
6. **consent_records** - GDPR consent audit trail (never deleted)
7. **idempotency_keys** - Ensures exactly-once processing (24-hour expiry)
8. **schema_migrations** - Tracks applied migrations

### Key Features

- **UUID Primary Keys**: All tables use UUID v4 for primary identifiers
- **Immutable Ledger**: `loyalty_ledger` cannot be updated or deleted (enforced by triggers)
- **Audit Fields**: All tables have `created_at`, `updated_at`, `created_by`, `updated_by`
- **Soft Delete**: Customer and card records use soft delete (`deleted_at`)
- **Timestamp Timezone**: All timestamps stored in UTC with timezone
- **Duplicate Prevention**: Email and phone hashes prevent duplicate customers
- **Foreign Key Constraints**: Referential integrity enforced at database level
- **Optimized Indexes**: 34 indexes for query performance
- **Automatic Triggers**: Email hash generation, updated_at, ledger protection

### Immutable Ledger

The `loyalty_ledger` table is append-only. UPDATE and DELETE operations are blocked by database triggers to ensure transaction immutability and audit compliance.

```sql
-- This will fail with: "UPDATE not allowed on loyalty_ledger (immutable ledger)"
UPDATE loyalty_ledger SET points_delta = 1000 WHERE ledger_id = '...';
```

### Automatic Triggers

- **update_updated_at_column()**: Automatically updates timestamp on row modification
- **generate_email_hash()**: Generates SHA-256 hashes for duplicate detection
- **prevent_ledger_modification()**: Prevents modifications to the immutable ledger

### Data Integrity

- **Foreign key constraints**: Ensure referential integrity across tables
- **Check constraints**: Enforce business rules (e.g., non-negative balances, valid statuses)
- **Unique constraints**: Prevent duplicate records (email hash, card UID, card number)
- **NOT NULL constraints**: Ensure required fields are always populated

## Rollback Migrations

To rollback a migration:

```bash
# ⚠️ WARNING: This will DROP ALL TABLES and DELETE ALL DATA
# Always backup before rollback!

# Create backup first
pg_dump -h $LOYALTY_DB_HOST -U $LOYALTY_DB_USER -d $LOYALTY_DB_NAME \
    -F c -f "backup_$(date +%Y%m%d_%H%M%S).dump"

# Then rollback
psql -h $LOYALTY_DB_HOST -p $LOYALTY_DB_PORT -U $LOYALTY_DB_USER -d $LOYALTY_DB_NAME \
    -f migrations/001_rollback.sql
```

## Verification Queries

### Check Applied Migrations

```sql
SELECT version, applied_at, description 
FROM schema_migrations 
ORDER BY version;
```

### Count Tables and Indexes

```sql
-- Count tables
SELECT COUNT(*) AS table_count
FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

-- Count indexes
SELECT COUNT(*) AS index_count
FROM pg_indexes 
WHERE schemaname = 'public';
```

### Verify Ledger Immutability

```sql
-- This should fail with: "UPDATE not allowed on loyalty_ledger (immutable ledger)"
UPDATE loyalty_ledger SET points_delta = 1000 
WHERE ledger_id = (SELECT ledger_id FROM loyalty_ledger LIMIT 1);
```

### Check Foreign Key Constraints

```sql
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name;
```

### Verify Customer Balances Match Ledger

```sql
-- Should return 0 rows (all balances match ledger)
SELECT 
    c.first_name || ' ' || c.last_name AS customer_name,
    la.current_balance_points AS cached_balance,
    SUM(ll.points_delta) AS computed_balance
FROM customers c
JOIN loyalty_accounts la ON la.customer_id = c.customer_id
JOIN loyalty_ledger ll ON ll.customer_id = c.customer_id
WHERE c.deleted_at IS NULL
GROUP BY c.customer_id, c.first_name, c.last_name, la.current_balance_points
HAVING la.current_balance_points != SUM(ll.points_delta);
```

## Test Data

The `test_data.sql` file includes:

- **3 Customers**: María García (POS), John Smith (PrestaShop), Jordi Puig (inactive)
- **4 Cards**: 2 active, 1 inactive, 1 lost
- **3 Loyalty Accounts**: With various balance levels
- **6 Ledger Transactions**: Earn, redeem, and adjustment examples
- **3 Consent Records**: Loyalty program and marketing consents
- **3 Order Mappings**: POS and PrestaShop order examples

After loading test data, verify with:

```sql
-- Show summary
SELECT 'Customers' AS entity, COUNT(*) AS count FROM customers
UNION ALL SELECT 'Cards', COUNT(*) FROM cards
UNION ALL SELECT 'Ledger Transactions', COUNT(*) FROM loyalty_ledger
UNION ALL SELECT 'Order Mappings', COUNT(*) FROM order_mapping;

-- Show customer balances
SELECT 
    c.first_name || ' ' || c.last_name AS customer,
    la.current_balance_eur AS balance_eur,
    la.total_earn_transactions AS earns,
    la.total_redeem_transactions AS redeems
FROM customers c
JOIN loyalty_accounts la ON la.customer_id = c.customer_id
ORDER BY la.current_balance_points DESC;
```

## Backup and Restore

### Backup
```bash
pg_dump -U postgres -d loyalty_system -F c -f loyalty_backup_$(date +%Y%m%d).dump
```

### Restore
```bash
pg_restore -U postgres -d loyalty_system -c loyalty_backup_20260213.dump
```

## Security Notes

1. **Never commit database credentials** to version control
2. Use environment variables or secrets management for credentials
3. Enable SSL/TLS for database connections in production
4. Restrict database user permissions (principle of least privilege)
5. Regular backups with encryption

## Related Documentation

- `../../../05_data/DATA_MODEL.md`: Complete data model specification
- `../../../02_architecture/SYSTEM_ARCHITECTURE.md`: System architecture
- `../../../06_security/SECURITY_MODEL.md`: Security requirements

## Troubleshooting

### Extension Not Found
```bash
# Install PostgreSQL contrib package
sudo apt-get install postgresql-contrib

# Then create extensions
psql -U postgres -d loyalty_system -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
psql -U postgres -d loyalty_system -c "CREATE EXTENSION IF NOT EXISTS \"pgcrypto\";"
```

### Permission Denied
```bash
# Grant necessary permissions
psql -U postgres -d loyalty_system -c "GRANT ALL PRIVILEGES ON DATABASE loyalty_system TO your_user;"
psql -U postgres -d loyalty_system -c "GRANT ALL ON ALL TABLES IN SCHEMA public TO your_user;"
```

### Migration Already Applied
Migrations track their status in the `schema_migrations` table. If a migration is already applied, it will be skipped automatically.
