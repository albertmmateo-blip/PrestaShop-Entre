# Data Model: Consent Records (GDPR Compliance)

## Purpose

Define the consent records entity for tracking customer consent to loyalty program participation and marketing communications, ensuring GDPR compliance through complete audit trail, consent lifecycle management, and withdrawal handling.

## Scope

### In Scope
- Consent records entity schema with all consent types
- GDPR consent types (loyalty program, marketing email, SMS, WhatsApp)
- Consent lifecycle (given, withdrawn, historical versions)
- Consent methods (POS enrollment, online signup, email link, account settings)
- Audit trail (consent version, IP address, user agent, timestamp)
- Withdrawal tracking and timestamps
- Immutable consent history (no DELETE)
- Query patterns for current consent status

### Out of Scope
- Consent form UI/UX (covered in feature documents)
- Email marketing platform integration (covered in integrations)
- WhatsApp messaging API (covered in WHATSAPP_API.md)
- GDPR data export functionality (covered in CUSTOMER_MODEL.md)
- Legal consent text versioning management (separate CMS)

## Consent Records Schema

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
        (withdrawn = FALSE AND withdrawal_date IS NULL AND withdrawal_method IS NULL) OR
        (withdrawn = TRUE AND withdrawal_date IS NOT NULL AND withdrawal_method IS NOT NULL)
    )
);

-- Indexes for performance
CREATE INDEX idx_consent_customer ON consent_records(customer_id, consent_date DESC);
CREATE INDEX idx_consent_type_status ON consent_records(consent_type, consent_given, withdrawn);
CREATE INDEX idx_consent_withdrawal ON consent_records(withdrawal_date DESC) WHERE withdrawn = TRUE;
CREATE INDEX idx_consent_active ON consent_records(customer_id, consent_type) WHERE consent_given = TRUE AND withdrawn = FALSE;

-- Comments
COMMENT ON TABLE consent_records IS 'GDPR consent audit trail for loyalty and marketing';
COMMENT ON COLUMN consent_records.consent_version IS 'Version of consent form/policy (e.g., v1.0, v2.1)';
COMMENT ON COLUMN consent_records.consent_text IS 'Full text of consent given (for audit purposes)';
COMMENT ON COLUMN consent_records.consent_ip_address IS 'IP address from which consent was given';
COMMENT ON COLUMN consent_records.consent_user_agent IS 'Browser/app user agent string';
```

## Field Definitions

### consent_id (UUID)
Internal primary identifier for consent record. Generated as UUIDv4.

**Properties**:
- Used in internal queries
- Immutable once created
- Never displayed to customers

### customer_id (UUID)
Foreign key to customer who gave/withdrew consent.

**Properties**:
- NOT NULL
- ON DELETE CASCADE (if customer deleted, consent records also deleted for cleanup)
- Used to query all consents for a customer

### consent_type (VARCHAR 50)
Type of consent being tracked.

**Values**:
- `loyalty_program` - Consent to participate in loyalty program and process transaction data
- `marketing_email` - Consent to receive promotional emails
- `marketing_sms` - Consent to receive promotional SMS messages
- `marketing_whatsapp` - Consent to receive promotional WhatsApp messages
- `data_processing` - General consent to process personal data (required by GDPR)

**Properties**:
- NOT NULL
- Multiple records can exist for same `customer_id` and `consent_type` (historical versions)

### consent_given (BOOLEAN)
Whether consent was given or denied.

**Properties**:
- NOT NULL
- `TRUE` - Customer consented
- `FALSE` - Customer explicitly declined (rare, usually just not asked)

**Note**: Most records have `consent_given = TRUE`. `FALSE` records are created when customer explicitly declines during enrollment.

### consent_date (TIMESTAMP WITH TIME ZONE)
Date and time when consent was given or declined.

**Properties**:
- NOT NULL with DEFAULT NOW()
- Stored in UTC
- Used for audit trail
- Determines which consent version is "current"

### consent_method (VARCHAR 50)
Method through which consent was obtained.

**Values**:
- `pos_enrollment` - Customer gave consent at POS during card enrollment
- `online_signup` - Customer gave consent during PrestaShop account creation
- `email_link` - Customer clicked consent link in email
- `account_settings` - Customer updated consent in PrestaShop account settings
- `customer_service` - Customer gave consent via phone/in-person to customer service rep

**Properties**:
- NOT NULL
- Used for compliance audits
- Helps understand consent quality and user intent

### consent_ip_address (INET)
IP address from which consent was given.

**Properties**:
- OPTIONAL (NULL for POS enrollments without internet)
- Stored for audit purposes
- Used to detect fraudulent consents
- Format: IPv4 or IPv6 (e.g., `192.168.1.100`, `2001:db8::1`)

### consent_user_agent (TEXT)
Browser or app user agent string.

**Properties**:
- OPTIONAL (NULL for POS enrollments)
- Stored for audit purposes
- Example: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...`

