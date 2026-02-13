# Features Documentation

This folder contains detailed documentation for all 9 core features of the Fidelity Points loyalty system.

## Feature Overview

Each feature document follows the mandatory template with these sections:
- **Purpose** - What the feature does and why it exists
- **Scope** - What's included and explicitly excluded
- **Inputs** - Request formats and validation rules
- **Outputs** - Response formats and side effects
- **Main Flows** - Sequence diagrams and happy paths
- **Edge Cases** - Unusual scenarios and handling
- **Failure Modes** - Error conditions and recovery
- **Offline Behavior** - How the feature works without internet
- **Security Considerations** - Auth, audit, fraud prevention
- **Related Documents** - Cross-references to other docs
- **Open Questions/TODOs** - Unresolved issues and future work

## Feature Files

### Customer Onboarding
- **[CARD_ENROLLMENT.md](CARD_ENROLLMENT.md)** - Customer enrollment and card assignment flow
  - Enrollment at POS and PrestaShop
  - Card-to-customer association
  - Offline enrollment queuing
  - GDPR consent capture

### Earning Points
- **[EARN_POINTS_POS.md](EARN_POINTS_POS.md)** - Earning points at physical POS
  - Automatic points calculation on purchases
  - Offline earn transaction queuing
  - Integration with Aniwin.net POS
  - Idempotent transaction processing

- **[EARN_POINTS_ONLINE.md](EARN_POINTS_ONLINE.md)** - Earning points from PrestaShop orders
  - Order confirmation hooks
  - Points on product subtotal only
  - Pending transactions for unlinked cards
  - Order status change handling

### Redeeming Points
- **[REDEEM_POINTS_POS.md](REDEEM_POINTS_POS.md)** - Redeeming points at physical POS
  - Balance check and redemption flow
  - Partial redemption support
  - Offline redemption with cached balance
  - Discount application to Aniwin.net sale

- **[REDEEM_POINTS_ONLINE.md](REDEEM_POINTS_ONLINE.md)** - Redeeming points in PrestaShop cart
  - Cart rule creation for point redemption
  - Real-time balance validation
  - Redemption removal before order placement
  - Payment failure rollback

### Balance Management
- **[REFUND_HANDLING.md](REFUND_HANDLING.md)** - Reversing points on refunds
  - Automatic earn reversal on returns
  - Automatic redeem reversal on order cancellation
  - Offline refund queuing
  - Negative balance handling

- **[MANUAL_ADJUSTMENTS.md](MANUAL_ADJUSTMENTS.md)** - Manager manual balance adjustments
  - Manager-only point additions/deductions
  - Reason codes and approval workflow
  - Error correction and compensation
  - Large adjustment approval requirement

- **[EXPIRATION.md](EXPIRATION.md)** - Points expiration after 3 months
  - Automatic scheduled expiration job
  - Per-transaction expiration tracking
  - Expiration warnings (7 days before)
  - FIFO expiration of oldest points first

### Customer Self-Service
- **[BALANCE_QUERY.md](BALANCE_QUERY.md)** - Querying customer balance
  - POS card tap balance check
  - PrestaShop account balance display
  - WhatsApp balance query via "Saldo" keyword
  - Transaction history display

## Feature Dependencies

```
                    CARD_ENROLLMENT
                          │
          ┌───────────────┼───────────────┐
          │               │               │
   EARN_POINTS_POS  EARN_POINTS_ONLINE  BALANCE_QUERY
          │               │               │
          ├───────────────┼───────────────┤
          │               │               │
   REDEEM_POINTS_POS REDEEM_POINTS_ONLINE│
          │               │               │
          └───────┬───────┴───────┬───────┘
                  │               │
          REFUND_HANDLING    EXPIRATION
                  │               │
                  └───────┬───────┘
                          │
                  MANUAL_ADJUSTMENTS
```

## Key Concepts

