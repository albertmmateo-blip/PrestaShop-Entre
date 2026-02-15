-- Test Data for Loyalty System
-- Description: Sample data for testing and validation
-- Created: 2026-02-15
-- Author: Database Migration System

BEGIN;

-- Verify schema is in place
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM schema_migrations WHERE version = '001') THEN
        RAISE EXCEPTION 'Migration 001 not applied. Please run migrations first.';
    END IF;
END $$;

-- =============================================================================
-- TEST CUSTOMERS
-- =============================================================================

-- Customer 1: María García (POS enrollment, has card)
INSERT INTO customers (
    customer_id,
    prestashop_customer_id,
    prestashop_email,
    first_name,
    last_name,
    phone_number,
    language_preference,
    address_line1,
    city,
    postal_code,
    country_code,
    enrollment_date,
    account_status,
    gdpr_consent_date,
    marketing_consent,
    whatsapp_consent,
    created_by
) VALUES (
    '11111111-1111-1111-1111-111111111111',
    NULL,
    'maria.garcia@example.com',
    'María',
    'García',
    '+34612345678',
    'es',
    'Carrer de Valencia, 123',
    'Barcelona',
    '08009',
    'ES',
    '2024-01-15 10:30:00+00',
    'active',
    '2024-01-15 10:30:00+00',
    TRUE,
    TRUE,
    'test_data_script'
);

-- Customer 2: John Smith (PrestaShop enrollment)
INSERT INTO customers (
    customer_id,
    prestashop_customer_id,
    prestashop_email,
    first_name,
    last_name,
    phone_number,
    language_preference,
    address_line1,
    city,
    postal_code,
    country_code,
    enrollment_date,
    account_status,
    gdpr_consent_date,
    marketing_consent,
    whatsapp_consent,
    created_by
) VALUES (
    '22222222-2222-2222-2222-222222222222',
    9876,
    'john.smith@example.com',
    'John',
    'Smith',
    '+34698765432',
    'en',
    'Gran Via, 456',
    'Madrid',
    '28013',
    'ES',
    '2024-02-20 14:15:00+00',
    'active',
    '2024-02-20 14:15:00+00',
    TRUE,
    FALSE,
    'test_data_script'
);

-- Customer 3: Jordi Puig (Catalan preference, inactive)
INSERT INTO customers (
    customer_id,
    prestashop_customer_id,
    prestashop_email,
    first_name,
    last_name,
    phone_number,
    language_preference,
    enrollment_date,
    account_status,
    gdpr_consent_date,
    marketing_consent,
    whatsapp_consent,
    created_by
) VALUES (
    '33333333-3333-3333-3333-333333333333',
    9877,
    'jordi.puig@example.cat',
    'Jordi',
    'Puig',
    '+34655123456',
    'ca',
    '2023-06-10 09:00:00+00',
    'inactive',
    '2023-06-10 09:00:00+00',
    FALSE,
    FALSE,
    'test_data_script'
);

-- =============================================================================
-- TEST LOYALTY ACCOUNTS
-- =============================================================================

-- Account for María García
INSERT INTO loyalty_accounts (
    account_id,
    customer_id,
    current_balance_points,
    lifetime_earned_points,
    lifetime_redeemed_points,
    lifetime_expired_points,
    lifetime_adjusted_points,
    total_earn_transactions,
    total_redeem_transactions,
    last_earn_date,
    last_redeem_date,
    last_transaction_date,
    account_tier,
    created_at,
    balance_last_computed_at
) VALUES (
    'aaaaaaaa-1111-1111-1111-111111111111',
    '11111111-1111-1111-1111-111111111111',
    250000, -- 25.00 EUR
    500000, -- 50.00 EUR lifetime earned
    200000, -- 20.00 EUR lifetime redeemed
    50000,  -- 5.00 EUR expired
    0,
    10,
    3,
    '2026-02-10 11:00:00+00',
    '2026-02-08 15:30:00+00',
    '2026-02-10 11:00:00+00',
    'silver',
    '2024-01-15 10:30:00+00',
    '2026-02-10 11:00:00+00'
);

