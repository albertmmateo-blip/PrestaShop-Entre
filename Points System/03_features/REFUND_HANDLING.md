# Feature: Refund Handling

## Purpose

Automatically reverse previously awarded or redeemed loyalty points when a customer returns merchandise or an order is cancelled, ensuring accurate balance and preventing point fraud from refund abuse.

## Scope

### In Scope
- Automatic point reversal on full refunds (POS and PrestaShop)
- Detecting refund events from Aniwin.net POS and PrestaShop
- Creating offsetting (negative) transactions in ledger
- Handling refunds for both earned points (reversal) and redeemed points (restoration)
- Offline refund queuing with sync
- Audit trail of all refund operations
- Manager approval for large refunds (> 100 EUR)

### Out of Scope
- Partial refunds (only full order refunds supported in MVP)
- Refunds after points already expired
- Refunds without original transaction reference
- Cross-channel refunds (POS purchase returned online, or vice versa)
- Refund abuse detection algorithms (future enhancement)

## Inputs

### From POS Windows Agent - Refund Detection
```json
{
  "refund_id": "REF-2025-02-15-0003",
  "original_sale_id": "POS-2025-02-13-0042",
  "refund_amount": 125.50,
  "refund_reason": "customer_return",
  "refunded_by": "CASHIER-001",
  "terminal_id": "POS-TERMINAL-001",
  "refund_timestamp": "2025-02-15T11:30:00Z",
  "card_uid": "04A1B2C3D4E5F6"
}
```

### From PrestaShop Module - Order Cancelled/Refunded
```json
{
  "order_id": 12345,
  "refund_type": "full",
  "refund_amount": 150.00,
  "refund_reason": "customer_cancelled",
  "order_date": "2025-02-14T10:30:00Z",
  "refund_timestamp": "2025-02-15T09:45:00Z",
  "customer_id": 9876,
  "card_uid": "04A1B2C3D4E5F6"
}
```

### Validation Rules
- `original_sale_id` or `order_id`: Must reference existing transaction in ledger
- `refund_amount`: Should match original transaction amount (full refund only)
- `card_uid`: Must match card used in original transaction
- Refund must not be already processed (idempotency check)

## Outputs

### Success Response - Earned Points Reversed
**Scenario**: Customer earned 188 points on 125.50 EUR purchase, now returning item

```json
{
  "success": true,
  "reversal_type": "earn_reversal",
  "reversal_transaction_id": "txn_rev_a1b2c3d4",
  "original_transaction_id": "txn_a1b2c3d4e5f6",
  "original_sale_id": "POS-2025-02-13-0042",
  "refund_id": "REF-2025-02-15-0003",
  "refund_amount": 125.50,
  "points_reversed": -18825,
  "points_reversed_display": "-188 points",
  "previous_balance": 23825,
  "new_balance": 5000,
  "new_balance_display": "50 EUR",
  "timestamp": "2025-02-15T11:30:00Z",
  "receipt_message": "Refund processed. Points reversed: -188 points"
}
```

### Success Response - Redeemed Points Restored
**Scenario**: Customer redeemed 250 points (25 EUR) on purchase, now returning item

```json
{
  "success": true,
  "reversal_type": "redeem_reversal",
  "reversal_transaction_id": "txn_rev_z9y8x7w6",
  "original_transaction_id": "txn_z9y8x7w6v5u4",
  "original_sale_id": "POS-2025-02-13-0058",
  "refund_id": "REF-2025-02-15-0004",
  "refund_amount": 75.00,
  "points_restored": 250000,
  "points_restored_display": "+250 points",
  "previous_balance": 0,
  "new_balance": 250000,
  "new_balance_display": "25 EUR",
  "timestamp": "2025-02-15T11:35:00Z",
  "receipt_message": "Refund processed. Points restored: +250 points"
}
```

### Success Response - Both Earned and Redeemed
**Scenario**: Customer earned 50 points AND redeemed 100 points on same purchase, now refunding

```json
{
  "success": true,
  "reversal_type": "mixed_reversal",
  "reversals": [
    {
      "type": "earn_reversal",
      "points": -5000,
      "original_txn": "txn_earn_abc123"
    },
    {
      "type": "redeem_reversal",
      "points": 10000,
      "original_txn": "txn_redeem_xyz789"
    }
  ],
  "net_points_change": 5000,
  "previous_balance": 30000,
  "new_balance": 35000,
  "timestamp": "2025-02-15T11:40:00Z"
}
```

