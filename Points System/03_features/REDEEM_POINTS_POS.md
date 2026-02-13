# Feature: Redeem Points at Physical POS

## Purpose

Enable customers to redeem accumulated Fidelity Points as payment toward purchases at the physical store by tapping their NFC loyalty card at checkout. Points are converted to EUR discount and applied to the sale total, with support for partial redemption (points + cash/card payment).

## Scope

### In Scope
- Card tap and balance lookup at checkout
- Cashier specifies redemption amount or "use all points"
- Points-to-EUR conversion (100 points = 0.01 EUR)
- Partial payment support (redeem some/all points, pay remainder with cash/card)
- Balance deduction in real-time (online) or queued (offline)
- Receipt printing with points redeemed and remaining balance
- Integration with Aniwin.net POS payment flow
- Idempotent transaction processing (no double redemption)
- Maximum redemption cap (up to 100% of sale amount)

### Out of Scope
- Points redemption on zero-value transactions (e.g., free items)
- Transferring points to cash without purchase
- Redeeming points across multiple sales simultaneously
- Points redemption from multiple cards on same sale
- Automatic redemption without customer consent

## Inputs

### From POS Windows Agent - Step 1: Check Balance
```json
{
  "card_uid": "04A1B2C3D4E5F6",
  "terminal_id": "POS-TERMINAL-001",
  "action": "check_balance_for_redemption"
}
```

### From POS Windows Agent - Step 2: Redeem Points
```json
{
  "card_uid": "04A1B2C3D4E5F6",
  "sale_id": "POS-2025-02-13-0058",
  "sale_amount": 75.00,
  "redemption_amount": 25.00,
  "currency": "EUR",
  "terminal_id": "POS-TERMINAL-001",
  "cashier_id": "CASHIER-001",
  "sale_timestamp": "2025-02-13T18:22:10Z",
  "transaction_type": "redeem",
  "idempotency_key": "redeem_POS-2025-02-13-0058_04A1B2C3D4E5F6"
}
```

### From Cashier UI
```json
{
  "redeem_option": "specify_amount",
  "redemption_amount": 25.00
}
```
OR
```json
{
  "redeem_option": "use_all_points",
  "max_redemption": 75.00
}
```

### Validation Rules
- `card_uid`: Must exist in customer database (enrolled card)
- `sale_amount`: Must be > 0.01 EUR
- `redemption_amount`: Must be > 0 AND <= customer balance AND <= sale_amount
- `idempotency_key`: Must be unique to prevent duplicate redemptions
- Customer balance must be >= redemption amount (in points equivalent)

## Outputs

### Success Response - Balance Check
```json
{
  "success": true,
  "card_uid": "04A1B2C3D4E5F6",
  "customer_name": "María García",
  "current_balance": 250000,
  "current_balance_eur": 25.00,
  "current_balance_display": "250 points (25.00 EUR)",
  "points_expiring_soon": 50000,
  "points_expiring_date": "2025-03-15"
}
```

### Success Response - Redeem Transaction (Online)
```json
{
  "success": true,
  "transaction_id": "txn_z9y8x7w6v5u4",
  "card_uid": "04A1B2C3D4E5F6",
  "customer_name": "María García",
  "sale_id": "POS-2025-02-13-0058",
  "sale_amount": 75.00,
  "redemption_amount": 25.00,
  "points_redeemed": 250000,
  "points_redeemed_display": "250 points",
  "previous_balance": 250000,
  "new_balance": 0,
  "new_balance_display": "0 EUR",
  "remaining_payment_due": 50.00,
  "timestamp": "2025-02-13T18:22:10Z",
  "receipt_message": "Redeemed 25.00 EUR in points! Remaining: 0 EUR"
}
```

### Success Response - Redeem Transaction (Offline/Queued)
```json
{
  "success": true,
  "transaction_id": "local_txn_005",
  "card_uid": "04A1B2C3D4E5F6",
  "customer_name": "María García",
  "sale_amount": 75.00,
  "redemption_amount": 25.00,
  "points_redeemed": 250000,
  "estimated_new_balance": 0,
  "balance_cache_warning": "Offline mode - balance may be outdated",
  "queued": true,
  "queue_position": 2,
  "remaining_payment_due": 50.00,
  "receipt_message": "Redeemed 25.00 EUR (Offline - will sync soon)"
}
```

