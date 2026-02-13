# Feature: Manual Adjustments

## Purpose

Enable managers to manually adjust customer loyalty point balances to correct errors, resolve disputes, provide customer service gestures, or handle edge cases not covered by automated flows (e.g., partial refunds, system errors, compensation).

## Scope

### In Scope
- Manager-only manual point additions
- Manager-only manual point deductions
- Reason code requirement for all adjustments
- Balance corrections for system errors
- Customer service compensation points
- Partial refund point adjustments
- Adjustment approval workflow (for large amounts)
- Full audit trail of all manual changes
- Integration with POS agent and PrestaShop admin panel

### Out of Scope
- Cashier manual adjustments (manager-only feature)
- Bulk adjustments (must be done individually)
- Scheduled/recurring adjustments
- Automatic error corrections (must be manual review)
- Customer-initiated adjustment requests (manager must review and execute)

## Inputs

### From POS Windows Agent - Manager Interface
```json
{
  "card_uid": "04A1B2C3D4E5F6",
  "adjustment_type": "credit",
  "adjustment_amount": 15.00,
  "adjustment_points": 150000,
  "reason_code": "customer_service_gesture",
  "reason_detail": "Apology for long wait time at checkout",
  "adjusted_by": "manager_maria",
  "terminal_id": "POS-TERMINAL-001",
  "timestamp": "2025-02-15T16:45:00Z",
  "requires_approval": false
}
```

### From PrestaShop Admin Panel - Loyalty Module
```json
{
  "customer_id": 9876,
  "card_uid": "04A1B2C3D4E5F6",
  "adjustment_type": "debit",
  "adjustment_amount": 5.50,
  "adjustment_points": 55000,
  "reason_code": "error_correction",
  "reason_detail": "Duplicate earn transaction detected for order #12345",
  "adjusted_by": "admin_juan",
  "admin_id": 42,
  "timestamp": "2025-02-15T17:00:00Z",
  "requires_approval": true,
  "approved_by": null
}
```

### Adjustment Types
- `credit` - Add points to balance
- `debit` - Remove points from balance

### Reason Codes (Required)
- `customer_service_gesture` - Goodwill points for poor experience
- `error_correction` - Fix system error or duplicate transaction
- `partial_refund` - Manual adjustment for partial refund
- `compensation` - Compensation for product issue
- `promotional_award` - Promotional point award
- `expired_points_restoration` - Restore expired points (exceptional case)
- `negative_balance_write_off` - Forgive negative balance
- `other` - Other reason (requires detailed explanation)

### Validation Rules
- `card_uid`: Must exist in system (enrolled customer)
- `adjustment_amount`: Must be > 0.01 EUR
- `reason_code`: Must be one of predefined codes
- `reason_detail`: Required, min 10 characters, max 500 characters
- `adjusted_by`: Must be manager role (authentication check)
- `requires_approval`: Automatically `true` if adjustment > 100 EUR

## Outputs

### Success Response - Immediate Adjustment (< 100 EUR)
```json
{
  "success": true,
  "adjustment_transaction_id": "txn_adj_m9n8b7v6",
  "card_uid": "04A1B2C3D4E5F6",
  "customer_name": "María García",
  "adjustment_type": "credit",
  "adjustment_amount": 15.00,
  "adjustment_points": 150000,
  "previous_balance": 50000,
  "new_balance": 200000,
  "new_balance_display": "20.00 EUR",
  "reason_code": "customer_service_gesture",
  "reason_detail": "Apology for long wait time at checkout",
  "adjusted_by": "manager_maria",
  "timestamp": "2025-02-15T16:45:00Z",
  "approval_required": false,
  "status": "completed"
}
```

### Success Response - Pending Approval (>= 100 EUR)
```json
{
  "success": true,
  "adjustment_request_id": "adj_req_123",
  "card_uid": "04A1B2C3D4E5F6",
  "customer_name": "María García",
  "adjustment_type": "credit",
  "adjustment_amount": 150.00,
  "adjustment_points": 1500000,
  "current_balance": 50000,
  "proposed_new_balance": 1550000,
  "reason_code": "compensation",
  "reason_detail": "Compensation for damaged product",
  "requested_by": "manager_maria",
  "timestamp": "2025-02-15T16:50:00Z",
  "approval_required": true,
  "status": "pending_approval",
  "message": "Adjustment request submitted for approval. Awaiting senior manager approval."
}
```

