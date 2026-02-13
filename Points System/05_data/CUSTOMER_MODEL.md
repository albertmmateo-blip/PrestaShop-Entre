# Data Model: Customer Entity

## Purpose

Define the customer entity structure with PrestaShop integration, contact information, GDPR consent tracking, and customer lifecycle management to maintain a unified customer profile across POS and online channels.

## Scope

### In Scope
- Customer entity schema with all fields and constraints
- PrestaShop customer ID linking and synchronization
- Contact information (name, email, phone, address)
- GDPR consent fields and tracking
- Customer lifecycle states (active, inactive, suspended, deleted)
- Duplicate prevention through email and phone hashing
- Customer enrollment process
- Soft delete implementation

### Out of Scope
- PrestaShop core customer table (ps_customer) - managed by PrestaShop
- Customer password management (handled by PrestaShop)
- Customer order history (covered in ORDER_MAPPING.md)
- Customer loyalty balance (covered in LOYALTY_LEDGER.md)
- Customer consent audit trail (covered in CONSENT_RECORDS.md)

## Customer Schema

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
CREATE INDEX idx_customers_phone_hash ON customers(phone_hash) WHERE phone_hash IS NOT NULL;
CREATE INDEX idx_customers_enrollment_date ON customers(enrollment_date DESC);

