-- Rollback Migration 001: Initial Loyalty System Database Schema
-- Description: Drops all tables, indexes, triggers, and functions created in migration 001
-- Created: 2026-02-15
-- Author: Database Migration System

BEGIN;

-- Drop triggers first (dependent on functions)
DROP TRIGGER IF EXISTS prevent_ledger_delete ON loyalty_ledger;
DROP TRIGGER IF EXISTS prevent_ledger_update ON loyalty_ledger;
DROP TRIGGER IF EXISTS generate_customer_hashes ON customers;
DROP TRIGGER IF EXISTS update_idempotency_keys_updated_at ON idempotency_keys;
DROP TRIGGER IF EXISTS update_order_mapping_updated_at ON order_mapping;
DROP TRIGGER IF EXISTS update_loyalty_accounts_updated_at ON loyalty_accounts;
DROP TRIGGER IF EXISTS update_cards_updated_at ON cards;
DROP TRIGGER IF EXISTS update_customers_updated_at ON customers;

-- Drop functions
DROP FUNCTION IF EXISTS prevent_ledger_modification();
DROP FUNCTION IF EXISTS generate_email_hash();
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS idempotency_keys CASCADE;
DROP TABLE IF EXISTS consent_records CASCADE;
DROP TABLE IF EXISTS order_mapping CASCADE;
DROP TABLE IF EXISTS loyalty_ledger CASCADE;
DROP TABLE IF EXISTS loyalty_accounts CASCADE;
DROP TABLE IF EXISTS cards CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS schema_migrations CASCADE;

-- Remove extensions (optional - only if no other schemas use them)
-- DROP EXTENSION IF EXISTS "pgcrypto";
-- DROP EXTENSION IF EXISTS "uuid-ossp";

-- Remove migration record
-- (No need since we're dropping schema_migrations table)

COMMIT;

-- Verification queries (run these after rollback to verify cleanup)
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
-- SELECT routine_name FROM information_schema.routines WHERE routine_schema = 'public';
