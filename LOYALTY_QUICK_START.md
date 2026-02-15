# Fidelity Points Loyalty System - Quick Start

Welcome to the Fidelity Points loyalty system for PrestaShop! This guide will help you get started quickly.

## What is This?

This repository contains a PrestaShop 9.1.0 installation with an integrated loyalty points system for retail operations. The loyalty system allows customers to:
- Earn points on purchases (both in-store and online)
- Redeem points for discounts
- Track their loyalty balance
- Use NFC cards for identification at POS

## Quick Setup (5 Minutes)

### Prerequisites
- Docker and Docker Compose installed
- 8GB+ RAM available
- 10GB+ free disk space

### Step 1: Clone and Configure

```bash
# Clone the repository
git clone https://github.com/albertmmateo-blip/PrestaShop-Entre.git
cd PrestaShop-Entre

# Copy loyalty environment template and customize
cp .env.loyalty .env.loyalty.local

# Edit .env.loyalty.local and set secure passwords
nano .env.loyalty.local  # or your preferred editor
```

**Important:** Change these values in `.env.loyalty.local`:
```bash
LOYALTY_DB_PASSWORD=your_secure_password_here
LOYALTY_JWT_SECRET=$(openssl rand -base64 32)
LOYALTY_SESSION_SECRET=$(openssl rand -base64 32)
```

### Step 2: Start Services

```bash
# Create Docker network
docker network create prestashop-network

# Start loyalty database
docker compose -f docker-compose.loyalty.yml up -d

# Wait 10 seconds for database to initialize
sleep 10

# Verify database is running
docker compose -f docker-compose.loyalty.yml ps
```

### Step 3: Verify Setup

```bash
# Check database tables
docker exec loyalty-postgres psql -U loyalty_user -d loyalty_system -c "\dt"

# You should see 8 tables:
# - customers
# - cards  
# - loyalty_accounts
# - loyalty_ledger
# - order_mapping
# - consent_records
# - idempotency_keys
# - schema_migrations
```

### Step 4: (Optional) Start PrestaShop

If you also want to run PrestaShop:

```bash
# Start PrestaShop services
docker compose up -d

# Wait for installation (5-10 minutes first time)
docker compose logs -f prestashop-git

# Access PrestaShop:
# Front: http://localhost:8001
# Admin: http://localhost:8001/admin-dev
# Credentials: demo@prestashop.com / Correct Horse Battery Staple
```

## What's Included

### Database Schema
- **8 tables** for loyalty operations
- **Immutable ledger** for transaction audit trail
- **Triggers** for data integrity and auto-hashing
- **Indexes** for performance optimization

### Development Tools
- **Docker Compose** configuration for PostgreSQL
- **Migration runner** script for database setup
- **CI/CD workflow** for automated testing
- **Environment templates** for configuration

### Documentation
Complete documentation in `Points System/` directory:
- Project overview and implementation plan
- System architecture and data model
- Feature specifications
- Integration guides
- Security model

## Next Steps

### For Developers

1. **Read the Documentation**
   ```bash
   # Main setup guide
   cat "Points System/DEV_ENVIRONMENT_SETUP.md"
   
   # System architecture
   cat "Points System/02_architecture/SYSTEM_ARCHITECTURE.md"
   
   # Data model
   cat "Points System/05_data/DATA_MODEL.md"
   ```

2. **Choose Technology Stack**
   - Node.js + TypeScript + PostgreSQL (recommended)
   - Python + FastAPI + PostgreSQL (alternative)
   
   Update `Points System/01_project/IMPLEMENTATION_PLAN.md` with your choice.

3. **Start Backend Development**
   - See `Points System/02_architecture/CLOUD_BACKEND.md`
   - Implement REST API endpoints for loyalty operations
   - Use migrations already set up

4. **Develop PrestaShop Module**
   - See `Points System/04_integrations/PRESTASHOP_MODULE.md`
   - Create module skeleton
   - Integrate with loyalty backend API

### For System Administrators

1. **Configure Production Environment**
   - Use managed PostgreSQL service
   - Set up proper backups
   - Configure SSL/TLS
   - Use secrets management (not `.env` files)

2. **Set Up Monitoring**
   - Database performance metrics
   - API response times
   - Error logging
   - Backup verification

3. **Security Hardening**
   - Change default passwords
   - Restrict database access
   - Enable SSL connections
   - Regular security audits

## Common Commands

### Database Management

