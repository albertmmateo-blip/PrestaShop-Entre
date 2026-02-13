# Feature: Earn Points from PrestaShop Orders

## Purpose

Enable customers to earn Fidelity Points automatically when placing orders on the PrestaShop e-commerce platform. Points are calculated based on order total and credited to the customer's loyalty account after order confirmation, with support for order status changes and cancellations.

## Scope

### In Scope
- Automatic points calculation on order placement
- Points credited after order confirmation (not on pending orders)
- Integration with PrestaShop order workflow and statuses
- Customer account linking via card UID or email
- Points display in cart, checkout, and order confirmation
- Email notification with points earned
- Handling of order status changes (paid, cancelled, refunded)
- Idempotent transaction processing

### Out of Scope
- Points earning on shipping costs (only product subtotal)
- Points earning on tax amount
- Bonus points for first online order (future enhancement)
- Points earning for guest checkout (must be logged-in customer)
- Points earning on B2B wholesale orders

## Inputs

### From PrestaShop Module - Order Confirmation Hook
```json
{
  "order_id": 12345,
  "customer_id": 9876,
  "customer_email": "maria.garcia@example.com",
  "card_uid": "04A1B2C3D4E5F6",
  "order_total": 150.00,
  "order_subtotal": 135.00,
  "shipping_cost": 10.00,
  "tax_amount": 5.00,
  "discount_amount": 0.00,
  "currency": "EUR",
  "order_date": "2025-02-14T10:30:00Z",
  "order_status": "payment_accepted",
  "payment_method": "credit_card",
  "transaction_type": "earn",
  "idempotency_key": "earn_ps_order_12345"
}
```

### PrestaShop Order Statuses Triggering Points Earn
- `payment_accepted` - Payment confirmed, order being processed
- `processing` - Order being prepared for shipment
- `shipped` - Order shipped (points already awarded on payment_accepted)

### Validation Rules
- `order_id`: Must be unique PrestaShop order ID
- `customer_email`: Must match enrolled card email OR customer must have linked card
- `order_subtotal`: Points calculated on subtotal only (excludes shipping, tax)
- `order_subtotal`: Must be > 0.01 EUR
- `idempotency_key`: Prevents duplicate points for same order

## Outputs

### Success Response - Points Earned
```json
{
  "success": true,
  "transaction_id": "txn_p9o8i7u6y5t4",
  "order_id": 12345,
  "card_uid": "04A1B2C3D4E5F6",
  "customer_name": "María García",
  "customer_email": "maria.garcia@example.com",
  "order_subtotal": 135.00,
  "points_earned": 20250,
  "points_earned_display": "202.50 points (2.02 EUR)",
  "calculation": "135.00 * 0.015 = 2.025 EUR = 20250 points",
  "previous_balance": 50000,
  "new_balance": 70250,
  "new_balance_display": "7.02 EUR",
  "timestamp": "2025-02-14T10:30:05Z",
  "email_sent": true
}
```

### Success Response - Card Not Linked (Pending)
```json
{
  "success": true,
  "status": "pending_card_link",
  "order_id": 12345,
  "customer_email": "maria.garcia@example.com",
  "order_subtotal": 135.00,
  "points_to_be_earned": 20250,
  "message": "Points will be credited when customer links loyalty card to account.",
  "action_required": "Customer should visit My Account > Loyalty Card to link card"
}
```

### Failure Response - Customer Not Enrolled
```json
{
  "success": false,
  "error_code": "CUSTOMER_NOT_ENROLLED",
  "error_message": "Customer does not have a loyalty card registered.",
  "customer_email": "maria.garcia@example.com",
  "resolution": "Customer can enroll at physical store or in My Account > Loyalty Card"
}
```

### Failure Response - Duplicate Order Points
```json
{
  "success": false,
  "error_code": "DUPLICATE_TRANSACTION",
  "error_message": "Points already awarded for this order.",
  "order_id": 12345,
  "original_transaction_id": "txn_p9o8i7u6y5t4",
  "original_timestamp": "2025-02-14T10:30:05Z"
}
```

