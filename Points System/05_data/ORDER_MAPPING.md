# Data Model: Order Mapping (Multi-Channel Order Tracking)

## Purpose

Define the order mapping entity that links POS orders (Aniwin), PrestaShop orders, and loyalty transactions to enable cross-channel order tracking, reconciliation, and loyalty point attribution across multiple sales channels.

## Scope

### In Scope
- Order mapping entity schema with POS and PrestaShop order references
- Loyalty transaction linkage (earn, redeem, refund ledger entries)
- Order metadata (date, total, status) for reconciliation
- Multi-channel support (POS and PrestaShop)
- Sync status tracking for offline-online synchronization
- Order-to-transaction relationship (1-to-many)
- Points earned and redeemed tracking per order

### Out of Scope
- Aniwin POS order schema (external system)
- PrestaShop order schema (ps_orders table, managed by PrestaShop)
- Order fulfillment and shipping (PrestaShop responsibility)
- Invoice generation (handled by POS and PrestaShop)
- Payment processing (handled by POS and PrestaShop)

## Order Mapping Schema

```sql
CREATE TABLE order_mapping (
    -- Primary identifier
    mapping_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Order identifiers
    order_type VARCHAR(20) NOT NULL CHECK (order_type IN ('pos', 'prestashop')),
    pos_order_id VARCHAR(100),
    prestashop_order_id INTEGER,
    
    -- Order details
    order_date TIMESTAMP WITH TIME ZONE NOT NULL,
    order_total_eur DECIMAL(10,2) NOT NULL,
    order_status VARCHAR(50) NOT NULL,
    
    -- Customer reference
    customer_id UUID REFERENCES customers(customer_id) ON DELETE SET NULL,
    
    -- Loyalty transaction linkage
    earn_ledger_id UUID REFERENCES loyalty_ledger(ledger_id) ON DELETE SET NULL,
    redeem_ledger_id UUID REFERENCES loyalty_ledger(ledger_id) ON DELETE SET NULL,
    refund_ledger_id UUID REFERENCES loyalty_ledger(ledger_id) ON DELETE SET NULL,
    
    -- Points earned/redeemed
    points_earned INTEGER DEFAULT 0,
    points_redeemed INTEGER DEFAULT 0,
    points_refunded INTEGER DEFAULT 0,
    
    -- Channel info
    terminal_id VARCHAR(50),
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('pos', 'online')),
    
    -- Sync status
    sync_status VARCHAR(20) DEFAULT 'pending' 
        CHECK (sync_status IN ('pending', 'synced', 'failed', 'reconciled')),
    last_sync_at TIMESTAMP WITH TIME ZONE,
    sync_error TEXT,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_order_id CHECK (
        (order_type = 'pos' AND pos_order_id IS NOT NULL) OR
        (order_type = 'prestashop' AND prestashop_order_id IS NOT NULL)
    ),
    CONSTRAINT uk_pos_order UNIQUE (pos_order_id),
    CONSTRAINT uk_prestashop_order UNIQUE (prestashop_order_id)
);

-- Indexes for performance
CREATE INDEX idx_order_mapping_customer ON order_mapping(customer_id, order_date DESC);
CREATE INDEX idx_order_mapping_pos_order ON order_mapping(pos_order_id) WHERE pos_order_id IS NOT NULL;
CREATE INDEX idx_order_mapping_prestashop_order ON order_mapping(prestashop_order_id) WHERE prestashop_order_id IS NOT NULL;
CREATE INDEX idx_order_mapping_earn_ledger ON order_mapping(earn_ledger_id) WHERE earn_ledger_id IS NOT NULL;
CREATE INDEX idx_order_mapping_redeem_ledger ON order_mapping(redeem_ledger_id) WHERE redeem_ledger_id IS NOT NULL;
CREATE INDEX idx_order_mapping_order_date ON order_mapping(order_date DESC);
CREATE INDEX idx_order_mapping_sync_status ON order_mapping(sync_status) WHERE sync_status != 'synced';
CREATE INDEX idx_order_mapping_channel ON order_mapping(channel, order_date DESC);

-- Comments
COMMENT ON TABLE order_mapping IS 'Mapping between POS/PrestaShop orders and loyalty transactions';
COMMENT ON COLUMN order_mapping.pos_order_id IS 'Aniwin POS order reference (e.g., POS-2025-02-15-0042)';
COMMENT ON COLUMN order_mapping.prestashop_order_id IS 'PrestaShop order ID from ps_orders.id_order';
COMMENT ON COLUMN order_mapping.earn_ledger_id IS 'Link to loyalty_ledger entry for points earned from this order';
COMMENT ON COLUMN order_mapping.redeem_ledger_id IS 'Link to loyalty_ledger entry for points redeemed on this order';
COMMENT ON COLUMN order_mapping.refund_ledger_id IS 'Link to loyalty_ledger entry for refund transaction';
```

