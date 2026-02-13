#!/bin/bash
# Database Migration Runner for Loyalty System
# Usage: ./run_migrations.sh [--test]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MIGRATIONS_DIR="${SCRIPT_DIR}/migrations"

# Database configuration from environment variables
DB_HOST="${LOYALTY_DB_HOST:-localhost}"
DB_PORT="${LOYALTY_DB_PORT:-5432}"
DB_NAME="${LOYALTY_DB_NAME:-loyalty_system}"
DB_USER="${LOYALTY_DB_USER:-postgres}"

# Check if --test flag is passed
TEST_MODE=false
if [[ "$1" == "--test" ]]; then
    TEST_MODE=true
    DB_NAME="${LOYALTY_DB_NAME}_test"
    echo -e "${YELLOW}Running in TEST mode. Using database: ${DB_NAME}${NC}"
fi

# Check if psql is available
if ! command -v psql &> /dev/null; then
    echo -e "${RED}Error: psql command not found. Please install PostgreSQL client.${NC}"
    exit 1
fi

# Check if password is set
if [ -z "$LOYALTY_DB_PASSWORD" ]; then
    echo -e "${YELLOW}Warning: LOYALTY_DB_PASSWORD not set. You may be prompted for password.${NC}"
    export PGPASSWORD=""
else
    export PGPASSWORD="$LOYALTY_DB_PASSWORD"
fi

# Function to run SQL command
run_sql() {
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "$1" -q
}

# Function to run SQL file
run_sql_file() {
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$1"
}

# Function to check if database exists
check_database() {
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"
}

# Function to create database if it doesn't exist
create_database() {
    echo -e "${YELLOW}Creating database: ${DB_NAME}${NC}"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "CREATE DATABASE $DB_NAME WITH ENCODING='UTF8' LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8' TEMPLATE=template0;" || true
    echo -e "${GREEN}Database created successfully${NC}"
}

# Function to get applied migrations
get_applied_migrations() {
    run_sql "SELECT version FROM schema_migrations ORDER BY version;" 2>/dev/null | grep -v "^$" | grep -v "version" | grep -v "row" | tr -d '[:space:]' || echo ""
}

# Main execution
echo "========================================="
echo "Loyalty System Database Migration Runner"
echo "========================================="
echo "Database: $DB_NAME"
echo "Host: $DB_HOST"
echo "Port: $DB_PORT"
echo "User: $DB_USER"
echo "========================================="

# Check if database exists, create if not
if ! check_database; then
    echo -e "${YELLOW}Database does not exist.${NC}"
    create_database
fi

# Get list of migration files
echo -e "${GREEN}Scanning for migration files...${NC}"
MIGRATION_FILES=$(find "$MIGRATIONS_DIR" -name "*.sql" -type f | sort)

if [ -z "$MIGRATION_FILES" ]; then
    echo -e "${RED}No migration files found in $MIGRATIONS_DIR${NC}"
    exit 1
fi

echo "Found $(echo "$MIGRATION_FILES" | wc -l) migration file(s)"
echo ""

# Get already applied migrations
APPLIED_MIGRATIONS=$(get_applied_migrations)

# Run migrations
MIGRATIONS_RUN=0
while IFS= read -r migration_file; do
    # Extract migration version from filename (e.g., 001 from 001_initial_schema.sql)
    migration_version=$(basename "$migration_file" | sed 's/^\([0-9]*\)_.*/\1/')
    migration_name=$(basename "$migration_file")
    
    # Check if migration already applied
    if echo "$APPLIED_MIGRATIONS" | grep -q "^${migration_version}$"; then
        echo -e "${YELLOW}[SKIP]${NC} $migration_name (already applied)"
    else
        echo -e "${GREEN}[RUN ]${NC} $migration_name"
        
        # Run the migration
        if run_sql_file "$migration_file"; then
            echo -e "${GREEN}[OK  ]${NC} $migration_name completed successfully"
            MIGRATIONS_RUN=$((MIGRATIONS_RUN + 1))
        else
            echo -e "${RED}[FAIL]${NC} $migration_name failed"
            exit 1
        fi
    fi
    echo ""
done <<< "$MIGRATION_FILES"

# Summary
echo "========================================="
if [ $MIGRATIONS_RUN -eq 0 ]; then
    echo -e "${GREEN}All migrations already applied. Database is up to date.${NC}"
else
    echo -e "${GREEN}Successfully applied $MIGRATIONS_RUN migration(s)${NC}"
fi
echo "========================================="

# Verify schema
echo ""
echo "Verifying schema..."
TABLE_COUNT=$(run_sql "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';" | grep -oP '\d+' | head -1)
echo -e "${GREEN}Database contains $TABLE_COUNT tables${NC}"

# Show applied migrations
echo ""
echo "Applied migrations:"
run_sql "SELECT version, applied_at, description FROM schema_migrations ORDER BY version;" || echo "Could not retrieve migration history"

unset PGPASSWORD
echo ""
echo -e "${GREEN}Migration process completed successfully!${NC}"