### Side Effects
- Customer balance increased by calculated points
- Transaction record created in cloud backend ledger
- Email sent to customer with points earned
- PrestaShop order note added: "Loyalty points: +202.50 pts"
- If card not linked: Pending transaction record created

## Main Flows

### Flow 1: Earn Points - Customer with Linked Card

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────────┐    ┌──────────┐
│ Customer │    │PrestaShop│    │  Loyalty │    │ Cloud API  │    │ Customer │
│ (Browser)│    │  Module  │    │  Backend │    │            │    │ (Email)  │
└────┬─────┘    └────┬─────┘    └────┬─────┘    └─────┬──────┘    └────┬─────┘
     │              │               │                │                 │
     │ 1. Add items │               │                │                 │
     │    to cart   │               │                │                 │
     ├─────────────>│               │                │                 │
     │              │               │                │                 │
     │ 2. View cart │               │                │                 │
     ├─────────────>│               │                │                 │
     │              │               │                │                 │
     │              │ 3. Display    │                │                 │
     │              │   "You will   │                │                 │
     │              │    earn 202   │                │                 │
     │              │    points"    │                │                 │
     │<─────────────┤               │                │                 │
     │              │               │                │                 │
     │ 4. Proceed   │               │                │                 │
     │    to checkout│              │                │                 │
     ├─────────────>│               │                │                 │
     │              │               │                │                 │
     │ 5. Select    │               │                │                 │
     │    payment & │               │                │                 │
     │    confirm   │               │                │                 │
     ├─────────────>│               │                │                 │
     │              │               │                │                 │
     │              │ 6. Hook:      │                │                 │
     │              │   actionOrderStatus           │                 │
     │              │   UpdateAfter │                │                 │
     │              ├──────────────>│                │                 │
     │              │               │                │                 │
     │              │               │ 7. Get customer│                 │
     │              │               │    card UID    │                 │
     │              │               ├────────┐       │                 │
     │              │               │        │       │                 │
     │              │               │<───────┘       │                 │
     │              │               │                │                 │
     │              │               │ 8. POST /api/v1│                 │
     │              │               │   /transactions│                 │
     │              │               │   /earn        │                 │
     │              │               ├───────────────>│                 │
     │              │               │                │                 │
     │              │               │                │ 9. Validate    │
     │              │               │                ├────────┐       │
     │              │               │                │        │       │
     │              │               │                │<───────┘       │
     │              │               │                │                 │
     │              │               │                │10. Calculate   │
     │              │               │                │   135*0.015    │
     │              │               │                ├────────┐       │
     │              │               │                │        │       │
     │              │               │                │<───────┘       │
     │              │               │                │                 │
     │              │               │                │11. Create txn  │
     │              │               │                ├────────┐       │
     │              │               │                │        │       │
     │              │               │                │<───────┘       │
     │              │               │                │                 │
     │              │               │12. 201 Created │                 │
     │              │               │<───────────────┤                 │
     │              │               │                │                 │
     │              │               │13. Add order   │                 │
     │              │               │   note         │                 │
     │              │               ├───────────────>│                 │
     │              │               │                │                 │
     │              │14. Order      │                │                 │
     │              │   confirmation│                │                 │
     │              │   page        │                │                 │
     │<─────────────┤               │                │                 │
     │              │               │                │                 │
     │              │               │                │15. Queue email │
     │              │               │                ├────────┐       │
     │              │               │                │        │       │
     │              │               │                │<───────┘       │
     │              │               │                │                 │
     │              │               │                │16. Send email  │
     │              │               │                │   "You earned  │
     │              │               │                │    202 pts!"   │
     │              │               │                ├────────────────>│
     │              │               │                │                 │