### Success Response - Approval Granted
```json
{
  "success": true,
  "adjustment_transaction_id": "txn_adj_p1o2i3u4",
  "adjustment_request_id": "adj_req_123",
  "card_uid": "04A1B2C3D4E5F6",
  "adjustment_points": 1500000,
  "new_balance": 1550000,
  "approved_by": "senior_manager_luis",
  "approved_at": "2025-02-15T17:10:00Z",
  "status": "approved_and_applied"
}
```

### Failure Response - Insufficient Balance for Debit
```json
{
  "success": false,
  "error_code": "INSUFFICIENT_BALANCE",
  "error_message": "Cannot deduct more points than customer has.",
  "requested_debit": 100.00,
  "requested_points": 1000000,
  "current_balance": 50000,
  "current_balance_eur": 5.00,
  "resolution": "Reduce debit amount or allow negative balance (manager override)"
}
```

### Failure Response - Unauthorized
```json
{
  "success": false,
  "error_code": "UNAUTHORIZED",
  "error_message": "Only managers can perform manual adjustments.",
  "attempted_by": "cashier_ana",
  "user_role": "cashier",
  "required_role": "manager"
}
```

### Side Effects
- Adjustment transaction created in ledger (positive for credit, negative for debit)
- Customer balance updated
- Audit log entry with full justification
- If online: Immediate balance update
- If offline (POS): Queued for sync
- If pending approval: Entry added to approval queue
- Customer notification email (optional, configurable)

## Main Flows

### Flow 1: Manual Credit - Immediate (Small Amount)

```
┌─────────┐    ┌──────────┐    ┌────────────┐    ┌──────────┐
│ Manager │    │ POS Agent│    │ Cloud API  │    │ Customer │
│         │    │  or Admin│    │            │    │          │
└────┬────┘    └────┬─────┘    └─────┬──────┘    └────┬─────┘
     │              │                │                 │
     │ 1. Select    │                │                 │
     │   "Manual    │                │                 │
     │    Adjustment"                │                 │
     ├─────────────>│                │                 │
     │              │                │                 │
     │ 2. Prompt    │                │                 │
     │   "Scan card"│                │                 │
     │<─────────────┤                │                 │
     │              │                │                 │
     │ 3. Tap card  │                │                 │
     ├─────────────>│                │                 │
     │              │                │                 │
     │              │ 4. Read UID    │                 │
     │              ├────────┐       │                 │
     │              │        │       │                 │
     │              │<───────┘       │                 │
     │              │                │                 │
     │              │ 5. GET balance │                 │
     │              ├───────────────>│                 │
     │              │                │                 │
     │              │ 6. 200 OK      │                 │
     │              │   {50 EUR}     │                 │
     │              │<───────────────┤                 │
     │              │                │                 │
     │ 7. Display   │                │                 │
     │   form:      │                │                 │
     │   Type: [+/-]│                │                 │
     │   Amount: ___│                │                 │
     │   Reason: ___│                │                 │
     │<─────────────┤                │                 │
     │              │                │                 │
     │ 8. Enter:    │                │                 │
     │   Type: +    │                │                 │
     │   Amount: 15 │                │                 │
     │   Reason:    │                │                 │
     │   "Customer  │                │                 │
     │    service"  │                │                 │
     ├─────────────>│                │                 │
     │              │                │                 │
     │              │ 9. Manager auth│                 │
     │              │   (Windows PIN)│                 │
     │              ├────────┐       │                 │
     │              │        │       │                 │
     │              │<───────┘       │                 │
     │              │                │                 │
     │              │10. POST /api/v1│                 │
     │              │   /transactions│                 │
     │              │   /adjustment  │                 │
     │              ├───────────────>│                 │
     │              │                │                 │
     │              │                │11. Validate    │
     │              │                ├────────┐       │
     │              │                │        │       │
     │              │                │<───────┘       │
     │              │                │                 │
     │              │                │12. Create txn  │
     │              │                ├────────┐       │
     │              │                │        │       │
     │              │                │<───────┘       │
     │              │                │                 │
     │              │                │13. Update      │
     │              │                │   balance      │
     │              │                ├────────┐       │
     │              │                │        │       │
     │              │                │<───────┘       │
     │              │                │                 │
     │              │14. 201 Created │                 │
     │              │<───────────────┤                 │
     │              │                │                 │
     │ 15. Display  │                │                 │
     │   "Adjustment│                │                 │
     │    complete: │                │                 │
     │    +15 EUR   │                │                 │
     │    New: 65EUR"                │                 │
     │<─────────────┤                │                 │
     │              │                │                 │
     │              │                │16. Email notify│
     │              │                │   (optional)   │
     │              │                ├────────────────>│
     │              │                │                 │
```