-- Comments
COMMENT ON TABLE customers IS 'Customer profiles with PrestaShop linking and loyalty enrollment';
COMMENT ON COLUMN customers.customer_id IS 'Internal UUID for loyalty system';
COMMENT ON COLUMN customers.prestashop_customer_id IS 'Foreign key to PrestaShop ps_customer.id_customer';
COMMENT ON COLUMN customers.email_hash IS 'SHA-256 hash of lowercase email for duplicate detection';
COMMENT ON COLUMN customers.phone_hash IS 'SHA-256 hash of normalized phone for duplicate detection';
```

## Field Definitions

### customer_id (UUID)
Internal primary identifier for loyalty system. Generated as UUIDv4.

**Properties**:
- Never exposed to customer
- Used in all internal relationships (cards, ledger, consents)
- Immutable once created

### prestashop_customer_id (INTEGER)
Foreign key to PrestaShop `ps_customer.id_customer` table.

**Properties**:
- UNIQUE constraint ensures 1:1 mapping
- NULL for POS-only customers not yet registered online
- Set during online enrollment or first PrestaShop order
- Enables bidirectional sync between loyalty and PrestaShop

### prestashop_email (VARCHAR 255)
Customer's email address, synced from PrestaShop or collected at POS enrollment.

**Properties**:
- NOT NULL - required for all customers
- Used for login in PrestaShop
- Used for email marketing (if consent given)
- Stored in lowercase for consistency
- Not enforced as UNIQUE (customers may change email in PrestaShop)

**Validation**:
```sql
CONSTRAINT chk_email_format CHECK (
    prestashop_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
)
```

### first_name, last_name (VARCHAR 100)
Customer's personal name.

**Properties**:
- NOT NULL - required for personalization
- Used in receipts, emails, WhatsApp messages
- Synced from PrestaShop or collected at POS
- Unicode-safe (supports accented characters: García, Müller)

### phone_number (VARCHAR 20)
Customer's mobile phone number.

**Properties**:
- OPTIONAL but highly recommended
- Required for WhatsApp balance queries
- Format: International (E.164) or local Spanish format
- Examples: `+34612345678`, `612345678`

**Normalization**:
```sql
-- Normalize phone before storage
phone_number = regexp_replace(phone_number, '[^0-9+]', '', 'g')
```

### language_preference (VARCHAR 5)
Customer's preferred language for communications.

**Properties**:
- Default: `'es'` (Spanish)
- Supported: `'es'`, `'ca'` (Catalan), `'en'` (English)
- Used for receipt printing, emails, WhatsApp messages
- Synced from PrestaShop language setting

### address_line1, address_line2, city, postal_code, country_code
Customer's address (optional, synced from PrestaShop).

**Properties**:
- Used for shipping if customer orders online
- Not required for loyalty program
- Synced from PrestaShop default delivery address
- `country_code` is ISO 3166-1 alpha-2 (e.g., `ES`, `FR`, `DE`)

### enrollment_date (TIMESTAMP WITH TIME ZONE)
Date and time when customer enrolled in loyalty program.

**Properties**:
- NOT NULL with DEFAULT NOW()
- Immutable after creation
- Used for customer lifetime value analysis
- Stored in UTC

### account_status (VARCHAR 20)
Current status of customer's loyalty account.

**Values**:
- `active` - Normal active customer
- `inactive` - Customer hasn't used loyalty in 12+ months (can be reactivated)
- `suspended` - Account temporarily suspended (fraud, dispute)
- `deleted` - Customer requested account deletion (GDPR right to erasure)

**State Transitions**:
```
active → inactive (automatic after 12 months no activity)
active → suspended (manual by admin)
active/inactive/suspended → deleted (GDPR request)
deleted → never reactivated (create new account if customer returns)
```

### gdpr_consent_date (TIMESTAMP WITH TIME ZONE)
Date customer gave consent to loyalty program data processing.

**Properties**:
- Set during enrollment
- Required for GDPR compliance
- Stored in UTC
- Linked to full consent record in `consent_records` table

### marketing_consent, whatsapp_consent (BOOLEAN)
Customer's consent for marketing communications.

**Properties**:
- Default: FALSE
- Can be changed at any time in PrestaShop account or at POS
- `marketing_consent` covers email marketing
- `whatsapp_consent` covers WhatsApp promotional messages
- Tracked separately in `consent_records` for audit trail

### email_hash, phone_hash (VARCHAR 64)
SHA-256 hashes for duplicate detection.

**Properties**:
- `email_hash`: UNIQUE constraint prevents duplicate emails
- `phone_hash`: Index for fast duplicate phone lookup
- Auto-generated by trigger on INSERT/UPDATE
- Never displayed to users

**Generation Algorithm**:
```sql
email_hash = SHA256(LOWER(TRIM(prestashop_email)))
phone_hash = SHA256(REGEXP_REPLACE(phone_number, '[^0-9]', '', 'g'))
```

### created_at, updated_at (TIMESTAMP WITH TIME ZONE)
Audit timestamps for record lifecycle.

**Properties**:
- `created_at`: Set once on INSERT
- `updated_at`: Auto-updated on every UPDATE via trigger
- Stored in UTC

### created_by, updated_by (VARCHAR 100)
Actor who created or last updated the record.

**Properties**:
- Examples: `'pos_agent_v1.2'`, `'prestashop_sync'`, `'admin_user_john'`
- Used for audit trail
- Set by application based on API caller

### deleted_at, deleted_by (TIMESTAMP WITH TIME ZONE, VARCHAR 100)
Soft delete tracking.

**Properties**:
- NULL for active customers
- Set when customer requests account deletion (GDPR)
- `deleted_by` records who processed deletion (admin user ID)
- Customer data retained for legal/audit purposes but hidden from queries

## Customer Lifecycle

### 1. Enrollment (Creation)

**POS Enrollment**:
```sql
INSERT INTO customers (
    prestashop_email,
    first_name,
    last_name,
    phone_number,
    language_preference,
    enrollment_date,
    account_status,
    gdpr_consent_date,
    created_by
) VALUES (
    'maria.garcia@example.com',
    'María',
    'García',
    '+34612345678',
    'es',
    NOW(),
    'active',
    NOW(),
    'pos_agent_v1.2'
);
```

**PrestaShop Enrollment** (customer already exists in PrestaShop):
```sql
INSERT INTO customers (
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
    created_by
) VALUES (
    9876, -- From ps_customer.id_customer
    'maria.garcia@example.com',
    'María',
    'García',
    '+34612345678',
    'es',
    'Carrer de Valencia, 123',
    'Barcelona',
    '08009',
    'ES',
    NOW(),
    'active',
    NOW(),
    'prestashop_module_v1.0'
);
```

### 2. Linking PrestaShop Customer (POS-first scenario)

Customer enrolls at POS, later creates PrestaShop account with same email:

```sql
UPDATE customers
SET 
    prestashop_customer_id = 9876,
    address_line1 = 'Carrer de Valencia, 123',
    city = 'Barcelona',
    postal_code = '08009',
    updated_at = NOW(),
    updated_by = 'prestashop_sync'
WHERE email_hash = SHA256(LOWER('maria.garcia@example.com'))
    AND prestashop_customer_id IS NULL
    AND deleted_at IS NULL;
```

### 3. Profile Update

Customer changes phone number in PrestaShop:

```sql
UPDATE customers
SET 
    phone_number = '+34698765432',
    updated_at = NOW(),
    updated_by = 'prestashop_sync'
WHERE prestashop_customer_id = 9876
    AND deleted_at IS NULL;
```

### 4. Account Inactivation (Automatic)

Customer inactive for 12 months:

```sql
UPDATE customers
SET 
    account_status = 'inactive',
    updated_at = NOW(),
    updated_by = 'inactivity_job'
WHERE last_transaction_date < NOW() - INTERVAL '12 months'
    AND account_status = 'active'
    AND deleted_at IS NULL;