### withdrawn (BOOLEAN)
Whether this consent has been withdrawn.

**Properties**:
- NOT NULL with DEFAULT FALSE
- Set to TRUE when customer withdraws consent
- Once withdrawn, consent record is immutable (never reactivated)

**Note**: If customer re-consents, a **new** consent record is created (not UPDATE).

### withdrawal_date (TIMESTAMP WITH TIME ZONE)
Date and time when consent was withdrawn.

**Properties**:
- NULL if not withdrawn
- NOT NULL if `withdrawn = TRUE`
- Stored in UTC
- Used for compliance reporting

### withdrawal_method (VARCHAR 50)
Method through which consent was withdrawn.

**Values**:
- `account_settings` - Customer withdrew via PrestaShop account settings
- `email_link` - Customer clicked unsubscribe link in email
- `customer_service` - Customer requested withdrawal via phone/in-person
- `right_to_be_forgotten` - Customer invoked GDPR right to erasure

**Properties**:
- NULL if not withdrawn
- NOT NULL if `withdrawn = TRUE`
- Used for compliance audits

### consent_version (VARCHAR 20)
Version identifier for consent form/policy.

**Format**: `v1.0`, `v2.1`, `v2024.02.15`

**Properties**:
- NOT NULL
- Tracks which version of consent form customer agreed to
- Changes when legal text is updated
- Used to identify customers who need to re-consent to new version

### consent_text (TEXT)
Full text of the consent that customer agreed to.

**Properties**:
- NOT NULL
- Stored verbatim from consent form
- Includes all legal language
- Immutable snapshot of what customer saw and agreed to
- Used for legal disputes and audits

**Example**:
```
I consent to participate in the Loyalty Program and agree to the processing of my transaction data to earn and redeem points. I understand that my data will be stored securely and used only for loyalty program purposes as described in the Privacy Policy available at www.example.com/privacy.
```

### created_at (TIMESTAMP WITH TIME ZONE)
Timestamp when consent record was created in database.

**Properties**:
- NOT NULL with DEFAULT NOW()
- Stored in UTC
- Usually same as `consent_date` (but may differ for historical imports)

### created_by (VARCHAR 100)
Actor who created the consent record.

**Properties**:
- OPTIONAL
- Examples: `'pos_agent_v1.2'`, `'prestashop_module_v1.0'`, `'admin_user_john'`
- Used for audit trail

## Consent Lifecycle

### 1. Initial Consent (POS Enrollment)

```sql
-- Customer enrolls at POS and gives consent
INSERT INTO consent_records (
    customer_id,
    consent_type,
    consent_given,
    consent_date,
    consent_method,
    consent_version,
    consent_text,
    created_by
) VALUES (
    'cust-uuid-123',
    'loyalty_program',
    TRUE,
    NOW(),
    'pos_enrollment',
    'v1.0',
    'I consent to participate in the Loyalty Program...',
    'pos_agent_v1.2'
);

-- Customer also opts into marketing emails
INSERT INTO consent_records (
    customer_id,
    consent_type,
    consent_given,
    consent_date,
    consent_method,
    consent_version,
    consent_text,
    created_by
) VALUES (
    'cust-uuid-123',
    'marketing_email',
    TRUE,
    NOW(),
    'pos_enrollment',
    'v1.0',
    'I consent to receive promotional emails...',
    'pos_agent_v1.2'
);
```