### Flow 2: Large Credit - Requires Approval

```
┌─────────┐    ┌──────────┐    ┌────────────┐    ┌──────────┐    ┌──────────┐
│ Manager │    │  Admin   │    │ Cloud API  │    │  Senior  │    │ Customer │
│         │    │  Panel   │    │            │    │ Manager  │    │          │
└────┬────┘    └────┬─────┘    └─────┬──────┘    └────┬─────┘    └────┬─────┘
     │              │                │                 │                │
     │ 1. Submit    │                │                 │                │
     │    150 EUR   │                │                 │                │
     │    adjustment│                │                 │                │
     ├─────────────>│                │                 │                │
     │              │                │                 │                │
     │              │ 2. POST /api/v1│                 │                │
     │              │   /adjustment_ │                 │                │
     │              │   requests     │                 │                │
     │              ├───────────────>│                 │                │
     │              │                │                 │                │
     │              │                │ 3. Create      │                │
     │              │                │   pending req  │                │
     │              │                ├────────┐       │                │
     │              │                │        │       │                │
     │              │                │<───────┘       │                │
     │              │                │                 │                │
     │              │ 4. 201 Pending │                 │                │
     │              │<───────────────┤                 │                │
     │              │                │                 │                │
     │ 5. Display   │                │                 │                │
     │   "Awaiting  │                │                 │                │
     │    approval" │                │                 │                │
     │<─────────────┤                │                 │                │
     │              │                │                 │                │
     │              │                │ 6. Email alert │                │
     │              │                │   to senior mgr│                │
     │              │                ├────────────────>│                │
     │              │                │                 │                │
     │              │                │                 │ 7. Login to   │
     │              │                │                 │    approval   │
     │              │                │                 │    dashboard  │
     │              │                │                 ├────────┐      │
     │              │                │                 │        │      │
     │              │                │                 │<───────┘      │
     │              │                │                 │                │
     │              │                │ 8. GET pending │                │
     │              │                │   requests     │                │
     │              │                │<────────────────┤                │
     │              │                │                 │                │
     │              │                │ 9. 200 OK      │                │
     │              │                │   [requests]   │                │
     │              │                ├────────────────>│                │
     │              │                │                 │                │
     │              │                │                 │10. Review     │
     │              │                │                 │   details     │
     │              │                │                 ├────────┐      │
     │              │                │                 │        │      │
     │              │                │                 │<───────┘      │
     │              │                │                 │                │
     │              │                │11. POST approve│                │
     │              │                │<────────────────┤                │
     │              │                │                 │                │
     │              │                │12. Apply adjust│                │
     │              │                ├────────┐       │                │
     │              │                │        │       │                │
     │              │                │<───────┘       │                │
     │              │                │                 │                │
     │              │                │13. 200 OK      │                │
     │              │                ├────────────────>│                │
     │              │                │                 │                │
     │              │                │14. Email notify│                │
     │              │                ├────────────────┼────────────────>│
     │              │                │                 │                │
```

### Flow 3: Offline Manual Adjustment (Queued)

When POS agent offline:
1. Manager initiates adjustment as normal
2. Agent validates input locally
3. Adjustment queued in local SQLite
4. Local cached balance updated (optimistic)
5. Manager sees: "Adjustment queued. Will sync when online."
6. When internet restored, agent syncs adjustment
7. If sync succeeds: Queue entry marked complete
8. If sync fails (e.g., insufficient balance): Manager notified to resolve

## Edge Cases

### Edge Case 1: Negative Balance After Debit
**Scenario**: Customer has 10 EUR balance, manager deducts 15 EUR

**Behavior**:
- By default, system prevents negative balance (error shown)
- Manager can check "Allow Negative Balance" override
- If approved, balance becomes -5 EUR
- Customer must earn 5 EUR before positive again
- Audit log flags "negative balance created"

### Edge Case 2: Multiple Pending Approvals for Same Customer
**Scenario**: Two managers submit adjustment requests for same customer

**Behavior**:
- Both requests queued independently
- Senior manager reviews and approves both
- Adjustments applied in order of approval
- Final balance reflects both adjustments

