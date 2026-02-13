# Data Model: Loyalty Ledger (Immutable Transaction Log)

## Purpose

Define the immutable append-only loyalty ledger design that serves as the single source of truth for all loyalty point transactions, ensuring data integrity, auditability, and accurate balance computation through event sourcing principles.

## Scope

### In Scope
- Immutable transaction ledger architecture
- All transaction types (earn, redeem, refund, adjustment, expiration, reversal)
- Balance computation algorithm from ledger
- Strict no-UPDATE/no-DELETE enforcement
- Sequence and timestamp ordering rules
- Idempotency key handling
- Transaction reversal pattern
- Expiration tracking and processing
- Multi-customer concurrent transaction handling

### Out of Scope
- Balance caching layer (covered in DATA_MODEL.md - loyalty_accounts table)
- Transaction receipt generation (covered in features)
- API request/response formats (covered in CLOUD_BACKEND.md)
- Database replication and backup (covered in DATABASE_DESIGN.md)

## Ledger Principles

### Immutability
Once a ledger entry is created, it **CANNOT** be modified or deleted. All corrections are made through compensating transactions.

### Append-Only
New transactions are always appended to the ledger. There is no in-place editing.

### Event Sourcing
Customer balance is **computed** from the ledger, not stored as a single value. The ledger is the source of truth.

### Total Ordering
All transactions have a strictly increasing sequence number (`ledger_sequence`) ensuring deterministic replay.

### Auditability
Every point movement has a complete audit trail with timestamp, actor, and reason.

## Ledger Schema

```sql
CREATE TABLE loyalty_ledger (
    -- Primary identifier
    ledger_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Sequence for ordering
    ledger_sequence BIGSERIAL NOT NULL UNIQUE,
    
    -- Customer reference
    customer_id UUID NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
    account_id UUID NOT NULL REFERENCES loyalty_accounts(account_id) ON DELETE RESTRICT,
    
    -- Transaction details
    transaction_type VARCHAR(20) NOT NULL 
        CHECK (transaction_type IN ('earn', 'redeem', 'refund', 'adjustment', 'expiration', 'reversal')),
    transaction_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Point movement
    points_delta INTEGER NOT NULL,
    balance_after INTEGER NOT NULL CHECK (balance_after >= 0),
    
    -- Source reference
    source_type VARCHAR(50) NOT NULL 
        CHECK (source_type IN ('pos_sale', 'online_order', 'manual_adjustment', 'expiration_policy', 'refund_reversal', 'migration')),
    source_reference VARCHAR(255),
    order_id VARCHAR(100),
    
    -- Transaction metadata
    order_amount_eur DECIMAL(10,2),
    earn_rate_percent DECIMAL(5,2),
    redemption_rate_percent DECIMAL(5,2),
    
    -- Description and notes
    description TEXT NOT NULL,
    notes TEXT,
    
    -- Expiration tracking
    expiration_date DATE,
    expired_by_ledger_id UUID REFERENCES loyalty_ledger(ledger_id) ON DELETE SET NULL,
    
    -- Idempotency
    idempotency_key VARCHAR(255) UNIQUE,
    
    -- Reversal tracking
    reversed_by_ledger_id UUID REFERENCES loyalty_ledger(ledger_id) ON DELETE SET NULL,
    reverses_ledger_id UUID REFERENCES loyalty_ledger(ledger_id) ON DELETE SET NULL,
    
    -- Terminal/channel
    terminal_id VARCHAR(50),
    channel VARCHAR(20) CHECK (channel IN ('pos', 'online', 'manual', 'system')),
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_by VARCHAR(100) NOT NULL,
    
    -- NO UPDATE/DELETE ALLOWED (immutable ledger)
    -- deleted_at intentionally omitted
    
    -- Constraints
    CONSTRAINT chk_ledger_points_delta CHECK (
        (transaction_type IN ('earn', 'refund', 'adjustment') AND points_delta > 0) OR
        (transaction_type IN ('redeem', 'expiration', 'reversal') AND points_delta < 0)
    )
);
```

## Transaction Types

### 1. EARN
Customer earns points from a purchase.

**Points Delta**: POSITIVE  
**Typical Sources**: `pos_sale`, `online_order`  
**Idempotency**: Required (prevents duplicate earns)

