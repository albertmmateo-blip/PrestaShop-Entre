# Conflict Resolution

## Purpose

This document defines how conflicts are detected and resolved during synchronization between Windows terminals and the cloud backend.

## Scope

Covers:
- Conflict types and detection
- Resolution rules and algorithms
- Manual intervention procedures
- Conflict logging and audit

Does not cover:
- General sync strategy (see `SYNC_STRATEGY.md`)
- Queue management (see `07_operations/OFFLINE_QUEUE.md`)

## Conflict Types

### 1. Insufficient Balance Conflict

**Scenario**: Offline redemption used stale balance; customer actually has less than requested

**Detection**:
```python
if transaction.type == "redeem":
    current_balance = compute_balance(customer_id)
    if current_balance < transaction.amount:
        raise InsufficientBalanceConflict(
            requested=transaction.amount,
            available=current_balance
        )
```

**Resolution**:
- **Automatic**: Reject the redemption transaction
- **Agent Action**: Mark transaction as failed with reason
- **Cashier Action**: 
  - Option A: Customer pays difference
  - Option B: Cashier issues refund in POS for overcharged amount
  - Option C: Manual adjustment to forgive difference (manager only)

**Prevention**:
- Offline redemption warnings ("Balance may not be current")
- Limit offline redemptions to cached balance minus safety margin
- Regular syncs to update cache

### 2. Duplicate Order ID

