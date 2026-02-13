# Project Overview: Fidelity Points Loyalty System

## Project Description

The Fidelity Points system is a comprehensive loyalty solution designed for a retail business operating both a physical store and an e-commerce platform. The system enables customers to earn and redeem loyalty points across both channels using NFC-enabled physical cards.

This is a production-ready system designed for real-world retail deployment, not a theoretical exercise.

## Business Goals

### Primary Goals

1. **Increase Customer Retention** - Incentivize repeat purchases through a points-based loyalty program
2. **Unified Customer Experience** - Provide seamless loyalty experience across physical and online channels
3. **Offline Reliability** - Ensure loyalty operations continue even when internet connectivity is unavailable
4. **Operational Simplicity** - Minimize training requirements for staff with simple, fast card-tap operations

### Secondary Goals

1. **Customer Engagement** - Enable WhatsApp-based balance queries to increase awareness
2. **Data Collection** - Capture customer contact information and consent for marketing
3. **Audit Compliance** - Maintain complete audit trail of all loyalty transactions
4. **Scalability** - Support future expansion to multiple terminals and additional stores

## Non-Goals

Explicitly out of scope:

1. **Complex Role-Based Access Control** - No cashier-level permission system required
2. **PIN-Based Security** - No PIN or password verification at point of redemption
3. **Fraud Prevention System** - No sophisticated anti-fraud mechanisms (acceptable risk for this business context)
4. **Partial Refunds** - Only full order refunds are supported
5. **Multi-Currency** - Single currency only (EUR)
6. **Card Balance Storage** - No value stored on card; cards are identification only
7. **Real-Time Inventory Sync** - Stock sync is one-way (POS → PrestaShop) and near-real-time, not instantaneous
8. **Mobile POS** - Physical terminal only; mobile devices for NFC reading only

## Operating Constraints

### Physical Store Environment

- **POS System**: Aniwin.net (existing, cannot be replaced)
- **Operating System**: Windows terminals
- **Terminals**: Currently 1, must support multiple in future
- **Connectivity**: Internet may be unavailable → offline mode is mandatory
- **Hardware Budget**: Maximum 1000 EUR
- **Languages**: Spanish and Catalan for POS UI

### E-Commerce Environment

- **Platform**: PrestaShop 9.1.0 (must not modify core)
- **Integration Method**: Custom module communicating with external loyalty backend via REST API
- **Connectivity**: Always online (no offline requirement for e-commerce)

### Technical Constraints

1. **No Direct POS Integration** - Aniwin.net has no plugin/API; must use database hooks, file exports, or receipt intercept
2. **Offline-First POS** - Physical store must continue operations without internet
3. **Audit Trail** - All transactions must be logged immutably for compliance
4. **Idempotency** - No duplicate points awards or redemptions (critical constraint)
5. **Data Backup** - All loyalty data must be backed up off-site
6. **Sync Safety** - Delayed sync between POS and PrestaShop must not cause data loss or inconsistency

## Explicit Scope Boundaries

### In Scope

**Customer Management**
- Card issuance and assignment to customers
- Customer enrollment with contact information
- GDPR consent capture (loyalty vs marketing)
- Customer balance queries

**Points Operations**
- Earn points on purchases (physical and online)
- Redeem points on purchases (physical and online)
- Reverse points on full refunds
- Manual balance adjustments by managers
- Points expiration (3-month rolling window)

**Integration Points**
- Aniwin.net POS integration (read sales data)
- PrestaShop module (earn/redeem/refund online)
- USB NFC reader integration (card tap)
- WhatsApp messaging (balance queries)
- Email notifications (receipts, balance updates)

**Offline Operations**
- Queue transactions when offline
- Sync transactions when connection restored
- Detect and resolve sync conflicts
- Inform operator of sync status and errors

**Data and Audit**
- Immutable ledger of all transactions
- Balance computation from ledger
- Audit log of all operations
- Order mapping between POS and PrestaShop

### Out of Scope

**Advanced Features**
- Tiered loyalty programs (VIP levels)
- Points transfer between customers
- Points gifting
- Partner integrations (other stores, airlines, etc.)
- Gamification or challenges
- Social media integration
- Mobile app for customers

