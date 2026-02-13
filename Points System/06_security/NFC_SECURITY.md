# NFC Security: Loyalty Cards

## Purpose

Document the security model for NFC-based loyalty cards, explicitly covering the UID-only approach, cloning risks, acceptable risk justification, detection mechanisms, physical security, and card lifecycle management.

## Scope

### In Scope
- NFC card technology and limitations
- UID-only identification approach (no encryption)
- Card cloning threat model
- Risk acceptance justification
- Basic fraud detection mitigations
- Physical security of cards
- Card enrollment and replacement procedures
- Future security enhancements (anomaly detection)

### Out of Scope
- Overall system security model (see `SECURITY_MODEL.md`)
- API authentication (see `AUTHENTICATION.md`)
- POS terminal security (see `02_architecture/WINDOWS_AGENT.md`)
- Backend security controls (see `02_architecture/CLOUD_BACKEND.md`)

## NFC Technology Overview

### Card Type: MIFARE Classic / NTAG Compatible
- **Technology**: ISO/IEC 14443 Type A
- **Frequency**: 13.56 MHz
- **Read Range**: 1-4 cm (typical)
- **Cost**: ~€0.50 per card (bulk purchase)
- **Lifespan**: 3-5 years (normal use)

### UID (Unique Identifier)
- **Length**: 7 bytes (14 hex characters)
- **Format**: `04:A1:B2:C3:D4:E5:F6`
- **Uniqueness**: Factory-programmed, globally unique
- **Writability**: **UID is read-only on genuine cards**
- **Clonability**: **UID can be cloned to writable "magic" cards**

### Data Storage (Not Used)
- **Capacity**: 1 KB user memory (MIFARE Classic)
- **Security**: Crypto1 cipher (weak, broken in 2008)
- **Our Approach**: **We do NOT store any data on the card**
- **Rationale**: Avoid encryption complexity, prevent on-card tampering

## UID-Only Security Model

### How It Works
1. Customer enrolls: NFC card UID linked to PrestaShop customer account
2. Card tap: POS reader reads 7-byte UID
3. Cloud lookup: UID sent to API, returns customer balance
4. Transaction: Earn or redeem points associated with that UID
5. No data on card: Card is merely an identifier, like a barcode

### Comparison to Alternatives

| Approach | Complexity | Cost | Security | Our Choice |
|----------|-----------|------|----------|------------|
| UID-only | Low | Low | Low | ✅ **YES** |
| Encrypted chip | High | High | High | ❌ No (overkill) |
| Signed data on card | Medium | Medium | Medium | ❌ No (unnecessary) |
| Mobile app (NFC emulation) | High | Low | High | ❌ Future phase |

### Why UID-Only?
- **Simplicity**: No cryptographic implementation needed
- **Cost**: Standard NFC cards, not secure elements
- **User Experience**: Fast tap, no PIN entry
- **Risk Tolerance**: Low-value balances (average 20 EUR)
- **Mitigation Strategy**: Anomaly detection, velocity limits, audit trail

## Threat Model: Card Cloning

### Attack: UID Cloning
**Description**: Attacker copies UID from legitimate card to "magic card" (rewritable UID)

**Equipment Needed**:
- NFC reader/writer (e.g., Proxmark3, PN532, ACR122U) - €50-€300
- "Magic card" with rewritable UID - €1-€5 per card
- Software: LibNFC, Proxmark3 client, or mobile app

**Attack Steps**:
1. Attacker obtains legitimate loyalty card (borrow, steal, or clone own card)
2. Read UID using NFC reader (takes 1 second)
3. Write UID to magic card
4. Attacker now has duplicate card with same identity

**Outcome**:
- Both cards have identical UID
- Both cards access the same customer balance
- System cannot distinguish original from clone

### Risk Assessment

#### Financial Impact
- **Per-incident**: Maximum loss = customer's current balance (typically 10-30 EUR)
- **Frequency**: Low (requires technical knowledge and equipment)
- **Annual exposure**: Estimated < 0.1% of customers (< €500 total loss)