-- Account for John Smith
INSERT INTO loyalty_accounts (
    account_id,
    customer_id,
    current_balance_points,
    lifetime_earned_points,
    lifetime_redeemed_points,
    lifetime_expired_points,
    lifetime_adjusted_points,
    total_earn_transactions,
    total_redeem_transactions,
    last_earn_date,
    last_redeem_date,
    last_transaction_date,
    account_tier,
    created_at,
    balance_last_computed_at
) VALUES (
    'aaaaaaaa-2222-2222-2222-222222222222',
    '22222222-2222-2222-2222-222222222222',
    150000, -- 15.00 EUR
    300000, -- 30.00 EUR lifetime earned
    150000, -- 15.00 EUR lifetime redeemed
    0,
    0,
    5,
    2,
    '2026-02-12 10:20:00+00',
    '2026-02-05 14:00:00+00',
    '2026-02-12 10:20:00+00',
    'standard',
    '2024-02-20 14:15:00+00',
    '2026-02-12 10:20:00+00'
);

-- Account for Jordi Puig (inactive, low balance)
INSERT INTO loyalty_accounts (
    account_id,
    customer_id,
    current_balance_points,
    lifetime_earned_points,
    lifetime_redeemed_points,
    lifetime_expired_points,
    lifetime_adjusted_points,
    total_earn_transactions,
    total_redeem_transactions,
    last_earn_date,
    last_redeem_date,
    last_transaction_date,
    account_tier,
    created_at,
    balance_last_computed_at
) VALUES (
    'aaaaaaaa-3333-3333-3333-333333333333',
    '33333333-3333-3333-3333-333333333333',
    5000,   -- 0.50 EUR
    100000, -- 10.00 EUR lifetime earned
    50000,  -- 5.00 EUR lifetime redeemed
    45000,  -- 4.50 EUR expired
    0,
    3,
    1,
    '2023-08-15 12:00:00+00',
    '2023-08-15 12:00:00+00',
    '2023-08-15 12:00:00+00',
    'standard',
    '2023-06-10 09:00:00+00',
    '2023-08-15 12:00:00+00'
);

-- =============================================================================
-- TEST CARDS
-- =============================================================================

-- Card 1: Assigned to María García
INSERT INTO cards (
    card_id,
    card_uid,
    card_number,
    card_status,
    customer_id,
    assigned_date,
    activated_date,
    expiration_date,
    printing_batch,
    printing_date,
    printed_by,
    created_by
) VALUES (
    'dddddddd-1111-1111-1111-111111111111',
    '04A1B2C3D4E5F6',
    'LC-00000001',
    'active',
    '11111111-1111-1111-1111-111111111111',
    '2024-01-15 10:30:00+00',
    '2024-01-15 10:30:00+00',
    '2029-01-15',
    'BATCH-20240115-001',
    '2024-01-10',
    'printer_operator_jane',
    'test_data_script'
);

-- Card 2: Assigned to John Smith
INSERT INTO cards (
    card_id,
    card_uid,
    card_number,
    card_status,
    customer_id,
    assigned_date,
    activated_date,
    expiration_date,
    printing_batch,
    printing_date,
    printed_by,
    created_by
) VALUES (
    'dddddddd-2222-2222-2222-222222222222',
    '04B1C2D3E4F5A6',
    'LC-00000002',
    'active',
    '22222222-2222-2222-2222-222222222222',
    '2024-02-20 14:15:00+00',
    '2024-02-20 14:15:00+00',
    '2029-02-20',
    'BATCH-20240115-001',
    '2024-01-10',
    'printer_operator_jane',
    'test_data_script'
);

-- Card 3: Inactive card (not assigned)
INSERT INTO cards (
    card_id,
    card_uid,
    card_number,
    card_status,
    printing_batch,
    printing_date,
    printed_by,
    created_by
) VALUES (
    'dddddddd-3333-3333-3333-333333333333',
    '04C1D2E3F4A5B6',
    'LC-00000003',
    'inactive',
    'BATCH-20240115-001',
    '2024-01-10',
    'printer_operator_jane',
    'test_data_script'
);

