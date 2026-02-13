# Feature: Balance Query

## Purpose

Enable customers to quickly check their current loyalty points balance across multiple channels (POS card tap, PrestaShop account, WhatsApp message) to understand their available rewards and encourage usage of the loyalty program.

## Scope

### In Scope
- Balance query via NFC card tap at POS
- Balance query via PrestaShop logged-in customer account
- Balance query via WhatsApp keyword "Saldo"
- Display current balance in EUR and points
- Show points expiring soon (within 30 days)
- Transaction history display (last 10 transactions)
- Offline balance query using cached data (POS only)
- Real-time balance computation from ledger
- Multi-language support (Spanish, Catalan)

### Out of Scope
- Balance query for guest/non-enrolled customers
- Balance query via SMS or phone call
- Balance history export (PDF/CSV download in future)
- Detailed transaction analytics or insights
- Balance comparison with other customers
- Balance transfer between cards

## Inputs

### From POS Windows Agent - Card Tap Query
```json
{
  "card_uid": "04A1B2C3D4E5F6",
  "query_type": "balance_check",
  "terminal_id": "POS-TERMINAL-001",
  "timestamp": "2025-02-16T11:30:00Z",
  "include_history": false
}
```

### From PrestaShop Module - Account Page
```json
{
  "customer_id": 9876,
  "customer_email": "maria.garcia@example.com",
  "query_type": "balance_with_history",
  "include_history": true,
  "history_limit": 10,
  "timestamp": "2025-02-16T11:35:00Z"
}
```

### From WhatsApp API - Message Received
```json
{
  "from_phone": "+34612345678",
  "message_text": "Saldo",
  "timestamp": "2025-02-16T11:40:00Z",
  "query_type": "balance_via_whatsapp"
}
```

### Validation Rules
- `card_uid`: Must exist in customer database (for POS query)
- `customer_id` or `customer_email`: Must be enrolled customer (for PrestaShop query)
- `from_phone`: Must be registered phone number (for WhatsApp query)
- Query rate limit: Max 10 balance checks per customer per hour

## Outputs

### Success Response - POS Balance Check
```json
{
  "success": true,
  "card_uid": "04A1B2C3D4E5F6",
  "customer_name": "María García",
  "current_balance": 250000,
  "current_balance_eur": 25.00,
  "current_balance_display": "25.00 EUR (250 points)",
  "points_expiring_soon": 50000,
  "points_expiring_date": "2025-03-15",
  "points_expiring_display": "5.00 EUR expires 15 March",
  "last_transaction_date": "2025-02-14T10:30:00Z",
  "last_transaction_type": "earn",
  "timestamp": "2025-02-16T11:30:00Z",
  "data_freshness": "real_time"
}
```

### Success Response - PrestaShop with History
```json
{
  "success": true,
  "card_uid": "04A1B2C3D4E5F6",
  "customer_name": "María García",
  "customer_email": "maria.garcia@example.com",
  "current_balance": 250000,
  "current_balance_display": "25.00 EUR",
  "points_expiring_soon": 50000,
  "points_expiring_date": "2025-03-15",
  "transaction_history": [
    {
      "transaction_id": "txn_p9o8i7u6y5t4",
      "date": "2025-02-14T10:30:00Z",
      "type": "earn",
      "description": "Earned from order #12345",
      "points": 20250,
      "points_display": "+202 points",
      "order_amount": 135.00,
      "balance_after": 250000
    },
    {
      "transaction_id": "txn_z9y8x7w6v5u4",
      "date": "2025-02-10T15:20:00Z",
      "type": "redeem",
      "description": "Redeemed on order #12340",
      "points": -100000,
      "points_display": "-100 points",
      "order_amount": 75.00,
      "balance_after": 229750
    },
    {
      "transaction_id": "txn_a1b2c3d4e5f6",
      "date": "2025-02-08T16:45:30Z",
      "type": "earn",
      "description": "Earned at store (POS-2025-02-08-0042)",
      "points": 18825,
      "points_display": "+188 points",
      "sale_amount": 125.50,
      "balance_after": 329750
    }
  ],
  "total_earned_lifetime": 1500000,
  "total_redeemed_lifetime": 800000,
  "timestamp": "2025-02-16T11:35:00Z"
}
```