```bash
# Connect to database
docker exec -it loyalty-postgres psql -U loyalty_user -d loyalty_system

# Run migrations manually
cd "Points System/07_operations/database"
export LOYALTY_DB_HOST=localhost
export LOYALTY_DB_PORT=5433
export LOYALTY_DB_NAME=loyalty_system
export LOYALTY_DB_USER=loyalty_user
export LOYALTY_DB_PASSWORD=loyalty_password_change_me
./run_migrations.sh

# Backup database
docker exec loyalty-postgres pg_dump -U loyalty_user loyalty_system > backup_$(date +%Y%m%d).sql

# View logs
docker compose -f docker-compose.loyalty.yml logs -f loyalty-postgres
```

### Service Management

```bash
# Stop services
docker compose -f docker-compose.loyalty.yml down

# Stop and remove volumes (⚠️  destroys data)
docker compose -f docker-compose.loyalty.yml down -v

# Restart services
docker compose -f docker-compose.loyalty.yml restart

# View service status
docker compose -f docker-compose.loyalty.yml ps
```

## Troubleshooting

### Database Won't Start

```bash
# Check logs
docker compose -f docker-compose.loyalty.yml logs loyalty-postgres

# Common fix: Port conflict
# Edit .env.loyalty.local and change LOYALTY_DB_PORT to different value

# Restart
docker compose -f docker-compose.loyalty.yml down
docker compose -f docker-compose.loyalty.yml up -d
```

### Migration Errors

```bash
# Check migration status
docker exec loyalty-postgres psql -U loyalty_user -d loyalty_system \
  -c "SELECT * FROM schema_migrations;"

# Reset database (⚠️  destroys data)
docker compose -f docker-compose.loyalty.yml down -v
docker compose -f docker-compose.loyalty.yml up -d
```

### Network Errors

```bash
# Recreate Docker network
docker network rm prestashop-network
docker network create prestashop-network

# Restart services
docker compose -f docker-compose.loyalty.yml restart
```

## Testing

### Run CI Tests Locally

```bash
# Install PostgreSQL client
sudo apt-get install postgresql-client

# Run tests
# (Will be implemented as backend is developed)
```

### Manual Testing

```bash
# Insert test customer
docker exec -i loyalty-postgres psql -U loyalty_user -d loyalty_system << 'EOF'
INSERT INTO customers (prestashop_email, first_name, last_name)
VALUES ('test@example.com', 'Test', 'Customer');
EOF

# Verify insertion
docker exec loyalty-postgres psql -U loyalty_user -d loyalty_system \
  -c "SELECT * FROM customers;"
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CUSTOMERS                                │
│  ┌──────────────────┐              ┌──────────────────────────┐ │
│  │ Physical Store   │              │  Online Store            │ │
│  │ NFC Card Tap     │              │  PrestaShop 9.1.0        │ │
│  └────────┬─────────┘              └──────────┬───────────────┘ │
└───────────┼────────────────────────────────────┼─────────────────┘
            │                                    │
            │                                    │
┌───────────▼──────────────────┐    ┌───────────▼──────────────┐
│  Windows Agent (POS)         │    │  PrestaShop Module       │
│  - NFC Reader                │    │  (REST API Client)       │
│  - Offline Queue             │    │                          │
│  - Aniwin Integration        │    │                          │
└───────────┬──────────────────┘    └───────────┬──────────────┘
            │                                    │
            │     ┌──────────────────────────────┘
            │     │
┌───────────▼─────▼──────────────────────────────────────────┐
│              CLOUD LOYALTY BACKEND                          │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  REST API (Node.js/TypeScript or Python/FastAPI)     │ │
│  └───────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  PostgreSQL Database (loyalty_system)                 │ │
│  │  ✓ Already set up and running!                        │ │
│  └───────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

## Documentation

- **📖 Full Setup Guide**: `Points System/DEV_ENVIRONMENT_SETUP.md`
- **🏗️ System Architecture**: `Points System/02_architecture/SYSTEM_ARCHITECTURE.md`
- **📊 Data Model**: `Points System/05_data/DATA_MODEL.md`
- **🔒 Security Model**: `Points System/06_security/SECURITY_MODEL.md`
- **💾 Database README**: `Points System/07_operations/database/README.md`

## Getting Help

1. Check the troubleshooting section above
2. Review documentation in `Points System/` directory
3. Check GitHub Issues
4. Contact the development team

## License

See [LICENSE.md](LICENSE.md) for details.

---

**Status**: ✅ Database setup complete | ⏳ Backend development pending | ⏳ Module development pending

Last Updated: 2026-02-13
