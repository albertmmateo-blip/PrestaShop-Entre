# Feature: Card Enrollment

## Purpose

Enable customers to register for the Fidelity Points loyalty program by associating an NFC card with their personal information and marketing consent. This is the entry point for all loyalty program participation, establishing the customer's identity and enabling future points earning and redemption.

## Scope

### In Scope
- Card UID reading via NFC tap
- Customer information capture (name, email, phone, language preference)
- GDPR consent collection (loyalty terms, marketing communications)
- Card-to-customer association in cloud backend
- Duplicate card detection and rejection
- Welcome email generation
- Manual card assignment by manager
- Enrollment at POS terminal or PrestaShop account page

### Out of Scope
- Card printing or physical card creation
- Batch enrollment from customer database
- Self-service enrollment kiosk
- Mobile app enrollment
- Card replacement or reissuance (future enhancement)
- Family account linking

## Inputs

### From POS Windows Agent
```json
{
  "card_uid": "04A1B2C3D4E5F6",
  "customer_name": "María García",
  "customer_email": "maria.garcia@example.com",
  "customer_phone": "+34612345678",
  "language_preference": "es",
  "consent_loyalty": true,
  "consent_marketing": true,
  "enrollment_source": "pos",
  "terminal_id": "POS-TERMINAL-001",
  "enrolled_by": "manager_username",
  "timestamp": "2025-02-13T14:30:00Z"
}
```

### From PrestaShop Module
```json
{
  "card_uid": "04A1B2C3D4E5F6",
  "customer_id": 12345,
  "customer_email": "maria.garcia@example.com",
  "customer_name": "María García",
  "customer_phone": "+34612345678",
  "language_preference": "es",
  "consent_loyalty": true,
  "consent_marketing": true,
  "enrollment_source": "prestashop",
  "timestamp": "2025-02-13T14:30:00Z"
}
```

### Validation Rules
- `card_uid`: 14 hex characters (7 bytes), must be unique across all cards
- `customer_name`: Required, 2-100 characters, UTF-8 (Spanish/Catalan names supported)
- `customer_email`: Required, valid email format, unique per card
- `customer_phone`: Optional, E.164 format recommended, used for WhatsApp
- `language_preference`: Required, one of `["es", "ca"]`
- `consent_loyalty`: Must be `true` (cannot enroll without accepting loyalty terms)
- `consent_marketing`: Optional, defaults to `false`

## Outputs

### Success Response
```json
{
  "success": true,
  "card_uid": "04A1B2C3D4E5F6",
  "customer_id": "cust_9f8e7d6c5b4a3b2c1d0e",
  "customer_name": "María García",
  "balance": 0.00,
  "balance_display": "0 points",
  "enrollment_date": "2025-02-13T14:30:00Z",
  "card_status": "active",
  "message": "Enrollment successful. Welcome email sent."
}
```

### Failure Response - Card Already Enrolled
```json
{
  "success": false,
  "error_code": "CARD_ALREADY_ENROLLED",
  "error_message": "This card is already registered to another customer.",
  "existing_customer_name": "Juan Pérez",
  "enrollment_date": "2024-12-01T10:00:00Z",
  "resolution": "Use a different card or contact manager to reassign."
}
```

### Failure Response - Invalid Input
```json
{
  "success": false,
  "error_code": "INVALID_INPUT",
  "error_message": "Customer email is required and must be valid.",
  "validation_errors": [
    {"field": "customer_email", "error": "Invalid email format"}
  ]
}
```

### Side Effects
- New customer record created in cloud backend database
- Card UID marked as assigned in card inventory
- Welcome email queued for sending
- Audit log entry created
- WhatsApp welcome message sent (if phone provided and consent granted)

## Main Flows

### Flow 1: POS Enrollment - Happy Path

