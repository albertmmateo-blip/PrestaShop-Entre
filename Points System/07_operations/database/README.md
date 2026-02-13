# Loyalty System Database Setup

This directory contains the database schema and migration scripts for the Fidelity Points loyalty system.

## Overview

The loyalty system uses PostgreSQL 14+ as its database management system. The schema includes:
- **customers**: Customer profiles with PrestaShop linking
- **cards**: NFC loyalty cards
- **loyalty_accounts**: Account metadata and cached balances
- **loyalty_ledger**: Immutable transaction ledger (append-only)
- **order_mapping**: Links between POS/PrestaShop orders and loyalty transactions
- **consent_records**: GDPR consent tracking
- **idempotency_keys**: Duplicate request prevention

## Requirements

- PostgreSQL 14 or higher
- Extensions: `uuid-ossp`, `pgcrypto`

## Quick Start

### 1. Create Database

```bash
# Using psql
psql -U postgres -c "CREATE DATABASE loyalty_system WITH ENCODING='UTF8' LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8' TEMPLATE=template0;"
```

### 2. Run Migrations

```bash
# Run initial schema migration
psql -U postgres -d loyalty_system -f migrations/001_initial_schema.sql
```

Or use the provided migration script:

```bash
# Make script executable
chmod +x run_migrations.sh

# Run all migrations
./run_migrations.sh
```

## Migration Files

- `001_initial_schema.sql`: Initial database schema with all core tables, indexes, triggers, and functions

## Schema Features

### Immutable Ledger
The `loyalty_ledger` table is append-only. UPDATE and DELETE operations are blocked by database triggers to ensure transaction immutability and audit compliance.

### Automatic Triggers
- **updated_at**: Automatically updates timestamp on row modification
- **email_hash**: Generates SHA-256 hashes for duplicate detection
- **ledger_protection**: Prevents modifications to the immutable ledger

### Data Integrity
- Foreign key constraints ensure referential integrity
- Check constraints enforce business rules (e.g., non-negative balances)
- Unique constraints prevent duplicate records

## Environment Variables

Set these variables before running migrations:

```bash
export LOYALTY_DB_HOST=localhost
export LOYALTY_DB_PORT=5432
export LOYALTY_DB_NAME=loyalty_system
export LOYALTY_DB_USER=postgres
export LOYALTY_DB_PASSWORD=your_secure_password
```

## Testing the Schema

After running migrations, verify the schema:

```bash
# List all tables
psql -U postgres -d loyalty_system -c "\dt"

# Verify schema_migrations table
psql -U postgres -d loyalty_system -c "SELECT * FROM schema_migrations;"

# Check table counts
psql -U postgres -d loyalty_system -c "
SELECT 
    tablename, 
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;
"
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