### Failure Response - Insufficient Balance
```json
{
  "success": false,
  "error_code": "INSUFFICIENT_BALANCE",
  "error_message": "Customer has insufficient points.",
  "requested_amount": 25.00,
  "requested_points": 250000,
  "available_balance": 120000,
  "available_balance_eur": 12.00,
  "resolution": "Customer can redeem up to 12.00 EUR."
}
```

### Failure Response - Redemption Exceeds Sale Amount
```json
{
  "success": false,
  "error_code": "REDEMPTION_EXCEEDS_SALE",
  "error_message": "Cannot redeem more points than sale amount.",
  "sale_amount": 75.00,
  "requested_redemption": 100.00,
  "max_allowed_redemption": 75.00,
  "resolution": "Reduce redemption amount to 75.00 EUR or less."
}
```

### Side Effects
- Customer balance decreased by redeemed points
- Negative transaction record created in ledger
- Aniwin.net sale modified to reflect points discount
- Receipt printed with redemption details
- Audit log entry created
- If offline: Transaction queued in local SQLite database

## Main Flows

### Flow 1: Redeem Points - Online Happy Path

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌────────────┐    ┌──────────┐
│ Cashier │    │ Customer │    │ POS Agent│    │ Cloud API  │    │ Aniwin   │
│         │    │          │    │          │    │            │    │ POS      │
└────┬────┘    └────┬─────┘    └────┬─────┘    └─────┬──────┘    └────┬─────┘
     │              │               │                │                 │
     │ 1. Start sale│               │                │                 │
     │    in Aniwin │               │                │                 │
     ├──────────────┼───────────────┼────────────────┼────────────────>│
     │              │               │                │                 │
     │ 2. Ask: "Use │               │                │                 │
     │    loyalty   │               │                │                 │
     │    points?"  │               │                │                 │
     ├──────────────>│               │                │                 │
     │              │               │                │                 │
     │              │ 3. "Yes"      │                │                 │
     │<─────────────┤               │                │                 │
     │              │               │                │                 │
     │ 4. Click     │               │                │                 │
     │   "Check     │               │                │                 │
     │    Balance"  │               │                │                 │
     ├──────────────┼──────────────>│                │                 │
     │              │               │                │                 │
     │ 5. Prompt:   │               │                │                 │
     │   "Tap card" │               │                │                 │
     ├──────────────┼──────────────>│                │                 │
     │              │               │                │                 │
     │              │ 6. Tap card   │                │                 │
     │              ├──────────────>│                │                 │
     │              │               │                │                 │
     │              │               │ 7. Read UID    │                 │
     │              │               ├────────┐       │                 │
     │              │               │        │       │                 │
     │              │               │<───────┘       │                 │
     │              │               │                │                 │
     │              │               │ 8. GET /api/v1/│                 │
     │              │               │   customers/   │                 │
     │              │               │   {uid}/balance│                 │
     │              │               ├───────────────>│                 │
     │              │               │                │                 │
     │              │               │ 9. 200 OK      │                 │
     │              │               │   {balance:250}│                 │
     │              │               │<───────────────┤                 │
     │              │               │                │                 │
     │ 10. Display  │               │                │                 │
     │    "Balance: │               │                │                 │
     │     25 EUR"  │               │                │                 │
     │<─────────────┼───────────────┤                │                 │
     │              │               │                │                 │
     │ 11. Enter    │               │                │                 │
     │    redeem amt│               │                │                 │
     │    "25.00"   │               │                │                 │
     ├──────────────┼──────────────>│                │                 │
     │              │               │                │                 │
     │              │               │12. Validate    │                 │
     │              │               │   25 <= 25 ✓   │                 │
     │              │               │   25 <= 75 ✓   │                 │
     │              │               ├────────┐       │                 │
     │              │               │        │       │                 │
     │              │               │<───────┘       │                 │
     │              │               │                │                 │
     │              │               │13. POST /api/v1│                 │
     │              │               │   /transactions│                 │
     │              │               │   /redeem      │                 │
     │              │               ├───────────────>│                 │
     │              │               │                │                 │
     │              │               │                │14. Check balance│
     │              │               │                ├────────┐       │
     │              │               │                │        │       │
     │              │               │                │<───────┘       │
     │              │               │                │                 │
     │              │               │                │15. Create txn  │
     │              │               │                │   (negative)   │
     │              │               │                ├────────┐       │
     │              │               │                │        │       │
     │              │               │                │<───────┘       │
     │              │               │                │                 │
     │              │               │                │16. Update      │
     │              │               │                │   balance      │
     │              │               │                ├────────┐       │
     │              │               │                │        │       │
     │              │               │                │<───────┘       │
     │              │               │                │                 │
     │              │               │17. 201 Created │                 │
     │              │               │   {new_balance:│                 │
     │              │               │    0}          │                 │
     │              │               │<───────────────┤                 │
     │              │               │                │                 │
     │              │               │18. Apply 25 EUR│                 │
     │              │               │   discount     │                 │
     │              │               ├────────────────┼────────────────>│
     │              │               │                │                 │
     │              │               │19. Sale updated│                 │
     │              │               │   New total:50 │                 │
     │              │               │<───────────────┼─────────────────┤
     │              │               │                │                 │
     │ 20. Display  │               │                │                 │
     │    "Pay 50   │               │                │                 │
     │     EUR"     │               │                │                 │
     │<─────────────┼───────────────┤                │                 │
     │              │               │                │                 │
     │              │21. Pay with   │                │                 │
     │              │   card/cash   │                │                 │
     │<─────────────┤               │                │                 │
     │              │               │                │                 │
     │ 22. Complete │               │                │                 │
     │    sale      │               │                │                 │
     ├──────────────┼───────────────┼────────────────┼────────────────>│
     │              │               │                │                 │
     │              │               │23. Print receipt                 │
     │              │               │   with points  │                 │
     │              │               │   redeemed     │                 │
     │              │               ├────────────────>│                 │
     │              │               │                │                 │
