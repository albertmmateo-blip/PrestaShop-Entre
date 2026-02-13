# Feature: Earn Points at Physical POS

## Purpose

Enable customers to earn Fidelity Points when making purchases at the physical store by tapping their NFC loyalty card at checkout. Points are automatically calculated based on the purchase amount and credited to the customer's balance, even when the POS terminal is offline.

## Scope

### In Scope
- Card tap and UID reading at checkout
- Points calculation (0.015 EUR per 1 EUR spent = 150 points per EUR)
- Balance crediting in real-time (online) or queued (offline)
- Receipt printing with points earned and new balance
- Integration with Aniwin.net POS sale data
- Idempotent transaction processing (no duplicates)
- Automatic sync when offline transactions are queued

### Out of Scope
- Points earning on returns or refunds (see REFUND_HANDLING.md)
- Bonus points promotions or multipliers (future enhancement)
- Points earning on partial payments (only full sale amount)
- Split transactions across multiple cards
- Manager override of points calculation

## Inputs

### From POS Windows Agent
```json
{
  "card_uid": "04A1B2C3D4E5F6",
  "sale_id": "POS-2025-02-13-0042",
  "sale_amount": 125.50,
  "currency": "EUR",
  "terminal_id": "POS-TERMINAL-001",
  "cashier_id": "CASHIER-001",
  "sale_timestamp": "2025-02-13T16:45:30Z",
  "transaction_type": "earn",
  "idempotency_key": "earn_POS-2025-02-13-0042_04A1B2C3D4E5F6"
}
```

### From Aniwin.net POS System
The Windows agent extracts sale data from Aniwin.net through one of these methods:
1. **Database Hook**: Query Aniwin.net database for completed sales
2. **Receipt Export**: Parse printed receipt text file
3. **File Watcher**: Monitor export folder for new sale records

Extracted data format:
```json
{
  "sale_id": "POS-2025-02-13-0042",
  "sale_amount": 125.50,
  "sale_date": "2025-02-13",
  "sale_time": "16:45:30",
  "items": [
    {"sku": "PROD-001", "name": "Product A", "quantity": 2, "price": 50.00},
    {"sku": "PROD-002", "name": "Product B", "quantity": 1, "price": 25.50}
  ],
  "payment_method": "card",
  "status": "completed"
}
```

### Validation Rules
- `card_uid`: Must exist in customer database (enrolled card)
- `sale_amount`: Must be > 0.01 EUR (minimum 1 cent)
- `sale_id`: Unique POS transaction ID, format validated
- `idempotency_key`: Must be unique to prevent duplicate credits

## Outputs

### Success Response - Online Mode
```json
{
  "success": true,
  "transaction_id": "txn_a1b2c3d4e5f6",
  "card_uid": "04A1B2C3D4E5F6",
  "customer_name": "María García",
  "sale_amount": 125.50,
  "points_earned": 18825,
  "points_earned_display": "188.25 EUR worth",
  "previous_balance": 5000,
  "new_balance": 23825,
  "new_balance_display": "238.25 EUR worth",
  "timestamp": "2025-02-13T16:45:30Z",
  "receipt_message": "Earned 188 points! New balance: 238 EUR"
}
```

### Success Response - Offline Mode (Queued)
```json
{
  "success": true,
  "transaction_id": "local_txn_001",
  "card_uid": "04A1B2C3D4E5F6",
  "customer_name": "María García",
  "sale_amount": 125.50,
  "points_earned": 18825,
  "points_earned_display": "188.25 EUR worth",
  "balance_unavailable": true,
  "queued": true,
  "queue_position": 3,
  "receipt_message": "Earned 188 points! (Offline - will sync soon)",
  "estimated_sync": "When internet connection restored"
}
```

### Failure Response - Card Not Enrolled
```json
{
  "success": false,
  "error_code": "CARD_NOT_ENROLLED",
  "error_message": "This card is not registered. Please enroll at customer service.",
  "card_uid": "04A1B2C3D4E5F6",
  "resolution": "Direct customer to enrollment counter."
}
```

### Failure Response - Duplicate Transaction
```json
{
  "success": false,
  "error_code": "DUPLICATE_TRANSACTION",
  "error_message": "Points already awarded for this sale.",
  "original_transaction_id": "txn_x9y8z7w6v5u4",
  "original_timestamp": "2025-02-13T16:45:30Z",
  "resolution": "Transaction skipped to prevent duplicate credit."
}
```

