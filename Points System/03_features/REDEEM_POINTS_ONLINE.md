# Feature: Redeem Points in PrestaShop Cart

## Purpose

Enable customers to redeem accumulated Fidelity Points as discount toward their PrestaShop online orders during checkout. Points are converted to EUR discount and applied as a cart rule, reducing the order total, with support for partial redemption.

## Scope

### In Scope
- Display available balance in cart and checkout
- Customer selects redemption amount or "use all points"
- Points-to-EUR conversion applied as PrestaShop cart rule
- Partial payment support (redeem some/all points, pay remainder with payment method)
- Real-time balance validation
- Redemption displayed on order confirmation and invoice
- Automatic redemption reversal if order cancelled
- Maximum redemption cap (up to 100% of cart total)

### Out of Scope
- Points redemption on shipping costs (only product subtotal)
- Automatic redemption without customer consent
- Points redemption for guest checkout
- Points redemption combined with certain promotional codes (configurable exclusion)
- Points transfer or gifting to another customer

## Inputs

### From PrestaShop Module - Balance Check
```json
{
  "customer_id": 9876,
  "customer_email": "maria.garcia@example.com",
  "action": "get_balance"
}
```

### From PrestaShop Module - Apply Redemption
```json
{
  "cart_id": 45678,
  "customer_id": 9876,
  "card_uid": "04A1B2C3D4E5F6",
  "cart_total": 89.50,
  "cart_subtotal": 85.00,
  "shipping_cost": 4.50,
  "redemption_amount": 30.00,
  "currency": "EUR",
  "timestamp": "2025-02-14T14:15:00Z",
  "action": "apply_redemption"
}
```

### From PrestaShop Module - Finalize Redemption (Order Placed)
```json
{
  "order_id": 12346,
  "cart_id": 45678,
  "customer_id": 9876,
  "card_uid": "04A1B2C3D4E5F6",
  "order_total": 89.50,
  "order_subtotal": 85.00,
  "redemption_amount": 30.00,
  "final_payment_amount": 59.50,
  "currency": "EUR",
  "order_timestamp": "2025-02-14T14:20:00Z",
  "transaction_type": "redeem",
  "idempotency_key": "redeem_ps_order_12346"
}
```

### Validation Rules
- `customer_id`: Must be logged-in PrestaShop customer
- `card_uid`: Customer must have linked loyalty card
- `redemption_amount`: Must be > 0 AND <= customer balance AND <= cart_subtotal
- `cart_subtotal`: Redemption applies to products only (not shipping or tax)
- `idempotency_key`: Prevents duplicate redemption

## Outputs

### Success Response - Balance Check
```json
{
  "success": true,
  "card_uid": "04A1B2C3D4E5F6",
  "customer_name": "María García",
  "current_balance": 500000,
  "current_balance_eur": 50.00,
  "current_balance_display": "50.00 EUR in points",
  "points_expiring_soon": 100000,
  "points_expiring_date": "2025-03-15",
  "expiring_soon_display": "10.00 EUR expires on 15 March"
}
```

### Success Response - Apply Redemption (Cart)
```json
{
  "success": true,
  "cart_id": 45678,
  "redemption_amount": 30.00,
  "points_to_redeem": 3000000,
  "cart_rule_id": 789,
  "cart_rule_code": "LOYALTY_30EUR",
  "new_cart_total": 59.50,
  "estimated_balance_after": 200000,
  "estimated_balance_after_display": "20.00 EUR"
}
```

### Success Response - Finalize Redemption (Order Placed)
```json
{
  "success": true,
  "transaction_id": "txn_l9k8j7h6g5f4",
  "order_id": 12346,
  "card_uid": "04A1B2C3D4E5F6",
  "customer_name": "María García",
  "redemption_amount": 30.00,
  "points_redeemed": 3000000,
  "previous_balance": 500000,
  "new_balance": 200000,
  "new_balance_display": "20.00 EUR",
  "order_total_before": 89.50,
  "order_total_after": 59.50,
  "timestamp": "2025-02-14T14:20:00Z",
  "receipt_message": "Redeemed 30.00 EUR in loyalty points"
}
```

