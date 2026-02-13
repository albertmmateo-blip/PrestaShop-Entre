# Data Model: Card Entity (NFC Loyalty Cards)

## Purpose

Define the NFC loyalty card entity structure including unique identifiers (UID, card number), status tracking, QR code support, customer assignment, and card lifecycle management for physical card operations at POS terminals.

## Scope

### In Scope
- Card entity schema with all fields and constraints
- Card UID (7-byte NFC identifier) and card number format
- Card status lifecycle (inactive, active, lost, stolen, expired, replaced)
- QR code generation and storage for non-NFC devices
- Customer assignment and unassignment
- Printing batch tracking for inventory management
- Card activation and expiration
- Card replacement process
- Soft delete implementation

### Out of Scope
- NFC reader hardware integration (covered in NFC_READER.md)
- Card enrollment process (covered in CARD_ENROLLMENT.md feature)
- Card tap transaction processing (covered in EARN_POINTS_POS.md)
- Physical card printing specifications (vendor-specific)
- Card inventory management system (future enhancement)

## Card Schema

```sql
CREATE TABLE cards (
    -- Primary identifier
    card_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Card identifiers
    card_uid VARCHAR(14) NOT NULL UNIQUE,
    card_number VARCHAR(20) NOT NULL UNIQUE,
    
    -- QR code for non-NFC devices
    qr_code_url TEXT,
    qr_code_data VARCHAR(255),
    
    -- Card status
    card_status VARCHAR(20) NOT NULL DEFAULT 'inactive' 
        CHECK (card_status IN ('active', 'inactive', 'lost', 'stolen', 'expired', 'replaced')),
    
    -- Customer association
    customer_id UUID REFERENCES customers(customer_id) ON DELETE SET NULL,
    assigned_date TIMESTAMP WITH TIME ZONE,
    unassigned_date TIMESTAMP WITH TIME ZONE,
    
    -- Physical card info
    printing_batch VARCHAR(50),
    printing_date DATE,
    printed_by VARCHAR(100),
    
    -- Card lifecycle
    activated_date TIMESTAMP WITH TIME ZONE,
    expiration_date DATE,
    replacement_card_id UUID REFERENCES cards(card_id) ON DELETE SET NULL,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    
    -- Soft delete
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by VARCHAR(100),
    
    -- Constraints
    CONSTRAINT chk_card_assigned CHECK (
        (customer_id IS NULL AND assigned_date IS NULL) OR
        (customer_id IS NOT NULL AND assigned_date IS NOT NULL)
    )
);

-- Indexes for performance
CREATE INDEX idx_cards_uid ON cards(card_uid) WHERE deleted_at IS NULL;
CREATE INDEX idx_cards_number ON cards(card_number) WHERE deleted_at IS NULL;
CREATE INDEX idx_cards_customer ON cards(customer_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_cards_status ON cards(card_status) WHERE deleted_at IS NULL;
CREATE INDEX idx_cards_printing_batch ON cards(printing_batch);
CREATE INDEX idx_cards_expiration ON cards(expiration_date) WHERE expiration_date IS NOT NULL;

-- Comments
COMMENT ON TABLE cards IS 'NFC loyalty cards with UID tracking and customer assignment';
COMMENT ON COLUMN cards.card_uid IS 'Unique 7-byte NFC UID in hex format (e.g., 04A1B2C3D4E5F6)';
COMMENT ON COLUMN cards.card_number IS 'Human-readable card number format: LC-XXXXXXXX';
COMMENT ON COLUMN cards.qr_code_data IS 'QR code payload for non-NFC scanning';
```

## Field Definitions

### card_id (UUID)
Internal primary identifier for card entity. Generated as UUIDv4.

**Properties**:
- Never displayed on physical card
- Used in internal database relationships
- Immutable once created

### card_uid (VARCHAR 14)
NFC chip's unique identifier (UID).

**Format**: 7 bytes encoded as 14 hexadecimal characters  
**Example**: `04A1B2C3D4E5F6`

