# Feature: Points Expiration

## Purpose

Automatically expire loyalty points 3 months after they are earned to encourage active participation in the loyalty program and prevent indefinite accumulation of points liability. Expiration runs as a scheduled background job and maintains accurate balance by removing expired points from customer accounts.

## Scope

### In Scope
- Automatic expiration of points 3 months (90 days) after earning date
- Scheduled nightly job to process expirations
- Per-transaction expiration (each earn transaction expires independently)
- FIFO expiration (oldest points expire first)
- Customer notification before expiration (7 days warning)
- Expiration transaction records in ledger
- Balance recalculation after expiration
- Integration with redemption (cannot redeem expired points)
- Expiration reporting and dashboard

### Out of Scope
- Expiration of manually adjusted points (configurable exception)
- Expiration of promotional points (may have different rules in future)
- Expiration extensions or point renewal
- Customer-initiated "reset expiration" actions
- Variable expiration periods per customer or point type

## Inputs

### From Scheduled Job (Daily 02:00 UTC)
```json
{
  "job_name": "points_expiration",
  "run_timestamp": "2025-02-16T02:00:00Z",
  "cutoff_date": "2024-11-16",
  "calculation": "current_date - 90 days",
  "batch_size": 1000
}
```

### Expiration Logic Query
```sql
-- Find all transactions eligible for expiration
SELECT 
  t.transaction_id,
  t.card_uid,
  t.points,
  t.transaction_timestamp,
  t.expires_at
FROM transactions t
WHERE 
  t.transaction_type = 'earn'
  AND t.points > 0
  AND t.expires_at <= CURRENT_DATE
  AND NOT EXISTS (
    SELECT 1 FROM transactions exp
    WHERE exp.parent_transaction_id = t.transaction_id
    AND exp.transaction_type = 'expiration'
  )
ORDER BY t.transaction_timestamp ASC
LIMIT 1000;
```

### Expiration Warning Query (7 Days Before)
```sql
-- Find customers with points expiring soon
SELECT 
  c.card_uid,
  c.customer_email,
  c.customer_name,
  SUM(t.points) as expiring_points,
  MIN(t.expires_at) as earliest_expiration_date
FROM transactions t
JOIN customers c ON t.card_uid = c.card_uid
WHERE 
  t.transaction_type = 'earn'
  AND t.points > 0
  AND t.expires_at BETWEEN CURRENT_DATE + INTERVAL '7 days' AND CURRENT_DATE + INTERVAL '8 days'
  AND NOT EXISTS (
    SELECT 1 FROM transactions exp
    WHERE exp.parent_transaction_id = t.transaction_id
    AND exp.transaction_type = 'expiration'
  )
GROUP BY c.card_uid, c.customer_email, c.customer_name;
```

## Outputs

### Success Response - Expiration Processed
```json
{
  "success": true,
  "expiration_transaction_id": "txn_exp_q1w2e3r4",
  "parent_transaction_id": "txn_a1b2c3d4e5f6",
  "card_uid": "04A1B2C3D4E5F6",
  "customer_name": "María García",
  "points_expired": -18825,
  "points_expired_display": "-188 points",
  "original_earn_date": "2024-11-16T16:45:30Z",
  "expiration_date": "2025-02-16T02:00:00Z",
  "days_since_earned": 92,
  "previous_balance": 23825,
  "new_balance": 5000,
  "new_balance_display": "50 EUR",
  "customer_notified": true
}
```

### Expiration Warning Notification (7 Days Before)
```json
{
  "notification_type": "expiration_warning",
  "card_uid": "04A1B2C3D4E5F6",
  "customer_email": "maria.garcia@example.com",
  "customer_name": "María García",
  "points_expiring_soon": 50000,
  "points_expiring_soon_display": "50 EUR (500 points)",
  "expiration_date": "2025-02-23",
  "days_until_expiration": 7,
  "current_balance": 75000,
  "message": "You have 50 EUR in points expiring on 23 February. Use them soon!"
}
```

### Expiration Batch Job Summary
```json
{
  "job_run_id": "exp_job_2025_02_16_001",
  "run_timestamp": "2025-02-16T02:05:32Z",
  "execution_time_seconds": 45.3,
  "customers_affected": 127,
  "transactions_expired": 342,
  "total_points_expired": 5420000,
  "total_value_expired_eur": 542.00,
  "errors": 0,
  "warnings": 2,
  "warnings_detail": [
    "Customer account CUST-123 deactivated, skipped expiration",
    "Transaction TXN-789 already has expiration record, skipped"
  ],
  "next_run_scheduled": "2025-02-17T02:00:00Z"
}
```