**Example**:
```sql
INSERT INTO loyalty_ledger (
    customer_id,
    account_id,
    transaction_type,
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
    'cust-uuid-123',
    'acct-uuid-456',
    'earn',
    20250,  -- 202.50 points (202.50 EUR * 1.5% * 10000)
    270250, -- New balance
    'pos_sale',
    'POS-2025-02-15-0042',
    'POS-2025-02-15-0042',
    135.00,
    1.50,
    'Earned 202 points from POS sale',
    '2026-02-15', -- Expires in 1 year
    'pos-earn-20250215-0042-cust123',
    'pos',
    'POS-TERMINAL-001',
    'pos_agent_v1.2'
);
```

### 2. REDEEM
Customer redeems points for a discount.

**Points Delta**: NEGATIVE  
**Typical Sources**: `pos_sale`, `online_order`  
**Idempotency**: Required (prevents duplicate redemptions)

**Example**:
```sql
INSERT INTO loyalty_ledger (
    customer_id,
    account_id,
    transaction_type,
    points_delta,
    balance_after,
    source_type,
    source_reference,
    order_id,
    order_amount_eur,
    redemption_rate_percent,
    description,
    idempotency_key,
    channel,
    terminal_id,
    created_by
) VALUES (
    'cust-uuid-123',
    'acct-uuid-456',
    'redeem',
    -100000, -- -100 points redeemed
    170250,  -- New balance
    'pos_sale',
    'POS-2025-02-16-0008',
    'POS-2025-02-16-0008',
    85.00,
    NULL,
    'Redeemed 100 points (10.00 EUR discount)',
    'pos-redeem-20250216-0008-cust123',
    'pos',
    'POS-TERMINAL-001',
    'pos_agent_v1.2'
);
```

### 3. REFUND
Customer returns a purchase, points are reversed (refund earn) or returned (refund redeem).

**Points Delta**: POSITIVE (returning redeemed points) or NEGATIVE (reversing earned points)  
**Typical Sources**: `refund_reversal`  
**Idempotency**: Required

**Example - Refund of Earned Points**:
```sql
INSERT INTO loyalty_ledger (
    customer_id,
    account_id,
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
    'acct-uuid-456',
    'refund',
    -20250, -- Reverse the 202 points earned
    150000,
    'refund_reversal',
    'REFUND-POS-2025-02-15-0042',
    'POS-2025-02-15-0042',
    135.00,
    'Refund: Reversed 202 earned points from order POS-2025-02-15-0042',
    'ledger-uuid-original-earn',
    'refund-20250220-0042',
    'pos',
    'pos_agent_v1.2'
);
```

### 4. ADJUSTMENT
Manual point adjustment by administrator (add or remove points).

**Points Delta**: POSITIVE (add) or NEGATIVE (remove)  
**Typical Sources**: `manual_adjustment`  
**Idempotency**: Required

**Example - Add Goodwill Points**:
```sql
INSERT INTO loyalty_ledger (
    customer_id,
    account_id,
    transaction_type,
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
    'cust-uuid-123',
    'acct-uuid-456',
    'adjustment',
    50000, -- Add 50 points
    200000,
    'manual_adjustment',
    'ADJ-2025-02-20-001',
    'Goodwill adjustment: Customer service recovery',
    'Compensating for technical issue during checkout. Approved by Manager ID: MGR-789',
    'adjustment-20250220-001',
    'manual',
    'admin_user_john'
);
```

### 5. EXPIRATION
Points expire due to expiration policy (e.g., 1 year).

**Points Delta**: NEGATIVE  
**Typical Sources**: `expiration_policy`  
**Idempotency**: Required (batch job)

**Example**:
```sql
INSERT INTO loyalty_ledger (
    customer_id,
    account_id,
    transaction_type,
    points_delta,
    balance_after,
    source_type,
    source_reference,
    description,
    expired_by_ledger_id, -- This is the new entry ID (self-reference handled after insert)
    idempotency_key,
    channel,
    created_by
) VALUES (
    'cust-uuid-123',
    'acct-uuid-456',
    'expiration',
    -30000, -- Expire 30 points
    170000,
    'expiration_policy',
    'EXP-BATCH-2025-02-15',
    'Expired 30 points from transaction on 2024-02-15',
    NULL, -- Set later via UPDATE to expired ledger entry
    'expiration-batch-20250215-cust123',
    'system',
    'expiration_job_v1.0'
);
```

### 6. REVERSAL
Reversal of a previous transaction due to error or fraud.

**Points Delta**: OPPOSITE of original transaction  
**Typical Sources**: `manual_adjustment`, `system`  
**Idempotency**: Required