**Properties**:
- UNIQUE constraint (no two cards can have same UID)
- NOT NULL
- Immutable (burned into NFC chip at manufacturing)
- Case-insensitive (stored as uppercase)
- Read from NFC chip by ACS ACR122U reader

**Validation**:
```sql
CONSTRAINT chk_card_uid_format CHECK (
    card_uid ~ '^[0-9A-F]{14}$'
)
```

**Reading UID Example**:
```javascript
// POS Windows Agent reads UID from NFC reader
const uid = reader.readUID(); // Returns: "04A1B2C3D4E5F6"
```

### card_number (VARCHAR 20)
Human-readable card number printed on physical card.

**Format**: `LC-XXXXXXXX` where X is 0-9 digit  
**Example**: `LC-00012345`

**Properties**:
- UNIQUE constraint (no duplicate card numbers)
- NOT NULL
- Printed on card for customer reference
- Used for manual entry if NFC reader fails
- Sequential numbering (incremented for each batch)

**Generation Algorithm**:
```sql
-- Generate next card number
SELECT 'LC-' || LPAD((COALESCE(MAX(SUBSTRING(card_number FROM 4)::INTEGER), 0) + 1)::TEXT, 8, '0')
FROM cards
WHERE card_number LIKE 'LC-%';
-- Returns: 'LC-00012346'
```

### qr_code_url (TEXT)
URL pointing to hosted QR code image.

**Format**: `https://cdn.example.com/qr/LC-00012345.png`

**Properties**:
- OPTIONAL (only generated if QR feature enabled)
- Publicly accessible URL
- QR code image generated from `qr_code_data`
- Used for printing on cards if NFC fails

### qr_code_data (VARCHAR 255)
Data encoded in QR code.

**Format**: `LOYALTY:LC-00012345:04A1B2C3D4E5F6`

**Properties**:
- OPTIONAL
- Contains card number and UID for verification
- Scanned by mobile apps or POS scanner
- Used as fallback if NFC not supported

**Generation**:
```javascript
// Generate QR code data
const qrData = `LOYALTY:${cardNumber}:${cardUID}`;
// Example: "LOYALTY:LC-00012345:04A1B2C3D4E5F6"
```

### card_status (VARCHAR 20)
Current lifecycle status of the card.

**Values**:
- `inactive` - Card printed but not yet assigned to customer
- `active` - Card assigned to customer and usable
- `lost` - Customer reported card lost (temporarily disabled)
- `stolen` - Customer reported card stolen (permanently disabled)
- `expired` - Card past expiration date (can be replaced)
- `replaced` - Card replaced by new card (old card disabled)

**State Transitions**:
```
inactive → active (customer enrollment)
active → lost (customer reports lost)
lost → active (card found, reactivated)
active → stolen (customer reports stolen)
active → expired (past expiration_date)
active/lost/expired → replaced (new card issued)
stolen/replaced → never reactivated
```

### customer_id (UUID)
Foreign key to customer who owns the card.

**Properties**:
- NULL for unassigned cards (`inactive` status)
- NOT NULL for assigned cards (`active` status)
- ON DELETE SET NULL (if customer deleted, card becomes unassigned)
- One customer can have multiple cards (though discouraged)

### assigned_date, unassigned_date (TIMESTAMP WITH TIME ZONE)
Timestamps for customer assignment lifecycle.

**Properties**:
- `assigned_date`: Set when card assigned to customer during enrollment
- `unassigned_date`: Set when card unassigned (e.g., replacement, customer deletion)
- Both stored in UTC
- Used for audit trail

**Constraint**: If `customer_id` is set, `assigned_date` must also be set.

### printing_batch (VARCHAR 50)
Identifier for card printing batch.

**Format**: `BATCH-YYYYMMDD-NNN`  
**Example**: `BATCH-20250115-001`

**Properties**:
- Used for inventory tracking
- All cards printed together share same batch ID
- Helps identify defective batches
- Referenced in printing logs

### printing_date, printed_by (DATE, VARCHAR 100)
Audit trail for card production.