### Side Effects
- Negative expiration transaction created in ledger for each expired earn transaction
- Customer balance decreased by expired points
- Expiration audit log entries created
- Customer email/WhatsApp notification sent (if opted in)
- Expiration metrics updated for reporting

## Main Flows

### Flow 1: Daily Expiration Job

```
┌──────────────┐    ┌────────────┐    ┌──────────┐    ┌──────────┐
│ Scheduled Job│    │ Cloud API  │    │ Database │    │ Customer │
│  (Cron)      │    │            │    │          │    │ (Email)  │
└──────┬───────┘    └─────┬──────┘    └────┬─────┘    └────┬─────┘
       │                  │                 │                │
       │ 1. Trigger at    │                 │                │
       │    02:00 UTC     │                 │                │
       ├─────────────────>│                 │                │
       │                  │                 │                │
       │                  │ 2. Query expired│                │
       │                  │    transactions │                │
       │                  ├────────────────>│                │
       │                  │                 │                │
       │                  │ 3. Return list  │                │
       │                  │    (batch 1000) │                │
       │                  │<────────────────┤                │
       │                  │                 │                │
       │                  │ 4. For each txn:│                │
       │                  │    create       │                │
       │                  │    expiration   │                │
       │                  │    record       │                │
       │                  ├────────────────>│                │
       │                  │                 │                │
       │                  │ 5. Update balance               │
       │                  │    cache        │                │
       │                  ├────────────────>│                │
       │                  │                 │                │
       │                  │ 6. Commit batch │                │
       │                  ├────────────────>│                │
       │                  │                 │                │
       │                  │ 7. Query next   │                │
       │                  │    batch (if any)                │
       │                  ├────────────────>│                │
       │                  │                 │                │
       │                  │ 8. No more      │                │
       │                  │<────────────────┤                │
       │                  │                 │                │
       │                  │ 9. Queue emails │                │
       │                  │    for affected │                │
       │                  │    customers    │                │
       │                  ├────────┐        │                │
       │                  │        │        │                │
       │                  │<───────┘        │                │
       │                  │                 │                │
       │                  │10. Send emails  │                │
       │                  ├────────────────┼────────────────>│
       │                  │                 │                │
       │ 11. Job complete │                 │                │
       │    summary       │                 │                │
       │<─────────────────┤                 │                │
       │                  │                 │                │
```

### Flow 2: Expiration Warning (7 Days Before)

```
┌──────────────┐    ┌────────────┐    ┌──────────┐    ┌──────────┐
│ Scheduled Job│    │ Cloud API  │    │ Database │    │ Customer │
│  (Cron)      │    │            │    │          │    │ (Email/  │
│              │    │            │    │          │    │ WhatsApp)│
└──────┬───────┘    └─────┬──────┘    └────┬─────┘    └────┬─────┘
       │                  │                 │                │
       │ 1. Trigger at    │                 │                │
       │    10:00 UTC     │                 │                │
       │    (daily)       │                 │                │
       ├─────────────────>│                 │                │
       │                  │                 │                │
       │                  │ 2. Query points │                │
       │                  │    expiring in  │                │
       │                  │    7-8 days     │                │
       │                  ├────────────────>│                │
       │                  │                 │                │
       │                  │ 3. Return       │                │
       │                  │    customers +  │                │
       │                  │    expiring pts │                │
       │                  │<────────────────┤                │
       │                  │                 │                │
       │                  │ 4. For each     │                │
       │                  │    customer:    │                │
       │                  │    generate     │                │
       │                  │    warning msg  │                │
       │                  ├────────┐        │                │
       │                  │        │        │                │
       │                  │<───────┘        │                │
       │                  │                 │                │
       │                  │ 5. Send email   │                │
       │                  ├────────────────┼────────────────>│
       │                  │                 │                │
       │                  │ 6. Send WhatsApp│                │
       │                  │    (if opted in)│                │
       │                  ├────────────────┼────────────────>│
       │                  │                 │                │
       │                  │ 7. Log warnings │                │
       │                  │    sent         │                │
       │                  ├────────────────>│                │
       │                  │                 │                │
```

### Flow 3: Customer Queries Balance with Expiring Points

```
Customer checks balance via POS, PrestaShop, or WhatsApp:

Response includes expiring points info:
{
  "current_balance": 75000,
  "current_balance_display": "75 EUR",
  "points_expiring_soon": 50000,
  "points_expiring_date": "2025-02-23",
  "days_until_expiration": 7,
  "points_expiring_display": "50 EUR expires in 7 days"
}
```