### Failure Response - Original Transaction Not Found
```json
{
  "success": false,
  "error_code": "ORIGINAL_TRANSACTION_NOT_FOUND",
  "error_message": "Cannot find loyalty transaction for this sale/order.",
  "original_sale_id": "POS-2025-02-13-0042",
  "possible_reasons": [
    "Customer did not use loyalty card on original purchase",
    "Sale ID mismatch or typo",
    "Transaction not yet synced (offline mode)"
  ],
  "resolution": "Verify sale ID or skip loyalty reversal"
}
```

### Failure Response - Already Refunded
```json
{
  "success": false,
  "error_code": "ALREADY_REFUNDED",
  "error_message": "Points already reversed for this transaction.",
  "original_transaction_id": "txn_a1b2c3d4e5f6",
  "reversal_transaction_id": "txn_rev_a1b2c3d4",
  "reversal_timestamp": "2025-02-15T10:00:00Z",
  "resolution": "No action needed. Reversal already processed."
}
```

### Side Effects
- Negative transaction(s) created in ledger (offsetting original)
- Customer balance adjusted (decreased if earn reversal, increased if redeem reversal)
- Audit log entry created with refund details
- If offline: Reversal queued in local SQLite
- Customer notification email sent (optional)

## Main Flows

### Flow 1: POS Refund - Earned Points Reversal

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌────────────┐    ┌──────────┐
│ Cashier │    │ Customer │    │ POS Agent│    │ Cloud API  │    │ Customer │
└────┬────┘    └────┬─────┘    └────┬─────┘    └─────┬──────┘    └────┬─────┘
     │              │               │                │                 │
     │ 1. Process   │               │                │                 │
     │    refund in │               │                │                 │
     │    Aniwin.net│               │                │                 │
     ├──────────────┼──────────────>│                │                 │
     │              │               │                │                 │
     │              │               │ 2. Detect      │                 │
     │              │               │    refund event│                 │
     │              │               ├────────┐       │                 │
     │              │               │        │       │                 │
     │              │               │<───────┘       │                 │
     │              │               │                │                 │
     │              │               │ 3. Lookup      │                 │
     │              │               │    original    │                 │
     │              │               │    sale_id     │                 │
     │              │               ├────────┐       │                 │
     │              │               │        │       │                 │
     │              │               │<───────┘       │                 │
     │              │               │                │                 │
     │ 4. Prompt:   │               │                │                 │
     │   "Customer  │               │                │                 │
     │    card for  │               │                │                 │
     │    refund?"  │               │                │                 │
     ├──────────────┼──────────────>│                │                 │
     │              │               │                │                 │
     │              │ 5. Tap card   │                │                 │
     │              ├──────────────>│                │                 │
     │              │               │                │                 │
     │              │               │ 6. Read UID    │                 │
     │              │               ├────────┐       │                 │
     │              │               │        │       │                 │
     │              │               │<───────┘       │                 │
     │              │               │                │                 │
     │              │               │ 7. POST /api/v1│                 │
     │              │               │   /transactions│                 │
     │              │               │   /reversal    │                 │
     │              │               ├───────────────>│                 │
     │              │               │                │                 │
     │              │               │                │ 8. Lookup orig │
     │              │               │                │    transaction │
     │              │               │                ├────────┐       │
     │              │               │                │        │       │
     │              │               │                │<───────┘       │
     │              │               │                │                 │
     │              │               │                │ 9. Validate    │
     │              │               │                │    not already │
     │              │               │                │    reversed    │
     │              │               │                ├────────┐       │
     │              │               │                │        │       │
     │              │               │                │<───────┘       │
     │              │               │                │                 │
     │              │               │                │10. Create      │
     │              │               │                │   reversal txn │
     │              │               │                │   (negative)   │
     │              │               │                ├────────┐       │
     │              │               │                │        │       │
     │              │               │                │<───────┘       │
     │              │               │                │                 │
     │              │               │                │11. Update      │
     │              │               │                │   balance      │
     │              │               │                ├────────┐       │
     │              │               │                │        │       │
     │              │               │                │<───────┘       │
     │              │               │                │                 │
     │              │               │12. 201 Created │                 │
     │              │               │<───────────────┤                 │
     │              │               │                │                 │
     │              │               │13. Print refund│                 │
     │              │               │   receipt      │                 │
     │              │               ├────────────────┼────────────────>│
     │              │               │                │                 │
     │ 14. Display  │               │                │                 │
     │    "Refund   │               │                │                 │
     │     complete"│               │                │                 │
     │<─────────────┼───────────────┤                │                 │
     │              │               │                │                 │