### Failure Response - Insufficient Balance
```json
{
  "success": false,
  "error_code": "INSUFFICIENT_BALANCE",
  "error_message": "Insufficient loyalty points.",
  "requested_amount": 50.00,
  "requested_points": 5000000,
  "available_balance": 300000,
  "available_balance_eur": 30.00,
  "max_redemption_display": "You can redeem up to 30.00 EUR"
}
```

### Failure Response - No Card Linked
```json
{
  "success": false,
  "error_code": "CARD_NOT_LINKED",
  "error_message": "No loyalty card linked to your account.",
  "resolution": "Please link your loyalty card in My Account > Loyalty Card",
  "enrollment_url": "/my-account/loyalty-card"
}
```

### Side Effects
- PrestaShop cart rule created with discount value
- Cart total recalculated with discount applied
- When order placed:
  - Customer balance decreased by redeemed points
  - Negative transaction record created in ledger
  - Order note added: "Loyalty points redeemed: 30.00 EUR"
  - Invoice shows loyalty discount line item

## Main Flows

### Flow 1: Redeem Points in Cart - Happy Path

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────────┐
│ Customer │    │PrestaShop│    │  Loyalty │    │ Cloud API  │
│ (Browser)│    │  Module  │    │  Module  │    │            │
└────┬─────┘    └────┬─────┘    └────┬─────┘    └─────┬──────┘
     │              │               │                │
     │ 1. Add items │               │                │
     │    to cart   │               │                │
     ├─────────────>│               │                │
     │              │               │                │
     │ 2. View cart │               │                │
     ├─────────────>│               │                │
     │              │               │                │
     │              │ 3. Display    │                │
     │              │    balance    │                │
     │              │    widget     │                │
     │              ├──────────────>│                │
     │              │               │                │
     │              │               │ 4. GET balance │
     │              │               ├───────────────>│
     │              │               │                │
     │              │               │ 5. 200 OK      │
     │              │               │   {50.00 EUR}  │
     │              │               │<───────────────┤
     │              │               │                │
     │              │ 6. Render     │                │
     │              │   "You have   │                │
     │              │    50 EUR"    │                │
     │              │<──────────────┤                │
     │              │               │                │
     │ 7. Display   │               │                │
     │   "Loyalty:  │               │                │
     │    50 EUR    │               │                │
     │    available"│               │                │
     │<─────────────┤               │                │
     │              │               │                │
     │ 8. Click "Use│               │                │
     │    Points"   │               │                │
     ├─────────────>│               │                │
     │              │               │                │
     │ 9. Show form:│               │                │
     │   "How much?"│               │                │
     │   [30.00 EUR]│               │                │
     │   [Use All]  │               │                │
     │<─────────────┤               │                │
     │              │               │                │
     │ 10. Enter    │               │                │
     │    "30.00"   │               │                │
     │    & submit  │               │                │
     ├─────────────>│               │                │
     │              │               │                │
     │              │               │11. Validate    │
     │              │               │   30 <= 50 ✓   │
     │              │               │   30 <= 85 ✓   │
     │              │               ├────────┐       │
     │              │               │        │       │
     │              │               │<───────┘       │
     │              │               │                │
     │              │               │12. Create cart │
     │              │               │   rule "30 EUR"│
     │              │               ├───────────────>│
     │              │               │                │
     │              │ 13. Cart rule │                │
     │              │    created    │                │
     │              │<──────────────┤                │
     │              │               │                │
     │              │ 14. Recalc    │                │
     │              │    cart total │                │
     │              ├────────┐      │                │
     │              │        │      │                │
     │              │<───────┘      │                │
     │              │               │                │
     │ 15. Display  │               │                │
     │   "Total:    │               │                │
     │    59.50 EUR"│               │                │
     │   "Discount: │               │                │
     │    -30 EUR"  │               │                │
     │<─────────────┤               │                │
     │              │               │                │
     │ 16. Proceed  │               │                │
     │    to checkout│              │                │
     ├─────────────>│               │                │
     │              │               │                │
     │ 17. Confirm  │               │                │
     │    & pay     │               │                │
     ├─────────────>│               │                │
     │              │               │                │
     │              │ 18. Hook:     │                │
     │              │   actionValidate               │
     │              │   Order       │                │
     │              ├──────────────>│                │
     │              │               │                │
     │              │               │19. POST /api/v1│
     │              │               │   /transactions│
     │              │               │   /redeem      │
     │              │               ├───────────────>│
     │              │               │                │
     │              │               │                │20. Deduct pts │
     │              │               │                ├────────┐      │
     │              │               │                │        │      │
     │              │               │                │<───────┘      │
     │              │               │                │               │
     │              │               │21. 201 Created │               │
     │              │               │<───────────────┤               │
     │              │               │                │               │
     │              │               │22. Add order   │               │
     │              │               │   note         │               │
     │              │               ├───────────────>│               │
     │              │               │                │               │
     │ 23. Order    │               │                │               │
     │    confirmation              │                │               │
     │    "Saved 30 │               │                │               │
     │     EUR!"    │               │                │               │
     │<─────────────┤               │                │               │
     │              │               │                │               │