-- Card 4: Lost card
INSERT INTO cards (
    card_id,
    card_uid,
    card_number,
    card_status,
    customer_id,
    assigned_date,
    activated_date,
    printing_batch,
    printing_date,
    printed_by,
    created_by
) VALUES (
    'dddddddd-4444-4444-4444-444444444444',
    '04D1E2F3A4B5C6',
    'LC-00000004',
    'lost',
    '33333333-3333-3333-3333-333333333333',
    '2023-06-10 09:00:00+00',
    '2023-06-10 09:00:00+00',
    'BATCH-20230601-001',
    '2023-06-01',
    'printer_operator_mike',
    'test_data_script'
);

-- =============================================================================
-- TEST LOYALTY LEDGER (Transaction History)
-- =============================================================================

-- María García - Earn transaction 1
INSERT INTO loyalty_ledger (
    ledger_id,
    customer_id,
    account_id,
    transaction_type,
    transaction_date,
    points_delta,
    balance_after,
    source_type,
    source_reference,
    order_id,
    order_amount_eur,
    earn_rate_percent,
    description,
    expiration_date,
    idempotency_key,
    channel,
    terminal_id,
    created_by
) VALUES (
    '11111111-1111-1111-1111-111111111111',
    '11111111-1111-1111-1111-111111111111',
    'aaaaaaaa-1111-1111-1111-111111111111',
    'earn',
    '2024-01-20 14:30:00+00',
    15000, -- 150 points from 100 EUR purchase @ 1.5%
    15000,
    'pos_sale',
    'POS-2024-01-20-0001',
    'POS-2024-01-20-0001',
    100.00,
    1.50,
    'Earned 150 points from POS sale',
    '2025-01-20',
    'pos-earn-20240120-0001-c1111111',
    'pos',
    'POS-TERMINAL-001',
    'pos_agent_v1.2'
);

-- María García - Redeem transaction 1
INSERT INTO loyalty_ledger (
    ledger_id,
    customer_id,
    account_id,
    transaction_type,
    transaction_date,
    points_delta,
    balance_after,
    source_type,
    source_reference,
    order_id,
    order_amount_eur,
    description,
    idempotency_key,
    channel,
    terminal_id,
    created_by
) VALUES (
    '11111111-1112-1111-1111-111111111111',
    '11111111-1111-1111-1111-111111111111',
    'aaaaaaaa-1111-1111-1111-111111111111',
    'redeem',
    '2024-02-01 10:15:00+00',
    -10000, -- Redeemed 100 points (10 EUR discount)
    5000,
    'pos_sale',
    'POS-2024-02-01-0025',
    'POS-2024-02-01-0025',
    80.00,
    'Redeemed 100 points (10.00 EUR discount)',
    'pos-redeem-20240201-0025-c1111111',
    'pos',
    'POS-TERMINAL-001',
    'pos_agent_v1.2'
);

-- María García - Earn transaction 2
INSERT INTO loyalty_ledger (
    ledger_id,
    customer_id,
    account_id,
    transaction_type,
    transaction_date,
    points_delta,
    balance_after,
    source_type,
    source_reference,
    order_id,
    order_amount_eur,
    earn_rate_percent,
    description,
    expiration_date,
    idempotency_key,
    channel,
    terminal_id,
    created_by
) VALUES (
    '11111111-1113-1111-1111-111111111111',
    '11111111-1111-1111-1111-111111111111',
    'aaaaaaaa-1111-1111-1111-111111111111',
    'earn',
    '2026-02-10 11:00:00+00',
    30000, -- 300 points from 200 EUR purchase @ 1.5%
    35000,
    'pos_sale',
    'POS-2026-02-10-0042',
    'POS-2026-02-10-0042',
    200.00,
    1.50,
    'Earned 300 points from POS sale',
    '2027-02-10',
    'pos-earn-20260210-0042-c1111111',
    'pos',
    'POS-TERMINAL-001',
    'pos_agent_v1.2'
);

-- John Smith - Online order earn
INSERT INTO loyalty_ledger (
    ledger_id,
    customer_id,
    account_id,
    transaction_type,
    transaction_date,
    points_delta,
    balance_after,
    source_type,
    source_reference,
    order_id,
    order_amount_eur,
    earn_rate_percent,
    description,
    expiration_date,
    idempotency_key,
    channel,
    created_by
) VALUES (
    '22222222-2221-2222-2222-222222222222',
    '22222222-2222-2222-2222-222222222222',
    'aaaaaaaa-2222-2222-2222-222222222222',
    'earn',
    '2024-03-15 10:20:00+00',
    20000, -- 200 points from 133.33 EUR online order @ 1.5%
    20000,
    'online_order',
    'PS-ORDER-12345',
    'PS-ORDER-12345',
    133.33,
    1.50,
    'Earned 200 points from online order #12345',
    '2025-03-15',
    'prestashop-earn-12345',
    'online',
    'prestashop_module_v1.0'
);