#### Likelihood
- **Low**: Most customers lack technical skills and equipment
- **Medium**: Technically savvy customers could clone easily
- **High**: Organized fraud unlikely (low payoff relative to effort)

#### Business Impact
- **Customer Trust**: Low (customer can report, card replaced)
- **Financial Loss**: Negligible (average balance €20)
- **Operational**: Minimal (dispute resolution process exists)

### Risk Acceptance Justification

**WE ACCEPT THE RISK OF UID CLONING**

**Reasons**:
1. **Low Financial Impact**: Average balance €20, maximum realistic loss €50 per incident
2. **Detection Possible**: Anomaly detection flags suspicious patterns
3. **Customer Service Recovery**: Disputes resolved quickly, customer satisfaction maintained
4. **Cost-Benefit**: Implementing secure cards would cost €5-€10 per card + complexity
5. **Alternative Mitigation**: Velocity limits prevent large-scale abuse

**Approved By**: [Management/Security Officer]  
**Date**: 2025-02-15  
**Review Date**: 2025-08-15 (6 months)

## Attack Scenarios and Mitigations

### Scenario 1: Customer Clones Own Card
**Attack**: Customer clones card, uses both cards simultaneously at different terminals

**Example**:
- Customer has 50 EUR balance
- Clones card at home
- Goes to Store A with original card, redeems 30 EUR
- Friend goes to Store B with cloned card, redeems 30 EUR
- Total redeemed: 60 EUR (overdrawn by 10 EUR)

**Mitigations**:
- **Row-level locking**: If both redemptions happen online, second one fails (insufficient balance)
- **Offline risk**: If one or both terminals offline, both may succeed temporarily
- **Sync conflict resolution**: When synced, system detects overdraft
- **Negative balance prevention**: Balance goes negative, flagged for review
- **Velocity limit**: Max 3 redemptions per day per card
- **Anomaly detection**: Two simultaneous redemptions from distant locations flagged

**Resolution**:
- Manager reviews case
- Customer contacted: "Unusual activity detected"
- If fraud confirmed: account suspended, balance correction
- If legitimate (e.g., card lent to family): customer warned, no penalty

**Residual Risk**: Customer may redeem up to 2x balance if both terminals offline

---

### Scenario 2: Stolen Card Cloned Before Cancellation
**Attack**: Thief steals card, clones it, returns original without customer noticing