### 2. Additional Consent (Online Account Settings)

```sql
-- Customer later opts into WhatsApp marketing
INSERT INTO consent_records (
    customer_id,
    consent_type,
    consent_given,
    consent_date,
    consent_method,
    consent_ip_address,
    consent_user_agent,
    consent_version,
    consent_text,
    created_by
) VALUES (
    'cust-uuid-123',
    'marketing_whatsapp',
    TRUE,
    NOW(),
    'account_settings',
    '192.168.1.100',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
    'v1.0',
    'I consent to receive promotional messages via WhatsApp...',
    'prestashop_module_v1.0'
);
```

### 3. Consent Withdrawal (Email Unsubscribe)

```sql
-- Customer clicks unsubscribe link in email
INSERT INTO consent_records (
    customer_id,
    consent_type,
    consent_given,
    consent_date,
    consent_method,
    withdrawn,
    withdrawal_date,
    withdrawal_method,
    consent_ip_address,
    consent_user_agent,
    consent_version,
    consent_text,
    created_by
) VALUES (
    'cust-uuid-123',
    'marketing_email',
    FALSE, -- Withdrawal is recorded as consent_given = FALSE
    NOW(),
    'email_link',
    TRUE,
    NOW(),
    'email_link',
    '192.168.1.100',
    'Mozilla/5.0...',
    'v1.0',
    'Withdrawal of consent to receive promotional emails',
    'email_unsubscribe_service'
);
```

**Alternative Pattern** (update existing record - **NOT RECOMMENDED** due to immutability):
```sql
-- ❌ WRONG - Do not UPDATE consent records
UPDATE consent_records
SET withdrawn = TRUE, withdrawal_date = NOW()
WHERE customer_id = 'cust-uuid-123' AND consent_type = 'marketing_email';

-- ✅ CORRECT - Insert new withdrawal record
INSERT INTO consent_records (customer_id, consent_type, consent_given, withdrawn, ...)
VALUES ('cust-uuid-123', 'marketing_email', FALSE, TRUE, ...);
```

### 4. Re-Consent After Withdrawal

```sql
-- Customer changes mind and re-consents to email marketing
INSERT INTO consent_records (
    customer_id,
    consent_type,
    consent_given,
    consent_date,
    consent_method,
    consent_ip_address,
    consent_version,
    consent_text,
    created_by
) VALUES (
    'cust-uuid-123',
    'marketing_email',
    TRUE,
    NOW(),
    'account_settings',
    '192.168.1.100',
    'v2.0', -- New consent version
    'I consent to receive promotional emails (updated policy)...',
    'prestashop_module_v1.0'
);
```

### 5. GDPR Right to Be Forgotten

```sql
-- Customer invokes right to erasure (entire account deleted)
-- This triggers CASCADE delete of all consent records
DELETE FROM customers WHERE customer_id = 'cust-uuid-123';

-- Or, if keeping customer record but marking as deleted:
INSERT INTO consent_records (
    customer_id,
    consent_type,
    consent_given,
    consent_date,
    consent_method,
    withdrawn,
    withdrawal_date,
    withdrawal_method,
    consent_version,
    consent_text,
    created_by
) VALUES (
    'cust-uuid-123',
    'data_processing',
    FALSE,
    NOW(),
    'customer_service',
    TRUE,
    NOW(),
    'right_to_be_forgotten',
    'v1.0',
    'Withdrawal of all consents under GDPR right to erasure',
    'admin_user_sarah'
);
```

## Current Consent Status Queries

### Query 1: Get current consent status for customer

```sql
-- Get latest consent record for each consent type
SELECT DISTINCT ON (consent_type)
    consent_type,
    consent_given,
    withdrawn,
    consent_date,
    withdrawal_date,
    consent_version
FROM consent_records
WHERE customer_id = $1
ORDER BY consent_type, consent_date DESC;
```