```

### Flow 2: PrestaShop Order Cancellation

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────────┐    ┌──────────┐
│ Customer │    │PrestaShop│    │  Loyalty │    │ Cloud API  │    │ Customer │
│ (Browser)│    │          │    │  Module  │    │            │    │ (Email)  │
└────┬─────┘    └────┬─────┘    └────┬─────┘    └─────┬──────┘    └────┬─────┘
     │              │               │                │                 │
     │ 1. Request   │               │                │                 │
     │    order     │               │                │                 │
     │    cancellation              │                │                 │
     ├─────────────>│               │                │                 │
     │              │               │                │                 │
     │              │ 2. Admin      │                │                 │
     │              │    changes    │                │                 │
     │              │    order status               │                 │
     │              │    to "Cancelled"             │                 │
     │              ├────────┐      │                │                 │
     │              │        │      │                │                 │
     │              │<───────┘      │                │                 │
     │              │               │                │                 │
     │              │ 3. Hook:      │                │                 │
     │              │   actionOrderStatus           │                 │
     │              │   UpdateAfter │                │                 │
     │              ├──────────────>│                │                 │
     │              │               │                │                 │
     │              │               │ 4. Check if    │                 │
     │              │               │    points were │                 │
     │              │               │    awarded     │                 │
     │              │               ├────────┐       │                 │
     │              │               │        │       │                 │
     │              │               │<───────┘       │                 │
     │              │               │                │                 │
     │              │               │ 5. POST /api/v1│                 │
     │              │               │   /transactions│                 │
     │              │               │   /reversal    │                 │
     │              │               ├───────────────>│                 │
     │              │               │                │                 │
     │              │               │                │ 6. Create      │
     │              │               │                │   reversal(s)  │
     │              │               │                ├────────┐       │
     │              │               │                │        │       │
     │              │               │                │<───────┘       │
     │              │               │                │                 │
     │              │               │ 7. 201 Created │                 │
     │              │               │<───────────────┤                 │
     │              │               │                │                 │
     │              │               │ 8. Update order│                 │
     │              │               │    note        │                 │
     │              │               ├───────────────>│                 │
     │              │               │                │                 │
     │              │ 9. Send       │                │                 │
     │              │    cancellation                │                 │
     │              │    email      │                │                 │
     │              ├───────────────┼────────────────┼────────────────>│
     │              │               │                │                 │
     │              │               │                │10. Send loyalty │
     │              │               │                │   reversal email│
     │              │               │                ├────────────────>│
     │              │               │                │                 │
```

### Flow 3: Offline Refund with Queued Reversal

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌────────────┐
│ Cashier │    │ POS Agent│    │Local DB  │    │ Cloud API  │
└────┬────┘    └────┬─────┘    └────┬─────┘    └─────┬──────┘
     │              │               │                │
     │ 1. Process   │               │                │
     │    refund    │               │                │
     ├─────────────>│               │                │
     │              │               │                │
     │              │ 2. Detect API │                │
     │              │    offline    │                │
     │              ├────────┐      │                │
     │              │        │      │                │
     │              │<───────┘      │                │
     │              │               │                │
     │              │ 3. Queue      │                │
     │              │    reversal   │                │
     │              ├──────────────>│                │
     │              │               │                │
     │              │ 4. Update     │                │
     │              │    local cache│                │
     │              ├──────────────>│                │
     │              │               │                │
     │ 5. Display   │               │                │
     │   "Refund    │               │                │
     │    queued"   │               │                │
     │<─────────────┤               │                │
     │              │               │                │
     │              │ ...Internet restored...        │
     │              │               │                │
     │              │ 6. Sync queued│                │
     │              │    reversals  │                │
     │              ├───────────────┼───────────────>│
     │              │               │                │
     │              │               │ 7. Process     │
     │              │               │    reversals   │
     │              │               │<───────────────┤
     │              │               │                │