```

### Flow 2: Use All Points (Partial Redemption)

```
Scenario: Customer has 30 EUR worth of points, sale is 75 EUR

1. Cashier checks balance → Shows 30 EUR available
2. Cashier clicks "Use All Points" button
3. Agent calculates: min(30, 75) = 30 EUR
4. Agent confirms: "Redeem 30 EUR in points? (45 EUR remaining)"
5. Cashier confirms
6. Agent calls API to redeem 30 EUR
7. Aniwin.net sale discounted by 30 EUR → New total: 45 EUR
8. Customer pays 45 EUR with cash/card
9. Receipt shows:
   - Original total: 75.00 EUR
   - Points redeemed: 30.00 EUR (300 points)
   - Remaining balance: 0.00 EUR
   - Amount paid: 45.00 EUR
```

### Flow 3: Offline Redemption with Cached Balance

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌────────────┐
│ Cashier │    │ Customer │    │ POS Agent│    │Local Cache │
└────┬────┘    └────┬─────┘    └────┬─────┘    └─────┬──────┘
     │              │               │                │
     │ 1. Check     │               │                │
     │    balance   │               │                │
     ├──────────────┼──────────────>│                │
     │              │               │                │
     │              │ 2. Tap card   │                │
     │              ├──────────────>│                │
     │              │               │                │
     │              │               │ 3. Ping API    │
     │              │               │   (FAILED)     │
     │              │               ├────────┐       │
     │              │               │        │       │
     │              │               │<───────┘       │
     │              │               │                │
     │              │               │ 4. Query cache │
     │              │               ├───────────────>│
     │              │               │                │
     │              │               │ 5. Last balance│
     │              │               │   from 2h ago  │
     │              │               │<───────────────┤
     │              │               │                │
     │ 6. Display   │               │                │
     │   "Balance:  │               │                │
     │    25 EUR    │               │                │
     │    (OFFLINE)"│               │                │
     │<─────────────┼───────────────┤                │
     │              │               │                │
     │ 7. WARNING:  │               │                │
     │   "Offline   │               │                │
     │    mode -    │               │                │
     │    balance   │               │                │
     │    may be    │               │                │
     │    outdated" │               │                │
     │<─────────────┼───────────────┤                │
     │              │               │                │
     │ 8. Confirm   │               │                │
     │   "Continue?"│               │                │
     ├──────────────┼──────────────>│                │
     │              │               │                │
     │              │               │ 9. Queue redeem│
     │              │               │   transaction  │
     │              │               ├───────────────>│
     │              │               │                │
     │              │               │10. Update local│
     │              │               │   cache balance│
     │              │               ├───────────────>│
     │              │               │                │
     │ 11. Proceed  │               │                │
     │    with sale │               │                │
     ├──────────────┼───────────────┼────────────────┤
     │              │               │                │
```