**Result Example**:
```
consent_type         | consent_given | withdrawn | consent_date        | consent_version
---------------------|---------------|-----------|---------------------|----------------
loyalty_program      | TRUE          | FALSE     | 2024-05-15 10:30:00 | v1.0
marketing_email      | TRUE          | TRUE      | 2024-08-10 14:20:00 | v1.0
marketing_whatsapp   | TRUE          | FALSE     | 2024-06-20 09:15:00 | v1.0
```

### Query 2: Check if customer has active consent for specific type

```sql
-- Check if customer has active marketing email consent
SELECT EXISTS (
    SELECT 1
    FROM consent_records cr
    WHERE cr.customer_id = $1
        AND cr.consent_type = 'marketing_email'
        AND cr.consent_given = TRUE
        AND cr.withdrawn = FALSE
        AND cr.consent_date = (
            SELECT MAX(consent_date)
            FROM consent_records
            WHERE customer_id = $1 AND consent_type = 'marketing_email'
        )
) AS has_active_consent;
```

### Query 3: Get all customers with active marketing consent

```sql
-- Find customers who can receive marketing emails
SELECT DISTINCT
    c.customer_id,
    c.first_name,
    c.last_name,
    c.prestashop_email
FROM customers c
JOIN consent_records cr ON cr.customer_id = c.customer_id
WHERE cr.consent_type = 'marketing_email'
    AND cr.consent_given = TRUE
    AND cr.withdrawn = FALSE
    AND cr.consent_date = (
        SELECT MAX(consent_date)
        FROM consent_records
        WHERE customer_id = c.customer_id AND consent_type = 'marketing_email'
    )
    AND c.deleted_at IS NULL;
```

### Query 4: Consent audit trail for customer

```sql
-- Get full consent history for customer
SELECT 
    consent_id,
    consent_type,
    consent_given,
    consent_date,
    consent_method,
    withdrawn,
    withdrawal_date,
    withdrawal_method,
    consent_version,
    consent_ip_address
FROM consent_records
WHERE customer_id = $1
ORDER BY consent_date DESC;
```

## GDPR Compliance Queries

### Query 5: Customers needing re-consent (new policy version)

```sql
-- Find customers with old consent version
SELECT DISTINCT
    c.customer_id,
    c.first_name,
    c.last_name,
    c.prestashop_email,
    cr.consent_version AS current_version,
    cr.consent_date
FROM customers c
JOIN consent_records cr ON cr.customer_id = c.customer_id
WHERE cr.consent_type = 'loyalty_program'
    AND cr.consent_version != 'v2.0' -- New version
    AND cr.consent_given = TRUE
    AND cr.withdrawn = FALSE
    AND cr.consent_date = (
        SELECT MAX(consent_date)
        FROM consent_records
        WHERE customer_id = c.customer_id AND consent_type = 'loyalty_program'
    )
    AND c.deleted_at IS NULL;
```

### Query 6: Consent withdrawal report (last 30 days)

```sql
-- GDPR compliance report: consents withdrawn in last 30 days
SELECT 
    DATE(withdrawal_date) AS withdrawal_day,
    consent_type,
    withdrawal_method,
    COUNT(*) AS total_withdrawals
FROM consent_records
WHERE withdrawn = TRUE
    AND withdrawal_date >= NOW() - INTERVAL '30 days'
GROUP BY DATE(withdrawal_date), consent_type, withdrawal_method
ORDER BY withdrawal_day DESC, consent_type;
```

### Query 7: Consent given by method (audit)

```sql
-- Distribution of consent methods
SELECT 
    consent_method,
    consent_type,
    COUNT(*) AS total_consents,
    COUNT(CASE WHEN withdrawn = TRUE THEN 1 END) AS withdrawals
FROM consent_records
WHERE consent_given = TRUE
GROUP BY consent_method, consent_type
ORDER BY consent_method, consent_type;
```