### Side Effects
- Customer balance increased by calculated points
- Transaction record created in ledger
- Receipt printed with points information
- Audit log entry created
- If offline: Transaction queued in local SQLite database

## Main Flows

### Flow 1: Earn Points - Online Happy Path

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌────────────┐    ┌──────────┐
│ Cashier │    │ Customer │    │ POS Agent│    │ Cloud API  │    │ Customer │
│         │    │          │    │          │    │            │    │ (Receipt)│
└────┬────┘    └────┬─────┘    └────┬─────┘    └─────┬──────┘    └────┬─────┘
     │              │               │                │                 │
     │ 1. Complete  │               │                │                 │
     │    sale in   │               │                │                 │
     │    Aniwin.net│               │                │                 │
     ├──────────────┼──────────────>│                │                 │
     │              │               │                │                 │
     │              │               │ 2. Detect new  │                 │
     │              │               │    sale (hook/ │                 │
     │              │               │    export)     │                 │
     │              │               ├────────┐       │                 │
     │              │               │        │       │                 │
     │              │               │<───────┘       │                 │
     │              │               │                │                 │
     │ 3. Prompt:   │               │                │                 │
     │   "Tap loyalty│              │                │                 │
     │    card"     │               │                │                 │
     ├──────────────┼──────────────>│                │                 │
     │              │               │                │                 │
     │              │ 4. Tap card   │                │                 │
     │              ├──────────────>│                │                 │
     │              │               │                │                 │
     │              │               │ 5. Read UID    │                 │
     │              │               ├────────┐       │                 │
     │              │               │        │       │                 │
     │              │               │<───────┘       │                 │
     │              │               │                │                 │
     │              │               │ 6. POST /api/v1│                 │
     │              │               │   /transactions│                 │
     │              │               │   /earn        │                 │
     │              │               ├───────────────>│                 │
     │              │               │                │                 │
     │              │               │                │ 7. Validate UID│
     │              │               │                ├────────┐       │
     │              │               │                │        │       │
     │              │               │                │<───────┘       │
     │              │               │                │                 │
     │              │               │                │ 8. Check       │
     │              │               │                │    idempotency │
     │              │               │                ├────────┐       │
     │              │               │                │        │       │
     │              │               │                │<───────┘       │
     │              │               │                │                 │
     │              │               │                │ 9. Calculate   │
     │              │               │                │    points      │
     │              │               │                │    125.50*0.015│
     │              │               │                ├────────┐       │
     │              │               │                │        │       │
     │              │               │                │<───────┘       │
     │              │               │                │                 │
     │              │               │                │10. Create txn  │
     │              │               │                │   in ledger    │
     │              │               │                ├────────┐       │
     │              │               │                │        │       │
     │              │               │                │<───────┘       │
     │              │               │                │                 │
     │              │               │                │11. Update      │
     │              │               │                │   balance cache│
     │              │               │                ├────────┐       │
     │              │               │                │        │       │
     │              │               │                │<───────┘       │
     │              │               │                │                 │
     │              │               │ 12. 201 Created│                 │
     │              │               │    {txn_id,    │                 │
     │              │               │     points,    │                 │
     │              │               │     balance}   │                 │
     │              │               │<───────────────┤                 │
     │              │               │                │                 │
     │              │               │13. Generate    │                 │
     │              │               │   receipt text │                 │
     │              │               ├────────┐       │                 │
     │              │               │        │       │                 │
     │              │               │<───────┘       │                 │
     │              │               │                │                 │
     │              │               │14. Print receipt                 │
     │              │               ├─────────────────────────────────>│
     │              │               │                │                 │
     │ 15. Display  │               │                │                 │
     │    "188 pts  │               │                │                 │
     │     earned!" │               │                │                 │
     │<─────────────┼───────────────┤                │                 │
     │              │               │                │                 │