### Success Response - WhatsApp Query
**Message sent to customer**:
```
¡Hola María! 👋

Tu saldo actual: 25.00 EUR (250 puntos)

⚠️ Tienes 5.00 EUR que expiran el 15 de marzo.

Última actividad: 14 febrero (ganaste 202 puntos)

Para usar tus puntos, visita nuestra tienda o compra online en www.example.com

¡Gracias por tu fidelidad! 🎉
```

### Success Response - Offline Balance (Cached)
```json
{
  "success": true,
  "card_uid": "04A1B2C3D4E5F6",
  "customer_name": "María García",
  "current_balance": 250000,
  "current_balance_display": "25.00 EUR (cached)",
  "data_freshness": "offline_cached",
  "cache_timestamp": "2025-02-16T08:00:00Z",
  "cache_age_hours": 3.5,
  "warning": "Balance shown is from cache. Actual balance may differ.",
  "points_expiring_soon": null,
  "transaction_history": null
}
```

### Failure Response - Card Not Enrolled
```json
{
  "success": false,
  "error_code": "CARD_NOT_ENROLLED",
  "error_message": "This card is not registered in the loyalty program.",
  "card_uid": "04A1B2C3D4E5F6",
  "resolution": "Please enroll at customer service counter."
}
```

### Failure Response - Phone Not Registered (WhatsApp)
**Message sent to customer**:
```
Número no registrado.

Para consultar tu saldo por WhatsApp, primero registra tu tarjeta de fidelidad con tu número de teléfono.

Visita nuestra tienda o www.example.com para registrarte.
```

### Failure Response - Rate Limit Exceeded
```json
{
  "success": false,
  "error_code": "RATE_LIMIT_EXCEEDED",
  "error_message": "Too many balance checks. Please try again later.",
  "retry_after_seconds": 300,
  "max_queries_per_hour": 10
}
```

## Main Flows

### Flow 1: POS Balance Check via Card Tap

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌────────────┐
│ Cashier │    │ Customer │    │ POS Agent│    │ Cloud API  │
└────┬────┘    └────┬─────┘    └────┬─────┘    └─────┬──────┘
     │              │               │                │
     │ 1. Customer  │               │                │
     │    asks for  │               │                │
     │    balance   │               │                │
     │<─────────────┤               │                │
     │              │               │                │
     │ 2. Click     │               │                │
     │   "Check     │               │                │
     │    Balance"  │               │                │
     ├──────────────┼──────────────>│                │
     │              │               │                │
     │ 3. Prompt:   │               │                │
     │   "Tap card" │               │                │
     │<─────────────┼───────────────┤                │
     │              │               │                │
     │              │ 4. Tap card   │                │
     │              ├──────────────>│                │
     │              │               │                │
     │              │               │ 5. Read UID    │
     │              │               ├────────┐       │
     │              │               │        │       │
     │              │               │<───────┘       │
     │              │               │                │
     │              │               │ 6. GET /api/v1/│
     │              │               │   customers/   │
     │              │               │   {uid}/balance│
     │              │               ├───────────────>│
     │              │               │                │
     │              │               │                │ 7. Query DB  │
     │              │               │                ├────────┐     │
     │              │               │                │        │     │
     │              │               │                │<───────┘     │
     │              │               │                │              │
     │              │               │                │ 8. Calculate │
     │              │               │                │    balance   │
     │              │               │                │    from ledger│
     │              │               │                ├────────┐     │
     │              │               │                │        │     │
     │              │               │                │<───────┘     │
     │              │               │                │              │
     │              │               │ 9. 200 OK      │              │
     │              │               │   {balance: 25}│              │
     │              │               │<───────────────┤              │
     │              │               │                │              │
     │              │               │10. Display     │              │
     │              │               │   balance      │              │
     │              │               ├────────┐       │              │
     │              │               │        │       │              │
     │              │               │<───────┘       │              │
     │              │               │                │              │
     │ 11. Show     │               │                │              │
     │    "Balance: │               │                │              │
     │     25 EUR"  │               │                │              │
     │    "5 EUR    │               │                │              │
     │     expires  │               │                │              │
     │     15 March"│               │                │              │
     │<─────────────┼───────────────┤                │              │
     │              │               │                │              │
     │ 12. Print    │               │                │              │
     │    balance   │               │                │              │
     │    receipt   │               │                │              │
     │    (optional)│               │                │              │
     │──────────────┼──────────────>│                │              │
     │              │               │                │              │