**Example - Reverse Fraudulent Redemption**:
```sql
INSERT INTO loyalty_ledger (
    customer_id,
    account_id,
    transaction_type,
    points_delta,
    balance_after,
    source_type,
    source_reference,
    description,
    notes,
    reverses_ledger_id,
    idempotency_key,
    channel,
    created_by
) VALUES (
    'cust-uuid-123',
    'acct-uuid-456',
    'reversal',
    -100000, -- Reverse the fraudulent redemption (remove points again)
    70000,
    'manual_adjustment',
    'REV-2025-02-22-FRAUD',
    'Reversal: Fraudulent redemption detected',
    'Fraud investigation case #FR-2025-0042. Customer account suspended pending review.',
    'ledger-uuid-fraudulent-redeem',
    'reversal-fraud-20250222',
    'manual',
    'security_team_admin'
);
```

## Balance Computation Algorithm

### Real-Time Balance Calculation

The customer's current balance is **always** computed from the ledger:

```sql
-- Compute current balance for a customer
SELECT 
    customer_id,
    SUM(points_delta) AS current_balance
FROM loyalty_ledger
WHERE customer_id = $1
GROUP BY customer_id;
```

### Incremental Balance After

Each transaction records `balance_after` for quick balance lookups without full ledger scan:

```sql
-- Get current balance from most recent transaction
SELECT balance_after AS current_balance
FROM loyalty_ledger
WHERE customer_id = $1
ORDER BY ledger_sequence DESC
LIMIT 1;
```

### Balance Verification

Periodically verify cached balance matches computed balance:

```sql
-- Verify balance integrity
WITH computed_balance AS (
    SELECT 
        customer_id,
        SUM(points_delta) AS ledger_balance
    FROM loyalty_ledger
    WHERE customer_id = $1
    GROUP BY customer_id
)
SELECT 
    la.customer_id,
    la.current_balance_points AS cached_balance,
    cb.ledger_balance AS computed_balance,
    (la.current_balance_points = cb.ledger_balance) AS balance_matches
FROM loyalty_accounts la
JOIN computed_balance cb ON cb.customer_id = la.customer_id
WHERE la.customer_id = $1;
```

## Sequence and Timestamp Handling

### Sequence Ordering

`ledger_sequence` is a BIGSERIAL auto-incrementing column ensuring strict total order:

```sql
-- Fetch transactions in order
SELECT *
FROM loyalty_ledger
WHERE customer_id = $1
ORDER BY ledger_sequence ASC;
```

**Important**: Sequence is database-assigned and **cannot** be set by application.

### Timestamp Ordering

`transaction_date` reflects when transaction occurred (may differ from `created_at` for offline transactions):

```sql
-- Offline transaction recorded later
INSERT INTO loyalty_ledger (
    transaction_date, -- When transaction actually occurred
    created_at,       -- When recorded in database
    ...
) VALUES (
    '2025-02-14T15:30:00Z', -- Transaction time
    NOW(),                   -- Record time
    ...
);
```

### Clock Skew Handling

If `transaction_date` is in the future (clock skew), use `created_at` for ordering:

```sql
-- Resilient ordering
SELECT *
FROM loyalty_ledger
WHERE customer_id = $1
ORDER BY 
    LEAST(transaction_date, created_at) ASC,
    ledger_sequence ASC;
```

## Immutability Enforcement

### Database-Level Triggers

```sql
-- Prevent UPDATE on loyalty_ledger
CREATE OR REPLACE FUNCTION prevent_ledger_modification()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'DELETE not allowed on loyalty_ledger (immutable ledger)';
    ELSIF TG_OP = 'UPDATE' THEN
        RAISE EXCEPTION 'UPDATE not allowed on loyalty_ledger (immutable ledger)';
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_ledger_update BEFORE UPDATE ON loyalty_ledger
    FOR EACH ROW EXECUTE FUNCTION prevent_ledger_modification();

CREATE TRIGGER prevent_ledger_delete BEFORE DELETE ON loyalty_ledger
    FOR EACH ROW EXECUTE FUNCTION prevent_ledger_modification();
```

### Application-Level Enforcement

**Never** issue UPDATE or DELETE statements on `loyalty_ledger` table:

```typescript
// ❌ WRONG - Never update ledger
await db.query(
  'UPDATE loyalty_ledger SET points_delta = $1 WHERE ledger_id = $2',
  [newPoints, ledgerId]
);

// ✅ CORRECT - Insert compensating transaction
await db.query(
  'INSERT INTO loyalty_ledger (transaction_type, points_delta, ...) VALUES ($1, $2, ...)',
  ['adjustment', correctionPoints, ...]
);
```

## Idempotency Key Handling

Every point-changing transaction **must** include an idempotency key to prevent duplicates.

### Idempotency Key Format