**Properties**:
- `printing_date`: Date when card was physically printed
- `printed_by`: Operator or system that printed the card
- Used for quality control and inventory management

### activated_date (TIMESTAMP WITH TIME ZONE)
When card was activated (transitioned from `inactive` to `active`).

**Properties**:
- Set during customer enrollment
- Stored in UTC
- Used to track card usage duration

### expiration_date (DATE)
Date when card expires and needs replacement.

**Properties**:
- OPTIONAL (some cards may not expire)
- Typical expiration: 5 years from printing date
- Automatic job checks for expired cards daily
- Customer notified 30 days before expiration

**Expiration Check**:
```sql
-- Find cards expiring in next 30 days
SELECT 
    c.card_id,
    c.card_number,
    c.expiration_date,
    cust.first_name,
    cust.last_name,
    cust.prestashop_email
FROM cards c
JOIN customers cust ON cust.customer_id = c.customer_id
WHERE c.expiration_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
    AND c.card_status = 'active'
    AND c.deleted_at IS NULL;
```

### replacement_card_id (UUID)
Foreign key to the card that replaces this card.

**Properties**:
- NULL for current active cards
- Set when card is replaced (status → `replaced`)
- Points to new card's `card_id`
- Creates replacement chain for audit trail

**Replacement Chain Query**:
```sql
-- Find replacement history for a card
WITH RECURSIVE replacement_chain AS (
    SELECT card_id, card_number, replacement_card_id, 1 AS depth
    FROM cards
    WHERE card_id = $1
    
    UNION ALL
    
    SELECT c.card_id, c.card_number, c.replacement_card_id, rc.depth + 1
    FROM cards c
    JOIN replacement_chain rc ON rc.replacement_card_id = c.card_id
)
SELECT * FROM replacement_chain ORDER BY depth;
```

## Card Number Format

### Format Specification

**Pattern**: `LC-XXXXXXXX`

**Components**:
- `LC`: Loyalty Card prefix (constant)
- `-`: Separator (constant)
- `XXXXXXXX`: 8-digit zero-padded sequential number

**Examples**:
- `LC-00000001` (first card)
- `LC-00012345` (card 12,345)
- `LC-99999999` (last card before rollover)

### Generation Logic

```sql
-- Function to generate next card number
CREATE OR REPLACE FUNCTION generate_next_card_number()
RETURNS VARCHAR(20) AS $$
DECLARE
    next_num INTEGER;
BEGIN
    SELECT COALESCE(MAX(SUBSTRING(card_number FROM 4)::INTEGER), 0) + 1
    INTO next_num
    FROM cards
    WHERE card_number ~ '^LC-[0-9]{8}$';
    
    RETURN 'LC-' || LPAD(next_num::TEXT, 8, '0');
END;
$$ LANGUAGE plpgsql;

-- Usage
SELECT generate_next_card_number(); -- Returns: 'LC-00012346'
```

### Printing on Physical Card

**Front of Card**:
```
┌─────────────────────────┐
│                         │
│   Loyalty Card          │
│                         │
│   LC-00012345           │ ← Card number printed here
│                         │
│   [QR Code]             │ ← Optional QR code
│                         │
└─────────────────────────┘
```

**Back of Card**:
```
┌─────────────────────────┐
│                         │
│   For support, visit:   │
│   www.example.com       │
│                         │
│   UID: 04A1B2C3D4E5F6   │ ← Optional UID print
│                         │
└─────────────────────────┘
```

## Card Lifecycle

### 1. Card Creation (Printing Batch)

```sql
-- Bulk insert for printing batch of 100 cards
INSERT INTO cards (
    card_uid,
    card_number,
    card_status,
    printing_batch,
    printing_date,
    printed_by,
    created_by
)
SELECT 
    uid,
    card_num,
    'inactive',
    'BATCH-20250215-001',
    '2025-02-15',
    'printer_operator_jane',
    'card_printing_service'
FROM (VALUES
    ('04A1B2C3D4E5F6', 'LC-00012345'),
    ('04A1B2C3D4E5F7', 'LC-00012346'),
    ('04A1B2C3D4E5F8', 'LC-00012347')
    -- ... 97 more cards
) AS batch_data(uid, card_num);
```

