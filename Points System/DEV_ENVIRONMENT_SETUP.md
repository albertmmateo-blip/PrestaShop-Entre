# Fidelity Points Loyalty System - Development Environment Setup

This guide will help you set up the development environment for the Fidelity Points loyalty system integrated with PrestaShop.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Environment Configuration](#environment-configuration)
- [Database Management](#database-management)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Overview

The Fidelity Points system is a comprehensive loyalty solution designed for retail operations with both physical store (POS) and e-commerce platforms. It enables customers to earn and redeem loyalty points across channels using NFC-enabled cards.

### System Components

1. **Cloud Loyalty Backend** - REST API for loyalty operations (Node.js/TypeScript or Python/FastAPI)
2. **PostgreSQL Database** - Central data storage for loyalty system
3. **PrestaShop Module** - E-commerce integration
4. **Windows Agent** - POS integration (offline-capable)
5. **NFC Hardware** - Card readers for customer identification

## Prerequisites

### Required Software

- **Docker** (20.10+) and Docker Compose (2.0+)
- **Git** (2.30+)
- **Node.js** (20.x) or **Python** (3.11+) - depending on backend choice
- **PostgreSQL Client** (psql) for database management

### Optional Tools

- **pgAdmin** or **DBeaver** for database GUI
- **Postman** or **Insomnia** for API testing
- **VS Code** with PostgreSQL extension

### System Requirements

- **OS**: Linux, macOS, or Windows 10/11 with WSL2
- **RAM**: 8GB minimum, 16GB recommended
- **Disk Space**: 10GB free space
- **Network**: Internet connection for initial setup

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/albertmmateo-blip/PrestaShop-Entre.git
cd PrestaShop-Entre
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.loyalty .env.loyalty.local

# Edit configuration (set secure passwords!)
nano .env.loyalty.local
```

### 3. Start Services

```bash
# Start PrestaShop and MySQL (existing services)
docker compose up -d

# Start Loyalty PostgreSQL Database
docker compose -f docker-compose.loyalty.yml up -d
```

### 4. Run Database Migrations

```bash
# Make migration script executable
chmod +x "Points System/07_operations/database/run_migrations.sh"

# Run migrations
cd "Points System/07_operations/database"
./run_migrations.sh
```

### 5. Verify Setup

```bash
# Check running containers
docker compose ps

# Verify loyalty database
docker exec -it loyalty-postgres psql -U loyalty_user -d loyalty_system -c "\dt"

# Expected output: List of 8 tables (customers, cards, loyalty_accounts, etc.)
```

## Detailed Setup

### Step 1: PrestaShop Setup

The repository already includes PrestaShop configuration. Follow existing PrestaShop setup:

```bash
# Start PrestaShop services
docker compose up -d

# Wait for PrestaShop installation (can take 5-10 minutes)
docker compose logs -f prestashop-git

# Access PrestaShop
# Front Office: http://localhost:8001
# Back Office: http://localhost:8001/admin-dev
# Default credentials: demo@prestashop.com / Correct Horse Battery Staple
```

### Step 2: Loyalty Database Setup

#### Option A: Using Docker Compose (Recommended)

```bash
# Start loyalty database service
docker compose -f docker-compose.loyalty.yml up -d loyalty-postgres

# Check health
docker compose -f docker-compose.loyalty.yml ps

# View logs
docker compose -f docker-compose.loyalty.yml logs -f loyalty-postgres
```

#### Option B: Local PostgreSQL Installation

If you have PostgreSQL installed locally:

```bash
# Create database
createdb -U postgres loyalty_system

# Or using psql
psql -U postgres -c "CREATE DATABASE loyalty_system WITH ENCODING='UTF8';"
```

#### Run Migrations

```bash
# Set environment variables
export LOYALTY_DB_HOST=localhost
export LOYALTY_DB_PORT=5433
export LOYALTY_DB_NAME=loyalty_system
export LOYALTY_DB_USER=loyalty_user
export LOYALTY_DB_PASSWORD=loyalty_password_change_me

# Run migration script
cd "Points System/07_operations/database"
./run_migrations.sh

# Expected output:
# =========================================
# Loyalty System Database Migration Runner
# =========================================
# [RUN ] 001_initial_schema.sql
# [OK  ] 001_initial_schema.sql completed successfully
# Successfully applied 1 migration(s)
```

### Step 3: Test Database Setup

Create a test database for integration testing:

```bash
# Start test database (using Docker profile)
docker compose -f docker-compose.loyalty.yml --profile test up -d loyalty-postgres-test

# Run migrations on test database
cd "Points System/07_operations/database"
./run_migrations.sh --test
```

## Environment Configuration

### Required Environment Variables

Edit `.env.loyalty.local` and set these critical variables:

```bash
# Database - Use strong passwords!
LOYALTY_DB_PASSWORD=your_secure_password_here

# JWT Secret - Generate random string
LOYALTY_JWT_SECRET=$(openssl rand -base64 32)

# Session Secret - Generate random string
LOYALTY_SESSION_SECRET=$(openssl rand -base64 32)

# Email Service (if using SendGrid)
LOYALTY_EMAIL_API_KEY=your_sendgrid_api_key

# PrestaShop API
PRESTASHOP_API_KEY=your_prestashop_api_key
```

### Generating Secure Secrets

```bash
# Generate random secrets
openssl rand -base64 32

# Or using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"

# Or using Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Database Management

### Accessing the Database

```bash
# Using Docker
docker exec -it loyalty-postgres psql -U loyalty_user -d loyalty_system

# Using local psql
psql -h localhost -p 5433 -U loyalty_user -d loyalty_system
```

### Common Database Operations

```sql
-- List all tables
\dt

-- Describe a table
\d customers

-- View applied migrations
SELECT * FROM schema_migrations;

-- Check customer count
SELECT COUNT(*) FROM customers;

-- View recent ledger entries
SELECT * FROM loyalty_ledger ORDER BY created_at DESC LIMIT 10;
```

### Database Backup

```bash
# Backup development database
docker exec loyalty-postgres pg_dump -U loyalty_user loyalty_system > backup_$(date +%Y%m%d).sql

# Or using Docker volume backup
docker run --rm \
  --volumes-from loyalty-postgres \
  -v $(pwd):/backup \
  ubuntu tar cvf /backup/loyalty-db-backup.tar /var/lib/postgresql/data
```

### Database Restore

```bash
# Restore from SQL backup
docker exec -i loyalty-postgres psql -U loyalty_user loyalty_system < backup_20260213.sql
```

## Development Workflow

### Project Structure

```
PrestaShop-Entre/
├── Points System/              # Loyalty system documentation and scripts
│   ├── 01_project/            # Project overview and plan
│   ├── 02_architecture/       # System architecture
│   ├── 03_features/           # Feature specifications
│   ├── 04_integrations/       # Integration docs
│   ├── 05_data/               # Data model
│   ├── 06_security/           # Security model
│   ├── 07_operations/         # Operations and deployment
│   │   └── database/          # Database scripts and migrations
│   └── 08_prompts/            # Development prompts
├── docker-compose.yml         # PrestaShop services
├── docker-compose.loyalty.yml # Loyalty database services
├── .env                       # PrestaShop environment
└── .env.loyalty.local         # Loyalty environment (DO NOT COMMIT)
```

### Adding New Migrations

```bash
# Create new migration file
cd "Points System/07_operations/database/migrations"

# Name format: XXX_description.sql (e.g., 002_add_card_qr_code.sql)
cat > 002_add_card_qr_code.sql << 'EOF'
-- Migration 002: Add QR Code Support
BEGIN;

ALTER TABLE cards
    ADD COLUMN IF NOT EXISTS qr_code_url TEXT,
    ADD COLUMN IF NOT EXISTS qr_code_data VARCHAR(255);

INSERT INTO schema_migrations (version, description) 
VALUES ('002', 'Add QR code support to cards table')
ON CONFLICT (version) DO NOTHING;

COMMIT;
EOF

# Run migration
cd ..
./run_migrations.sh
```

### Code Quality Tools

The repository includes linting and formatting tools:

```bash
# PHP Code Style Fixer
make cs-fixer

# PHPStan Static Analysis
make phpstan

# Run all tests
make test
```

## Testing

### Unit Tests

Create unit tests for loyalty business logic:

```bash
# PHPUnit for PHP components
./vendor/bin/phpunit tests/Unit/Loyalty/

# Jest for Node.js/TypeScript (if using Node.js backend)
npm test
```

### Integration Tests

Test database operations:

```bash
# Use test database
export LOYALTY_DB_NAME=loyalty_system_test

# Run integration tests
./vendor/bin/phpunit tests/Integration/Loyalty/
```

### Manual Testing

```bash
# Insert test customer
docker exec -it loyalty-postgres psql -U loyalty_user -d loyalty_system << 'EOF'
INSERT INTO customers (prestashop_email, first_name, last_name, prestashop_customer_id)
VALUES ('test@example.com', 'Test', 'Customer', 999);
EOF

# Verify insertion
docker exec -it loyalty-postgres psql -U loyalty_user -d loyalty_system \
  -c "SELECT * FROM customers WHERE prestashop_email = 'test@example.com';"
```

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker compose -f docker-compose.loyalty.yml ps

# Check logs
docker compose -f docker-compose.loyalty.yml logs loyalty-postgres

# Test connection
docker exec loyalty-postgres pg_isready -U loyalty_user -d loyalty_system

# Common fix: Restart container
docker compose -f docker-compose.loyalty.yml restart loyalty-postgres
```

### Migration Failures

```bash
# Check migration status
docker exec -it loyalty-postgres psql -U loyalty_user -d loyalty_system \
  -c "SELECT * FROM schema_migrations;"

# Rollback last migration (manual)
docker exec -it loyalty-postgres psql -U loyalty_user -d loyalty_system \
  -c "DELETE FROM schema_migrations WHERE version = '002';"

# Re-run migration
cd "Points System/07_operations/database"
./run_migrations.sh
```

### Port Conflicts

If port 5433 is already in use:

```bash
# Change port in .env.loyalty.local
LOYALTY_DB_PORT=5435

# Restart container
docker compose -f docker-compose.loyalty.yml down
docker compose -f docker-compose.loyalty.yml up -d
```

### Permission Errors

```bash
# Grant permissions to loyalty user
docker exec -it loyalty-postgres psql -U loyalty_user -d loyalty_system << 'EOF'
GRANT ALL ON ALL TABLES IN SCHEMA public TO loyalty_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO loyalty_user;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO loyalty_user;
EOF
```

## Next Steps

After completing the development environment setup:

1. **Backend Development**: Choose technology stack (Node.js/TypeScript or Python/FastAPI)
   - See `Points System/02_architecture/CLOUD_BACKEND.md`
   
2. **Windows Agent**: Develop POS integration agent
   - See `Points System/02_architecture/WINDOWS_AGENT.md`
   
3. **PrestaShop Module**: Create loyalty module
   - See `Points System/04_integrations/PRESTASHOP_MODULE.md`
   
4. **NFC Hardware**: Set up card readers
   - See `Points System/04_integrations/NFC_HARDWARE.md`

## Documentation

For complete system documentation, see:

- **Project Overview**: `Points System/01_project/PROJECT_OVERVIEW.md`
- **Implementation Plan**: `Points System/01_project/IMPLEMENTATION_PLAN.md`
- **System Architecture**: `Points System/02_architecture/SYSTEM_ARCHITECTURE.md`
- **Data Model**: `Points System/05_data/DATA_MODEL.md`
- **Database Setup**: `Points System/07_operations/database/README.md`

## Support

For questions or issues:

1. Check existing documentation in `Points System/` directory
2. Review troubleshooting section above
3. Check GitHub Issues
4. Contact development team

## License

See LICENSE.md file in repository root.