```
┌─────────┐         ┌──────────┐         ┌────────────┐         ┌──────────┐
│ Manager │         │ POS Agent│         │ Cloud API  │         │ Customer │
└────┬────┘         └────┬─────┘         └─────┬──────┘         └────┬─────┘
     │                   │                     │                      │
     │ 1. Select "New    │                     │                      │
     │    Card" option   │                     │                      │
     ├──────────────────>│                     │                      │
     │                   │                     │                      │
     │ 2. Prompt "Tap    │                     │                      │
     │    card"          │                     │                      │
     │<──────────────────┤                     │                      │
     │                   │                     │                      │
     │ 3. Tap card       │                     │                      │
     ├──────────────────>│                     │                      │
     │                   │                     │                      │
     │                   │ 4. Read UID         │                      │
     │                   ├─────────────┐       │                      │
     │                   │             │       │                      │
     │                   │<────────────┘       │                      │
     │                   │                     │                      │
     │ 5. Display form   │                     │                      │
     │    (name, email,  │                     │                      │
     │     phone, consent)│                    │                      │
     │<──────────────────┤                     │                      │
     │                   │                     │                      │
     │ 6. Enter customer │                     │                      │
     │    information    │                     │                      │
     ├──────────────────>│                     │                      │
     │                   │                     │                      │
     │                   │ 7. POST /api/v1/    │                      │
     │                   │    customers/enroll │                      │
     │                   ├────────────────────>│                      │
     │                   │                     │                      │
     │                   │                     │ 8. Validate input    │
     │                   │                     ├──────────┐           │
     │                   │                     │          │           │
     │                   │                     │<─────────┘           │
     │                   │                     │                      │
     │                   │                     │ 9. Check UID not     │
     │                   │                     │    already enrolled  │
     │                   │                     ├──────────┐           │
     │                   │                     │          │           │
     │                   │                     │<─────────┘           │
     │                   │                     │                      │
     │                   │                     │ 10. Create customer  │
     │                   │                     │     record           │
     │                   │                     ├──────────┐           │
     │                   │                     │          │           │
     │                   │                     │<─────────┘           │
     │                   │                     │                      │
     │                   │                     │ 11. Queue welcome    │
     │                   │                     │     email            │
     │                   │                     ├──────────┐           │
     │                   │                     │          │           │
     │                   │                     │<─────────┘           │
     │                   │                     │                      │
     │                   │ 12. 201 Created     │                      │
     │                   │    {customer_id, etc}│                     │
     │                   │<────────────────────┤                      │
     │                   │                     │                      │
     │ 13. Display       │                     │                      │
     │    "Welcome!"     │                     │                      │
     │    success msg    │                     │                      │
     │<──────────────────┤                     │                      │
     │                   │                     │                      │
     │                   │                     │ 14. Send welcome     │
     │                   │                     │     email            │
     │                   │                     ├─────────────────────>│
     │                   │                     │                      │
```

### Flow 2: PrestaShop Self-Enrollment

```
┌─────────┐         ┌──────────┐         ┌────────────┐         ┌──────────┐
│ Customer│         │PrestaShop│         │ Cloud API  │         │ Customer │
│ (Browser)         │  Module  │         │            │         │ (Email)  │
└────┬────┘         └────┬─────┘         └─────┬──────┘         └────┬─────┘
     │                   │                     │                      │
     │ 1. Navigate to    │                     │                      │
     │   "My Loyalty"    │                     │                      │
     ├──────────────────>│                     │                      │
     │                   │                     │                      │
     │ 2. Display        │                     │                      │
     │   "Enroll Card"   │                     │                      │
     │    button         │                     │                      │
     │<──────────────────┤                     │                      │
     │                   │                     │                      │
     │ 3. Click "Enroll  │                     │                      │
     │    Card"          │                     │                      │
     ├──────────────────>│                     │                      │
     │                   │                     │                      │
     │ 4. Show form:     │                     │                      │
     │   "Enter card #   │                     │                      │
     │    from card"     │                     │                      │
     │<──────────────────┤                     │                      │
     │                   │                     │                      │
     │ 5. Enter UID      │                     │                      │
     │   (from card)     │                     │                      │
     ├──────────────────>│                     │                      │
     │                   │                     │                      │
     │                   │ 6. POST /api/v1/    │                      │
     │                   │    customers/enroll │                      │
     │                   ├────────────────────>│                      │
     │                   │                     │                      │
     │                   │                     │ 7. Validate & create │
     │                   │                     ├──────────┐           │
     │                   │                     │          │           │
     │                   │                     │<─────────┘           │
     │                   │                     │                      │
     │                   │ 8. 201 Created      │                      │
     │                   │<────────────────────┤                      │
     │                   │                     │                      │
     │ 9. Display success│                     │                      │
     │   "Card enrolled! │                     │                      │
     │    Balance: 0"    │                     │                      │
     │<──────────────────┤                     │                      │
     │                   │                     │                      │
     │                   │                     │ 10. Send email       │
     │                   │                     ├─────────────────────>│
     │                   │                     │                      │
```

### Flow 3: Offline Enrollment (Queued)

When the POS Windows Agent has no internet connection:

1. Manager initiates enrollment as normal
2. Agent reads card UID from NFC reader
3. Agent displays enrollment form
4. Manager enters customer information
5. **Agent stores enrollment request in local SQLite queue**
6. Agent displays: "Enrollment queued. Will sync when online."
7. Customer receives temporary paper receipt with card UID
8. When internet restored, agent syncs queued enrollments
9. Cloud backend processes enrollment
10. If successful, welcome email sent (delayed)
11. If UID conflict detected, agent notifies manager to resolve