### 2. Card Assignment (Enrollment)

```sql
-- Assign card to customer during enrollment
UPDATE cards
SET 
    customer_id = 'cust-uuid-123',
    assigned_date = NOW(),
    activated_date = NOW(),
    card_status = 'active',
    expiration_date = CURRENT_DATE + INTERVAL '5 years',
    updated_at = NOW(),
    updated_by = 'pos_agent_v1.2'
WHERE card_uid = '04A1B2C3D4E5F6'
    AND card_status = 'inactive'
    AND customer_id IS NULL;
```

### 3. Card Loss Report

```sql
-- Customer reports card lost
UPDATE cards
SET 
    card_status = 'lost',
    updated_at = NOW(),
    updated_by = 'customer_service_rep'
WHERE card_id = 'card-uuid-456'
    AND card_status = 'active'
    AND customer_id = 'cust-uuid-123';
```

### 4. Card Found and Reactivation

```sql
-- Customer found lost card, reactivate it
UPDATE cards
SET 
    card_status = 'active',
    updated_at = NOW(),
    updated_by = 'customer_service_rep'
WHERE card_id = 'card-uuid-456'
    AND card_status = 'lost'
    AND customer_id = 'cust-uuid-123';
```

### 5. Card Replacement

```sql
-- Step 1: Create new card and assign to customer
INSERT INTO cards (
    card_uid,
    card_number,
    card_status,
    customer_id,
    assigned_date,
    activated_date,
    expiration_date,
    printing_batch,
    created_by
) VALUES (
    '04B2C3D4E5F6G7',
    'LC-00012500',
    'active',
    'cust-uuid-123',
    NOW(),
    NOW(),
    CURRENT_DATE + INTERVAL '5 years',
    'BATCH-20250220-002',
    'customer_service_rep'
)
RETURNING card_id INTO new_card_id;

-- Step 2: Mark old card as replaced
UPDATE cards
SET 
    card_status = 'replaced',
    unassigned_date = NOW(),
    replacement_card_id = new_card_id,
    updated_at = NOW(),
    updated_by = 'customer_service_rep'
WHERE card_id = 'old-card-uuid-456'
    AND customer_id = 'cust-uuid-123';
```

### 6. Card Expiration (Automatic)

```sql
-- Nightly job to expire cards
UPDATE cards
SET 
    card_status = 'expired',
    updated_at = NOW(),
    updated_by = 'expiration_job'
WHERE expiration_date < CURRENT_DATE
    AND card_status = 'active'
    AND deleted_at IS NULL;
```

## QR Code Support

### QR Code Generation

```javascript
// Generate QR code for card
const QRCode = require('qrcode');

async function generateCardQRCode(cardNumber, cardUID) {
    const qrData = `LOYALTY:${cardNumber}:${cardUID}`;
    
    // Generate QR code image
    const qrCodeBuffer = await QRCode.toBuffer(qrData, {
        errorCorrectionLevel: 'H',
        type: 'image/png',
        width: 300,
        margin: 1
    });
    
    // Upload to CDN
    const qrCodeUrl = await uploadToCDN(qrCodeBuffer, `qr/${cardNumber}.png`);
    
    // Update database
    await db.query(
        'UPDATE cards SET qr_code_data = $1, qr_code_url = $2 WHERE card_number = $3',
        [qrData, qrCodeUrl, cardNumber]
    );
    
    return { qrData, qrCodeUrl };
}
```

### QR Code Scanning

```javascript
// POS scans QR code
const scannedQRData = scanner.read(); // "LOYALTY:LC-00012345:04A1B2C3D4E5F6"

// Parse QR data
const [prefix, cardNumber, cardUID] = scannedQRData.split(':');

if (prefix !== 'LOYALTY') {
    throw new Error('Invalid QR code format');
}

// Lookup card by UID (primary) or card number (fallback)
const card = await db.query(
    'SELECT * FROM cards WHERE card_uid = $1 OR card_number = $2',
    [cardUID, cardNumber]
);
```