```
{source}-{transaction_type}-{date}-{reference}-{customer_id}
```

**Examples**:
- `pos-earn-20250215-0042-cust123`
- `online-redeem-20250216-order12345-cust456`
- `manual-adjustment-20250220-001-cust789`

### Duplicate Detection

```sql
-- Attempt to insert with idempotency key
INSERT INTO loyalty_ledger (
    idempotency_key,
    transaction_type,
    points_delta,
    ...
) VALUES (
    'pos-earn-20250215-0042-cust123',
    'earn',
    20250,
    ...
)
ON CONFLICT (idempotency_key) DO NOTHING
RETURNING ledger_id;
```

If `ledger_id` is NULL, transaction was duplicate and rejected.

### Idempotency Key Expiration

Keys are retained forever in ledger for audit. Separate `idempotency_keys` table caches responses for 24 hours.

## Transaction Reversal Pattern

To reverse a transaction, insert a new compensating transaction:

### Reversal Example

```sql
-- Original earn transaction
INSERT INTO loyalty_ledger (
    ledger_id, -- ledger-uuid-original
    transaction_type,
    points_delta,
    balance_after,
    ...
) VALUES (
    'ledger-uuid-original',
    'earn',
    20000,
    150000,
    ...
);

-- Reversal transaction (refund)
INSERT INTO loyalty_ledger (
    transaction_type,
    points_delta,
    balance_after,
    reverses_ledger_id,
    description,
    ...
) VALUES (
    'refund',
    -20000, -- Opposite of original
    130000, -- Adjusted balance
    'ledger-uuid-original', -- Link to original
    'Refund: Reversed earn from order #12345',
    ...
);

-- Mark original as reversed
UPDATE loyalty_ledger
SET reversed_by_ledger_id = 'ledger-uuid-reversal'
WHERE ledger_id = 'ledger-uuid-original';
-- ❌ WAIT! This is an UPDATE - PROHIBITED!
```

**Correction**: We **cannot** update original transaction. Instead, use application logic to detect reversals:

```sql
-- Query to find reversed transactions
SELECT 
    ll.ledger_id,
    ll.transaction_type,
    ll.points_delta,
    reversal.ledger_id AS reversed_by,
    reversal.transaction_date AS reversed_date
FROM loyalty_ledger ll
LEFT JOIN loyalty_ledger reversal ON reversal.reverses_ledger_id = ll.ledger_id
WHERE ll.customer_id = $1;
```

## Expiration Tracking

### Expiration Date Assignment

All earned points include an `expiration_date`:

```sql
INSERT INTO loyalty_ledger (
    transaction_type,
    points_delta,
    expiration_date, -- 1 year from transaction
    ...
) VALUES (
    'earn',
    20000,
    NOW()::DATE + INTERVAL '1 year',
    ...
);
```

### Expiration Job

Nightly batch job expires points:

```sql
-- Find points expiring today
SELECT 
    ll.customer_id,
    ll.account_id,
    SUM(ll.points_delta) AS points_to_expire
FROM loyalty_ledger ll
WHERE ll.expiration_date = CURRENT_DATE
    AND ll.expired_by_ledger_id IS NULL
    AND ll.transaction_type = 'earn'
GROUP BY ll.customer_id, ll.account_id;

-- Insert expiration transaction
INSERT INTO loyalty_ledger (
    customer_id,
    account_id,
    transaction_type,
    points_delta,
    balance_after,
    source_type,
    description,
    idempotency_key,
    channel,
    created_by
) VALUES (
    'cust-uuid',
    'acct-uuid',
    'expiration',
    -20000,
    new_balance,
    'expiration_policy',
    'Expired 200 points from 2024-02-15 transaction',
    'expiration-batch-20250215-custXYZ',
    'system',
    'expiration_job'
);

-- Update expired transactions (exception to immutability for linking only)
UPDATE loyalty_ledger
SET expired_by_ledger_id = new_expiration_ledger_id
WHERE ledger_id IN (expired_transaction_ids);
```

**Note**: Updating `expired_by_ledger_id` is an **exception** to immutability - it's a one-time link set by system job.

### Query Expiring Points

```sql
-- Points expiring in next 30 days
SELECT 
    ll.customer_id,
    ll.expiration_date,
    SUM(ll.points_delta) AS points_expiring
FROM loyalty_ledger ll
WHERE ll.expiration_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
    AND ll.expired_by_ledger_id IS NULL
    AND ll.transaction_type = 'earn'
GROUP BY ll.customer_id, ll.expiration_date
ORDER BY ll.expiration_date ASC;
```

## Edge Cases