```

### 5. Account Suspension (Manual)

Admin suspends account due to fraud:

```sql
UPDATE customers
SET 
    account_status = 'suspended',
    updated_at = NOW(),
    updated_by = 'admin_user_john'
WHERE customer_id = 'cust-uuid-123'
    AND deleted_at IS NULL;
```

### 6. Account Deletion (GDPR)

Customer requests account deletion:

```sql
UPDATE customers
SET 
    account_status = 'deleted',
    deleted_at = NOW(),
    deleted_by = 'admin_user_sarah',
    updated_at = NOW(),
    updated_by = 'admin_user_sarah'
WHERE customer_id = 'cust-uuid-123'
    AND deleted_at IS NULL;
```

**Important**: Soft delete only. Customer record retained for audit/legal purposes.

## PrestaShop Linking

### Linking Strategies

#### Strategy 1: PrestaShop-First (Online Enrollment)
Customer creates PrestaShop account, then opts into loyalty program.

**Flow**:
1. Customer creates PrestaShop account → `ps_customer` record created
2. Customer checks "Join loyalty program" during checkout
3. PrestaShop module creates `customers` record with `prestashop_customer_id`

#### Strategy 2: POS-First (In-Store Enrollment)
Customer enrolls at POS, later creates PrestaShop account.

**Flow**:
1. Customer enrolls at POS → `customers` record created with `prestashop_customer_id = NULL`
2. Customer creates PrestaShop account with same email
3. Sync job detects match via `email_hash` and links accounts

#### Strategy 3: Simultaneous Accounts (Different Emails)
Customer has POS loyalty card and PrestaShop account with different emails.

**Flow**:
1. Both accounts exist separately
2. Customer contacts support to merge
3. Admin manually links accounts by setting `prestashop_customer_id`

### Duplicate Detection Query

```sql
-- Find potential duplicate by email
SELECT customer_id, prestashop_email, phone_number, enrollment_date
FROM customers
WHERE email_hash = encode(digest(lower('maria.garcia@example.com'), 'sha256'), 'hex')
    AND deleted_at IS NULL;

-- Find potential duplicate by phone
SELECT customer_id, prestashop_email, phone_number, enrollment_date
FROM customers
WHERE phone_hash = encode(digest(regexp_replace('+34612345678', '[^0-9]', '', 'g'), 'sha256'), 'hex')
    AND deleted_at IS NULL;
```

### Sync from PrestaShop

```sql
-- Sync customer updates from PrestaShop (runs every 5 minutes)
UPDATE customers c
SET 
    first_name = ps.firstname,
    last_name = ps.lastname,
    prestashop_email = ps.email,
    language_preference = CASE ps.id_lang WHEN 1 THEN 'es' WHEN 2 THEN 'ca' ELSE 'en' END,
    updated_at = NOW(),
    updated_by = 'prestashop_sync'
FROM prestashop_customers_view ps
WHERE c.prestashop_customer_id = ps.id_customer
    AND c.deleted_at IS NULL
    AND ps.deleted = 0
    AND (
        c.first_name != ps.firstname OR
        c.last_name != ps.lastname OR
        c.prestashop_email != ps.email
    );
```

## Duplicate Prevention

### Email Hash Generation

```sql
-- Trigger to generate email hash on INSERT/UPDATE
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

CREATE TRIGGER generate_customer_hashes BEFORE INSERT OR UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION generate_email_hash();
```

### Pre-Enrollment Duplicate Check

```sql
-- Check for existing customer before enrollment
WITH duplicate_check AS (
    SELECT customer_id
    FROM customers
    WHERE email_hash = encode(digest(lower($1), 'sha256'), 'hex')
        AND deleted_at IS NULL
    LIMIT 1
)
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM duplicate_check) THEN 'DUPLICATE_EMAIL'
        ELSE 'OK'
    END AS status,
    (SELECT customer_id FROM duplicate_check) AS existing_customer_id;
```

## GDPR Compliance

### Right to Access (Data Export)

```sql
-- Export all customer data
SELECT 
    c.customer_id,
    c.prestashop_customer_id,
    c.prestashop_email,
    c.first_name,
    c.last_name,
    c.phone_number,
    c.address_line1,
    c.city,
    c.postal_code,
    c.enrollment_date,
    c.account_status,
    c.gdpr_consent_date,
    c.marketing_consent,
    c.whatsapp_consent,
    la.current_balance_points,
    la.lifetime_earned_points,
    la.lifetime_redeemed_points