**Constraint**: Customer cannot earn/redeem points until enrollment syncs successfully.

## Edge Cases

### Edge Case 1: Card Already Enrolled to Same Email
**Scenario**: Customer tries to enroll second card with same email address

**Behavior**: 
- Backend allows this (one customer can have multiple cards)
- All cards share the same balance
- Audit log records which card was used for each transaction
- System warns manager: "Email already has 1 card. Continue?"

### Edge Case 2: Card Enrollment During Offline Mode
**Scenario**: No internet connection during enrollment

**Behavior**:
- Enrollment queued locally in SQLite
- Customer informed enrollment is pending
- Card cannot be used until sync completes
- Manager can check sync status in agent dashboard
- Failed syncs require manual resolution

### Edge Case 3: Duplicate Email Detection
**Scenario**: Customer enrolls with email already in system

**Behavior**:
- System checks if same customer (name match)
- If same customer: Link new card to existing account
- If different customer: Reject with error "Email already in use"
- Manager can override with "Force New Account" option

### Edge Case 4: Invalid Card UID
**Scenario**: NFC reader returns malformed or empty UID

**Behavior**:
- Agent validates UID format before showing form
- If invalid: "Card read error. Please try again."
- Retry up to 3 times
- After 3 failures: "Card may be damaged. Try different card."

### Edge Case 5: Consent Revocation
**Scenario**: Customer enrolled but later revokes consent

**Behavior**:
- GDPR requires deletion or anonymization
- Manager can mark account as "consent revoked"
- Card deactivated but transaction history anonymized and retained
- Customer receives confirmation email

### Edge Case 6: Manager Typo in Customer Information
**Scenario**: Manager makes mistake entering customer data

**Behavior**:
- No edit feature post-enrollment (future enhancement)
- Manager must create manual adjustment request
- IT support updates backend directly with audit trail
- Alternative: Deactivate card and re-enroll with correct information

## Failure Modes

### Failure Mode 1: Cloud API Unreachable
**Symptoms**: HTTP timeout or connection refused

**System Behavior**:
- POS agent queues enrollment locally
- User notified: "Offline mode. Enrollment will sync later."
- Agent retries sync every 5 minutes
- Success/failure shown in agent status dashboard

**Recovery**:
- Automatic when connection restored
- Manual retry button in agent UI

### Failure Mode 2: Database Write Failure
**Symptoms**: 500 Internal Server Error from API

**System Behavior**:
- Agent receives error response
- User notified: "System error. Please try again."
- Enrollment NOT queued (server-side issue, not connectivity)
- Agent logs error details for support team

**Recovery**:
- Manager retries enrollment
- If persistent, escalate to IT support
- Backend team investigates database issue

### Failure Mode 3: Email Service Unavailable
**Symptoms**: Welcome email fails to send

**System Behavior**:
- Enrollment still succeeds (email is non-critical)
- Email queued for retry
- Customer can use card immediately
- Backend retries email every 30 minutes for 24 hours

**Recovery**:
- Automatic retry until success
- If 24 hours pass, email marked as failed
- Customer can request resend via "Resend Welcome Email" in PrestaShop account

### Failure Mode 4: NFC Reader Hardware Failure
**Symptoms**: Reader not detected or not responding

**System Behavior**:
- Agent displays: "NFC reader not connected"
- Enrollment form disabled
- Manager can manually enter card UID from printed card

**Recovery**:
- Check USB connection
- Restart Windows agent
- Replace reader if hardware failure

### Failure Mode 5: UID Collision (Theoretical)
**Symptoms**: Two physically different cards read as same UID

**System Behavior**:
- Backend detects duplicate UID on enrollment
- Second enrollment rejected
- Manager investigates card source

**Recovery**:
- Verify card authenticity
- Use different card from different batch
- Report to card supplier

## Offline Behavior

### Offline Enrollment Workflow
1. **Detection**: Agent detects no internet (ping to backend fails)
2. **Queue**: Enrollment request stored in local SQLite database
   ```sql
   INSERT INTO enrollment_queue (
     card_uid, customer_name, customer_email, customer_phone,
     language_preference, consent_loyalty, consent_marketing,
     enrolled_by, queued_at, sync_status
   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending');
   ```
3. **User Feedback**: "Enrollment queued. Card will be active after sync."
4. **Temporary Receipt**: Print paper receipt with pending status
5. **Sync Attempt**: Every 5 minutes, agent attempts to sync queued enrollments
6. **Success**: Move record from queue to synced table, update status dashboard
7. **Conflict**: If UID already enrolled (by another terminal), notify manager