**Risk**: If customer redeemed points on another channel (PrestaShop) while POS offline, cached balance may be higher than actual. This could result in insufficient balance error during sync.

**Mitigation**: See "Offline Balance Sync Conflict" in Edge Cases.

## Edge Cases

### Edge Case 1: Customer Wants to Redeem More Than Sale Amount
**Scenario**: Sale is 30 EUR, customer has 50 EUR in points, wants to use all

**Behavior**:
- Agent caps redemption at sale amount (30 EUR)
- Display: "Maximum redemption: 30 EUR (sale total)"
- Remaining 20 EUR stays in customer balance
- Receipt shows: "Redeemed 30 EUR, Remaining balance: 20 EUR"

### Edge Case 2: Customer Has Exactly Enough Points
**Scenario**: Sale is 25 EUR, customer has exactly 25 EUR in points

**Behavior**:
- Agent redeems all 25 EUR
- Sale total becomes 0.00 EUR
- No additional payment required
- Aniwin.net records as "paid in full with loyalty points"
- Receipt shows "PAID WITH POINTS" and 0.00 EUR balance remaining

### Edge Case 3: Offline Balance Sync Conflict
**Scenario**: 
1. POS goes offline with cached balance of 50 EUR
2. Customer redeems 30 EUR online via PrestaShop
3. Customer tries to redeem 40 EUR at POS (offline)
4. POS allows (based on cached 50 EUR)
5. POS comes online and syncs

**Behavior**:
- Sync detects insufficient balance (actual balance: 20 EUR, attempted: 40 EUR)
- Agent flags transaction as `sync_status: 'failed_insufficient_balance'`
- Manager receives alert: "Transaction failed - insufficient balance"
- **Resolution Options**:
  - **Option A**: Void the POS sale (requires customer to return)
  - **Option B**: Customer pays the difference (40 - 20 = 20 EUR shortfall)
  - **Option C**: Accept as loss (business decision for goodwill)

**Prevention**: Limit offline redemption to <= 50% of cached balance (configurable)

### Edge Case 4: Multiple Redemptions Same Card, Different Terminals (Offline)
**Scenario**: Two terminals offline, same card redeems at both

**Behavior**:
- Both terminals allow redemption based on cached balance
- First terminal syncs successfully
- Second terminal sync fails (insufficient balance)
- Manager notified of conflict
- Manual resolution required (same as Edge Case 3)

### Edge Case 5: Redemption Amount Not Available in Cash Register
**Scenario**: Customer redeems 47.37 EUR, cashier doesn't have exact change

**Behavior**:
- Cashier can adjust redemption to round number (e.g., 47.00 EUR)
- Agent recalculates remaining payment
- Redemption processed with adjusted amount

### Edge Case 6: Customer Changes Mind Mid-Transaction
**Scenario**: Customer decides not to redeem after balance check

**Behavior**:
- Cashier clicks "Cancel Redemption"
- No transaction created
- Sale proceeds without points discount

### Edge Case 7: Redemption on Zero-Value Sale
**Scenario**: Sale total is 0 EUR (e.g., exchange or return)

**Behavior**:
- Agent prevents redemption
- Display: "Cannot redeem points on zero-value transaction"

## Failure Modes

### Failure Mode 1: Balance Check Fails (Online)
**Symptoms**: API returns 500 or times out during balance check

**System Behavior**:
- Display: "Cannot check balance. Try again or proceed without points."
- Cashier options:
  - Retry balance check
  - Proceed with sale without redemption
  - Wait for connection

**Recovery**:
- Retry automatically after 3 seconds
- Manual retry button
- If persistent, fall back to offline mode with cached balance

### Failure Mode 2: Redemption Transaction Fails After Balance Check
**Symptoms**: Balance check succeeds, but redemption API call fails

