#!/bin/bash
# Loyalty System Setup Verification Script
# This script verifies that the loyalty system development environment is correctly set up

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REQUIRED_TABLES=("customers" "cards" "loyalty_accounts" "loyalty_ledger" "order_mapping" "consent_records" "idempotency_keys" "schema_migrations")
DB_HOST="${LOYALTY_DB_HOST:-localhost}"
DB_PORT="${LOYALTY_DB_PORT:-5433}"
DB_NAME="${LOYALTY_DB_NAME:-loyalty_system}"
DB_USER="${LOYALTY_DB_USER:-loyalty_user}"
DB_PASSWORD="${LOYALTY_DB_PASSWORD:-loyalty_password_change_me}"

# Statistics
CHECKS_PASSED=0
CHECKS_FAILED=0
WARNINGS=0

# Function to print section header
print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
}

# Function to print test result
print_result() {
    if [ "$1" = "PASS" ]; then
        echo -e "${GREEN}✓${NC} $2"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    elif [ "$1" = "FAIL" ]; then
        echo -e "${RED}✗${NC} $2"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
    elif [ "$1" = "WARN" ]; then
        echo -e "${YELLOW}⚠${NC} $2"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "  $2"
    fi
}

# Function to run database query
run_query() {
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "$1" 2>/dev/null || echo "ERROR"
}

print_header "Loyalty System Setup Verification"

# Check 1: Docker
echo ""
echo "Checking prerequisites..."
if command -v docker &> /dev/null; then
    print_result "PASS" "Docker is installed"
else
    print_result "FAIL" "Docker is not installed"
fi

if command -v psql &> /dev/null; then
    print_result "PASS" "PostgreSQL client (psql) is installed"
else
    print_result "WARN" "PostgreSQL client (psql) not found - install with: sudo apt-get install postgresql-client"
fi

# Check 2: Docker containers
print_header "Docker Services"
if docker ps --format "{{.Names}}" | grep -q "loyalty-postgres"; then
    print_result "PASS" "loyalty-postgres container is running"
    
    # Check container health
    HEALTH=$(docker inspect --format='{{.State.Health.Status}}' loyalty-postgres 2>/dev/null || echo "unknown")
    if [ "$HEALTH" = "healthy" ]; then
        print_result "PASS" "loyalty-postgres is healthy"
    else
        print_result "WARN" "loyalty-postgres health status: $HEALTH"
    fi
else
    print_result "FAIL" "loyalty-postgres container is not running"
    echo ""
    echo "To start the container, run:"
    echo "  docker compose -f docker-compose.loyalty.yml up -d"
    exit 1
fi

# Check 3: Database connection
print_header "Database Connection"
if command -v psql &> /dev/null; then
    CONNECTION_TEST=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" 2>&1)
    if [[ "$CONNECTION_TEST" == *"1 row"* ]] || [[ "$CONNECTION_TEST" == *"(1 row)"* ]]; then
        print_result "PASS" "Successfully connected to database"
    else
        print_result "FAIL" "Cannot connect to database"
        echo "  Connection string: postgresql://$DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"
        echo "  Error: $CONNECTION_TEST"
    fi
else
    print_result "WARN" "Skipping connection test (psql not installed)"
fi

# Check 4: Database schema
print_header "Database Schema"
if command -v psql &> /dev/null; then
    # Check if schema_migrations table exists
    TABLE_EXISTS=$(run_query "SELECT 1 FROM information_schema.tables WHERE table_name = 'schema_migrations';" | tr -d '[:space:]')
    if [ "$TABLE_EXISTS" = "1" ]; then
        print_result "PASS" "schema_migrations table exists"
        
        # Check applied migrations
        MIGRATION_COUNT=$(run_query "SELECT COUNT(*) FROM schema_migrations;" | tr -d '[:space:]')
        if [ "$MIGRATION_COUNT" -gt 0 ] 2>/dev/null; then
            print_result "PASS" "Found $MIGRATION_COUNT applied migration(s)"
        else
            print_result "FAIL" "No migrations applied"
        fi
    else
        print_result "FAIL" "schema_migrations table does not exist - run migrations first"
    fi
    
    # Check for required tables
    echo ""
    echo "Checking required tables..."
    for table in "${REQUIRED_TABLES[@]}"; do
        EXISTS=$(run_query "SELECT 1 FROM information_schema.tables WHERE table_name = '$table';" | tr -d '[:space:]')
        if [ "$EXISTS" = "1" ]; then
            # Get row count
            COUNT=$(run_query "SELECT COUNT(*) FROM $table;" | tr -d '[:space:]')
            if [ "$COUNT" != "ERROR" ]; then
                print_result "PASS" "$table ($COUNT rows)"
            else
                print_result "PASS" "$table (exists)"
            fi
        else
            print_result "FAIL" "$table (missing)"
        fi
    done