### Offline Constraints
- **Card Unusable**: Customer cannot earn/redeem until enrollment syncs
- **No Balance Query**: Card UID not yet in backend, so balance query fails
- **Manager Visibility**: Agent shows count of pending enrollments in status bar
- **Sync Order**: Enrollments synced in FIFO order (oldest first)

### Sync Conflict Resolution
**Scenario**: Two terminals enroll same UID while both offline

**Resolution**:
1. First sync succeeds (creates customer)
2. Second sync fails with "CARD_ALREADY_ENROLLED"
3. Agent notifies manager of conflict
4. Manager must resolve:
   - Option A: Accept existing enrollment, discard local
   - Option B: Override (deactivate first enrollment, use second)
5. Decision logged in audit trail

## Security Considerations

### Data Protection
- **PII Encryption**: Customer name, email, phone encrypted at rest in cloud database
- **Transport Security**: All API calls use HTTPS (TLS 1.2+)
- **Local Storage**: Queued enrollments in SQLite with Windows file system encryption (BitLocker recommended)
- **GDPR Compliance**: Consent timestamp and source recorded, supports right to erasure

### Authentication & Authorization
- **POS Enrollment**: Requires manager login to Windows agent (Windows user authentication)
- **PrestaShop Enrollment**: Requires logged-in customer (PrestaShop session)
- **API Security**: Backend validates API key in request header
- **No PIN**: Enrollment does not require customer PIN (intentional simplification)

### Audit Trail
Every enrollment creates audit log entry:
```json
{
  "event_type": "CARD_ENROLLMENT",
  "timestamp": "2025-02-13T14:30:00Z",
  "card_uid": "04A1B2C3D4E5F6",
  "customer_id": "cust_9f8e7d6c5b4a3b2c1d0e",
  "enrolled_by": "manager_username",
  "source": "pos",
  "terminal_id": "POS-TERMINAL-001",
  "consent_loyalty": true,
  "consent_marketing": false,
  "ip_address": "192.168.1.100"
}
```

### Fraud Mitigation
- **Rate Limiting**: Max 20 enrollments per terminal per hour (prevents bulk fraud)
- **UID Uniqueness**: Enforced at database level (unique constraint)
- **Email Verification**: Optional email verification link (future enhancement)
- **Manager Approval**: Only authorized managers can enroll cards at POS

## Related Documents

### Dependencies
- `02_architecture/WINDOWS_AGENT.md` - POS agent handling enrollment
- `02_architecture/CLOUD_BACKEND.md` - Backend API processing enrollments
- `04_integrations/NFC_READER.md` - Card UID reading
- `05_data/CUSTOMER.md` - Customer data model
- `05_data/CARD.md` - Card data model
- `06_security/SECURITY_MODEL.md` - Overall security approach
- `06_security/GDPR_COMPLIANCE.md` - Consent and data protection

### Related Features
- `03_features/BALANCE_QUERY.md` - Querying balance after enrollment
- `03_features/EARN_POINTS_POS.md` - Using card after enrollment
- `03_features/EARN_POINTS_ONLINE.md` - Linking PrestaShop account

### Integration Points
- `04_integrations/PRESTASHOP_MODULE.md` - PrestaShop enrollment flow
- `04_integrations/EMAIL_SERVICE.md` - Welcome email sending
- `04_integrations/WHATSAPP_API.md` - WhatsApp welcome message

## Open Questions / TODOs

### TODO: Email Verification
**Status**: Not implemented in MVP  
**Required by**: Phase 2 (Post-MVP)  
**Description**: Send verification link in welcome email to confirm customer email address is valid and owned by customer.

### TODO: Card Replacement Flow
**Status**: Designed but not implemented  
**Required by**: Phase 2  
**Description**: Allow customer to replace lost/damaged card while retaining existing balance. Requires deactivating old UID and activating new UID with same customer_id.

### TODO: Bulk Enrollment Import
**Status**: Future enhancement  
**Required by**: If migrating from existing loyalty system  
**Description**: CSV upload to enroll many customers at once from existing database.

### Open Question: Multi-Language Support
**Question**: Should enrollment form support English in addition to Spanish/Catalan?  
**Context**: Some tourists may want to enroll  
**Impact**: UI translation, email templates in English  
**Decision Required By**: Before international marketing campaigns

### Open Question: Age Restrictions
**Question**: Should there be minimum age for enrollment (e.g., 18+)?  
**Context**: GDPR consent requirements differ for minors  
**Impact**: Age field in enrollment form, consent validation  
**Decision Required By**: Legal review before launch