FROM customers c
LEFT JOIN loyalty_accounts la ON la.customer_id = c.customer_id
WHERE c.customer_id = $1;
```

### Right to Erasure (Deletion Request)

```sql
-- Soft delete customer (GDPR erasure)
UPDATE customers
SET 
    account_status = 'deleted',
    deleted_at = NOW(),
    deleted_by = 'gdpr_erasure_request',
    -- Optionally anonymize PII
    prestashop_email = 'deleted_' || customer_id || '@deleted.local',
    first_name = 'DELETED',
    last_name = 'DELETED',
    phone_number = NULL,
    address_line1 = NULL,
    address_line2 = NULL,
    city = NULL,
    postal_code = NULL,
    updated_at = NOW()
WHERE customer_id = $1
    AND deleted_at IS NULL;

-- Unassign cards
UPDATE cards
SET 
    customer_id = NULL,
    unassigned_date = NOW(),
    card_status = 'inactive',
    updated_at = NOW()
WHERE customer_id = $1;
```

**Note**: Loyalty ledger transactions are **NOT** deleted (required for financial audit).

### Right to Data Portability

```json
// Export customer data as JSON
{
  "customer_id": "cust-uuid-123",
  "email": "maria.garcia@example.com",
  "first_name": "María",
  "last_name": "García",
  "phone": "+34612345678",
  "enrollment_date": "2024-05-15T10:30:00Z",
  "loyalty": {
    "current_balance_points": 250000,
    "current_balance_eur": 25.00,
    "lifetime_earned": 1500000,
    "lifetime_redeemed": 800000
  },
  "consents": [
    {
      "type": "loyalty_program",
      "given": true,
      "date": "2024-05-15T10:30:00Z"
    },
    {
      "type": "marketing_email",
      "given": true,
      "date": "2024-05-15T10:30:00Z"
    }
  ]
}
```

## Common Queries

### Query 1: Find customer by email

```sql
SELECT customer_id, first_name, last_name, account_status
FROM customers
WHERE prestashop_email = LOWER($1)
    AND deleted_at IS NULL
LIMIT 1;
```

### Query 2: Find customer by card UID

```sql
SELECT c.customer_id, c.first_name, c.last_name, c.prestashop_email
FROM customers c
JOIN cards card ON card.customer_id = c.customer_id
WHERE card.card_uid = $1
    AND card.card_status = 'active'
    AND c.deleted_at IS NULL
LIMIT 1;
```

### Query 3: Find customer by phone

```sql
SELECT customer_id, first_name, last_name, prestashop_email
FROM customers
WHERE phone_hash = encode(digest(regexp_replace($1, '[^0-9]', '', 'g'), 'sha256'), 'hex')
    AND deleted_at IS NULL
LIMIT 1;
```

### Query 4: List inactive customers

```sql
SELECT 
    customer_id,
    first_name,
    last_name,
    prestashop_email,
    last_transaction_date,
    NOW() - last_transaction_date AS days_inactive
FROM customers c
JOIN loyalty_accounts la ON la.customer_id = c.customer_id
WHERE account_status = 'inactive'
    AND deleted_at IS NULL
ORDER BY last_transaction_date ASC;
```

## Related Documents

### Dependencies
- `05_data/DATA_MODEL.md` - Full database schema
- `02_architecture/DATABASE_DESIGN.md` - Database architecture
- `04_integrations/PRESTASHOP_MODULE.md` - PrestaShop customer sync
- `06_security/GDPR_COMPLIANCE.md` - GDPR requirements

### Dependents
- `05_data/LOYALTY_LEDGER.md` - References customer_id
- `05_data/CARD_MODEL.md` - Links cards to customers
- `05_data/CONSENT_RECORDS.md` - Tracks customer consents
- `05_data/ORDER_MAPPING.md` - Links orders to customers

### Related Features
- `03_features/CARD_ENROLLMENT.md` - Creates customer records
- `03_features/BALANCE_QUERY.md` - Queries customer balance
- `03_features/EARN_POINTS_POS.md` - Updates customer activity
- `03_features/REDEEM_POINTS_POS.md` - Updates customer activity

## Open Questions / TODOs

### TODO: Customer Merge Tool
**Status**: Not implemented  
**Required by**: Phase 2  
**Description**: Admin tool to merge duplicate customer accounts

### TODO: Customer Tier System
**Status**: Planned for Phase 3  
**Required by**: Q4 2025  
**Description**: Implement bronze/silver/gold customer tiers based on activity

### Open Question: Email Change Handling
**Question**: What happens if customer changes email in PrestaShop?  
**Context**: Should we update loyalty record or keep original email?  
**Decision Required By**: Before PrestaShop sync launch