**System Behavior**:
- Display: "Redemption failed. Sale not modified."
- Cashier must decide:
  - Retry redemption
  - Proceed without redemption
- Sale remains at original amount

**Recovery**:
- Retry redemption transaction
- If fails repeatedly, proceed without points
- Customer can redeem later using manual adjustment

### Failure Mode 3: Aniwin.net Discount Application Fails
**Symptoms**: API credits points successfully, but Aniwin.net rejects discount

**System Behavior**:
- **Critical failure**: Points already deducted but sale not discounted
- Agent immediately calls reversal API to restore points
- Display: "System error. Points not deducted. Please retry."
- Audit log flagged for investigation

**Recovery**:
- Automatic reversal transaction
- Cashier retries redemption
- If persistent, escalate to manager

### Failure Mode 4: Insufficient Balance Detected Late
**Symptoms**: Cached balance shows 30 EUR, API reveals only 10 EUR available

**System Behavior**:
- API returns 402 "Insufficient Balance"
- Display: "Actual balance: 10 EUR. Adjust redemption amount."
- Cashier can redeem up to 10 EUR or cancel

**Recovery**:
- Update local cache with correct balance
- Retry with adjusted amount

### Failure Mode 5: Idempotency Key Collision
**Symptoms**: Duplicate redemption attempt (e.g., double-tap, retry)

**System Behavior**:
- API returns 409 Conflict with original transaction details
- Agent checks if original succeeded
- If yes: Display "Points already redeemed" and skip
- If no: Regenerate key and retry

**Recovery**:
- Automatic detection and skip
- No customer impact

### Failure Mode 6: Receipt Printer Fails After Redemption
**Symptoms**: Points deducted successfully, receipt won't print

**System Behavior**:
- Redemption still successful
- Display redemption details on screen
- Save transaction for later reprint
- Email receipt to customer (if email on file)

**Recovery**:
- Fix printer
- Reprint from transaction history

## Offline Behavior

### Offline Redemption Requirements
1. **Cached Balance**: Agent must have recent balance (< 24 hours old)
2. **Conservative Limit**: By default, limit offline redemption to 50% of cached balance
3. **Manager Override**: Manager can allow up to 100% of cached balance
4. **Warning Display**: Always show "OFFLINE - Balance may be outdated"

### Offline Queue Structure
```sql
CREATE TABLE redeem_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  card_uid TEXT NOT NULL,
  sale_id TEXT NOT NULL UNIQUE,
  sale_amount REAL NOT NULL,
  redemption_amount REAL NOT NULL,
  points_redeemed INTEGER NOT NULL,
  sale_timestamp TEXT NOT NULL,
  queued_at TEXT NOT NULL,
  cached_balance_before INTEGER NOT NULL,
  estimated_balance_after INTEGER NOT NULL,
  sync_status TEXT DEFAULT 'pending',
  sync_attempts INTEGER DEFAULT 0,
  last_sync_attempt TEXT,
  sync_error TEXT,
  idempotency_key TEXT UNIQUE
);
```

### Offline Redemption Limits
**Configurable Settings**:
- `offline_redemption_max_percent`: Default 50%
- `offline_redemption_absolute_max`: Default 100 EUR
- `cached_balance_max_age`: Default 24 hours

**Validation**:
```python
if offline_mode:
    max_allowed = min(
        cached_balance * offline_redemption_max_percent,
        offline_redemption_absolute_max,
        sale_amount
    )
    if redemption_amount > max_allowed:
        raise OfflineRedemptionLimitExceeded(max_allowed)
```

### Sync Conflict Resolution

**Insufficient Balance During Sync**:
1. Agent detects sync failure: actual balance < redeemed amount
2. Transaction marked `sync_status: 'failed_insufficient_balance'`
3. Manager alert with details:
   - Card UID
   - Cached balance used
   - Actual balance
   - Shortfall amount
4. Manager actions:
   - **Approve**: Accept as business loss, force sync (creates negative balance)
   - **Void Sale**: Reverse in Aniwin.net, delete queued transaction
   - **Collect Payment**: Contact customer for shortfall payment

## Security Considerations