```

### Flow 2: PrestaShop Account Page Balance

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────────┐
│ Customer │    │PrestaShop│    │  Loyalty │    │ Cloud API  │
│ (Browser)│    │          │    │  Module  │    │            │
└────┬─────┘    └────┬─────┘    └────┬─────┘    └─────┬──────┘
     │              │               │                │
     │ 1. Login to  │               │                │
     │    account   │               │                │
     ├─────────────>│               │                │
     │              │               │                │
     │ 2. Navigate  │               │                │
     │    "My Loyalty│              │                │
     │     Points"  │               │                │
     ├─────────────>│               │                │
     │              │               │                │
     │              │ 3. Load module│                │
     │              ├──────────────>│                │
     │              │               │                │
     │              │               │ 4. GET /api/v1/│
     │              │               │   customers/   │
     │              │               │   {id}/balance │
     │              │               │   ?history=true│
     │              │               ├───────────────>│
     │              │               │                │
     │              │               │ 5. Query balance│
     │              │               │   + history    │
     │              │               │<───────────────┤
     │              │               │                │
     │              │ 6. Render     │                │
     │              │    balance +  │                │
     │              │    history    │                │
     │              │<──────────────┤                │
     │              │               │                │
     │ 7. Display:  │               │                │
     │   "Balance:  │               │                │
     │    25 EUR"   │               │                │
     │   "Recent:   │               │                │
     │    +202 pts  │               │                │
     │    14 Feb"   │               │                │
     │<─────────────┤               │                │
     │              │               │                │
```

### Flow 3: WhatsApp Balance Query

```
┌──────────┐    ┌──────────┐    ┌────────────┐    ┌────────────┐
│ Customer │    │ WhatsApp │    │ Cloud API  │    │ Customer   │
│ (phone)  │    │ Business │    │            │    │ (WhatsApp) │
└────┬─────┘    └────┬─────┘    └─────┬──────┘    └─────┬──────┘
     │              │                │                  │
     │ 1. Send msg: │                │                  │
     │   "Saldo"    │                │                  │
     ├─────────────>│                │                  │
     │              │                │                  │
     │              │ 2. Webhook:    │                  │
     │              │   POST /whatsapp│                 │
     │              │   /incoming    │                  │
     │              ├───────────────>│                  │
     │              │                │                  │
     │              │                │ 3. Lookup phone │
     │              │                │   in customers  │
     │              │                ├────────┐        │
     │              │                │        │        │
     │              │                │<───────┘        │
     │              │                │                  │
     │              │                │ 4. Get balance  │
     │              │                ├────────┐        │
     │              │                │        │        │
     │              │                │<───────┘        │
     │              │                │                  │
     │              │                │ 5. Format msg   │
     │              │                ├────────┐        │
     │              │                │        │        │
     │              │                │<───────┘        │
     │              │                │                  │
     │              │                │ 6. POST WhatsApp│
     │              │                │   send API      │
     │              │                ├────────────────>│
     │              │                │                  │
     │              │                │                  │ 7. Deliver msg
     │              │                │                  ├──────────┐
     │              │                │                  │          │
     │              │                │                  │<─────────┘
     │              │                │                  │
     │ 8. Receive:  │                │                  │
     │   "Balance:  │                │                  │
     │    25 EUR"   │                │                  │
     │<─────────────┼────────────────┼──────────────────┤
     │              │                │                  │
```

## Edge Cases

### Edge Case 1: Balance Query Immediately After Transaction
**Scenario**: Customer earns points, then immediately checks balance

**Behavior**:
- If online: Balance reflects earn immediately (real-time)
- If offline: Balance reflects earn in local cache (optimistic update)
- Typical latency: < 100ms (database query + calculation)

### Edge Case 2: Multiple Cards, Same Customer
**Scenario**: Customer has 2 cards enrolled with same email

**Behavior**:
- POS query: Shows balance for tapped card only
- PrestaShop query: Shows combined balance from all cards
- WhatsApp query: Shows combined balance with note "across 2 cards"

### Edge Case 3: Balance Query During Sync
**Scenario**: POS syncing offline transactions while customer checks balance

**Behavior**:
- Online query returns current balance (may be mid-sync)
- Balance may change during query (acceptable eventual consistency)
- Sync completes, next query shows updated balance