## Edge Cases

### Edge Case 1: Customer Earns and Redeems Same Day
**Scenario**: 
1. Customer earns 500 points on 2024-11-16
2. Customer immediately redeems 500 points same day
3. 90 days later (2025-02-16), expiration job runs

**Behavior**:
- Earn transaction still marked for expiration (independent of redemption)
- Expiration creates negative transaction: -500 points
- Balance becomes: 0 - 500 = -500 (negative balance)
- Customer owes 500 points

**Alternative**: Expiration logic could check if points were redeemed and skip expiration (complex to implement)

### Edge Case 2: Points Expire During Offline Sync
**Scenario**:
1. POS offline for 2 days
2. Points expiration job runs and expires 200 points
3. POS comes online, syncs queued earn of 300 points (dated 3 months ago)

**Behavior**:
- Queued earn transaction immediately subject to expiration (already past 90 days)
- Next expiration job run will expire the 300 points
- Customer never actually had usable 300 points

**Mitigation**: POS agent should warn manager: "This transaction is already expired (dated 91 days ago)"

### Edge Case 3: Customer Receives Expiration Email After Already Using Points
**Scenario**:
1. Warning email sent: "50 EUR expiring in 7 days"
2. Customer redeems 50 EUR within 7 days
3. Expiration job runs and finds 0 points to expire for that customer

**Behavior**:
- Expiration job skips customer (no eligible transactions)
- No follow-up email sent
- Customer experience: Warning prompted action (positive UX)

### Edge Case 4: Partial Points Redeemed from Expiring Transaction
**Scenario**:
1. Customer earned 500 points on 2024-11-16
2. Customer redeemed 300 points on 2025-01-15
3. Expiration job runs on 2025-02-16

**Behavior** (Depends on expiration logic):
- **Option A**: Expire full 500 points (ignore redemptions)
- **Option B**: Expire only unredeemed 200 points (complex tracking)

**Recommendation**: Option A (simpler), with note that redemptions don't affect expiration of original earn transaction

### Edge Case 5: Expiration on Suspended Account
**Scenario**: Customer account suspended (e.g., fraud investigation), points still expiring

**Behavior**:
- Expiration job checks account status
- If suspended: Skip expiration, add note "Expiration paused due to account suspension"
- Resume expiration when account reactivated

### Edge Case 6: System Clock Issue (Time Travel)
**Scenario**: Server clock set incorrectly to future date, then corrected

**Behavior**:
- Expiration job may expire points prematurely
- When clock corrected, already-expired transactions cannot be "unexpired"
- Resolution: Manual adjustments to restore incorrectly expired points
- Prevention: Monitor server time sync (NTP)

### Edge Case 7: Mass Expiration Event
**Scenario**: System launched 3 months ago, first wave of expirations affects 80% of customers

**Behavior**:
- Expiration job processes in batches (1000 at a time)
- Total job may take several minutes
- Email queue may be large (rate limit sending)
- Customer impact: Many customers lose significant balances simultaneously

**Mitigation**: Send proactive communications 2 weeks before first mass expiration

## Failure Modes

### Failure Mode 1: Expiration Job Crashes Mid-Execution
**Symptoms**: Job processes 500 of 1000 transactions, then crashes

**System Behavior**:
- Transactions processed so far are committed
- Next job run will continue with remaining transactions
- No duplicate expirations (idempotency check)

**Recovery**:
- Automatic on next scheduled run
- Manual trigger option in admin panel

### Failure Mode 2: Database Lock During Expiration
**Symptoms**: High transaction volume prevents expiration job from acquiring lock

**System Behavior**:
- Job retries with backoff
- If lock unavailable after 5 minutes, job skips this run
- Admin alert sent: "Expiration job skipped due to database contention"
- Next run will catch up

**Recovery**:
- Investigate database performance
- Optimize expiration query
- Consider running expiration at lower-traffic time

### Failure Mode 3: Email Service Failure
**Symptoms**: Expiration warning emails fail to send

**System Behavior**:
- Expiration still proceeds (email is secondary)
- Failed emails queued for retry
- Retry every hour for 24 hours
- After 24 hours, mark as failed

**Recovery**:
- Fix email service
- Emails will retry automatically
- Customer can check balance via other channels

### Failure Mode 4: Negative Balance After Expiration
**Symptoms**: Customer balance goes negative due to expiration

**System Behavior**:
- Expiration allows negative balance
- Customer notified: "Your balance is now negative due to expired points"
- Customer must earn points to return to positive
- Manager can waive negative balance via manual adjustment