## Field Definitions

### mapping_id (UUID)
Internal primary identifier for the order mapping. Generated as UUIDv4.

**Properties**:
- Used in internal queries and relationships
- Immutable once created

### order_type (VARCHAR 20)
Type of order (POS or PrestaShop).

**Values**:
- `pos` - Order from Aniwin POS system
- `prestashop` - Order from PrestaShop online store

**Determines**: Which `*_order_id` field is populated.

### pos_order_id (VARCHAR 100)
Aniwin POS order identifier.

**Format**: `POS-YYYY-MM-DD-NNNN`  
**Example**: `POS-2025-02-15-0042`

**Properties**:
- UNIQUE constraint (one mapping per POS order)
- NULL if `order_type = 'prestashop'`
- NOT NULL if `order_type = 'pos'`
- Generated by Aniwin POS system

### prestashop_order_id (INTEGER)
PrestaShop order identifier from `ps_orders.id_order`.

**Properties**:
- UNIQUE constraint (one mapping per PrestaShop order)
- NULL if `order_type = 'pos'`
- NOT NULL if `order_type = 'prestashop'`
- Foreign key to PrestaShop database

**Example**: `12345` (refers to order #12345 in PrestaShop)

### order_date (TIMESTAMP WITH TIME ZONE)
Date and time when order was placed.

**Properties**:
- NOT NULL
- Stored in UTC
- Synced from POS or PrestaShop
- Used for chronological order history

### order_total_eur (DECIMAL 10,2)
Total order amount in EUR.

**Properties**:
- NOT NULL
- Includes taxes and shipping
- Used to calculate loyalty points earned
- Stored with 2 decimal precision (e.g., 135.50)

### order_status (VARCHAR 50)
Current status of the order.

**POS Order Status Values**:
- `completed` - Order completed at POS
- `refunded` - Order fully refunded
- `partially_refunded` - Order partially refunded

**PrestaShop Order Status Values**:
- `payment_accepted` - Payment confirmed
- `processing` - Order being prepared
- `shipped` - Order shipped to customer
- `delivered` - Order delivered
- `cancelled` - Order cancelled
- `refunded` - Order refunded

**Properties**:
- Synced from source system (POS or PrestaShop)
- Used to determine loyalty point eligibility

### customer_id (UUID)
Foreign key to customer who placed the order.

**Properties**:
- NULL if guest order (PrestaShop only)
- NULL if customer not enrolled in loyalty (POS)
- ON DELETE SET NULL (order retained even if customer deleted)
- Used to link order to customer's loyalty account

### earn_ledger_id, redeem_ledger_id, refund_ledger_id (UUID)
Foreign keys to loyalty_ledger entries.

**Properties**:
- `earn_ledger_id`: Points earned from this order
- `redeem_ledger_id`: Points redeemed on this order
- `refund_ledger_id`: Points reversed due to refund
- All are OPTIONAL (NULL if no loyalty activity)
- ON DELETE SET NULL (order retained even if ledger entries archived)

**Relationship**:
- One order can have multiple ledger entries (earn + redeem)
- One ledger entry can link to one order

### points_earned, points_redeemed, points_refunded (INTEGER)
Cached point totals for quick queries.

**Properties**:
- Denormalized from loyalty_ledger for performance
- Default: 0
- Updated when loyalty transactions created
- Used for reporting and analytics

### terminal_id (VARCHAR 50)
POS terminal identifier (POS orders only).

**Format**: `POS-TERMINAL-001`

**Properties**:
- NULL for PrestaShop orders
- Used to identify which POS terminal processed order
- Used for per-terminal reporting

### channel (VARCHAR 20)
Sales channel (POS or online).

**Values**:
- `pos` - In-store purchase at POS terminal
- `online` - Online purchase through PrestaShop

**Properties**:
- NOT NULL
- Used for multi-channel analytics
- Distinct from `order_type` (channel is business view, order_type is technical view)

### sync_status (VARCHAR 20)
Synchronization status for offline-online reconciliation.

**Values**:
- `pending` - Order awaiting sync (POS offline transaction)
- `synced` - Order successfully synced to cloud
- `failed` - Sync failed (error during sync)
- `reconciled` - Order manually reconciled by admin

**Properties**:
- Default: `pending`
- Transitions: `pending` → `synced` (successful sync)
- Transitions: `pending` → `failed` (sync error) → `synced` (retry success)
- Transitions: `failed` → `reconciled` (manual fix)

### last_sync_at (TIMESTAMP WITH TIME ZONE)
Timestamp of last sync attempt.

**Properties**:
- NULL if never synced
- Updated on each sync attempt (success or failure)
- Stored in UTC

### sync_error (TEXT)
Error message if sync failed.

**Properties**:
- NULL if sync succeeded
- Contains error details for troubleshooting
- Example: `"Network timeout connecting to cloud API"`

## Order Mapping Flows

### Flow 1: POS Order with Earn and Redeem

**Scenario**: Customer makes POS purchase, earns 200 points, redeems 100 points.

```sql
-- Step 1: Create order mapping (during checkout)
INSERT INTO order_mapping (
    order_type,
    pos_order_id,
    order_date,
    order_total_eur,
    order_status,
    customer_id,
    terminal_id,
    channel,
    sync_status
) VALUES (
    'pos',
    'POS-2025-02-15-0042',
    '2025-02-15T14:30:00Z',
    135.00,
    'completed',
    'cust-uuid-123',
    'POS-TERMINAL-001',
    'pos',
    'pending'
)
RETURNING mapping_id;

-- Step 2: Insert earn transaction into loyalty_ledger
INSERT INTO loyalty_ledger (
    customer_id,
    transaction_type,
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
    'cust-uuid-123',
    'earn',
    20000, -- 200 points earned
    320000,
    'pos_sale',
    'POS-2025-02-15-0042',
    'POS-2025-02-15-0042',
    135.00,
    'Earned 200 points from POS order',
    'pos-earn-20250215-0042',
    'pos',
    'pos_agent_v1.2'
)
RETURNING ledger_id AS earn_ledger_id;

-- Step 3: Insert redeem transaction into loyalty_ledger
INSERT INTO loyalty_ledger (
    customer_id,
    transaction_type,
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
    'cust-uuid-123',
    'redeem',
    -10000, -- 100 points redeemed
    310000,
    'pos_sale',
    'POS-2025-02-15-0042',
    'POS-2025-02-15-0042',
    135.00,
    'Redeemed 100 points on POS order',
    'pos-redeem-20250215-0042',
    'pos',
    'pos_agent_v1.2'
)
RETURNING ledger_id AS redeem_ledger_id;

-- Step 4: Update order mapping with ledger IDs
UPDATE order_mapping
SET 
    earn_ledger_id = earn_ledger_id,
    redeem_ledger_id = redeem_ledger_id,
    points_earned = 20000,
    points_redeemed = 10000,
    sync_status = 'synced',
    last_sync_at = NOW(),
    updated_at = NOW()
WHERE mapping_id = mapping_id;
```

### Flow 2: PrestaShop Online Order

**Scenario**: Customer places online order, earns 150 points.

```sql
-- Insert order mapping (triggered by PrestaShop order webhook)
INSERT INTO order_mapping (
    order_type,
    prestashop_order_id,
    order_date,
    order_total_eur,
    order_status,
    customer_id,
    channel,
    sync_status
) VALUES (
    'prestashop',
    12345, -- PrestaShop order ID
    '2025-02-16T10:20:00Z',
    100.00,
    'payment_accepted',
    'cust-uuid-456',
    'online',
    'synced'
)
RETURNING mapping_id;

-- Insert earn transaction
INSERT INTO loyalty_ledger (
    customer_id,
    transaction_type,
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
    'cust-uuid-456',
    'earn',
    15000, -- 150 points earned
    185000,
    'online_order',
    'PS-ORDER-12345',
    'PS-ORDER-12345',
    100.00,
    'Earned 150 points from online order #12345',
    'prestashop-earn-12345',
    'online',
    'prestashop_module_v1.0'
)
RETURNING ledger_id;

-- Update order mapping
UPDATE order_mapping
SET 
    earn_ledger_id = ledger_id,
    points_earned = 15000,
    updated_at = NOW()
WHERE prestashop_order_id = 12345;
```

### Flow 3: Order Refund

**Scenario**: Customer returns POS order, points are reversed.

```sql
-- Step 1: Update order status
UPDATE order_mapping
SET 
    order_status = 'refunded',
    updated_at = NOW()
WHERE pos_order_id = 'POS-2025-02-15-0042';

-- Step 2: Insert refund transaction (reverses earn)
INSERT INTO loyalty_ledger (
    customer_id,
    transaction_type,
    points_delta,
    balance_after,
    source_type,
    source_reference,
    order_id,
    order_amount_eur,
    description,
    reverses_ledger_id,
    idempotency_key,
    channel,
    created_by
) VALUES (
    'cust-uuid-123',
    'refund',
    -20000, -- Reverse 200 earned points
    290000,
    'refund_reversal',
    'REFUND-POS-2025-02-15-0042',
    'POS-2025-02-15-0042',
    135.00,
    'Refund: Reversed 200 earned points',
    earn_ledger_id, -- Link to original earn transaction
    'refund-20250220-0042',
    'pos',
    'pos_agent_v1.2'
)
RETURNING ledger_id AS refund_ledger_id;

-- Step 3: Update order mapping with refund
UPDATE order_mapping
SET 
    refund_ledger_id = refund_ledger_id,
    points_refunded = 20000,
    updated_at = NOW()
WHERE pos_order_id = 'POS-2025-02-15-0042';
```

## Sync Status Management

### Offline POS Order Sync

```sql
-- POS agent syncs offline orders to cloud
-- Orders created offline start with sync_status = 'pending'

-- Mark order as synced after successful API call
UPDATE order_mapping
SET 
    sync_status = 'synced',
    last_sync_at = NOW(),
    updated_at = NOW()
WHERE pos_order_id = 'POS-2025-02-15-0042'
    AND sync_status = 'pending';
```

### Sync Failure Handling

```sql
-- Mark order sync as failed
UPDATE order_mapping
SET 
    sync_status = 'failed',
    last_sync_at = NOW(),
    sync_error = 'Network timeout: Unable to reach cloud API',
    updated_at = NOW()
WHERE pos_order_id = 'POS-2025-02-15-0043'
    AND sync_status = 'pending';

-- Retry failed syncs (called by background job)
SELECT 
    mapping_id,
    pos_order_id,
    order_date,
    order_total_eur,
    customer_id,
    sync_error
FROM order_mapping
WHERE sync_status = 'failed'
    AND last_sync_at < NOW() - INTERVAL '5 minutes' -- Wait 5 min between retries
ORDER BY order_date ASC
LIMIT 50;
```

### Manual Reconciliation

```sql
-- Admin manually reconciles failed order
UPDATE order_mapping
SET 
    sync_status = 'reconciled',
    sync_error = NULL,
    updated_at = NOW()
WHERE pos_order_id = 'POS-2025-02-15-0043'
    AND sync_status = 'failed';
```

## Common Queries

### Query 1: Customer order history with loyalty activity

```sql
SELECT 
    om.order_date,
    om.order_type,
    COALESCE(om.pos_order_id, om.prestashop_order_id::TEXT) AS order_reference,
    om.order_total_eur,
    om.order_status,
    om.points_earned,
    om.points_redeemed,
    om.points_refunded,
    ll_earn.transaction_date AS earn_date,
    ll_redeem.transaction_date AS redeem_date
FROM order_mapping om
LEFT JOIN loyalty_ledger ll_earn ON ll_earn.ledger_id = om.earn_ledger_id
LEFT JOIN loyalty_ledger ll_redeem ON ll_redeem.ledger_id = om.redeem_ledger_id
WHERE om.customer_id = $1
ORDER BY om.order_date DESC
LIMIT 50;
```

### Query 2: Find order by POS order ID

```sql
SELECT 
    om.*,
    c.first_name,
    c.last_name,
    c.prestashop_email
FROM order_mapping om
LEFT JOIN customers c ON c.customer_id = om.customer_id
WHERE om.pos_order_id = $1;
```

### Query 3: Find order by PrestaShop order ID

```sql
SELECT 
    om.*,
    c.first_name,
    c.last_name,
    c.prestashop_email
FROM order_mapping om
LEFT JOIN customers c ON c.customer_id = om.customer_id
WHERE om.prestashop_order_id = $1;
```

### Query 4: Find ledger transaction by order ID

```sql
SELECT 
    ll.ledger_id,
    ll.transaction_type,
    ll.transaction_date,
    ll.points_delta,
    ll.balance_after,
    ll.description,
    om.order_type,
    COALESCE(om.pos_order_id, om.prestashop_order_id::TEXT) AS order_reference
FROM loyalty_ledger ll
JOIN order_mapping om ON (
    ll.ledger_id = om.earn_ledger_id OR
    ll.ledger_id = om.redeem_ledger_id OR
    ll.ledger_id = om.refund_ledger_id
)
WHERE om.pos_order_id = $1 OR om.prestashop_order_id::TEXT = $1
ORDER BY ll.ledger_sequence ASC;
```

### Query 5: Orders pending sync

```sql
SELECT 
    mapping_id,
    pos_order_id,
    order_date,
    order_total_eur,
    customer_id,
    terminal_id,
    sync_status,
    last_sync_at
FROM order_mapping
WHERE sync_status IN ('pending', 'failed')
ORDER BY order_date ASC;
```

### Query 6: Daily order and loyalty summary

```sql
SELECT 
    DATE(order_date) AS order_day,
    channel,
    COUNT(*) AS total_orders,
    SUM(order_total_eur) AS total_revenue,
    SUM(points_earned) AS total_points_earned,
    SUM(points_redeemed) AS total_points_redeemed,
    COUNT(CASE WHEN points_earned > 0 THEN 1 END) AS orders_with_earn,
    COUNT(CASE WHEN points_redeemed > 0 THEN 1 END) AS orders_with_redeem
FROM order_mapping
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(order_date), channel
ORDER BY order_day DESC, channel;
```

## Edge Cases

### Edge Case 1: Order without customer (guest checkout)
PrestaShop guest orders have no `customer_id`.

**Behavior**:
- Order mapping created with `customer_id = NULL`
- No loyalty points earned (not enrolled)
- Order appears in order history but not linked to customer

### Edge Case 2: Customer enrolls after placing guest order
Customer creates account using same email as guest order.

**Behavior**:
- Historical guest orders remain unlinked (manual reconciliation required)
- Future orders automatically linked via `prestashop_customer_id`

### Edge Case 3: Partial refund
Customer returns part of order.

**Behavior**:
- `order_status` updated to `partially_refunded`
- Partial refund transaction inserted into loyalty_ledger
- `points_refunded` reflects partial amount

### Edge Case 4: Duplicate order sync
POS syncs same order twice due to network retry.

**Behavior**:
- UNIQUE constraint on `pos_order_id` prevents duplicate mapping
- Second INSERT fails with constraint violation
- Application detects duplicate via idempotency key in loyalty_ledger

## Related Documents

### Dependencies
- `05_data/DATA_MODEL.md` - Full database schema
- `05_data/LOYALTY_LEDGER.md` - Loyalty transaction details
- `05_data/CUSTOMER_MODEL.md` - Customer entity
- `04_integrations/PRESTASHOP_MODULE.md` - PrestaShop order sync
- `04_integrations/POS_WINDOWS_AGENT.md` - POS order creation

### Dependents
- `03_features/EARN_POINTS_POS.md` - Creates order mapping with earn
- `03_features/EARN_POINTS_ONLINE.md` - Creates order mapping for PrestaShop
- `03_features/REDEEM_POINTS_POS.md` - Links redemption to order
- `03_features/REFUND_HANDLING.md` - Updates order mapping on refund

### Related Features
- `03_features/BALANCE_QUERY.md` - Displays order history
- `07_operations/SYNC_RECONCILIATION.md` - Handles sync failures

## Open Questions / TODOs

### TODO: Multi-currency support
**Status**: Not implemented  
**Required by**: If expanding internationally  
**Description**: Store order amount in original currency and EUR equivalent

### TODO: Partial refund points calculation
**Status**: Needs clarification  
**Required by**: Before MVP launch  
**Description**: Define how to calculate points refund for partial order returns

### Open Question: Sync retry limit
**Question**: How many times should we retry failed syncs before giving up?  
**Context**: Network issues vs permanent failures  
**Decision Required By**: Before POS deployment