### Edge Case 4: Cached Balance Very Old (Offline)
**Scenario**: POS offline for 24 hours, customer checks balance

**Behavior**:
- Agent displays cached balance with warning
- Display: "Balance: 25 EUR (as of 24 hours ago)"
- Warning: "Offline mode. Actual balance may differ."
- Recommends: "Check online at www.example.com or wait for connection"

### Edge Case 5: WhatsApp Query with Typo
**Scenario**: Customer sends "Saldoo" or "saldo" (lowercase)

**Behavior**:
- System matches case-insensitive: "saldo", "Saldo", "SALDO" all work
- Fuzzy match: "Saldoo" may suggest "Did you mean 'Saldo'?"
- Unknown keyword: "Unknown command. Reply 'Saldo' to check balance."

### Edge Case 6: Balance Zero or Negative
**Scenario**: Customer has 0 or negative balance

**Behavior**:
- Display: "Balance: 0 EUR" or "Balance: -5 EUR (owe 5 EUR)"
- Explanation: "Earn points by shopping to increase balance!"
- For negative: "Previous redemption exceeded earnings. Balance will recover as you shop."

### Edge Case 7: Customer Queries Balance at POS During Checkout
**Scenario**: Customer wants balance check before deciding to redeem

**Behavior**:
- Cashier can check balance mid-checkout (non-blocking)
- Display balance without completing redemption
- Customer decides: redeem or proceed with regular payment

## Failure Modes

### Failure Mode 1: Cloud API Timeout (Online Query)
**Symptoms**: HTTP timeout after 5 seconds

**System Behavior** (depends on channel):
- **POS**: Fall back to cached balance with warning
- **PrestaShop**: Display error "Service temporarily unavailable. Try again."
- **WhatsApp**: Send message "Service busy. Please try again in a moment."

**Recovery**:
- Automatic retry after timeout
- Manual refresh button (PrestaShop)
- Customer can retry query

### Failure Mode 2: Database Query Slow
**Symptoms**: Balance query takes > 5 seconds

**System Behavior**:
- Query timeout triggers
- Return cached balance if available
- Display warning: "Using cached balance due to slow response"

**Recovery**:
- Investigate database performance
- Optimize balance calculation query
- Add database index on transaction table

### Failure Mode 3: Balance Calculation Error
**Symptoms**: Transaction ledger corrupted, balance calculation fails

**System Behavior**:
- API returns 500 Internal Server Error
- POS displays: "Unable to retrieve balance. Please try again."
- Error logged for investigation

**Recovery**:
- Manual investigation of customer transaction history
- Database repair if corruption detected
- Temporary manual adjustment to correct balance

### Failure Mode 4: WhatsApp API Unreachable
**Symptoms**: Cannot send response message to customer

**System Behavior**:
- Message queued for retry
- Retry every 5 minutes for 1 hour
- If still fails, marked as undelivered
- Customer receives no response (timeout on their end)

**Recovery**:
- WhatsApp API typically recovers quickly
- Customer can retry "Saldo" message
- Alternative: Check balance via PrestaShop or POS

### Failure Mode 5: Card UID Read Error
**Symptoms**: NFC reader returns invalid or empty UID

**System Behavior**:
- POS displays: "Card read error. Please tap again."
- Retry up to 3 times
- If still fails: "Unable to read card. Please check card or try different reader."

**Recovery**:
- Re-tap card
- Clean card and reader
- Try different card
- Manual UID entry by manager

## Offline Behavior

### POS Offline Balance Query
When POS Windows Agent offline:
1. Agent checks local balance cache (SQLite database)
2. Retrieves most recent balance sync timestamp
3. Displays balance with warnings:
   - "OFFLINE MODE"
   - "Balance as of [timestamp]"
   - "Actual balance may differ"