```

### Flow 2: Earn Points - Card Not Linked (Deferred)

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────────┐
│ Customer │    │PrestaShop│    │  Loyalty │    │ Cloud API  │
│ (Browser)│    │  Module  │    │  Backend │    │            │
└────┬─────┘    └────┬─────┘    └────┬─────┘    └─────┬──────┘
     │              │               │                │
     │ 1. Place     │               │                │
     │    order     │               │                │
     ├─────────────>│               │                │
     │              │               │                │
     │              │ 2. Hook:      │                │
     │              │   order status│                │
     │              ├──────────────>│                │
     │              │               │                │
     │              │               │ 3. Check if    │
     │              │               │    customer has│
     │              │               │    card        │
     │              │               ├────────┐       │
     │              │               │        │       │
     │              │               │<───────┘       │
     │              │               │                │
     │              │               │ 4. No card     │
     │              │               │    found       │
     │              │               ├────────┐       │
     │              │               │        │       │
     │              │               │<───────┘       │
     │              │               │                │
     │              │               │ 5. POST /api/v1│
     │              │               │   /pending_    │
     │              │               │   transactions │
     │              │               ├───────────────>│
     │              │               │                │
     │              │               │                │ 6. Create      │
     │              │               │                │   pending txn  │
     │              │               │                ├────────┐       │
     │              │               │                │        │       │
     │              │               │                │<───────┘       │
     │              │               │                │                │
     │              │               │ 7. 201 Pending │                │
     │              │               │<───────────────┤                │
     │              │               │                │                │
     │              │ 8. Add order  │                │                │
     │              │    note:      │                │                │
     │              │   "Points     │                │                │
     │              │    pending    │                │                │
     │              │    card link" │                │                │
     │              │<──────────────┤                │                │
     │              │               │                │                │
     │ 9. Order page│               │                │                │
     │    shows:    │               │                │                │
     │   "Link card │               │                │                │
     │    to earn   │               │                │                │
     │    points"   │               │                │                │
     │<─────────────┤               │                │                │
     │              │               │                │                │
     │ ...Later...  │               │                │                │
     │              │               │                │                │
     │ 10. Customer │               │                │                │
     │    links card│               │                │                │
     ├─────────────>│               │                │                │
     │              │               │                │                │
     │              │               │11. Trigger     │                │
     │              │               │   pending txn  │                │
     │              │               │   processing   │                │
     │              │               ├───────────────>│                │
     │              │               │                │                │
     │              │               │                │12. Award points│
     │              │               │                ├────────┐       │
     │              │               │                │        │       │
     │              │               │                │<───────┘       │
     │              │               │                │                │
```

### Flow 3: Order Status Change (Payment Failed)

If order status changes from `payment_accepted` to `payment_error` or `cancelled`:
1. PrestaShop triggers `actionOrderStatusUpdate` hook
2. Module checks if points were already awarded
3. If yes, module calls reversal API
4. Points automatically reversed (see REFUND_HANDLING.md)
5. Customer notified: "Order cancelled. Points reversed."

## Edge Cases

### Edge Case 1: Customer Has Multiple Cards
**Scenario**: Customer enrolled two cards with same email

**Behavior**:
- Points awarded to most recently used card
- If no recent activity, awarded to first enrolled card
- Customer can change default card in account settings

### Edge Case 2: Order Placed While POS Offline
**Scenario**: Customer places PrestaShop order while physical store POS is offline

**Behavior**:
- PrestaShop always online, points awarded immediately
- When POS comes online, syncs with updated balance
- No conflict (PrestaShop order separate from POS sales)

### Edge Case 3: Order Total Includes Discount Code
**Scenario**: Customer applies 10 EUR discount code, subtotal reduces from 135 to 125 EUR

**Behavior**:
- Points calculated on **discounted subtotal** (125 EUR)
- Reasoning: Customer only "spent" 125 EUR
- Receipt shows: "Earned 187.50 points on 125 EUR purchase"

### Edge Case 4: Order Edited After Placement
**Scenario**: Customer calls to add item, order total increases

**Behavior**:
- PrestaShop creates new order or updates existing
- Module detects order_id change or update
- If new order: Award points normally
- If update: Award additional points for difference
- Prevent double-award with idempotency key check

### Edge Case 5: Free Shipping Promotion
**Scenario**: Order has free shipping (shipping_cost = 0)