```

### Flow 2: Earn Points - Offline Mode (Queued)

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌────────────┐
│ Cashier │    │ Customer │    │ POS Agent│    │Local SQLite│
└────┬────┘    └────┬─────┘    └────┬─────┘    └─────┬──────┘
     │              │               │                │
     │ 1. Complete  │               │                │
     │    sale      │               │                │
     ├──────────────┼──────────────>│                │
     │              │               │                │
     │              │               │ 2. Detect sale │
     │              │               ├────────┐       │
     │              │               │        │       │
     │              │               │<───────┘       │
     │              │               │                │
     │ 3. Prompt:   │               │                │
     │   "Tap card" │               │                │
     ├──────────────┼──────────────>│                │
     │              │               │                │
     │              │ 4. Tap card   │                │
     │              ├──────────────>│                │
     │              │               │                │
     │              │               │ 5. Read UID    │
     │              │               ├────────┐       │
     │              │               │        │       │
     │              │               │<───────┘       │
     │              │               │                │
     │              │               │ 6. Check cloud │
     │              │               │    API (FAILED)│
     │              │               ├────────┐       │
     │              │               │        │       │
     │              │               │<───────┘       │
     │              │               │                │
     │              │               │ 7. Calculate   │
     │              │               │    points local│
     │              │               ├────────┐       │
     │              │               │        │       │
     │              │               │<───────┘       │
     │              │               │                │
     │              │               │ 8. INSERT INTO │
     │              │               │   earn_queue   │
     │              │               ├───────────────>│
     │              │               │                │
     │              │               │ 9. OK          │
     │              │               │<───────────────┤
     │              │               │                │
     │              │               │10. Print receipt                │
     │              │               │   with "OFFLINE"│               │
     │              │               ├────────────────>│               │
     │              │               │                │                │
     │ 11. Display  │               │                │                │
     │    "188 pts  │               │                │                │
     │     queued"  │               │                │                │
     │<─────────────┼───────────────┤                │                │
     │              │               │                │                │
     │              │               │ ...5 min later...               │
     │              │               │                │                │
     │              │               │12. Retry sync  │                │
     │              │               │   (SUCCESS)    │                │
     │              │               ├────────┐       │                │
     │              │               │        │       │                │
     │              │               │<───────┘       │                │
     │              │               │                │                │
     │              │               │13. UPDATE      │                │
     │              │               │   sync_status  │                │
     │              │               ├───────────────>│                │
     │              │               │                │                │
```

### Flow 3: Automatic Sale Detection

The Windows Agent continuously monitors Aniwin.net for completed sales:

**Method 1: Database Polling**
1. Every 5 seconds, query Aniwin.net database for new sales since last check
2. Filter for `status = 'completed'` AND `timestamp > last_check_time`
3. For each new sale, check if loyalty card was associated
4. If card UID present, trigger earn points flow