**Scenario**: Same order_id appears in multiple transactions (shouldn't happen, but possible with bugs)

**Detection**:
```python
existing_transactions = ledger.find(order_id=transaction.order_id)
if existing_transactions:
    raise DuplicateOrderIdConflict(
        order_id=transaction.order_id,
        existing=existing_transactions
    )
```

**Resolution**:
- **Automatic**: Check if transaction amounts match
  - If match exactly: Mark new transaction as synced (duplicate prevented by idempotency)
  - If different: Reject and flag for manual investigation

**Log For Investigation**:
```json
{
  "conflict_type": "DUPLICATE_ORDER_ID",
  "order_id": "POS-2026021312345",
  "existing_transactions": [
    {"transaction_id": "uuid1", "amount": 1.50, "type": "earn"}
  ],
  "new_transaction": {
    "transaction_id": "uuid2", "amount": 1.50, "type": "earn"
  },
  "resolution": "marked_synced",
  "reason": "amounts_match"
}
```

### 3. Customer Not Found

**Scenario**: Transaction references customer_id that doesn't exist in backend

**Possible Causes**:
- Customer enrollment not yet synced
- Customer deleted in backend (rare)
- Customer enrollment sync failed

**Detection**:
```python
customer = db.customers.get(transaction.customer_id)
if not customer:
    raise CustomerNotFoundConflict(customer_id=transaction.customer_id)
```

**Resolution**:
- **Automatic**: Check queue for pending customer enrollment
  - If found: Sync enrollment first, then retry transaction
  - If not found: Mark transaction as failed

**Agent Action**: Flag for manual investigation

### 4. Card UID Changed

**Scenario**: Transaction references old card UID; customer has new card

**Detection**:
```python
customer = db.customers.get(transaction.customer_id)
current_card = customer.active_card
if transaction.card_uid != current_card.uid:
    raise CardUidChangedConflict(
        old_uid=transaction.card_uid,
        new_uid=current_card.uid
    )
```

**Resolution**:
- **Automatic**: Accept transaction (card UIDs can change when cards replaced)
- **Log**: Record that transaction used old UID
- **Audit**: Flag for review if multiple UID changes detected

### 5. Timestamp Out of Order

**Scenario**: Transaction timestamp is older than last transaction

**Causes**:
- Clock skew
- Delayed offline sync
- Transactions synced out of order

**Detection**:
```python
last_transaction = ledger.get_last(customer_id=customer_id)
if transaction.timestamp < last_transaction.timestamp:
    raise TimestampOutOfOrderConflict(
        transaction_time=transaction.timestamp,
        last_transaction_time=last_transaction.timestamp
    )
```

**Resolution**:
- **Automatic**: Accept transaction (ledger allows out-of-order)
- **Ledger Ordering**: Use sequence number, not timestamp, for canonical order
- **Balance Computation**: Unaffected (all transactions counted)

**Not a Real Conflict**: This is informational only; no action needed

### 6. Idempotency Key Collision

**Scenario**: Same idempotency key used with different request data

**Detection**:
```python
existing = idempotency_keys.get(transaction.idempotency_key)
if existing:
    if existing.request_hash != hash(transaction):
        raise IdempotencyKeyCollisionConflict(
            key=transaction.idempotency_key,
            existing_hash=existing.request_hash,
            new_hash=hash(transaction)
        )
```

**Resolution**:
- **Manual**: This indicates a serious bug
- **Agent Action**: Mark transaction as failed
- **Investigate**: Log full details for developer investigation
- **Fix**: Likely requires code fix, then manual replay

### 7. Refund Without Original Order

**Scenario**: Refund transaction references order_id that doesn't exist

**Detection**:
```python
if transaction.type == "refund":
    original_transactions = ledger.find(order_id=transaction.original_order_id)
    if not original_transactions:
        raise RefundWithoutOrderConflict(
            order_id=transaction.original_order_id
        )
```

**Resolution**:
- **Automatic**: Reject refund transaction
- **Agent Action**: Mark as failed with reason
- **Investigation**: Manual check if original order was never synced

## Resolution Priority

1. **Automatic Resolutions** (no human intervention)
   - Duplicate prevention (same idempotency key, same request)
   - Timestamp out of order (accept)
   - Matching duplicate order IDs (accept)

2. **Semi-Automatic** (automatic with logging)
   - Customer not found with pending enrollment (retry)
   - Card UID changed (accept, log)

3. **Manual Intervention Required**
   - Insufficient balance (cashier resolves)
   - Idempotency key collision (developer investigates)
   - Refund without order (investigate)
   - Conflicting duplicate order IDs (investigate)

## Conflict Resolution Workflow

```
┌─────────────────────────────────┐
│ Transaction Sync Attempted      │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Backend Validates Transaction   │
└────────────┬────────────────────┘
             │
        ┌────▼────┐
        │ Valid?  │
        └────┬────┘
             │
      ┌──────┴──────┐
      │             │
     NO            YES
      │             │
      ▼             ▼
┌─────────────┐   ┌────────────────┐
│ Conflict    │   │ Process Trans. │
│ Detected    │   │ Successfully   │
└──────┬──────┘   └────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Determine Conflict Type         │
└────────────┬────────────────────┘
             │
       ┌─────▼─────┐
       │ Automatic │
       │ Resolve?  │
       └─────┬─────┘
             │
      ┌──────┴──────┐
      │             │
     YES           NO
      │             │
      ▼             ▼
┌─────────────┐   ┌──────────────────┐
│ Apply Auto  │   │ Mark Failed      │
│ Resolution  │   │ Log for Manual   │
└──────┬──────┘   └────────┬─────────┘
       │                   │
       ▼                   ▼
┌─────────────┐   ┌──────────────────┐
│ Mark Synced │   │ Notify Cashier   │
│ Log Result  │   │ Alert Admin      │
└─────────────┘   └──────────────────┘
```

## Conflict Logging

### Log Entry Format

```json
{
  "conflict_id": "uuid",
  "timestamp": "2026-02-13T14:35:22Z",
  "terminal_id": "TERM-001",
  "transaction_id": "uuid",
  "idempotency_key": "TERM-001-20260213-00042-...",
  "conflict_type": "INSUFFICIENT_BALANCE",
  "severity": "WARNING",
  "details": {
    "customer_id": "uuid",
    "requested_amount": 10.00,
    "available_balance": 5.50,
    "stale_cache_balance": 12.00
  },
  "resolution": "REJECTED",
  "resolution_method": "AUTOMATIC",
  "notes": "Offline redemption with stale balance"
}
```

### Conflict Severity Levels

- **INFO**: Resolved automatically, no action needed (e.g., timestamp out of order)
- **WARNING**: Resolved automatically, but noteworthy (e.g., insufficient balance)
- **ERROR**: Requires manual intervention (e.g., idempotency collision)
- **CRITICAL**: Indicates system bug (e.g., data corruption)

## Manual Intervention Procedures

### Insufficient Balance Scenario

**Cashier Runbook**:

1. **Alert Displayed**: "Redemption failed: insufficient balance"
2. **Inform Customer**: "Your actual balance is X EUR, not Y EUR as shown offline"
3. **Options**:
   - Customer pays difference in cash/card
   - Cashier refunds overcharged amount in POS
   - Manager approves manual adjustment (rare, goodwill)
4. **Record Resolution** in sync log

**Manager Adjustment** (if approved):
```
1. Open Windows Agent admin UI
2. Select failed transaction
3. Click "Resolve with Manual Adjustment"
4. Enter reason: "Offline redemption difference, approved by Manager X"
5. System creates compensating adjustment transaction
6. Sync adjustment transaction
```

### Duplicate Order Investigation

**Admin Runbook**:

1. **Review Conflict Log**: Identify order_id and transactions
2. **Check Ledger**: Query backend for all transactions with that order_id
3. **Compare Amounts**: Do amounts match?
   - If yes: No action (duplicate prevented correctly)
   - If no: Investigate further
4. **Determine Root Cause**:
   - POS integration bug?
   - Manual entry error?
   - Race condition?
5. **Fix Root Cause**
6. **Manual Correction** if needed:
   - Delete incorrect ledger entry (exception to append-only)
   - Create compensating transaction
   - Document exception in audit log

### Customer Not Found Investigation

**Admin Runbook**:

1. **Check Queue**: Is customer enrollment pending sync?
   - If yes: Wait for enrollment sync, retry transaction
2. **Check Backend**: Does customer exist?
   - If no: Enrollment lost, re-enroll customer
3. **Check Local Cache**: Does agent have customer locally?
   - If yes: Force re-sync enrollment
   - If no: Bug in enrollment flow, investigate
4. **After Fix**: Retry failed transaction manually

## Conflict Prevention

### Best Practices

1. **Sync Frequently**: Reduce staleness of cached data
2. **Warn Users**: Display warnings when operating offline
3. **Safety Margins**: Limit offline redemptions to cached balance - 10%
4. **Queue Monitoring**: Alert when queue depth > 100
5. **Test Offline Scenarios**: Regular testing of offline/online transitions

### Code Reviews

- Review idempotency key generation logic carefully
- Review balance caching and invalidation logic
- Review redemption validation in offline mode

### Monitoring

- Alert on conflict rate > 1%
- Alert on manual interventions > 1 per week
- Dashboard showing conflict types and frequencies

## Testing Conflict Scenarios

### Test Cases

1. **Insufficient Balance**
   - Cache balance = 10.00 EUR
   - Queue redemption for 8.00 EUR offline
   - Meanwhile, online terminal redeems 6.00 EUR
   - Sync offline redemption (now balance is 4.00 EUR)
   - Expect: Conflict detected, redemption rejected

2. **Duplicate Order Prevention**
   - Create transaction with order_id X
   - Sync successfully
   - Create another transaction with same order_id X
   - Sync again
   - Expect: Duplicate detected, second transaction rejected

3. **Customer Not Found**
   - Enqueue customer enrollment
   - Enqueue transaction for that customer
   - Sync transaction first (enrollment still pending)
   - Expect: Customer not found, transaction requeued
   - Sync enrollment
   - Sync transaction again
   - Expect: Success

4. **Timestamp Out of Order**
   - Set terminal clock back 1 hour
   - Create transaction
   - Set clock forward
   - Sync transaction
   - Expect: Warning logged, transaction accepted

## Related Documents

### Architecture
- `02_architecture/SYSTEM_ARCHITECTURE.md` - Overall architecture
- `02_architecture/CLOUD_BACKEND.md` - API validation logic
- `02_architecture/SYNC_STRATEGY.md` - Sync algorithm
- `02_architecture/WINDOWS_AGENT.md` - Agent implementation

### Operations
- `07_operations/OFFLINE_QUEUE.md` - Queue management
- `07_operations/ERROR_HANDLING.md` - Error handling
- `07_operations/SYNC_MONITORING.md` - Monitoring conflicts

### Data
- `05_data/LOYALTY_LEDGER.md` - Ledger append-only rules