## Consent Validation

### Function: Check active consent

```sql
-- Function to check if customer has active consent
CREATE OR REPLACE FUNCTION has_active_consent(
    p_customer_id UUID,
    p_consent_type VARCHAR
)
RETURNS BOOLEAN AS $$
DECLARE
    has_consent BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1
        FROM consent_records cr
        WHERE cr.customer_id = p_customer_id
            AND cr.consent_type = p_consent_type
            AND cr.consent_given = TRUE
            AND cr.withdrawn = FALSE
            AND cr.consent_date = (
                SELECT MAX(consent_date)
                FROM consent_records
                WHERE customer_id = p_customer_id AND consent_type = p_consent_type
            )
    ) INTO has_consent;
    
    RETURN has_consent;
END;
$$ LANGUAGE plpgsql;

-- Usage
SELECT has_active_consent('cust-uuid-123', 'marketing_email');
-- Returns: TRUE or FALSE
```

## Consent Text Examples

### Loyalty Program Consent (v1.0)
```
I consent to participate in the Loyalty Program operated by [Company Name]. I understand that:
- My purchase transactions will be recorded to calculate loyalty points
- My personal data (name, email, phone) will be stored and processed
- I can earn points on purchases and redeem them for discounts
- Points expire after 12 months of inactivity
- I can withdraw my consent and close my account at any time

For full details, see our Privacy Policy at www.example.com/privacy
```

### Marketing Email Consent (v1.0)
```
I consent to receive promotional emails from [Company Name] including:
- Special offers and discounts
- New product announcements
- Loyalty program updates

I can unsubscribe at any time by clicking the unsubscribe link in any email or by updating my preferences in my account settings.
```

### Marketing WhatsApp Consent (v1.0)
```
I consent to receive promotional messages via WhatsApp from [Company Name] to the phone number I provided. Messages may include special offers, loyalty updates, and product recommendations. I can opt out at any time by replying STOP or updating my account settings.

Standard message rates may apply.
```

## Edge Cases

### Edge Case 1: Customer withdraws then re-consents multiple times
**Behavior**: Create new consent record for each consent/withdrawal. Query returns most recent status.

### Edge Case 2: Customer gives consent at POS without IP address
**Behavior**: `consent_ip_address` and `consent_user_agent` are NULL. Still valid consent.

### Edge Case 3: Consent policy updated (v1.0 → v2.0)
**Behavior**: Existing consents remain valid but flagged as old version. Customers notified to re-consent.

### Edge Case 4: Customer deletes account (GDPR)
**Behavior**: Consent records CASCADE deleted with customer record (or retained if soft delete used).

## Related Documents

### Dependencies
- `05_data/DATA_MODEL.md` - Full database schema
- `05_data/CUSTOMER_MODEL.md` - Customer entity that consents link to
- `06_security/GDPR_COMPLIANCE.md` - GDPR legal requirements
- `06_security/DATA_PRIVACY.md` - Privacy and data protection

### Dependents
- `03_features/CARD_ENROLLMENT.md` - Creates initial consent records
- `04_integrations/PRESTASHOP_MODULE.md` - Syncs consent settings
- `04_integrations/WHATSAPP_API.md` - Checks WhatsApp consent before messaging

### Related Features
- `03_features/MARKETING_CONSENT.md` - Consent management UI
- `07_operations/GDPR_TOOLS.md` - GDPR data export and deletion tools

## Open Questions / TODOs

### TODO: Consent re-confirmation flow
**Status**: Not implemented  
**Required by**: When policy updates  
**Description**: Automated flow to request re-consent from customers with old consent version

### TODO: Consent heatmap analytics
**Status**: Future enhancement  
**Required by**: Phase 3  
**Description**: Analytics dashboard showing consent rates by method, withdrawal trends, etc.

### Open Question: Consent retention period
**Question**: How long to retain withdrawn consent records?  
**Context**: GDPR requires retention for legal defense but not indefinitely  
**Decision Required By**: Consult with legal team before launch