-- John Smith - Redeem on online order
INSERT INTO loyalty_ledger (
    ledger_id,
    customer_id,
    account_id,
    transaction_type,
    transaction_date,
    points_delta,
    balance_after,
    source_type,
    source_reference,
    order_id,
    order_amount_eur,
    description,
    idempotency_key,
    channel,
    created_by
) VALUES (
    '22222222-2222-2222-2222-222222222222',
    '22222222-2222-2222-2222-222222222222',
    'aaaaaaaa-2222-2222-2222-222222222222',
    'redeem',
    '2026-02-05 14:00:00+00',
    -5000, -- Redeemed 50 points (5 EUR discount)
    15000,
    'online_order',
    'PS-ORDER-12350',
    'PS-ORDER-12350',
    95.00,
    'Redeemed 50 points (5.00 EUR discount) on online order',
    'prestashop-redeem-12350',
    'online',
    'prestashop_module_v1.0'
);

-- Manual adjustment example (goodwill points)
INSERT INTO loyalty_ledger (
    ledger_id,
    customer_id,
    account_id,
    transaction_type,
    transaction_date,
    points_delta,
    balance_after,
    source_type,
    source_reference,
    description,
    notes,
    idempotency_key,
    channel,
    created_by
) VALUES (
    '11111111-1114-1111-1111-111111111111',
    '11111111-1111-1111-1111-111111111111',
    'aaaaaaaa-1111-1111-1111-111111111111',
    'adjustment',
    '2026-01-05 09:30:00+00',
    10000, -- Add 100 points as goodwill
    45000,
    'manual_adjustment',
    'ADJ-2026-01-05-001',
    'Goodwill adjustment: Customer service recovery',
    'Compensating for technical issue during checkout. Approved by Manager ID: MGR-789',
    'adjustment-20260105-001-c1111111',
    'manual',
    'admin_user_john'
);

-- =============================================================================
-- TEST CONSENT RECORDS
-- =============================================================================

-- María García - Initial loyalty program consent
INSERT INTO consent_records (
    consent_id,
    customer_id,
    consent_type,
    consent_given,
    consent_date,
    consent_method,
    consent_version,
    consent_text,
    withdrawn,
    created_by
) VALUES (
    'eeeeeeee-1111-1111-1111-111111111111',
    '11111111-1111-1111-1111-111111111111',
    'loyalty_program',
    TRUE,
    '2024-01-15 10:30:00+00',
    'pos_enrollment',
    'v1.0',
    'I consent to participate in the Loyalty Program and agree to the processing of my transaction data to earn and redeem points.',
    FALSE,
    'test_data_script'
);

-- María García - Marketing email consent
INSERT INTO consent_records (
    consent_id,
    customer_id,
    consent_type,
    consent_given,
    consent_date,
    consent_method,
    consent_version,
    consent_text,
    withdrawn,
    created_by
) VALUES (
    'eeeeeeee-1112-1111-1111-111111111111',
    '11111111-1111-1111-1111-111111111111',
    'marketing_email',
    TRUE,
    '2024-01-15 10:30:00+00',
    'pos_enrollment',
    'v1.0',
    'I consent to receive promotional emails from the company including special offers, discounts, and loyalty program updates.',
    FALSE,
    'test_data_script'
);

-- John Smith - All consents from online signup
INSERT INTO consent_records (
    consent_id,
    customer_id,
    consent_type,
    consent_given,
    consent_date,
    consent_method,
    consent_ip_address,
    consent_user_agent,
    consent_version,
    consent_text,
    withdrawn,
    created_by
) VALUES (
    'eeeeeeee-2221-2222-2222-222222222222',
    '22222222-2222-2222-2222-222222222222',
    'loyalty_program',
    TRUE,
    '2024-02-20 14:15:00+00',
    'online_signup',
    '192.168.1.100',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'v1.0',
    'I consent to participate in the Loyalty Program and agree to the processing of my transaction data to earn and redeem points.',
    FALSE,
    'test_data_script'
);