**Example**:
- Thief steals card from customer's wallet
- Clones UID within 5 minutes
- Returns card to wallet (customer doesn't notice)
- Thief uses cloned card to redeem points

**Mitigations**:
- **Limited opportunity**: Thief must return card quickly (requires physical access)
- **Balance limit**: Maximum loss = customer's balance at theft time
- **Customer monitoring**: Customer notices unexpected redemptions (email notifications)
- **Dispute process**: Customer reports, cloned redemptions reviewed and reversed
- **Card replacement**: New card issued, old UID deactivated

**Resolution**:
- Customer reports: "I didn't make this redemption"
- Manager reviews transaction: location, time, terminal
- If fraud confirmed: transaction reversed, points restored, card replaced
- Customer receives new card with new UID

**Residual Risk**: Up to 48 hours before customer notices and reports

---

### Scenario 3: Employee Clones Customer Cards
**Attack**: Dishonest employee clones high-balance customer cards

**Example**:
- Cashier sees customer with 100 EUR balance
- Covertly reads UID during transaction (using personal NFC reader)
- Later, creates clone and redeems points for self

**Mitigations**:
- **Audit trail**: All redemptions logged with terminal ID and cashier ID
- **Pattern detection**: Flag if employee has unusually high redemptions at own register
- **Employee cards monitored**: Employees cannot redeem on cards they processed
- **Manager review**: Weekly report of employee loyalty transactions
- **Surveillance**: Store CCTV can correlate suspicious transactions

**Resolution**:
- Automated alert: "Employee cashier_ana redeemed 100 EUR on own account"
- Manager investigates transaction history
- If fraud confirmed: employee terminated, police report, restitution

**Residual Risk**: Sophisticated employee may use accomplice to avoid detection

---

### Scenario 4: Mass Cloning at Event
**Attack**: Attacker brings NFC reader to crowded event, clones multiple cards remotely

**Feasibility**: **LOW**
- NFC read range: 1-4 cm (must be very close)
- Wallet shielding: Most wallets naturally shield NFC (metal clips, other cards)
- Success rate: < 10% in crowded environment

**Mitigations**:
- **Limited success**: Most cards in wallets are not readable from distance
- **Balance limit**: Each cloned card limited to current balance
- **Velocity limits**: Attacker can't redeem all cards quickly (rate limits)
- **Anomaly detection**: Surge of redemptions from newly cloned cards triggers alert

**Residual Risk**: Theoretical attack, very low probability

---

### Scenario 5: UID Collision (Accidental Duplicate)
**Attack**: Not an attack, but two cards randomly have same UID

**Probability**: **NEGLIGIBLE**
- UID space: 2^56 (72 quadrillion possible UIDs)
- Cards issued: ~10,000
- Birthday paradox: Collision probability ≈ 0.0000000000001%

**Mitigation**:
- Enrollment validation: If UID already enrolled, error shown
- Customer prompted to request replacement card

**Resolution**: Extremely unlikely to occur in practice

## Detection Mechanisms

### Anomaly Detection (Future Enhancement)

#### Rule 1: Simultaneous Redemptions
**Trigger**: Two redemptions from same UID within 5 minutes at different terminals

**Logic**:
```
IF redemption_1.card_uid == redemption_2.card_uid
   AND redemption_1.timestamp - redemption_2.timestamp < 5 minutes
   AND redemption_1.terminal_id != redemption_2.terminal_id
   AND distance(redemption_1.terminal, redemption_2.terminal) > 1 km
THEN flag = "simultaneous_redemption_alert"
```

**Action**:
- Automated alert to manager
- Both transactions marked "under review"
- Customer contacted: "Unusual activity detected on your loyalty account"

#### Rule 2: Velocity Limit Exceeded
**Trigger**: More than 3 redemptions in 24 hours

**Logic**:
```
IF count(redemptions WHERE card_uid = X AND timestamp > now - 24h) > 3
THEN reject_redemption
     return "Velocity limit exceeded. Contact customer service."
```

**Action**:
- Redemption blocked
- Customer must contact store to resolve

#### Rule 3: Geographically Impossible Redemption
**Trigger**: Card used in two distant locations within short time

**Logic**:
```
IF distance(redemption_1.terminal, redemption_2.terminal) > 100 km
   AND redemption_2.timestamp - redemption_1.timestamp < 1 hour
THEN flag = "impossible_travel_alert"
```

**Example**:
- 10:00 AM: Redemption in Madrid
- 10:30 AM: Redemption in Barcelona (600 km away)
- Alert: "Impossible travel detected"

**Action**:
- Second redemption flagged for review
- Customer contacted

#### Rule 4: High-Value Redemption After Long Inactivity
**Trigger**: Large redemption after months of inactivity

**Logic**:
```
IF redemption.amount > 50 EUR
   AND last_activity_date < now - 90 days
THEN flag = "dormant_account_alert"
```

**Rationale**: Cloned card may be used after long period

**Action**:
- Redemption allowed but flagged
- Manager notified for follow-up

### Manual Review Process
1. Automated alert generated
2. Manager reviews transaction details
3. Manager calls customer: "We noticed unusual activity..."
4. If fraud confirmed:
   - Reverse fraudulent transaction
   - Issue new card
   - Investigate: employee involvement?
5. If legitimate:
   - Clear alert
   - Update customer profile (note: "Lends card to family")

## Physical Security

### Card Distribution
- **Enrollment**: Customer receives card at store enrollment desk
- **Initial Balance**: 0 EUR (customer earns points via purchases)
- **No Activation**: Card active immediately upon enrollment

### Card Storage (Customer)
- **Recommendation**: Store in wallet like credit card
- **Protection**: No special protection needed (UID not secret)
- **Loss Prevention**: Customer responsible for safekeeping

### Card Replacement

#### Scenario 1: Lost Card
**Process**:
1. Customer reports: "I lost my loyalty card"
2. Store staff deactivates old UID
3. New card issued with new UID
4. Balance transferred to new card
5. Old card cannot be used (deactivated)

**Cost**: Free replacement (customer service)

#### Scenario 2: Suspected Cloning
**Process**:
1. Customer reports: "Someone is using my points"
2. Manager reviews transaction history
3. If fraud confirmed:
   - Reverse fraudulent transactions
   - Deactivate old UID immediately
   - Issue new card
   - Balance restored
4. If not fraud (e.g., family member):
   - Explain to customer
   - No replacement needed

**Cost**: Free replacement if fraud confirmed

#### Scenario 3: Damaged Card
**Process**:
1. Customer presents damaged card (not readable)
2. If UID still readable: balance lookup, new card issued
3. If UID not readable: customer provides PrestaShop account email
4. Staff lookup customer, verify identity, issue new card
5. Balance transferred

**Cost**: Free replacement

### Card Deactivation
- **Method**: UID added to deactivation list in database
- **Effect**: API rejects all transactions for that UID
- **Response**: "Card deactivated. Please contact customer service."
- **Reactivation**: Possible if customer found lost card (manager approval)

## No Encryption on Card - Design Decision

### Why No Encryption?

#### Alternative 1: Store Encrypted Balance on Card
**Rejected Reasons**:
- **Complexity**: Requires cryptographic key management on every POS terminal
- **Key Distribution**: How to securely distribute keys to 50+ terminals?
- **Key Rotation**: What happens when key rotated? Re-encrypt all cards?
- **Offline Sync**: If balance on card differs from cloud, which is authoritative?
- **Card Damage**: If card corrupted, customer loses balance permanently

#### Alternative 2: Challenge-Response Authentication
**Rejected Reasons**:
- **Requires Secure Element**: Need expensive cards (€5-€10 each)
- **NFC Protocol**: Must implement ISO/IEC 7816 smart card protocol
- **User Experience**: Slower transaction (2-3 seconds vs. instant)
- **Cost**: 10x card cost for minimal security benefit

#### Alternative 3: Digital Signatures on Card
**Rejected Reasons**:
- **Write Operations**: Each transaction must write to card (slower, wears out card)
- **Offline Conflicts**: Signature on card may differ from cloud state
- **Key Management**: Still need cryptographic key distribution

### Our Design: Cloud-Authoritative Balance
- **Card**: Only stores UID (read-only identifier)
- **Cloud**: Stores actual balance, transaction history
- **POS**: Reads UID, queries cloud for balance
- **Benefit**: Simple, reliable, no crypto key management
- **Trade-off**: UID cloning possible (accepted risk)

## Card Lifecycle Management

### Enrollment
1. Customer requests loyalty card at checkout or customer service
2. Staff scans new card, reads UID
3. UID linked to customer's PrestaShop account
4. Card activated (balance = 0)
5. Customer receives card and welcome info

### Active Use
- Customer taps card at POS for earn and redeem transactions
- Balance tracked server-side
- No maintenance required

### Deactivation
**Triggers**:
- Customer requests card deactivation (lost, stolen)
- Fraud detected (cloned card suspected)
- Customer closes PrestaShop account (right to be forgotten)

**Process**:
1. UID added to deactivation table
2. All future transactions rejected
3. Balance preserved (can be transferred to new card)

### Reactivation
**Triggers**:
- Customer found lost card
- False positive fraud alert (customer requests reinstatement)

**Process**:
1. Manager approves reactivation
2. UID removed from deactivation table
3. Card functional again

### Card Expiration
**Policy**: Cards do NOT expire
- No expiration date on card
- UID remains valid indefinitely
- Customer can use same card for years

**Rationale**: Simplicity, customer convenience

### Bulk Deactivation
**Scenario**: Security incident (e.g., database breach, mass cloning detected)

**Process**:
1. Emergency response team activated
2. All UIDs deactivated immediately (API returns 403 for all cards)
3. Customers notified via email: "We are issuing new loyalty cards for security"
4. Customers visit store to receive new card (balance transferred)
5. Old UIDs permanently deactivated

## Future Security Enhancements

### Phase 2: Mobile App with Secure Element
**Description**: Customers use mobile app instead of physical card

**Benefits**:
- Secure element on phone (hardware-backed crypto)
- Dynamic authentication (challenge-response)
- Biometric authentication (fingerprint, Face ID)
- No physical card to clone

**Challenges**:
- User adoption (must download app)
- Older customers prefer physical cards
- NFC support required (not all phones)

**Timeline**: Phase 2 (6-12 months)

### Phase 3: Anomaly Detection Machine Learning
**Description**: ML model detects unusual transaction patterns

**Features**:
- Learns normal customer behavior
- Flags outliers (e.g., sudden large redemption)
- Adapts to individual customer patterns

**Timeline**: Phase 3 (12+ months)

### Phase 4: Blockchain Audit Trail
**Description**: Immutable transaction ledger

**Benefits**:
- Tamper-proof audit trail
- Distributed trust

**Challenges**:
- Complexity
- Cost
- Questionable benefit for centralized system

**Timeline**: Research phase (may not implement)

## Physical Security Recommendations for Stores

### POS Terminals
- Secure POS terminals to counter (prevent theft)
- Restrict physical access to employee-only areas
- BitLocker encryption on Windows terminals (recommended)

### NFC Readers
- Use USB NFC readers securely mounted
- No special security needed (readers contain no secrets)
- Replacement readers can be provisioned easily

### Customer Service Desk
- Train staff on card replacement procedures
- Verify customer identity before issuing replacement (email or ID)
- Keep supply of blank NFC cards (100-200 cards)

### Surveillance
- CCTV cameras at POS terminals (recommended)
- Recordings retained 30 days
- Used for fraud investigation

## Related Documents

### Dependencies
- `06_security/SECURITY_MODEL.md` - Overall security architecture
- `02_architecture/WINDOWS_AGENT.md` - NFC reader integration
- `05_data/CUSTOMER.md` - Customer enrollment and UID linking

### Related Features
- `03_features/ENROLLMENT.md` - Card enrollment process
- `03_features/CARD_REPLACEMENT.md` - Lost/stolen card handling

### Security Details
- `06_security/AUTHENTICATION.md` - API security (not card security)
- `06_security/IDEMPOTENCY.md` - Duplicate transaction prevention

## Open Questions / TODOs

### TODO: Anomaly Detection Implementation
**Status**: Not implemented  
**Required by**: Phase 2  
**Description**: Build rule-based anomaly detection system for suspicious card usage

### TODO: Card Inventory Management
**Status**: Needs process definition  
**Required by**: Launch  
**Description**: How do stores order new blank cards? Min/max inventory levels?

### TODO: Fraud Investigation Playbook
**Status**: Draft needed  
**Required by**: Launch  
**Description**: Step-by-step guide for managers investigating suspected cloning

### Open Question: Card Expiration Policy
**Question**: Should cards expire after X years of inactivity?  
**Context**: Prevent zombie accounts, reclaim UIDs  
**Impact**: Customer experience, database cleanup  
**Decision Required By**: Before launch

### Open Question: Card Personalization
**Question**: Should cards be printed with customer name?  
**Context**: Reduces theft (card personalized), but increases cost/complexity  
**Impact**: Card printing process, cost (+€0.50/card), enrollment time (+2 minutes)  
**Decision Required By**: Before launch

### Open Question: UID Collision Handling
**Question**: What happens if UID collision detected during enrollment?  
**Context**: Astronomically unlikely, but should have process  
**Impact**: Enrollment error handling  
**Decision Required By**: Before launch (edge case documentation)