### Edge Case 3: Customer Uses Points During Approval Waiting
**Scenario**: 
1. Manager requests +100 EUR credit (pending approval)
2. Customer redeems 50 EUR at POS
3. Senior manager approves +100 EUR

**Behavior**:
- Approval system rechecks balance at approval time
- If customer balance changed, approval displays current balance
- Senior manager can still approve (adjustment adds to current balance)
- Final balance: (original balance - 50 EUR redeemed + 100 EUR approved)

### Edge Case 4: Adjustment for Partial Refund
**Scenario**: Customer bought 3 items (earned 300 points), returns 1 item

**Behavior**:
- Manager calculates: 300 points / 3 items = 100 points per item
- Manager creates debit adjustment: -100 points
- Reason: "Partial refund for order #12345, item SKU-789"
- Balance adjusted accordingly

### Edge Case 5: Expired Points Restoration
**Scenario**: Customer complains points expired unfairly due to system downtime

**Behavior**:
- Manager reviews case
- If justified, manager creates credit adjustment
- Reason code: "expired_points_restoration"
- Detailed reason: "System downtime prevented redemption before expiration"
- Balance restored with restored points

### Edge Case 6: Duplicate Adjustment Attempt
**Scenario**: Manager clicks "Submit" twice

**Behavior**:
- First request creates transaction
- Second request fails idempotency check (if within 1 minute)
- Display: "Adjustment already submitted"
- Prevents accidental duplicate

### Edge Case 7: Adjustment on Deactivated Account
**Scenario**: Manager tries to adjust balance for closed account

**Behavior**:
- API returns error "Account deactivated"
- Manager can choose to:
  - Reactivate account, then adjust
  - Cancel adjustment

## Failure Modes

### Failure Mode 1: Cloud API Unreachable (POS Offline)
**Symptoms**: HTTP timeout during adjustment request

**System Behavior**:
- Agent queues adjustment in local SQLite
- Manager sees: "Offline mode. Adjustment will sync later."
- Local balance cache updated optimistically
- Syncs when internet restored

**Recovery**:
- Automatic sync when online
- Manual "Sync Now" button

### Failure Mode 2: Approval Timeout
**Symptoms**: Adjustment pending approval for > 7 days

**System Behavior**:
- Automated reminder email to senior manager every 24 hours
- After 7 days, adjustment auto-expires
- Requesting manager notified: "Adjustment expired. Please resubmit."

**Recovery**:
- Resubmit adjustment request
- Escalate to higher-level manager

### Failure Mode 3: Manager Authentication Failure
**Symptoms**: Manager enters wrong PIN/password

**System Behavior**:
- Adjustment blocked
- Display: "Authentication failed. Please try again."
- After 3 failures, account locked for 15 minutes

**Recovery**:
- Re-enter correct credentials
- Wait for lockout to expire
- Contact IT support to reset

### Failure Mode 4: Database Write Failure
**Symptoms**: 500 Internal Server Error from API

**System Behavior**:
- Display: "System error. Adjustment not applied. Please retry."
- No local queue (server-side issue, not connectivity)
- Audit log entry with failure details

**Recovery**:
- Retry adjustment
- If persistent, escalate to IT support
- Backend team investigates database issue

### Failure Mode 5: Concurrent Adjustments
**Symptoms**: Two managers adjust same customer balance simultaneously

**System Behavior**:
- Database row-level locking prevents race condition
- First adjustment completes
- Second adjustment sees updated balance
- Both succeed with correct final balance

**Recovery**:
- No recovery needed (handled by database)

## Offline Behavior

### Offline Adjustment Queue
```sql
CREATE TABLE adjustment_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  card_uid TEXT NOT NULL,
  adjustment_type TEXT NOT NULL,
  adjustment_amount REAL NOT NULL,
  adjustment_points INTEGER NOT NULL,
  reason_code TEXT NOT NULL,
  reason_detail TEXT NOT NULL,
  adjusted_by TEXT NOT NULL,
  timestamp TEXT NOT NULL,
  queued_at TEXT NOT NULL,
  sync_status TEXT DEFAULT 'pending',
  sync_attempts INTEGER DEFAULT 0,
  last_sync_attempt TEXT,
  sync_error TEXT,
  idempotency_key TEXT UNIQUE
);
```