-- =============================================================================
-- TEST ORDER MAPPING
-- =============================================================================

-- POS Order 1 - María García (earn + redeem)
INSERT INTO order_mapping (
    mapping_id,
    order_type,
    pos_order_id,
    order_date,
    order_total_eur,
    order_status,
    customer_id,
    earn_ledger_id,
    points_earned,
    terminal_id,
    channel,
    sync_status,
    last_sync_at
) VALUES (
    'cccccccc-1111-1111-1111-111111111111',
    'pos',
    'POS-2024-01-20-0001',
    '2024-01-20 14:30:00+00',
    100.00,
    'completed',
    '11111111-1111-1111-1111-111111111111',
    '11111111-1111-1111-1111-111111111111',
    15000,
    'POS-TERMINAL-001',
    'pos',
    'synced',
    '2024-01-20 14:31:00+00'
);

-- POS Order 2 - María García (redeem)
INSERT INTO order_mapping (
    mapping_id,
    order_type,
    pos_order_id,
    order_date,
    order_total_eur,
    order_status,
    customer_id,
    redeem_ledger_id,
    points_redeemed,
    terminal_id,
    channel,
    sync_status,
    last_sync_at
) VALUES (
    'cccccccc-1112-1111-1111-111111111111',
    'pos',
    'POS-2024-02-01-0025',
    '2024-02-01 10:15:00+00',
    80.00,
    'completed',
    '11111111-1111-1111-1111-111111111111',
    '11111111-1112-1111-1111-111111111111',
    10000,
    'POS-TERMINAL-001',
    'pos',
    'synced',
    '2024-02-01 10:16:00+00'
);

-- PrestaShop Order 1 - John Smith (earn)
INSERT INTO order_mapping (
    mapping_id,
    order_type,
    prestashop_order_id,
    order_date,
    order_total_eur,
    order_status,
    customer_id,
    earn_ledger_id,
    points_earned,
    channel,
    sync_status,
    last_sync_at
) VALUES (
    'cccccccc-2221-2222-2222-222222222222',
    'prestashop',
    12345,
    '2024-03-15 10:20:00+00',
    133.33,
    'delivered',
    '22222222-2222-2222-2222-222222222222',
    '22222222-2221-2222-2222-222222222222',
    20000,
    'online',
    'synced',
    '2024-03-15 10:21:00+00'
);

COMMIT;

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

-- Show summary of test data
SELECT 
    'Customers' AS entity,
    COUNT(*) AS count,
    COUNT(CASE WHEN account_status = 'active' THEN 1 END) AS active_count
FROM customers

UNION ALL

SELECT 
    'Loyalty Accounts' AS entity,
    COUNT(*) AS count,
    SUM(current_balance_points) AS total_points
FROM loyalty_accounts

UNION ALL

SELECT 
    'Cards' AS entity,
    COUNT(*) AS count,
    COUNT(CASE WHEN card_status = 'active' THEN 1 END) AS active_count
FROM cards

UNION ALL

SELECT 
    'Ledger Transactions' AS entity,
    COUNT(*) AS count,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM loyalty_ledger

UNION ALL

SELECT 
    'Consent Records' AS entity,
    COUNT(*) AS count,
    COUNT(CASE WHEN consent_given = TRUE THEN 1 END) AS consents_given
FROM consent_records

UNION ALL

SELECT 
    'Order Mappings' AS entity,
    COUNT(*) AS count,
    SUM(order_total_eur)::INTEGER AS total_revenue
FROM order_mapping;

-- Show customer balances
SELECT 
    c.first_name || ' ' || c.last_name AS customer_name,
    la.current_balance_points AS balance_points,
    la.current_balance_eur AS balance_eur,
    la.total_earn_transactions AS earn_txs,
    la.total_redeem_transactions AS redeem_txs,
    la.account_tier AS tier
FROM customers c
JOIN loyalty_accounts la ON la.customer_id = c.customer_id
ORDER BY la.current_balance_points DESC;