fi

# Check 5: Triggers and functions
print_header "Database Integrity"
if command -v psql &> /dev/null; then
    # Check for immutable ledger trigger
    TRIGGER_EXISTS=$(run_query "SELECT 1 FROM information_schema.triggers WHERE trigger_name = 'prevent_ledger_update';" | tr -d '[:space:]')
    if [ "$TRIGGER_EXISTS" = "1" ]; then
        print_result "PASS" "Immutable ledger trigger (prevent_ledger_update) exists"
    else
        print_result "FAIL" "Immutable ledger trigger missing"
    fi
    
    # Check for email hash function
    FUNCTION_EXISTS=$(run_query "SELECT 1 FROM pg_proc WHERE proname = 'generate_email_hash';" | tr -d '[:space:]')
    if [ "$FUNCTION_EXISTS" = "1" ]; then
        print_result "PASS" "Email hash function exists"
    else
        print_result "FAIL" "Email hash function missing"
    fi
    
    # Check for updated_at function
    FUNCTION_EXISTS=$(run_query "SELECT 1 FROM pg_proc WHERE proname = 'update_updated_at_column';" | tr -d '[:space:]')
    if [ "$FUNCTION_EXISTS" = "1" ]; then
        print_result "PASS" "Auto-update timestamp function exists"
    else
        print_result "FAIL" "Auto-update timestamp function missing"
    fi
fi

# Check 6: Environment configuration
print_header "Environment Configuration"
if [ -f ".env.loyalty" ]; then
    print_result "PASS" ".env.loyalty template file exists"
else
    print_result "FAIL" ".env.loyalty template file missing"
fi

if [ -f ".env.loyalty.local" ]; then
    print_result "PASS" ".env.loyalty.local configuration file exists"
    
    # Check if passwords have been changed from defaults
    if grep -q "loyalty_password_change_me" ".env.loyalty.local" 2>/dev/null; then
        print_result "WARN" "Default password detected in .env.loyalty.local - please change it!"
    else
        print_result "PASS" "Custom password configured"
    fi
else
    print_result "WARN" ".env.loyalty.local not found - copy from .env.loyalty template"
fi

# Check 7: Docker Compose configuration
print_header "Docker Compose Configuration"
if [ -f "docker-compose.loyalty.yml" ]; then
    print_result "PASS" "docker-compose.loyalty.yml exists"
    
    # Validate docker-compose file
    if docker compose -f docker-compose.loyalty.yml config > /dev/null 2>&1; then
        print_result "PASS" "docker-compose.loyalty.yml is valid"
    else
        print_result "FAIL" "docker-compose.loyalty.yml has syntax errors"
    fi
else
    print_result "FAIL" "docker-compose.loyalty.yml missing"
fi

# Check 8: Documentation
print_header "Documentation"
DOCS=(
    "Points System/DEV_ENVIRONMENT_SETUP.md"
    "Points System/01_project/PROJECT_OVERVIEW.md"
    "Points System/02_architecture/SYSTEM_ARCHITECTURE.md"
    "Points System/05_data/DATA_MODEL.md"
    "Points System/07_operations/database/README.md"
    "LOYALTY_QUICK_START.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        print_result "PASS" "$doc"
    else
        print_result "FAIL" "$doc missing"
    fi
done

# Summary
print_header "Verification Summary"
echo ""
echo -e "${GREEN}Passed:${NC}  $CHECKS_PASSED"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo -e "${RED}Failed:${NC}  $CHECKS_FAILED"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    echo ""
    echo "Your loyalty system development environment is ready."
    echo ""
    echo "Next steps:"
    echo "  1. Review documentation: cat 'Points System/DEV_ENVIRONMENT_SETUP.md'"
    echo "  2. Choose technology stack (Node.js or Python)"
    echo "  3. Start backend development"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please review the errors above.${NC}"
    echo ""
    echo "Common fixes:"
    echo "  - Start database: docker compose -f docker-compose.loyalty.yml up -d"
    echo "  - Run migrations: cd 'Points System/07_operations/database' && ./run_migrations.sh"
    echo "  - Create config: cp .env.loyalty .env.loyalty.local"
    echo ""
    exit 1
fi