4. Cannot retrieve expiring points info (requires real-time calculation)
5. Cannot retrieve transaction history (local cache doesn't store full history)

### Cache Update Strategy
- **Full Sync**: Every successful online balance query updates cache
- **Transaction Sync**: Each synced earn/redeem updates cache incrementally
- **Expiration**: Cache marked stale after 24 hours
- **Invalidation**: Cache cleared on account deactivation

### Offline Query Limitations
- No transaction history available
- No expiring points calculation
- Balance may be outdated by queued transactions
- Display shows cache age prominently

## Security Considerations

### Authentication
- **POS Query**: No authentication required (card tap is implicit auth)
- **PrestaShop Query**: Requires logged-in customer session
- **WhatsApp Query**: Phone number must match enrollment record

### Rate Limiting
- **Per Customer**: 10 balance queries per hour
- **Per Terminal**: 100 balance queries per hour
- **Per IP**: 500 balance queries per hour (PrestaShop)
- **WhatsApp**: 20 queries per day per phone number

### Data Privacy
- **PII Redaction**: Balance query logs don't include full customer name
- **Transaction History**: Limited to customer's own transactions only
- **WhatsApp**: Messages encrypted in transit
- **No Public API**: Balance cannot be queried without authentication

### Audit Trail
Balance queries logged for audit (sampled to reduce volume):
```json
{
  "event_type": "BALANCE_QUERY",
  "timestamp": "2025-02-16T11:30:00Z",
  "card_uid": "04A1B2C3D4E5F6",
  "customer_id": "cust_xyz",
  "query_channel": "pos",
  "terminal_id": "POS-TERMINAL-001",
  "balance_returned": 250000,
  "query_duration_ms": 45,
  "data_freshness": "real_time"
}
```

## Related Documents

### Dependencies
- `02_architecture/WINDOWS_AGENT.md` - POS balance query implementation
- `02_architecture/CLOUD_BACKEND.md` - Backend balance calculation
- `04_integrations/PRESTASHOP_MODULE.md` - PrestaShop balance display
- `04_integrations/WHATSAPP_API.md` - WhatsApp balance queries
- `04_integrations/NFC_READER.md` - Card tap for balance
- `05_data/TRANSACTION.md` - Transaction ledger for balance calculation
- `05_data/CUSTOMER.md` - Customer balance cache

### Related Features
- `03_features/CARD_ENROLLMENT.md` - Must be enrolled to query balance
- `03_features/EARN_POINTS_POS.md` - Balance increases after earning
- `03_features/EARN_POINTS_ONLINE.md` - Balance increases from online orders
- `03_features/REDEEM_POINTS_POS.md` - Balance decreases after redemption
- `03_features/REDEEM_POINTS_ONLINE.md` - Balance decreases from online redemptions
- `03_features/EXPIRATION.md` - Balance reflects expired points
- `03_features/MANUAL_ADJUSTMENTS.md` - Balance reflects manual adjustments
- `03_features/REFUND_HANDLING.md` - Balance changes on refunds

### Integration Points
- `04_integrations/RECEIPT_PRINTER.md` - Printing balance receipt
- `07_operations/MONITORING.md` - Balance query performance monitoring

## Open Questions / TODOs

### TODO: Balance Query Analytics
**Status**: Not implemented  
**Required by**: Phase 2  
**Description**: Track how often customers check balance, which channels they use, correlation with redemptions

### TODO: Balance History Export
**Status**: Future enhancement  
**Required by**: Customer request  
**Description**: Allow customers to download transaction history as PDF or CSV

### TODO: Balance Insights
**Status**: Not planned for MVP  
**Required by**: Phase 3  
**Description**: Show insights like "You're in the top 20% of loyalty members!" or "3 more purchases until next reward"

### Open Question: Transaction History Limit
**Question**: Show last 10 transactions or all transactions?  
**Context**: Performance vs completeness  
**Impact**: API response size, page load time  
**Decision Required By**: Before launch

### Open Question: Real-Time vs Cached Balance
**Question**: Should PrestaShop always show real-time balance or allow caching?  
**Context**: Performance vs accuracy  
**Impact**: API load, customer experience  
**Decision Required By**: Before launch

### Open Question: WhatsApp Auto-Response Time
**Question**: Should WhatsApp balance query be instant or allow brief delay for batch processing?  
**Context**: Cost optimization vs UX  
**Impact**: WhatsApp API costs, customer satisfaction  
**Decision Required By**: After evaluating WhatsApp API pricing

### Open Question: Balance Notification Push
**Question**: Should customers receive proactive balance updates (e.g., "You earned 200 points today!")?  
**Context**: Engagement vs notification fatigue  
**Impact**: Email/WhatsApp volume, customer engagement  
**Decision Required By**: Phase 2 based on customer feedback