**Recovery**:
- Customer earns points to repay negative balance
- Or manager manual adjustment to forgive

### Failure Mode 5: Expiration Date Calculation Error
**Symptoms**: Bug in expiration logic expires points too early/late

**System Behavior**:
- Incorrect expirations applied
- Customers complain
- Audit log can identify affected customers

**Recovery**:
- Fix bug
- Run script to identify incorrectly expired transactions
- Manual adjustments to restore incorrectly expired points
- Communication to affected customers with apology

## Offline Behavior

### POS Agent - No Direct Expiration
- POS Windows Agent does NOT run expiration job locally
- Expiration is cloud-only operation
- When POS syncs, it receives updated balance reflecting expirations

### Cached Balance Outdated
- If POS offline for extended period, cached balance may not reflect recent expirations
- When displaying balance, agent shows age: "Balance as of 2 days ago (may have changed)"
- Manager can force refresh when online

### Queued Transactions May Expire Before Sync
- Transactions queued offline for > 90 days are expired immediately upon sync
- POS agent should warn: "This transaction is already past expiration date"

## Security Considerations

### Expiration Integrity
- **Immutable Expiration**: Once expired, transaction cannot be "unexpired" without manual adjustment
- **Audit Trail**: All expirations logged with timestamp and batch ID
- **Idempotency**: Each earn transaction can only be expired once

### Fraud Prevention
- **Expiration Extensions**: No mechanism to extend expiration (prevents abuse)
- **Manager Override**: Only senior managers can restore expired points via manual adjustment
- **Rate Limiting**: Restore expired points limited to 5 per customer per year

### Data Privacy
- **Expiration Notifications**: Only sent to opted-in customers
- **Email Content**: Does not include full balance (only expiring amount)
- **GDPR Compliance**: Customer can opt out of expiration warnings

## Related Documents

### Dependencies
- `02_architecture/CLOUD_BACKEND.md` - Backend job scheduler
- `05_data/TRANSACTION.md` - Transaction expiration fields
- `05_data/CUSTOMER.md` - Balance computation with expirations
- `07_operations/SCHEDULED_JOBS.md` - Cron job configuration

### Related Features
- `03_features/EARN_POINTS_POS.md` - Earned points that will expire
- `03_features/EARN_POINTS_ONLINE.md` - Online earned points expiration
- `03_features/REDEEM_POINTS_POS.md` - Cannot redeem expired points
- `03_features/REDEEM_POINTS_ONLINE.md` - Expired points excluded from balance
- `03_features/MANUAL_ADJUSTMENTS.md` - Restoring expired points
- `03_features/BALANCE_QUERY.md` - Display expiring points

### Integration Points
- `04_integrations/EMAIL_SERVICE.md` - Expiration warning emails
- `04_integrations/WHATSAPP_API.md` - Expiration warning WhatsApp
- `07_operations/MONITORING.md` - Expiration job monitoring

## Open Questions / TODOs

### TODO: Expiration Notifications UI
**Status**: Partially implemented  
**Required by**: Phase 2  
**Description**: Show expiring points prominently in POS agent and PrestaShop account dashboard

### TODO: Expiration Grace Period
**Status**: Not implemented  
**Required by**: TBD based on customer feedback  
**Description**: Option to extend expiration by 7 days if customer has recent activity

### TODO: Variable Expiration Rules
**Status**: Future enhancement  
**Required by**: Phase 3  
**Description**: Different expiration periods for promotional points, manually adjusted points, etc.

### Open Question: Negative Balance Handling
**Question**: Should expiration be blocked if it would create negative balance?  
**Context**: Customer redeemed more than they earned, now earn transaction expires  
**Impact**: Balance integrity, customer experience  
**Decision Required By**: Before launch

### Open Question: Expiration on Manual Adjustments
**Question**: Should manually credited points expire or be permanent?  
**Context**: Customer service gestures may deserve permanent status  
**Impact**: Business policy, liability accounting  
**Decision Required By**: Before launch

### Open Question: Notification Frequency
**Question**: Should warnings be sent at 7 days, 3 days, and 1 day before expiration?  
**Context**: More reminders = better customer retention, but also more emails  
**Impact**: Email volume, customer experience  
**Decision Required By**: After MVP launch based on customer feedback

### Open Question: Expiration Metrics
**Question**: What expiration KPIs should be tracked?  
**Context**: % of points expired, avg days to expiration, etc.  
**Impact**: Business intelligence, program optimization  
**Decision Required By**: Phase 2 (reporting phase)