**Complex Security**
- Multi-factor authentication
- Role-based access control
- Cashier fraud detection
- Cloning prevention beyond basic mitigation
- Real-time fraud alerts

**Advanced Operations**
- Partial refund handling
- Split payments with multiple cards
- Family accounts or shared balances
- Merchant network or coalition loyalty

## Loyalty Business Rules

### Earn Rate
- **Rate**: 0.015 EUR credited per 1 EUR spent
- **Display**: 1 EUR spent = 150 points (1 point = 0.0001 EUR)
- **Application**: Points earned on all items, including discounted items
- **Timing**: Points awarded after sale is completed

### Redemption Rules
- **Minimum**: No minimum redemption amount
- **Maximum**: Up to 100% of order value
- **Partial Payment**: Can combine points + cash/card
- **Application**: Applied as discount at POS, as cart rule/voucher in PrestaShop

### Expiration
- **Period**: Points expire 3 months after earning
- **Calculation**: Rolling expiration per transaction
- **Processing**: Automated nightly job to expire old points
- **Notification**: Customers notified before expiration (future enhancement)

### Refunds
- **Type**: Full refund only
- **Effect**: Points automatically reversed for the refunded order
- **Timing**: Immediate reversal upon refund processing

### Adjustments
- **Authorization**: Manager only (no PIN required)
- **Types**: Add points, remove points, correct errors
- **Audit**: All adjustments logged with reason code

## Card Specifications

### Physical Card
- **Type**: NFC contactless card (credit card size, ISO/IEC 14443 Type A)
- **Technology**: UID-only cards (MIFARE Classic or compatible)
- **Printed Information**: Customer name, card number, date of issue
- **Optional**: QR code for mobile scanning (future enhancement)

### Card Security Model
- **Acceptable Risk**: UID cloning is acknowledged risk
- **Justification**: Low-value transactions, no high-risk fraud expected
- **Mitigation**: Basic unusual activity detection (future enhancement)

## Customer Communication Channels

### Receipt
- Points earned this transaction
- Points redeemed this transaction
- Current balance after transaction
- Points expiring soon (future enhancement)

### Email
- Welcome email with card number
- Transaction confirmations
- Balance updates on request
- Points expiring soon (future enhancement)

### WhatsApp
- Balance query via keyword "Saldo"
- Transaction notifications (optional, future enhancement)

### Web Portal
- Customer login to view balance and transaction history (future enhancement for MVP)

## Success Criteria

The system is successful when:

1. **Offline Operations Work** - POS can earn/redeem points with no internet for at least 1 full business day
2. **Sync is Reliable** - All offline transactions sync correctly when connection restored, with no duplicates
3. **Performance is Fast** - Card tap to balance display < 2 seconds
4. **Error Rate is Low** - < 1% transaction failure rate
5. **Customer Adoption** - > 50% of customers enroll in loyalty program within 6 months
6. **Staff Acceptance** - Staff can complete loyalty transaction with < 5 seconds added to checkout time

## Known Limitations

1. **POS Integration Complexity** - No native API requires custom integration approach
2. **UID-Only Cards** - Cloneable cards are acceptable risk for this business
3. **Full Refunds Only** - Partial refunds require manual adjustment
4. **Single Currency** - No multi-currency support
5. **Windows Only** - Local agent requires Windows; no Mac/Linux support
6. **Internet Dependency** - E-commerce channel requires online backend (no offline PrestaShop)

## Stakeholders

- **Store Owner** - Final decision authority, budget holder
- **Store Manager** - Daily operations, staff training
- **Cashiers** - Primary system users at POS
- **Customers** - Card holders, system beneficiaries
- **IT Support** - System maintenance, troubleshooting
- **Compliance** - GDPR compliance, audit requirements

## Related Documents

### Critical Dependencies
- `01_project/IMPLEMENTATION_PLAN.md` - Current project status and timeline
- `02_architecture/SYSTEM_ARCHITECTURE.md` - Overall system design
- `06_security/SECURITY_MODEL.md` - Security assumptions and constraints

### Feature Documentation
- All files in `03_features/` - Detailed feature descriptions

### Integration Documentation
- All files in `04_integrations/` - External system integration details

### Data Model
- All files in `05_data/` - Data structures and relationships