### Authorization
- **Cashier**: Can initiate redemption up to 100 EUR
- **Manager**: Can approve redemptions > 100 EUR
- **Offline Manager Override**: Can bypass 50% offline limit

### Idempotency Protection
- **Key Format**: `redeem_{sale_id}_{card_uid}_{timestamp}`
- **Validation**: Backend checks for duplicate redemption within 24 hours
- **Prevents**: Double redemption from retry, card re-tap, sync collision

### Audit Trail
Every redemption creates detailed audit log:
```json
{
  "event_type": "POINTS_REDEMPTION",
  "transaction_id": "txn_z9y8x7w6v5u4",
  "timestamp": "2025-02-13T18:22:10Z",
  "card_uid": "04A1B2C3D4E5F6",
  "sale_id": "POS-2025-02-13-0058",
  "sale_amount": 75.00,
  "redemption_amount": 25.00,
  "points_redeemed": 250000,
  "balance_before": 250000,
  "balance_after": 0,
  "terminal_id": "POS-TERMINAL-001",
  "cashier_id": "CASHIER-001",
  "offline_mode": false
}
```

### Fraud Prevention
- **Velocity Limit**: Max 10 redemptions per card per day
- **Large Transaction Alert**: Flag redemptions > 100 EUR for review
- **Negative Balance Prevention**: Cannot redeem more than available
- **Offline Abuse Prevention**: 50% cached balance limit

### Balance Integrity
- **Atomic Operations**: Balance check + deduction in single DB transaction
- **Race Condition Prevention**: Row-level locking on customer balance
- **Consistency**: Balance always computed from immutable ledger

## Related Documents

### Dependencies
- `02_architecture/WINDOWS_AGENT.md` - Agent processing redemptions
- `02_architecture/CLOUD_BACKEND.md` - Backend API handling redemptions
- `02_architecture/SYNC_STRATEGY.md` - Offline sync with conflict resolution
- `02_architecture/CONFLICT_RESOLUTION.md` - Balance conflict handling
- `04_integrations/ANIWIN_POS.md` - Applying discount to sale
- `04_integrations/NFC_READER.md` - Card UID reading
- `05_data/TRANSACTION.md` - Redemption transaction structure
- `05_data/CUSTOMER.md` - Balance computation

### Related Features
- `03_features/CARD_ENROLLMENT.md` - Customer must enroll before redeeming
- `03_features/EARN_POINTS_POS.md` - Earning points to redeem
- `03_features/BALANCE_QUERY.md` - Checking available balance
- `03_features/REFUND_HANDLING.md` - Reversing redemption on refund
- `03_features/EXPIRATION.md` - Only non-expired points can be redeemed

### Integration Points
- `04_integrations/RECEIPT_PRINTER.md` - Printing redemption receipt
- `06_security/IDEMPOTENCY.md` - Duplicate prevention

## Open Questions / TODOs

### TODO: Redemption Limits Per Transaction
**Status**: Not implemented  
**Required by**: Phase 2  
**Description**: Implement business rule for maximum redemption per transaction (e.g., 100 EUR max)

### TODO: Priority Redemption (FIFO Expiration)
**Status**: Designed but not implemented  
**Required by**: Phase 2  
**Description**: Automatically redeem points closest to expiration first

### TODO: Partial Payment Receipt Format
**Status**: Open question  
**Question**: Should receipt show points redemption as separate line item or as discount?  
**Decision Required By**: Before launch

### Open Question: Negative Balance Handling
**Question**: Should system allow temporary negative balance in offline mode?  
**Context**: Edge Case 3 - offline sync conflict may result in negative balance  
**Impact**: Business policy, recovery procedures  
**Decision Required By**: Before deploying multiple terminals

### Open Question: Redemption Rounding
**Question**: Customer has 25.47 EUR in points, sale is 30 EUR. Can redeem exactly 25.47 or round to 25.00?  
**Context**: Aniwin.net discount precision, receipt display  
**Impact**: UX, calculation logic  
**Decision Required By**: Before launch

### Open Question: Redemption on Discounted Items
**Question**: Can points be redeemed on already-discounted sale items?  
**Context**: Promotional sales, clearance items  
**Impact**: Business rules, profit margins  
**Decision Required By**: Before launch marketing campaigns