**Behavior**:
- No impact on points (shipping never earns points anyway)
- Points calculated on product subtotal as normal

### Edge Case 6: B2B Customer Places Order
**Scenario**: Business customer with wholesale pricing

**Behavior** (configurable):
- Option A: B2B customers excluded from loyalty program
- Option B: B2B customers earn points at reduced rate (e.g., 0.005 instead of 0.015)
- Configuration in PrestaShop module settings

### Edge Case 7: Order Contains Gift Card Product
**Scenario**: Customer buys a gift card (balance transfer product)

**Behavior**:
- Configuration option: Exclude gift cards from points earning
- Prevents: Customer buys gift card, earns points, then buys with gift card, earns more points (point inflation)

## Failure Modes

### Failure Mode 1: Cloud API Unreachable
**Symptoms**: HTTP timeout or connection refused during order confirmation

**System Behavior**:
- Order proceeds normally (points are secondary to order processing)
- Module creates pending transaction record in PrestaShop database
- Module retries every 5 minutes (via cron job)
- Customer sees: "Order confirmed. Loyalty points will be credited shortly."

**Recovery**:
- Automatic retry via PrestaShop cron
- Manual retry in module admin panel
- Customer can see "Points pending" in order history

### Failure Mode 2: Customer Deleted During Order Processing
**Symptoms**: Order placed, but customer account deleted before points awarded

**System Behavior**:
- Module checks customer exists before awarding points
- If not found: Log warning, skip points award
- Order still processes (no customer impact)

**Recovery**:
- No recovery needed (customer deleted, points irrelevant)

### Failure Mode 3: Duplicate Order Hook Trigger
**Symptoms**: PrestaShop triggers same hook multiple times for same order

**System Behavior**:
- Idempotency key prevents duplicate points award
- Backend returns 409 Conflict with original transaction
- Module logs "Points already awarded" and skips

**Recovery**:
- Automatic via idempotency (no action needed)

### Failure Mode 4: Points Calculation Error
**Symptoms**: Order subtotal is NaN or negative (data corruption)

**System Behavior**:
- Module validates order data before sending to API
- If invalid: Log error, skip points award
- Order still completes
- Admin notification: "Points calculation failed for order 12345"

**Recovery**:
- Admin manually awards points using MANUAL_ADJUSTMENTS.md
- Investigate root cause of data corruption

### Failure Mode 5: Email Service Failure
**Symptoms**: Points awarded but confirmation email fails

**System Behavior**:
- Points credit still succeeds
- Email queued for retry
- Customer can see points in balance (email not critical)

**Recovery**:
- Automatic email retry
- Customer can check balance via WhatsApp or PrestaShop account

## Offline Behavior

### PrestaShop Module - Always Online
- PrestaShop requires internet to function, no offline mode
- If cloud backend unreachable, module queues pending transactions
- Pending transactions stored in PrestaShop database table:
  ```sql
  CREATE TABLE IF NOT EXISTS `ps_loyalty_pending_transactions` (
    `id_transaction` INT AUTO_INCREMENT PRIMARY KEY,
    `order_id` INT NOT NULL,
    `customer_id` INT NOT NULL,
    `card_uid` VARCHAR(20),
    `order_subtotal` DECIMAL(10,2) NOT NULL,
    `points_to_award` INT NOT NULL,
    `date_created` DATETIME NOT NULL,
    `retry_count` INT DEFAULT 0,
    `last_retry` DATETIME,
    `status` ENUM('pending', 'processing', 'failed', 'completed') DEFAULT 'pending',
    `error_message` TEXT
  );
  ```

### Retry Mechanism
- **Trigger**: PrestaShop cron job runs every 5 minutes
- **Processing**: Module attempts to sync pending transactions
- **Batch Size**: 50 transactions per cron run
- **Max Retries**: 20 attempts (24+ hours)
- **Failure**: After 20 failures, transaction marked `failed`, admin notified