```

## Edge Cases

### Edge Case 1: Refund Without Card Tap
**Scenario**: Customer returns item but doesn't have loyalty card with them

**Behavior**:
- Cashier can look up customer by email or phone
- Agent retrieves card UID from backend
- Reversal processed without card tap
- Alternative: Reversal queued as "pending customer verification"

### Edge Case 2: Points Already Expired Before Refund
**Scenario**: Customer purchased 3 months ago, earned points, points expired, now returning item

**Behavior**:
- Reversal creates negative transaction
- Balance becomes negative (e.g., -188 points)
- Customer notified: "Refund processed. Points were already expired."
- Negative balance persists as debt (can be zeroed by manager or future earns)

**Alternative Approach**: Allow reversal only if points haven't expired (business decision)

### Edge Case 3: Customer Already Redeemed Earned Points
**Scenario**: 
1. Customer earned 500 points on purchase
2. Customer redeemed 500 points on another purchase
3. Customer returns original item

**Behavior**:
- Reversal creates negative transaction (-500 points)
- Balance becomes negative: 0 - 500 = -500
- Customer must "repay" points with future purchases
- Manager can waive negative balance as goodwill

### Edge Case 4: Partial Refund Attempt
**Scenario**: Customer returns 1 of 3 items

**Behavior** (MVP):
- System does NOT support partial refunds
- Options:
  - **Option A**: Manager manually adjusts points proportionally
  - **Option B**: No point reversal (customer keeps all points)
  - **Option C**: Full reversal (customer loses all points, even for kept items)

**Recommendation**: Option A (manual adjustment) documented in MANUAL_ADJUSTMENTS.md

### Edge Case 5: Refund on Different Card
**Scenario**: Customer used Card A on purchase, presents Card B for refund

**Behavior**:
- Agent looks up original transaction by sale ID
- Finds Card A was used
- Reversal applied to Card A (original card)
- Customer notified: "Points reversed from card ending ...E5F6"

### Edge Case 6: Multiple Refunds from Same Sale
**Scenario**: Cashier accidentally processes refund twice

**Behavior**:
- First refund succeeds
- Second refund returns "ALREADY_REFUNDED" error
- No duplicate reversal
- Idempotency protection prevents issue

### Edge Case 7: Refund After Account Closed
**Scenario**: Customer closed loyalty account, then returns item

**Behavior**:
- Agent detects account deactivated
- Options:
  - Skip loyalty reversal (account already closed)
  - Reactivate account temporarily to process reversal
- Manager decision required

## Failure Modes

### Failure Mode 1: Original Transaction Not Found
**Symptoms**: Reversal API returns 404 "Transaction not found"

**System Behavior**:
- Agent displays: "No loyalty transaction found for this sale"
- Cashier can proceed with refund without loyalty reversal
- Options:
  - Skip loyalty (customer didn't use card on original purchase)
  - Manual lookup by manager

**Recovery**:
- Verify sale ID correct
- Check if sale was offline and not yet synced
- If truly missing, skip loyalty reversal

### Failure Mode 2: Cloud API Unreachable (Offline)
**Symptoms**: HTTP timeout during reversal request

**System Behavior**:
- Agent queues reversal in local SQLite
- Cashier sees: "Refund processed. Points will sync later."
- Refund proceeds normally
- Reversal syncs when online

**Recovery**:
- Automatic sync when internet restored
- Manual "Sync Now" option in agent UI

### Failure Mode 3: Database Write Failure
**Symptoms**: 500 Internal Server Error from reversal API

**System Behavior**:
- Agent displays: "System error. Please try again."
- Refund NOT queued locally (server-side issue)
- Cashier retries

**Recovery**:
- Retry reversal request
- If persistent, escalate to IT support
- Manager can manually adjust later

### Failure Mode 4: Negative Balance Exceeds Threshold
**Symptoms**: Reversal would create balance < -100 EUR

**System Behavior**:
- Backend flags for manager approval
- Agent displays: "Large negative balance. Manager approval required."
- Manager reviews and approves/rejects
- If approved, reversal proceeds

**Recovery**:
- Manager approval workflow
- Contact customer if fraud suspected

### Failure Mode 5: Concurrent Refund and Redemption
**Symptoms**: Customer returns item (reversal) while simultaneously redeeming points online

**System Behavior**:
- Database row-level locking prevents race condition
- One transaction completes first
- Second transaction sees updated balance
- Both succeed (order doesn't matter for correctness)

**Recovery**:
- No recovery needed (handled by database locks)

## Offline Behavior

### Offline Reversal Queue
Reversals queued when POS offline:

```sql
CREATE TABLE refund_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  refund_id TEXT NOT NULL UNIQUE,
  original_sale_id TEXT NOT NULL,
  card_uid TEXT NOT NULL,
  refund_amount REAL NOT NULL,
  points_to_reverse INTEGER NOT NULL,
  refund_timestamp TEXT NOT NULL,
  queued_at TEXT NOT NULL,
  sync_status TEXT DEFAULT 'pending',
  sync_attempts INTEGER DEFAULT 0,
  last_sync_attempt TEXT,
  sync_error TEXT,
  idempotency_key TEXT UNIQUE
);
```

### Sync Process
1. **Trigger**: Every 5 minutes, or manual "Sync Now"
2. **Order**: FIFO (oldest first)
3. **Retry**: Exponential backoff on failure
4. **Max Retries**: 10 attempts, then flag for manual review

### Offline Balance Impact
- When reversal queued offline, agent updates local cached balance
- Balance may be slightly incorrect until sync completes
- Customer sees approximate balance with "OFFLINE" indicator

## Security Considerations

### Authorization
- **Cashier**: Can process refunds up to 100 EUR
- **Manager**: Required for refunds > 100 EUR or negative balance > 50 EUR
- **Audit**: All reversals logged with who, when, why

### Fraud Prevention
- **Velocity Limit**: Max 10 refunds per card per month
- **Suspicious Pattern**: Alert if > 3 refunds in 1 week
- **Cross-Check**: Verify refund_id matches Aniwin.net record
- **Negative Balance Alert**: Flag accounts with balance < -50 EUR

### Idempotency Protection
- **Key Format**: `reversal_{refund_id}_{card_uid}`
- **Storage**: Keys stored 60 days (longer than POS refund window)
- **Validation**: Prevents duplicate reversal from retry or double-tap

### Audit Trail
Every reversal creates detailed audit log:
```json
{
  "event_type": "POINTS_REVERSAL",
  "reversal_transaction_id": "txn_rev_a1b2c3d4",
  "original_transaction_id": "txn_a1b2c3d4e5f6",
  "reversal_type": "earn_reversal",
  "timestamp": "2025-02-15T11:30:00Z",
  "card_uid": "04A1B2C3D4E5F6",
  "refund_id": "REF-2025-02-15-0003",
  "original_sale_id": "POS-2025-02-13-0042",
  "refund_amount": 125.50,
  "points_reversed": -18825,
  "balance_before": 23825,
  "balance_after": 5000,
  "refunded_by": "CASHIER-001",
  "terminal_id": "POS-TERMINAL-001"
}
```

## Related Documents

### Dependencies
- `02_architecture/WINDOWS_AGENT.md` - Agent processing refunds
- `02_architecture/CLOUD_BACKEND.md` - Backend API handling reversals
- `02_architecture/SYNC_STRATEGY.md` - Offline refund sync
- `04_integrations/ANIWIN_POS.md` - Detecting POS refunds
- `04_integrations/PRESTASHOP_MODULE.md` - Detecting order cancellations
- `05_data/TRANSACTION.md` - Reversal transaction structure
- `05_data/CUSTOMER.md` - Balance computation with reversals

### Related Features
- `03_features/EARN_POINTS_POS.md` - Original earn transactions
- `03_features/EARN_POINTS_ONLINE.md` - Original online earn transactions
- `03_features/REDEEM_POINTS_POS.md` - Original redeem transactions
- `03_features/REDEEM_POINTS_ONLINE.md` - Original online redeem transactions
- `03_features/MANUAL_ADJUSTMENTS.md` - Manual reversal alternative
- `03_features/EXPIRATION.md` - Handling expired points in refunds

### Integration Points
- `04_integrations/RECEIPT_PRINTER.md` - Printing refund receipt
- `04_integrations/EMAIL_SERVICE.md` - Refund notification emails
- `06_security/IDEMPOTENCY.md` - Duplicate reversal prevention

## Open Questions / TODOs

### TODO: Partial Refund Support
**Status**: Not implemented in MVP  
**Required by**: Phase 2  
**Description**: Support refunding individual line items from order with proportional point reversal

### TODO: Refund Time Limit
**Status**: Open question  
**Question**: Should there be time limit for refunds with point reversal (e.g., 30 days)?  
**Context**: Prevent abuse of "buy, earn, return" cycles  
**Impact**: Business policy, validation logic  
**Decision Required By**: Before launch

### TODO: Negative Balance Policy
**Status**: Open question  
**Question**: Should negative balances be allowed, or should refunds be blocked if balance would go negative?  
**Context**: Customer already spent earned points, now returning original purchase  
**Impact**: UX, accounting  
**Decision Required By**: Before launch

### Open Question: Expired Points Reversal
**Question**: If points expired before refund, should reversal restore them or keep them expired?  
**Context**: Customer earned points 4 months ago, now returning item  
**Impact**: Customer satisfaction vs business policy  
**Decision Required By**: Before launch

### Open Question: Refund Notification
**Question**: Should customer receive email/WhatsApp notification when points reversed?  
**Context**: Transparency vs potential negative customer experience  
**Impact**: Communication strategy  
**Decision Required By**: Before launch