### Transaction Types
- **Earn** - Customer earns points from purchases (positive balance change)
- **Redeem** - Customer uses points as payment (negative balance change)
- **Reversal** - Offsetting transaction for refunds (reverses earn or redeem)
- **Adjustment** - Manual manager correction (positive or negative)
- **Expiration** - Automatic points removal after 90 days (negative)

### Offline Operations
All POS features support offline operation:
- Transactions queued in local SQLite database
- Automatic sync when internet connection restored
- Conflict resolution for duplicate transactions
- Cached balance for offline redemptions (with warnings)

### Idempotency
All transactions use idempotency keys to prevent duplicates:
- Format: `{type}_{sale_id}_{card_uid}`
- Stored in backend for retention period (7-60 days)
- Prevents double-crediting from retries, multi-terminal, or sync issues

### Balance Calculation
Customer balance computed from immutable transaction ledger:
```sql
SELECT SUM(points) as balance
FROM transactions
WHERE card_uid = ? AND transaction_timestamp <= ?
```

## Integration Points

### POS Integration
- Aniwin.net sale detection (database hooks or file export)
- NFC card reader (USB, read-only UID)
- Receipt printer (points earned/redeemed display)

### PrestaShop Integration
- Custom loyalty module
- Order hooks (earn on confirmation)
- Cart rules (redeem as discount)
- Customer account page (balance display)

### External Services
- WhatsApp Business API (balance queries)
- Email service (notifications)
- Cloud backend API (all loyalty operations)

## Testing Scenarios

### Happy Paths
1. Customer enrolls → earns points → redeems points → checks balance
2. Online order → points earned → used online → refunded → points reversed
3. POS goes offline → transactions queued → internet restored → sync successful

### Edge Cases
1. Customer redeems more than earned → negative balance → refund → still negative
2. Points expire → customer tries to redeem → insufficient balance error
3. Offline transaction syncs after points already expired → immediately expired
4. Two terminals enroll same card offline → sync conflict → manager resolution

### Failure Scenarios
1. Cloud API down → transactions queue → retry after recovery
2. Database write fails → error logged → retry → manual investigation if persistent
3. NFC reader disconnects → card tap fails → reconnect → retry
4. Payment fails after redemption → automatic reversal → customer retry

## Performance Requirements

- **Balance Query**: < 500ms (95th percentile)
- **Earn Transaction**: < 1s (online), queue immediately (offline)
- **Redeem Transaction**: < 2s (online), queue with warning (offline)
- **Sync**: Process 100 queued transactions per minute
- **Expiration Job**: Process 10,000 transactions in < 5 minutes

## Security Requirements

- Manager authentication for enrollment, manual adjustments
- Idempotency protection on all transactions
- Rate limiting on balance queries and API endpoints
- Audit logging of all balance-changing operations
- GDPR compliance for customer data and consent

## Related Documentation

- **[00_meta/DOCUMENTATION_RULES.md](../00_meta/DOCUMENTATION_RULES.md)** - Documentation standards and enforcement
- **[01_project/PROJECT_OVERVIEW.md](../01_project/PROJECT_OVERVIEW.md)** - Business context and goals
- **[02_architecture/SYSTEM_ARCHITECTURE.md](../02_architecture/SYSTEM_ARCHITECTURE.md)** - Overall system design
- **[04_integrations/](../04_integrations/)** - External system integration details
- **[05_data/](../05_data/)** - Data models and database schema
- **[06_security/](../06_security/)** - Security model and considerations
- **[07_operations/](../07_operations/)** - Deployment and monitoring

## Change Log

| Date | Feature | Change | Author |
|------|---------|--------|--------|
| 2025-02-13 | All | Initial comprehensive documentation created | System |

---

**Note**: All feature documents are living documents and must be updated whenever implementation changes. See [DOCUMENTATION_RULES.md](../00_meta/DOCUMENTATION_RULES.md) for enforcement policy.