## Common Queries

### Query 1: Find card by UID

```sql
SELECT 
    c.card_id,
    c.card_uid,
    c.card_number,
    c.card_status,
    c.customer_id,
    cust.first_name,
    cust.last_name
FROM cards c
LEFT JOIN customers cust ON cust.customer_id = c.customer_id
WHERE c.card_uid = $1
    AND c.deleted_at IS NULL;
```

### Query 2: Find cards by customer

```sql
SELECT 
    card_id,
    card_uid,
    card_number,
    card_status,
    assigned_date,
    expiration_date
FROM cards
WHERE customer_id = $1
    AND deleted_at IS NULL
ORDER BY assigned_date DESC;
```

### Query 3: Find inactive cards (available for assignment)

```sql
SELECT 
    card_id,
    card_uid,
    card_number,
    printing_batch,
    printing_date
FROM cards
WHERE card_status = 'inactive'
    AND customer_id IS NULL
    AND deleted_at IS NULL
ORDER BY created_at ASC
LIMIT 100;
```

### Query 4: Find cards expiring soon

```sql
SELECT 
    c.card_id,
    c.card_number,
    c.expiration_date,
    CURRENT_DATE - c.expiration_date AS days_until_expiration,
    cust.customer_id,
    cust.first_name,
    cust.last_name,
    cust.prestashop_email
FROM cards c
JOIN customers cust ON cust.customer_id = c.customer_id
WHERE c.expiration_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
    AND c.card_status = 'active'
    AND c.deleted_at IS NULL
ORDER BY c.expiration_date ASC;
```

## Card Inventory Management

### Query: Cards by printing batch

```sql
SELECT 
    printing_batch,
    COUNT(*) AS total_cards,
    COUNT(CASE WHEN card_status = 'inactive' THEN 1 END) AS unassigned,
    COUNT(CASE WHEN card_status = 'active' THEN 1 END) AS active,
    COUNT(CASE WHEN card_status IN ('lost', 'stolen', 'replaced') THEN 1 END) AS disabled
FROM cards
WHERE printing_batch = 'BATCH-20250215-001'
    AND deleted_at IS NULL
GROUP BY printing_batch;
```

### Query: Cards needing reprint

```sql
-- Find defective cards that need reprinting
SELECT 
    card_id,
    card_uid,
    card_number,
    card_status,
    printing_batch
FROM cards
WHERE card_status = 'inactive'
    AND customer_id IS NULL
    AND created_at < NOW() - INTERVAL '6 months' -- Old unassigned cards
    AND deleted_at IS NULL;
```

## Related Documents

### Dependencies
- `05_data/DATA_MODEL.md` - Full database schema including cards table
- `05_data/CUSTOMER_MODEL.md` - Customer entity that cards link to
- `02_architecture/DATABASE_DESIGN.md` - Database architecture

### Dependents
- `03_features/CARD_ENROLLMENT.md` - Assigns cards to customers
- `03_features/EARN_POINTS_POS.md` - Uses card UID to identify customer
- `03_features/REDEEM_POINTS_POS.md` - Uses card UID for redemption
- `03_features/BALANCE_QUERY.md` - Queries balance via card tap

### Integration Points
- `04_integrations/NFC_READER.md` - Reads card UID from NFC chip
- `04_integrations/POS_WINDOWS_AGENT.md` - Handles card tap events
- `02_architecture/CLOUD_BACKEND.md` - Card lookup API endpoints

## Open Questions / TODOs

### TODO: Card Reprinting Service
**Status**: Not implemented  
**Required by**: Phase 2  
**Description**: Automated service to request card reprints for defective or damaged cards

### TODO: Multi-Card Support
**Status**: Future consideration  
**Required by**: Customer request  
**Description**: Allow one customer to have multiple active cards (e.g., family sharing)

### Open Question: QR Code Always Printed?
**Question**: Should all cards have QR codes or only upon request?  
**Context**: QR adds cost to printing but provides NFC fallback  
**Decision Required By**: Before first printing batch