### Offline Constraints
- Adjustments < 100 EUR processed immediately when online restored
- Adjustments >= 100 EUR require approval (cannot be done offline)
- Manager can view pending adjustments in agent dashboard
- Local balance cache updated optimistically (shown with "OFFLINE" indicator)

## Security Considerations

### Authorization
- **Role Check**: Only manager role can access adjustment feature
- **Authentication**: Manager must re-authenticate (PIN/password) before adjustment
- **Approval Threshold**: Adjustments >= 100 EUR require senior manager approval
- **IP Logging**: All adjustments log IP address for audit

### Audit Trail
Every adjustment creates comprehensive audit log:
```json
{
  "event_type": "MANUAL_ADJUSTMENT",
  "transaction_id": "txn_adj_m9n8b7v6",
  "timestamp": "2025-02-15T16:45:00Z",
  "card_uid": "04A1B2C3D4E5F6",
  "adjustment_type": "credit",
  "adjustment_amount": 15.00,
  "adjustment_points": 150000,
  "reason_code": "customer_service_gesture",
  "reason_detail": "Apology for long wait time at checkout",
  "balance_before": 50000,
  "balance_after": 200000,
  "adjusted_by": "manager_maria",
  "adjusted_by_id": "MGR-001",
  "terminal_id": "POS-TERMINAL-001",
  "ip_address": "192.168.1.100",
  "requires_approval": false,
  "approval_status": "not_required",
  "approved_by": null,
  "approved_at": null
}
```

### Fraud Prevention
- **Velocity Limit**: Max 10 adjustments per manager per day
- **Large Adjustment Alert**: Adjustments > 50 EUR flagged for review
- **Pattern Detection**: Alert if manager consistently favors specific customers
- **Monthly Report**: Summary of all adjustments by manager for audit

### Idempotency Protection
- **Key Format**: `adjustment_{card_uid}_{timestamp}_{adjusted_by}`
- **Window**: Duplicate detection within 60 seconds
- **Validation**: Prevents accidental double-click submissions

## Related Documents

### Dependencies
- `02_architecture/WINDOWS_AGENT.md` - POS agent adjustment interface
- `02_architecture/CLOUD_BACKEND.md` - Backend API processing adjustments
- `04_integrations/PRESTASHOP_MODULE.md` - PrestaShop admin adjustment interface
- `05_data/TRANSACTION.md` - Adjustment transaction structure
- `05_data/CUSTOMER.md` - Balance computation
- `06_security/SECURITY_MODEL.md` - Authorization and authentication

### Related Features
- `03_features/REFUND_HANDLING.md` - Automatic vs manual adjustments
- `03_features/EARN_POINTS_POS.md` - Earn transactions that may need correction
- `03_features/REDEEM_POINTS_POS.md` - Redeem transactions that may need correction
- `03_features/EXPIRATION.md` - Expired points restoration via adjustment

### Integration Points
- `04_integrations/EMAIL_SERVICE.md` - Approval and notification emails
- `06_security/RBAC.md` - Role-based access control for managers

## Open Questions / TODOs

### TODO: Bulk Adjustment Tool
**Status**: Not implemented  
**Required by**: Phase 2  
**Description**: Admin tool to upload CSV of adjustments for batch processing (e.g., promotional awards)

### TODO: Adjustment Templates
**Status**: Future enhancement  
**Required by**: Phase 3  
**Description**: Pre-defined adjustment templates with standard amounts and reasons (e.g., "Wait time apology: +10 EUR")

### TODO: Customer Self-Service Adjustment Request
**Status**: Not planned for MVP  
**Required by**: TBD  
**Description**: Allow customers to request adjustments via PrestaShop account, manager reviews and approves

### Open Question: Adjustment Expiration
**Question**: Should manually credited points have same 3-month expiration as earned points?  
**Context**: Promotional or compensation points may have different rules  
**Impact**: Expiration logic, customer expectations  
**Decision Required By**: Before launch

### Open Question: Adjustment Limits
**Question**: Should there be per-customer max adjustment per month (e.g., 100 EUR)?  
**Context**: Prevent abuse or excessive goodwill gestures  
**Impact**: Business policy, validation logic  
**Decision Required By**: Before launch

### Open Question: Negative Balance Write-Off
**Question**: Should there be automated write-off of small negative balances (e.g., < 1 EUR)?  
**Context**: Simplify accounting, improve customer experience  
**Impact**: Business policy, automated job  
**Decision Required By**: Phase 2