### No Sync Conflicts
- PrestaShop orders are distinct from POS sales
- Order IDs unique, no collision with POS sale IDs
- Customer balance is additive (PrestaShop earns don't conflict with POS earns)

## Security Considerations

### Customer Identity Verification
- **Logged-In Requirement**: Must be authenticated PrestaShop customer
- **Email Match**: Customer email must match loyalty card enrollment email
- **Session Validation**: PrestaShop session token validated

### Idempotency Protection
- **Key Format**: `earn_ps_order_{order_id}`
- **Storage**: Keys stored in backend for 30 days (longer than refund window)
- **Validation**: Prevents duplicate points if order hook fires multiple times

### Fraud Prevention
- **Rate Limiting**: Max 10 orders per customer per day
- **Velocity Check**: Alert if > 3 orders in 1 hour
- **High-Value Alert**: Flag orders > 1,000 EUR for manual review
- **IP Tracking**: Log IP address for audit

### Authorization
- **PrestaShop API Key**: Module authenticates with backend using secret API key
- **No Customer API Key**: Customer cannot directly call loyalty API
- **Module Gateway**: All requests proxied through PrestaShop module

### Data Protection
- **PII Encryption**: Customer email encrypted in pending transaction table
- **HTTPS Only**: All API calls encrypted in transit
- **Audit Log**: Full audit trail of who earned points, when, why

## Related Documents

### Dependencies
- `02_architecture/CLOUD_BACKEND.md` - Backend API processing earn requests
- `04_integrations/PRESTASHOP_MODULE.md` - Module implementation details
- `05_data/TRANSACTION.md` - Transaction ledger structure
- `05_data/CUSTOMER.md` - Customer account and card linking
- `06_security/SECURITY_MODEL.md` - Authentication and authorization

### Related Features
- `03_features/CARD_ENROLLMENT.md` - Customer must enroll to earn
- `03_features/EARN_POINTS_POS.md` - Earning at physical store
- `03_features/REDEEM_POINTS_ONLINE.md` - Using earned points online
- `03_features/REFUND_HANDLING.md` - Reversing points on order refund
- `03_features/BALANCE_QUERY.md` - Checking earned points
- `03_features/EXPIRATION.md` - Points expire 3 months after earning

### Integration Points
- `04_integrations/EMAIL_SERVICE.md` - Sending earn confirmation emails
- `06_security/IDEMPOTENCY.md` - Duplicate prevention

## Open Questions / TODOs

### TODO: Pending Transaction Dashboard
**Status**: Designed but not implemented  
**Required by**: Phase 2  
**Description**: Admin UI to view and manually retry failed pending transactions

### TODO: Points Earning on Guest Checkout
**Status**: Future enhancement  
**Required by**: TBD  
**Description**: Allow guest orders to retroactively earn points if customer later creates account and links card

### TODO: Tiered Earn Rates
**Status**: Not planned for MVP  
**Required by**: Phase 3 (if VIP program launched)  
**Description**: VIP customers earn at higher rate (e.g., 0.02 instead of 0.015)

### Open Question: Earn Points on Shipping Cost
**Question**: Should customers earn points on shipping fees?  
**Context**: Current rule excludes shipping, but could incentivize larger orders  
**Impact**: Business rule, calculation logic  
**Decision Required By**: Before launch

### Open Question: Earn Points on Tax
**Question**: Should points be calculated on total including tax, or subtotal excluding tax?  
**Context**: Current implementation uses subtotal (pre-tax)  
**Impact**: Customer perceived value, accounting  
**Decision Required By**: Before launch

### Open Question: Order Status Threshold
**Question**: Should points be awarded on `payment_accepted` or wait until `shipped`?  
**Context**: Early award better UX, but risk if order cancelled  
**Impact**: Customer experience, reversal frequency  
**Decision Required By**: Before launch

### Open Question: Multi-Currency Orders
**Question**: How to handle orders in non-EUR currency?  
**Context**: PrestaShop supports multi-currency, but points are EUR-based  
**Impact**: Currency conversion, rate fluctuation  
**Decision Required By**: If expanding to other countries