```

### Flow 2: Use All Points (Partial Redemption)

```
Scenario: Customer has 20 EUR in points, cart total is 85 EUR

1. Customer views cart, sees "20 EUR available in points"
2. Customer clicks "Use All Points"
3. Module validates: min(20, 85) = 20 EUR
4. Module confirms: "Use 20 EUR in points? (Remaining: 65 EUR)"
5. Customer confirms
6. Cart rule created for 20 EUR discount
7. Cart total: 89.50 - 20.00 = 69.50 EUR
8. Customer proceeds to checkout and pays 69.50 EUR
9. Order confirmation shows:
   - Subtotal: 85.00 EUR
   - Loyalty discount: -20.00 EUR
   - Shipping: 4.50 EUR
   - Total paid: 69.50 EUR
   - Remaining balance: 0.00 EUR
```

### Flow 3: Remove Redemption from Cart

```
Customer can remove or modify redemption before placing order:

1. Customer has applied 30 EUR redemption
2. Customer clicks "Remove loyalty discount"
3. Module deletes cart rule
4. Cart total recalculated (back to 89.50 EUR)
5. Customer balance remains unchanged (points not yet deducted)
6. Customer can reapply with different amount

Points only deducted when order is placed, not when cart rule applied.
```

## Edge Cases

### Edge Case 1: Redemption Exceeds Cart Subtotal
**Scenario**: Customer has 100 EUR in points, cart subtotal is 50 EUR

**Behavior**:
- Module caps redemption at cart subtotal (50 EUR)
- Display: "Maximum redemption: 50 EUR (cart subtotal)"
- Remaining 50 EUR stays in balance
- Shipping cost still charged (4.50 EUR), so total is 4.50 EUR

### Edge Case 2: Cart Modified After Redemption Applied
**Scenario**: Customer applies 30 EUR redemption, then adds another item worth 20 EUR

**Behavior**:
- Cart rule remains at 30 EUR (doesn't auto-adjust)
- Customer can increase redemption if desired
- New cart total: 105.00 - 30.00 = 75.00 EUR + shipping

### Edge Case 3: Cart Modified Below Redemption Amount
**Scenario**: Customer applies 30 EUR redemption, then removes items, cart subtotal now 20 EUR

**Behavior**:
- Cart rule automatically adjusted to max allowed (20 EUR)
- Customer notified: "Loyalty discount adjusted to 20 EUR (max cart value)"
- Alternatively: Cart rule removed, customer must reapply

### Edge Case 4: Redemption Combined with Promo Code
**Scenario**: Customer has 10% off promo code AND wants to use points

**Behavior** (configurable):
- **Option A**: Allow stacking (promo applies first, then points on discounted total)
- **Option B**: Exclusive (customer chooses promo OR points, not both)
- **Option C**: Partial stacking (points allowed with specific promo types only)

Default: Option A (allow stacking)

### Edge Case 5: Order Cancelled After Redemption
**Scenario**: Customer places order with points redemption, then cancels order

**Behavior**:
- Order status changes to `cancelled`
- Module hooks into `actionOrderStatusUpdate`
- Automatically calls reversal API (see REFUND_HANDLING.md)
- Points restored to customer balance
- Customer notified: "Order cancelled. Points restored."

### Edge Case 6: Payment Fails After Points Deducted
**Scenario**: Points deducted, but payment gateway returns error

**Behavior**:
- Order creation rolls back
- Module detects failure in `actionValidateOrder` hook
- Immediately calls reversal API
- Points restored
- Customer sees: "Payment failed. Please try again. Points not deducted."

### Edge Case 7: Customer Has Zero Balance
**Scenario**: Customer tries to redeem but has 0 points

**Behavior**:
- "Use Points" button disabled
- Display: "No loyalty points available. Make purchases to earn points!"

### Edge Case 8: Balance Changes During Checkout
**Scenario**: 
1. Customer checks balance: 50 EUR
2. Applies 50 EUR redemption
3. Meanwhile, points expire (background job runs)
4. Customer places order

**Behavior**:
- Module validates balance again at order placement
- If insufficient: Order fails with "Insufficient balance"
- Customer notified: "Your balance has changed. Please refresh and retry."
- Cart rule removed

## Failure Modes

### Failure Mode 1: Cloud API Unreachable During Checkout
**Symptoms**: Balance check or redemption API times out

**System Behavior**:
- Module cannot validate balance
- Display: "Loyalty service temporarily unavailable. Please complete checkout without points or try again later."
- Customer can:
  - **Option A**: Proceed without points redemption
  - **Option B**: Wait and retry
- Order processing continues (points are optional)

**Recovery**:
- Customer can request manual points redemption via customer service
- Admin manually adjusts balance using MANUAL_ADJUSTMENTS.md

### Failure Mode 2: Balance Deduction Succeeds, Order Creation Fails
**Symptoms**: Points deducted via API, but PrestaShop order creation fails

**System Behavior**:
- **Critical failure**: Points deducted without order
- Module wrapped in transaction:
  1. Deduct points
  2. Create order
  3. If step 2 fails, immediately reverse step 1
- Automatic reversal API call
- Customer notified: "Order failed. Points not deducted. Please try again."

**Recovery**:
- Automatic reversal (no manual intervention)
- Customer retries order

### Failure Mode 3: Duplicate Redemption Attempt
**Symptoms**: Customer double-clicks "Place Order" button

**System Behavior**:
- Idempotency key prevents duplicate redemption
- First request succeeds
- Second request returns 409 Conflict
- Module ignores duplicate, proceeds with order

**Recovery**:
- Automatic via idempotency (no action needed)

### Failure Mode 4: Cart Rule Creation Fails
**Symptoms**: PrestaShop cart rule insertion fails (database error)

**System Behavior**:
- Module catches exception
- Display: "Cannot apply loyalty discount. Please try again."
- Points not deducted (cart rule creation is prerequisite)

**Recovery**:
- Customer retries "Use Points"
- If persistent, clear cart cache and retry

### Failure Mode 5: Balance Cache Outdated
**Symptoms**: Customer sees 50 EUR balance, tries to redeem, API says only 30 EUR available

**System Behavior**:
- API returns 402 "Insufficient Balance" with actual balance
- Module updates displayed balance
- Display: "Your balance is 30 EUR. Adjust redemption amount."
- Cart rule adjusted or removed

**Recovery**:
- Customer adjusts redemption to 30 EUR or less
- Proceeds with order

## Offline Behavior

### PrestaShop Module - Always Online
- PrestaShop requires internet to function, no offline mode
- If cloud API unreachable:
  - Redemption feature disabled
  - Customer can still place order without points
  - Admin can manually credit points later

### No Queuing for Redemptions
Unlike earn transactions, redemptions cannot be queued offline because:
- Balance validation requires real-time check
- Risk of insufficient balance if queued
- Customer expects immediate discount visibility

**Mitigation**: If API temporarily unavailable, customer places order without points, then contacts support for manual redemption.

## Security Considerations

### Customer Authorization
- **Logged-In Only**: Redemption requires authenticated PrestaShop session
- **Card Ownership**: Customer must own the linked card (email match)
- **Session Validation**: PrestaShop session token validated on each request

### Idempotency Protection
- **Key Format**: `redeem_ps_order_{order_id}_{cart_id}`
- **Storage**: Keys stored in backend for 30 days
- **Validation**: Prevents duplicate redemption if order processed multiple times

### Balance Integrity
- **Atomic Transaction**: Balance check + deduction in single DB transaction
- **Race Condition Prevention**: Row-level lock on customer balance record
- **Validation**: Balance validated again at order placement (not just cart)

### Fraud Prevention
- **Velocity Limit**: Max 5 redemptions per customer per day
- **High-Value Alert**: Flag redemptions > 100 EUR for review
- **IP Tracking**: Log IP address for audit
- **Rate Limiting**: API rate limited to 100 requests/minute per customer

### Cart Rule Security
- **Unique Code**: Each loyalty cart rule has unique code (prevents sharing)
- **Single Use**: Cart rule marked as used after order placed
- **Expiration**: Cart rule expires after 30 minutes if order not placed
- **Customer Binding**: Cart rule locked to specific customer_id

## Related Documents

### Dependencies
- `02_architecture/CLOUD_BACKEND.md` - Backend API handling redemptions
- `04_integrations/PRESTASHOP_MODULE.md` - Module implementation
- `05_data/TRANSACTION.md` - Redemption transaction structure
- `05_data/CUSTOMER.md` - Balance computation
- `06_security/SECURITY_MODEL.md` - Authentication and authorization

### Related Features
- `03_features/CARD_ENROLLMENT.md` - Customer must enroll and link card
- `03_features/EARN_POINTS_ONLINE.md` - Earning points to redeem
- `03_features/REDEEM_POINTS_POS.md` - Redeeming at physical store
- `03_features/BALANCE_QUERY.md` - Checking available balance
- `03_features/REFUND_HANDLING.md` - Reversing redemption on order refund/cancel
- `03_features/EXPIRATION.md` - Only non-expired points can be redeemed

### Integration Points
- `04_integrations/EMAIL_SERVICE.md` - Order confirmation with redemption details
- `06_security/IDEMPOTENCY.md` - Duplicate prevention

## Open Questions / TODOs

### TODO: Redemption Priority (FIFO Expiration)
**Status**: Designed but not implemented  
**Required by**: Phase 2  
**Description**: Automatically redeem points closest to expiration first to minimize waste

### TODO: Redemption Limits Per Order
**Status**: Open question  
**Question**: Should there be max redemption per order (e.g., 100 EUR)?  
**Decision Required By**: Before launch

### TODO: Redemption on Free Shipping Threshold
**Status**: Edge case not handled  
**Question**: If cart has "free shipping over 75 EUR", and redemption brings cart below 75 EUR, should shipping be charged?  
**Decision Required By**: Before launch

### Open Question: Redemption with Gift Cards
**Question**: Can customer combine loyalty points + gift card payment?  
**Context**: Multiple discount sources on same order  
**Impact**: Payment flow, cart rule stacking  
**Decision Required By**: Before launch

### Open Question: Redemption Rounding
**Question**: If balance is 30.47 EUR, can customer redeem exactly 30.47 or must round?  
**Context**: UX simplicity vs precision  
**Impact**: Cart rule creation, display  
**Decision Required By**: Before launch

### Open Question: Redemption on B2B Orders
**Question**: Should B2B customers be allowed to redeem points?  
**Context**: Wholesale pricing may exclude loyalty benefits  
**Impact**: Business rules, configuration  
**Decision Required By**: If B2B feature enabled

### Open Question: Min Redemption Amount
**Question**: Should there be minimum redemption (e.g., 5 EUR)?  
**Context**: Prevent tiny redemptions for simplicity  
**Impact**: UX, validation  
**Decision Required By**: Before launch