### Edge Case 1: Concurrent Transactions
Two transactions for same customer happen simultaneously.

**Behavior**:
- Database sequence ensures unique ordering
- Both transactions succeed with different `ledger_sequence`
- `balance_after` may appear non-sequential (acceptable - recompute from ledger)

### Edge Case 2: Negative Balance Attempt
Customer tries to redeem more points than available.

**Behavior**:
- Application checks current balance before insert
- If insufficient, reject redemption request
- Database CHECK constraint `balance_after >= 0` as final safeguard

### Edge Case 3: Offline Transaction Replay
POS syncs offline transaction after customer already made online redemption.

**Behavior**:
- Offline earn uses `transaction_date` from offline timestamp
- `created_at` reflects sync time
- Sequence ensures correct total order even if timestamps are out of order

### Edge Case 4: Duplicate Idempotency Key
Same transaction submitted twice (network retry).

**Behavior**:
- First insert succeeds
- Second insert fails due to UNIQUE constraint on `idempotency_key`
- Application returns result from first transaction (idempotent response)

### Edge Case 5: Expiration Job Interrupted
Expiration batch job crashes mid-run.

**Behavior**:
- Completed expirations are already in ledger (durable)
- Next run detects already-expired transactions via `expired_by_ledger_id IS NOT NULL`
- Idempotency key prevents duplicate expiration entries

## Performance Optimization

### Index Strategy

```sql
-- Customer transaction history (most common query)
CREATE INDEX idx_loyalty_ledger_customer_seq ON loyalty_ledger(customer_id, ledger_sequence DESC);

-- Order reference lookup
CREATE INDEX idx_loyalty_ledger_order_id ON loyalty_ledger(order_id) WHERE order_id IS NOT NULL;

-- Expiration job
CREATE INDEX idx_loyalty_ledger_expiration ON loyalty_ledger(expiration_date) 
    WHERE expiration_date IS NOT NULL AND expired_by_ledger_id IS NULL;

-- Idempotency check
CREATE INDEX idx_loyalty_ledger_idempotency ON loyalty_ledger(idempotency_key) 
    WHERE idempotency_key IS NOT NULL;
```

### Partitioning by Date

For large ledgers (> 10M rows), partition by `transaction_date`:

```sql
CREATE TABLE loyalty_ledger_partitioned (
    LIKE loyalty_ledger INCLUDING ALL
) PARTITION BY RANGE (transaction_date);

CREATE TABLE loyalty_ledger_2025_02 PARTITION OF loyalty_ledger_partitioned
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
```

### Balance Caching

To avoid scanning entire ledger, maintain `loyalty_accounts.current_balance_points`:

```sql
-- Update cached balance after ledger insert
UPDATE loyalty_accounts
SET 
    current_balance_points = $1, -- balance_after from ledger
    last_transaction_date = $2,
    updated_at = NOW()
WHERE account_id = $3;
```

## Related Documents

### Dependencies
- `05_data/DATA_MODEL.md` - Full schema including loyalty_ledger table
- `02_architecture/DATABASE_DESIGN.md` - Database architecture and replication
- `06_security/AUDIT_LOGGING.md` - Audit trail for ledger access

### Dependents
- `03_features/EARN_POINTS_POS.md` - Inserts earn transactions
- `03_features/REDEEM_POINTS_POS.md` - Inserts redeem transactions
- `03_features/REFUND_HANDLING.md` - Inserts refund transactions
- `03_features/MANUAL_ADJUSTMENTS.md` - Inserts adjustment transactions
- `03_features/EXPIRATION.md` - Inserts expiration transactions
- `03_features/BALANCE_QUERY.md` - Queries ledger for balance computation

### Related Data Models
- `05_data/CUSTOMER_MODEL.md` - Customer entity referenced by ledger
- `05_data/ORDER_MAPPING.md` - Order mapping references ledger entries
- `05_data/CARD_MODEL.md` - Card used to identify customer for transactions

## Open Questions / TODOs

### TODO: Ledger Archival
**Status**: Not implemented  
**Required by**: When ledger exceeds 10M rows  
**Description**: Move transactions older than 5 years to archive table while preserving integrity

### TODO: Ledger Snapshots
**Status**: Future optimization  
**Required by**: If balance queries become slow  
**Description**: Daily snapshot of balances to avoid full ledger scan

### Open Question: Expiration FIFO vs LIFO
**Question**: Should oldest points expire first (FIFO) or newest (LIFO)?  
**Context**: FIFO is standard, but LIFO may encourage more frequent redemptions  
**Decision Required By**: Before MVP launch