**Method 2: File Watcher**
1. Aniwin.net exports sale receipts to `C:\AniwinData\Receipts\`
2. Agent monitors folder for new `.txt` files
3. Parse receipt file for sale details
4. Extract sale ID and amount
5. Trigger earn points flow

## Edge Cases

### Edge Case 1: No Card Tap (Cashier Forgets)
**Scenario**: Sale completes but customer doesn't tap card

**Behavior**:
- Agent waits 10 seconds after sale completion
- If no card tap, show reminder: "Did customer tap loyalty card?"
- Cashier can select "No card" to proceed
- Customer can return later to credit points manually (requires manager)

### Edge Case 2: Card Tap Before Sale Complete
**Scenario**: Customer taps card before sale is finalized

**Behavior**:
- Agent stores card UID in memory
- Waits for sale completion event from Aniwin.net
- When sale completes, automatically credits points to stored UID
- Timeout: 2 minutes, then forgets stored UID

### Edge Case 3: Multiple Cards Tapped
**Scenario**: Customer taps two different cards for same sale

**Behavior**:
- Agent uses FIRST card tapped
- Displays: "Using card ending in ...E5F6"
- Cashier can cancel and retry if wrong card

### Edge Case 4: Very Small Purchase (< 0.01 EUR)
**Scenario**: Free item or promotional transaction with 0 amount

**Behavior**:
- No points earned (calculation rounds down to 0)
- Receipt shows: "No points earned (minimum 0.01 EUR)"

### Edge Case 5: Very Large Purchase (> 10,000 EUR)
**Scenario**: Bulk order or special event

**Behavior**:
- Points calculated normally (no cap)
- If > 1,000 points earned, agent flags for review
- Manager receives notification for unusual activity
- Prevents bulk point farming detection

### Edge Case 6: Duplicate Card Tap
**Scenario**: Customer accidentally taps card twice

**Behavior**:
- Agent ignores second tap within 30 seconds
- Displays: "Card already processed for this sale"

### Edge Case 7: Sale Cancellation After Points Awarded
**Scenario**: Sale is voided in Aniwin.net after points already credited

**Behavior**:
- Agent detects void event
- Automatically creates reversal transaction (negative points)
- Customer balance updated
- Receipt printed: "Points reversed for cancelled sale"

## Failure Modes

### Failure Mode 1: Cloud API Timeout (Offline Mode)
**Symptoms**: HTTP request timeout after 5 seconds

**System Behavior**:
- Agent queues transaction in local SQLite
- User sees: "Offline mode. Points will sync later."
- Retry every 5 minutes
- Status dashboard shows queue size

**Recovery**:
- Automatic when internet restored
- Manual "Sync Now" button in agent UI

### Failure Mode 2: Idempotency Key Collision
**Symptoms**: Backend returns 409 Conflict

**System Behavior**:
- Agent checks if this is legitimate duplicate or sync error
- If duplicate: Display "Points already awarded" and skip
- If sync error: Regenerate idempotency key and retry

**Recovery**:
- Skip duplicate silently
- Log warning for admin review

### Failure Mode 3: NFC Reader Not Responding
**Symptoms**: No UID read after 5 seconds

**System Behavior**:
- Display: "Card read error. Please try again."
- Retry up to 3 times
- If failed: Allow manual UID entry (manager only)

**Recovery**:
- Restart NFC reader service
- Check USB connection
- Replace reader if hardware failure

### Failure Mode 4: Aniwin.net Database Locked
**Symptoms**: Database query returns "database locked" error

**System Behavior**:
- Agent retries after 1 second
- Up to 5 retries
- If still locked: Skip this sale detection cycle
- Sale will be caught in next cycle (5 seconds later)

**Recovery**:
- Automatic retry
- No data loss (sale still in Aniwin.net database)

### Failure Mode 5: Points Calculation Error
**Symptoms**: Calculation returns NaN or negative value

**System Behavior**:
- Agent logs error with full context
- Display: "Error calculating points. Please contact support."
- Sale proceeds normally but no points awarded
- Manual adjustment required

**Recovery**:
- Review error log
- Award points manually using MANUAL_ADJUSTMENTS.md flow
- Fix calculation bug if software issue

### Failure Mode 6: Receipt Printer Offline
**Symptoms**: Receipt print command fails

**System Behavior**:
- Points still credited successfully
- Display on screen: "Points earned: 188 (receipt printer offline)"
- Transaction saved with flag `receipt_printed: false`
- Reprint available from transaction history

**Recovery**:
- Check printer connection
- Reprint receipt from agent UI using transaction ID

## Offline Behavior

### Offline Detection
Agent determines offline state by:
1. Ping cloud backend every 30 seconds (`GET /api/v1/health`)
2. If 2 consecutive pings fail: Enter offline mode
3. Display "OFFLINE" indicator in agent status bar

### Offline Queue Structure
```sql
CREATE TABLE earn_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  card_uid TEXT NOT NULL,
  sale_id TEXT NOT NULL UNIQUE,
  sale_amount REAL NOT NULL,
  points_earned INTEGER NOT NULL,
  sale_timestamp TEXT NOT NULL,
  queued_at TEXT NOT NULL,
  sync_status TEXT DEFAULT 'pending',
  sync_attempts INTEGER DEFAULT 0,
  last_sync_attempt TEXT,
  sync_error TEXT,
  idempotency_key TEXT UNIQUE
);
```

### Sync Process
1. **Trigger**: Every 5 minutes, or on manual "Sync Now" button
2. **Batch Size**: Sync up to 100 transactions per batch
3. **Order**: FIFO (oldest first) to preserve transaction order
4. **Retry**: Failed transactions retry with exponential backoff
5. **Max Retries**: After 10 failed attempts, flag for manual review

### Sync Conflict Resolution

**Conflict Type 1: Duplicate Transaction**
- Backend returns 409 with existing transaction ID
- Agent marks local transaction as `sync_status: 'duplicate'`
- No further action (points already credited on other terminal)

**Conflict Type 2: Card Deactivated**
- Backend returns 404 "Card not found"
- Agent marks transaction as `sync_status: 'failed_card_deactivated'`
- Manager notified to investigate

**Conflict Type 3: Backend Balance Mismatch**
- Agent's cached balance differs from backend
- Agent trusts backend as source of truth
- Updates local cache
- Transaction proceeds normally

## Security Considerations

### Idempotency Protection
- **Key Generation**: `earn_{sale_id}_{card_uid}`
- **Storage**: Idempotency keys stored in backend for 7 days
- **Validation**: Backend checks key before processing transaction
- **Prevents**: Duplicate credits from retry, multi-terminal, or sync

### Transaction Integrity
- **Immutable Ledger**: All earn transactions append-only
- **No Updates**: Cannot modify transaction amount after creation
- **Audit Trail**: Full history of who, when, where, why
- **Reversal Only**: Errors corrected with offsetting transactions

### Fraud Prevention
- **Rate Limiting**: Max 50 earn transactions per card per day
- **Velocity Checks**: Alert if > 5 transactions in 5 minutes
- **Amount Threshold**: Flag transactions > 1,000 EUR for review
- **Pattern Detection**: Alert on unusual patterns (future enhancement)

### Authorization
- **Cashier Role**: Can initiate earn transaction (no special permission)
- **Manager Role**: Can override errors, manual adjustments
- **API Key**: Windows agent authenticates with API key in header

### Data Protection
- **PII Logging**: Customer name not logged in earn transactions (only card UID)
- **Encryption**: Sale data encrypted in transit (HTTPS)
- **Local Storage**: SQLite queue file protected by Windows file permissions

## Related Documents

### Dependencies
- `02_architecture/WINDOWS_AGENT.md` - Agent processing earn transactions
- `02_architecture/CLOUD_BACKEND.md` - Backend API handling earn requests
- `02_architecture/SYNC_STRATEGY.md` - Offline sync mechanism
- `04_integrations/ANIWIN_POS.md` - POS sale data extraction
- `04_integrations/NFC_READER.md` - Card UID reading
- `05_data/TRANSACTION.md` - Transaction ledger structure
- `05_data/CUSTOMER.md` - Customer balance updates

### Related Features
- `03_features/CARD_ENROLLMENT.md` - Customer must enroll before earning
- `03_features/REDEEM_POINTS_POS.md` - Using earned points
- `03_features/REFUND_HANDLING.md` - Reversing earned points on refunds
- `03_features/BALANCE_QUERY.md` - Checking earned points balance
- `03_features/EXPIRATION.md` - Points expire 3 months after earning

### Integration Points
- `04_integrations/RECEIPT_PRINTER.md` - Printing earn confirmation
- `06_security/IDEMPOTENCY.md` - Duplicate prevention strategy

## Open Questions / TODOs

### TODO: Bonus Points Campaigns
**Status**: Designed but not implemented  
**Required by**: Phase 2 (Marketing campaigns)  
**Description**: Support promotional earn multipliers (e.g., "Double points on Tuesdays")

### TODO: Category-Based Earn Rates
**Status**: Future enhancement  
**Required by**: TBD based on business needs  
**Description**: Different earn rates for different product categories (e.g., higher rate on electronics)

### TODO: Receipt Email Option
**Status**: Not implemented  
**Required by**: Post-MVP  
**Description**: Option to email receipt instead of printing, includes points earned

### Open Question: Minimum Purchase Amount
**Question**: Should there be minimum purchase amount to earn points (e.g., 5 EUR)?  
**Context**: Prevent gaming system with tiny transactions  
**Impact**: Validation logic, business rules  
**Decision Required By**: Before launch

### Open Question: Points Rounding
**Question**: Current system rounds points to nearest integer. Should we support fractional points?  
**Context**: 0.50 EUR purchase currently earns 0 points (0.0075 EUR)  
**Impact**: Database schema (INTEGER vs DECIMAL), display logic  
**Decision Required By**: Before launch

### Open Question: Multi-Terminal Sale Correlation
**Question**: If multiple terminals complete sales simultaneously, how to prevent race condition?  
**Context**: Customer taps card at Terminal 1, then immediately at Terminal 2  
**Impact**: Sync logic, idempotency key generation  
**Decision Required By**: Before deploying multiple terminals
