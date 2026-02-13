# Build Sequence: Complete Project Implementation Guide

## Purpose

This document provides a comprehensive, ordered sequence of prompts for building the Fidelity Points loyalty system from scratch. Each prompt is designed to be **copy-and-paste ready** and includes all necessary context, documentation references, and acceptance criteria.

**Use this guide to build the project in an orderly, systematic manner.**

## How to Use This Guide

1. **Follow the sequence** - Each phase builds on the previous one
2. **Copy the entire prompt** - Each prompt block contains everything needed for that step
3. **Complete each step fully** - Don't move to the next step until current one is validated
4. **Update documentation** - Document as you go, following the workflow in AGENT_WORKFLOW.md
5. **Track progress** - Check off each step as completed

## Prerequisites

Before starting, ensure you have read:
- [ ] `00_meta/SESSION_START.md` - Session start checklist
- [ ] `00_meta/DOCUMENTATION_RULES.md` - Documentation rules
- [ ] `01_project/PROJECT_OVERVIEW.md` - Complete project overview
- [ ] `01_project/IMPLEMENTATION_PLAN.md` - Implementation plan and current status
- [ ] `08_prompts/AGENT_WORKFLOW.md` - Required workflow for all work

---

# PHASE 1: PROJECT FOUNDATION

## Step 1.1: Environment Setup and Repository Configuration

```
I am setting up the development environment for the Fidelity Points loyalty system.

Before I begin, I have read:
- 01_project/PROJECT_OVERVIEW.md - Project scope and constraints
- 01_project/IMPLEMENTATION_PLAN.md - Implementation plan
- 02_architecture/SYSTEM_ARCHITECTURE.md - Overall system architecture

Task:
1. Set up development environment (Docker, database, development tools)
2. Configure version control and branching strategy
3. Set up CI/CD pipeline basics
4. Configure code quality tools (linters, formatters)
5. Create development database schema from DATA_MODEL.md
6. Set up test database for integration testing
7. Configure environment variables and secrets management
8. Document environment setup process
9. Create README with setup instructions
10. Verify all team members can replicate the setup

Deliverables:
- [ ] Development environment running locally
- [ ] Database migrations executable
- [ ] CI/CD pipeline executing basic checks
- [ ] Environment setup documented
- [ ] All secrets properly managed (not in code)

Testing checklist:
- [ ] Fresh clone works on new machine
- [ ] Database migrations run successfully
- [ ] Development server starts without errors
- [ ] All required services are accessible
- [ ] Environment variables properly loaded
```

## Step 1.2: Data Model Implementation

```
I am implementing the core data model for the Fidelity Points loyalty system.

Before I begin, I have read:
- 05_data/DATA_MODEL.md - Complete data model specification
- 05_data/LOYALTY_LEDGER.md - Ledger append-only requirements
- 05_data/CUSTOMER_MODEL.md - Customer entity specification
- 05_data/CARD_MODEL.md - Card entity specification
- 05_data/CONSENT_RECORDS.md - Consent tracking requirements
- 05_data/ORDER_MAPPING.md - Order mapping requirements

Task:
1. Create database schema for all core entities
2. Implement ledger table with append-only constraints
3. Create customer table with contact information fields
4. Create card table with UID and assignment tracking
5. Create consent records table for GDPR compliance
6. Create order mapping table for POS/PrestaShop sync
7. Add all necessary indexes for performance
8. Add all foreign key constraints
9. Create database migration scripts
10. Test migrations on sample data
11. Create rollback scripts
12. Document all tables, columns, and relationships

Deliverables:
- [ ] All tables created with proper constraints
- [ ] Ledger immutability enforced at database level
- [ ] Migration scripts tested and documented
- [ ] Rollback scripts tested
- [ ] All relationships properly defined
- [ ] Indexes optimized for query patterns

Testing checklist:
- [ ] Migration applies cleanly
- [ ] Rollback restores previous state
- [ ] Cannot modify ledger entries (constraint enforced)
- [ ] Foreign key constraints work correctly
- [ ] Indexes improve query performance
- [ ] Sample data loads successfully
```

---

# PHASE 2: BACKEND FOUNDATION

## Step 2.1: Backend API Structure and Authentication

```
I am implementing the backend API structure and authentication for the Fidelity Points loyalty system.

Before I begin, I have read:
- 02_architecture/CLOUD_BACKEND.md - Backend architecture and API contracts
- 06_security/SECURITY_MODEL.md - Overall security model
- 06_security/AUTHENTICATION.md - Authentication requirements
- 06_security/IDEMPOTENCY.md - Idempotency requirements
- 05_data/DATA_MODEL.md - Database schema

Task:
1. Set up REST API framework (Express/FastAPI/equivalent)
2. Implement authentication middleware (API keys, JWT, or similar)
3. Implement authorization checks (basic role validation)
4. Create idempotency middleware (check and store idempotency keys)
5. Add request logging middleware
6. Add error handling middleware
7. Create health check endpoint
8. Create API documentation structure (OpenAPI/Swagger)
9. Implement rate limiting
10. Add security headers (CORS, CSP, etc.)
11. Write integration tests for authentication
12. Document all API endpoints in CLOUD_BACKEND.md

Deliverables:
- [ ] API framework configured and running
- [ ] Authentication working and tested
- [ ] Idempotency middleware functioning
- [ ] API documentation auto-generated
- [ ] Security headers properly configured
- [ ] Error responses standardized

Testing checklist:
- [ ] Authenticated requests succeed
- [ ] Unauthenticated requests rejected
- [ ] Idempotency keys prevent duplicates
- [ ] Rate limiting works correctly
- [ ] Error responses don't leak sensitive info
- [ ] CORS configured correctly
```

## Step 2.2: Core Loyalty Transaction Endpoints

```
I am implementing core loyalty transaction endpoints for the Fidelity Points loyalty system.

Before I begin, I have read:
- 02_architecture/CLOUD_BACKEND.md - Backend architecture and API contracts
- 05_data/LOYALTY_LEDGER.md - Ledger append-only requirements
- 06_security/IDEMPOTENCY.md - Idempotency requirements
- 03_features/EARN_POINTS_POS.md - Earn points at POS
- 03_features/EARN_POINTS_ONLINE.md - Earn points online
- 03_features/REDEEM_POINTS_POS.md - Redeem points at POS
- 03_features/REDEEM_POINTS_ONLINE.md - Redeem points online
- 03_features/BALANCE_QUERY.md - Balance query feature

Task:
1. Implement POST /transactions/earn endpoint
2. Implement POST /transactions/redeem endpoint
3. Implement POST /transactions/reverse endpoint (for refunds)
4. Implement GET /customers/{id}/balance endpoint
5. Ensure all transactions append to ledger (never modify)
6. Implement idempotency check for all transaction endpoints
7. Validate all inputs (amounts, customer IDs, etc.)
8. Calculate points according to business rules
9. Handle insufficient balance gracefully
10. Add comprehensive error handling
11. Add audit logging for all state changes
12. Write unit tests for all endpoints
13. Write integration tests with test database
14. Update API documentation

Deliverables:
- [ ] All transaction endpoints implemented
- [ ] Ledger append-only principle enforced
- [ ] Idempotency working for all transactions
- [ ] Balance calculation accurate
- [ ] All edge cases handled
- [ ] Complete test coverage

Testing checklist:
- [ ] Earn points transaction recorded correctly
- [ ] Redeem points transaction recorded correctly
- [ ] Insufficient balance returns proper error
- [ ] Duplicate idempotency key returns same result
- [ ] Balance calculation includes all transactions
- [ ] Invalid inputs rejected with clear errors
- [ ] Audit log captures all operations
```

## Step 2.3: Customer and Card Management Endpoints

```
I am implementing customer and card management endpoints for the Fidelity Points loyalty system.

Before I begin, I have read:
- 02_architecture/CLOUD_BACKEND.md - Backend architecture
- 05_data/CUSTOMER_MODEL.md - Customer entity specification
- 05_data/CARD_MODEL.md - Card entity specification
- 05_data/CONSENT_RECORDS.md - Consent tracking
- 03_features/CARD_ENROLLMENT.md - Card enrollment flow
- 06_security/NFC_SECURITY.md - Card security considerations

Task:
1. Implement POST /customers endpoint (create customer)
2. Implement GET /customers/{id} endpoint
3. Implement PATCH /customers/{id} endpoint (update contact info)
4. Implement POST /cards endpoint (register card)
5. Implement POST /cards/{uid}/assign endpoint (assign card to customer)
6. Implement GET /cards/{uid}/customer endpoint (lookup customer by card)
7. Implement consent tracking on customer creation/update
8. Validate email and phone number formats
9. Ensure card UIDs are unique
10. Prevent card reassignment without proper workflow
11. Add comprehensive validation
12. Write unit and integration tests
13. Update API documentation

Deliverables:
- [ ] All customer endpoints working
- [ ] All card endpoints working
- [ ] Consent properly tracked
- [ ] Validation preventing invalid data
- [ ] Complete test coverage

Testing checklist:
- [ ] Customer created with valid data
- [ ] Invalid email/phone rejected
- [ ] Card registered successfully
- [ ] Card assigned to customer successfully
- [ ] Card lookup returns correct customer
- [ ] Cannot assign card already assigned
- [ ] Consent recorded correctly
```

---

# PHASE 3: WINDOWS AGENT - POS INTEGRATION

## Step 3.1: Windows Agent Core Structure

```
I am implementing the Windows agent core structure for the Fidelity Points loyalty system.

Before I begin, I have read:
- 02_architecture/WINDOWS_AGENT.md - Agent architecture
- 02_architecture/SYNC_STRATEGY.md - Sync requirements
- 07_operations/OFFLINE_QUEUE.md - Offline queue requirements
- 07_operations/ERROR_HANDLING.md - Error handling requirements

Task:
1. Set up Windows application structure (WPF/WinForms/Electron)
2. Implement offline queue with disk persistence
3. Create queue management (add, process, retry, remove)
4. Implement sync service with exponential backoff
5. Create UI shell with Spanish and Catalan language support
6. Implement configuration management (API endpoint, terminal ID, etc.)
7. Create status display (online/offline, queue size)
8. Add logging infrastructure
9. Implement graceful degradation when offline
10. Create installer package
11. Write integration tests for queue operations
12. Document agent architecture and components

Deliverables:
- [ ] Windows agent runs on Windows terminal
- [ ] Offline queue persists to disk
- [ ] Sync service processes queue
- [ ] UI displays in Spanish and Catalan
- [ ] Configuration manageable by staff
- [ ] Logging captures all events

Testing checklist:
- [ ] Agent starts successfully
- [ ] Queue survives application restart
- [ ] Sync processes queued items
- [ ] Retry logic works with exponential backoff
- [ ] Offline mode degrades gracefully
- [ ] Language switching works
- [ ] Configuration changes persist
```

## Step 3.2: NFC Reader Integration

```
I am implementing NFC reader integration for the Windows agent.

Before I begin, I have read:
- 04_integrations/NFC_HARDWARE.md - NFC hardware specification
- 06_security/NFC_SECURITY.md - Security considerations
- 02_architecture/WINDOWS_AGENT.md - Agent architecture

Task:
1. Implement PC/SC interface for USB NFC readers
2. Detect and connect to NFC reader on startup
3. Read card UID when card is tapped
4. Handle reader not connected gracefully
5. Handle card read failures gracefully
6. Implement card read timeout (2 seconds max)
7. Provide clear UI feedback for card operations
8. Support multiple card types (MIFARE Classic, DESFire, etc.)
9. Test with multiple NFC reader models
10. Handle reader disconnect during operation
11. Provide Spanish and Catalan messages
12. Document tested hardware and findings

Deliverables:
- [ ] NFC reader detected and connected
- [ ] Card UID read successfully
- [ ] All error scenarios handled
- [ ] UI provides clear feedback
- [ ] Multiple card types supported
- [ ] Hardware compatibility documented

Testing checklist:
- [ ] Card read success rate >99%
- [ ] Read completes in <2 seconds
- [ ] Reader not found displays clear error
- [ ] Card read error displays clear error
- [ ] Multiple rapid taps handled correctly
- [ ] Works with documented card models
- [ ] Error messages in both languages
```

## Step 3.3: Aniwin POS Integration

```
I am implementing the integration between the Windows agent and Aniwin.net POS system.

Before I begin, I have read:
- 04_integrations/ANIWIN_POS_INTEGRATION.md - Integration specification
- 02_architecture/WINDOWS_AGENT.md - Agent architecture
- 03_features/EARN_POINTS_POS.md - Earn points flow
- 05_data/ORDER_MAPPING.md - Order mapping requirements

Task:
1. Analyze Aniwin.net to determine integration approach (database hook, file export, or receipt intercept)
2. Implement detection mechanism for new sales
3. Extract order ID, amount, timestamp, and customer identifier
4. Create loyalty transaction with proper idempotency key (order ID based)
5. Handle cases where customer not identified (skip quietly)
6. Handle Aniwin database/file unavailability gracefully
7. Queue transaction if offline
8. Store order mapping (Aniwin order ID → loyalty transaction ID)
9. Log all integration events for debugging
10. Test with Aniwin test environment
11. Document integration approach and assumptions
12. Document recovery procedures if integration fails

Deliverables:
- [ ] Integration method selected and implemented
- [ ] New sales detected reliably
- [ ] Order data extracted correctly
- [ ] Loyalty transactions created properly
- [ ] Order mapping stored
- [ ] Integration documented

Testing checklist:
- [ ] New sale detected within acceptable time
- [ ] Order mapping correctly stored
- [ ] Points awarded correctly
- [ ] Multiple rapid sales handled correctly
- [ ] Aniwin offline/error handled gracefully
- [ ] No crashes if Aniwin data format changes
- [ ] Idempotency prevents duplicate awards
```

## Step 3.4: POS Earn Points Feature

```
I am implementing the earn points feature at POS for the Fidelity Points loyalty system.

Before I begin, I have read:
- 03_features/EARN_POINTS_POS.md - Earn points at POS specification
- 02_architecture/WINDOWS_AGENT.md - Agent architecture
- 07_operations/OFFLINE_QUEUE.md - Offline queue management
- 04_integrations/NFC_HARDWARE.md - NFC integration
- 04_integrations/ANIWIN_POS_INTEGRATION.md - POS integration

Task:
1. Create UI for "Earn Points" operation
2. Implement card tap workflow (prompt, read, verify)
3. Retrieve transaction details from Aniwin POS
4. Calculate points based on business rules
5. Call backend API to record earn transaction
6. Queue transaction if offline
7. Display confirmation to customer and cashier
8. Print receipt or show on screen
9. Handle all error scenarios gracefully
10. Provide feedback in Spanish and Catalan
11. Test end-to-end flow (online and offline)
12. Document feature and user workflow

Deliverables:
- [ ] Earn points UI implemented
- [ ] Card tap workflow working
- [ ] Points calculation correct
- [ ] Online and offline modes working
- [ ] User feedback clear and helpful
- [ ] Feature fully documented

Testing checklist:
- [ ] Card tap prompts for card
- [ ] Card read succeeds
- [ ] Customer lookup succeeds
- [ ] Points calculated correctly
- [ ] Transaction recorded online
- [ ] Transaction queued when offline
- [ ] Confirmation displayed clearly
- [ ] All error messages clear and actionable
- [ ] Works in both Spanish and Catalan
```

## Step 3.5: POS Redeem Points Feature

```
I am implementing the redeem points feature at POS for the Fidelity Points loyalty system.

Before I begin, I have read:
- 03_features/REDEEM_POINTS_POS.md - Redeem points at POS specification
- 02_architecture/WINDOWS_AGENT.md - Agent architecture
- 07_operations/OFFLINE_QUEUE.md - Offline queue management
- 04_integrations/NFC_HARDWARE.md - NFC integration
- 03_features/BALANCE_QUERY.md - Balance display

Task:
1. Create UI for "Redeem Points" operation
2. Implement card tap workflow
3. Retrieve customer balance from backend
4. Display available balance and redemption options
5. Allow cashier to select redemption amount
6. Validate sufficient balance
7. Call backend API to record redemption transaction
8. Queue transaction if offline (with balance validation)
9. Generate discount code/voucher for POS entry
10. Display confirmation with discount amount
11. Handle insufficient balance gracefully
12. Provide feedback in Spanish and Catalan
13. Test end-to-end flow (online and offline)
14. Document feature and user workflow

Deliverables:
- [ ] Redeem points UI implemented
- [ ] Balance display working
- [ ] Redemption flow complete
- [ ] Online and offline modes working
- [ ] Error handling comprehensive
- [ ] Feature fully documented

Testing checklist:
- [ ] Card tap retrieves customer balance
- [ ] Balance displayed correctly
- [ ] Redemption amount selectable
- [ ] Insufficient balance shows error
- [ ] Redemption recorded online
- [ ] Redemption queued when offline
- [ ] Discount amount calculated correctly
- [ ] Confirmation clear to cashier
- [ ] Works in both languages
```

---

# PHASE 4: PRESTASHOP MODULE

## Step 4.1: PrestaShop Module Structure

```
I am creating the PrestaShop module structure for the Fidelity Points loyalty system.

Before I begin, I have read:
- 04_integrations/PRESTASHOP_MODULE.md - Module specification
- 02_architecture/CLOUD_BACKEND.md - API contracts
- PrestaShop 9.1.0 module development documentation

Task:
1. Create module directory structure per PrestaShop standards
2. Create module configuration file (module name, version, etc.)
3. Implement install() method (create config, register hooks)
4. Implement uninstall() method (clean removal)
5. Create admin configuration page (API endpoint, credentials, settings)
6. Implement configuration saving and loading
7. Create API client for backend communication
8. Add error logging for debugging
9. Ensure no core PrestaShop files are modified
10. Test module installation on clean PrestaShop 9.1.0
11. Test module uninstallation (clean removal)
12. Document module structure and hooks used

Deliverables:
- [ ] Module structure follows PrestaShop standards
- [ ] Module installs cleanly
- [ ] Module uninstalls cleanly
- [ ] Admin configuration page functional
- [ ] API client ready for use
- [ ] No core modifications

Testing checklist:
- [ ] Module installs without errors
- [ ] Configuration page accessible
- [ ] Settings save and load correctly
- [ ] Module uninstalls completely
- [ ] No core files modified
- [ ] Compatible with PrestaShop 9.1.0
- [ ] Module passes PrestaShop validator
```

## Step 4.2: Online Earn Points Feature

```
I am implementing the earn points feature for PrestaShop online orders.

Before I begin, I have read:
- 03_features/EARN_POINTS_ONLINE.md - Earn points online specification
- 04_integrations/PRESTASHOP_MODULE.md - Module specification
- 02_architecture/CLOUD_BACKEND.md - API contracts
- 05_data/ORDER_MAPPING.md - Order mapping requirements

Task:
1. Identify correct PrestaShop hook for order completion (actionValidateOrder or similar)
2. Extract order ID, amount, customer email, timestamp
3. Lookup customer by email in loyalty backend
4. Calculate points based on order amount
5. Call backend API to record earn transaction
6. Include idempotency key (based on PrestaShop order ID)
7. Store order mapping (PrestaShop order ID → loyalty transaction ID)
8. Handle API failures gracefully (retry logic)
9. Log all API calls and responses
10. Display points earned on order confirmation page
11. Send email notification to customer
12. Test end-to-end flow
13. Document hooks used and integration flow

Deliverables:
- [ ] Hook identified and registered
- [ ] Points earned on order completion
- [ ] API call includes idempotency key
- [ ] Order mapping stored
- [ ] Customer sees points earned
- [ ] Email notification sent
- [ ] Integration documented

Testing checklist:
- [ ] Order completion triggers points award
- [ ] Points calculated correctly
- [ ] API call succeeds
- [ ] Idempotency prevents duplicates
- [ ] Order mapping stored correctly
- [ ] API failure handled gracefully (retry)
- [ ] Customer sees points on confirmation
- [ ] Email received
```

## Step 4.3: Online Redeem Points Feature

```
I am implementing the redeem points feature for PrestaShop online orders.

Before I begin, I have read:
- 03_features/REDEEM_POINTS_ONLINE.md - Redemption flow
- 04_integrations/PRESTASHOP_MODULE.md - Module specification
- 02_architecture/CLOUD_BACKEND.md - API contracts
- PrestaShop cart rule documentation

Task:
1. Add "Use Loyalty Points" option to checkout page
2. Display customer's available balance
3. Allow customer to select redemption amount
4. Validate sufficient balance via API call
5. Create programmatic PrestaShop cart rule for discount
6. Set cart rule properties (amount, validity, single-use)
7. Apply cart rule to current cart
8. Call backend API to record redemption transaction
9. Include idempotency key (based on order ID + redemption timestamp)
10. Handle insufficient balance gracefully
11. Ensure cart rule is deleted if order fails
12. Hook into order cancellation to reverse redemption
13. Test redemption flow end-to-end
14. Test partial payment (points + money)
15. Document cart rule lifecycle

Deliverables:
- [ ] Redemption UI on checkout page
- [ ] Balance display working
- [ ] Cart rule created and applied
- [ ] Redemption recorded in backend
- [ ] Insufficient balance handled
- [ ] Failed order cleanup working
- [ ] Feature documented

Testing checklist:
- [ ] Balance displayed correctly
- [ ] Redemption amount selectable
- [ ] Insufficient balance shows error
- [ ] Cart rule created with correct amount
- [ ] Cart rule applied to cart successfully
- [ ] Order completion recorded in ledger
- [ ] Failed order doesn't consume points
- [ ] Partial payment (points + money) works
```

## Step 4.4: Online Refund Handling

```
I am implementing refund handling for PrestaShop online orders in the Fidelity Points loyalty system.

Before I begin, I have read:
- 03_features/REFUND_HANDLING.md - Refund reversal flow
- 04_integrations/PRESTASHOP_MODULE.md - Module specification
- 02_architecture/CLOUD_BACKEND.md - API contracts
- 05_data/ORDER_MAPPING.md - Order mapping requirements

Task:
1. Identify correct PrestaShop hook for order refund (actionOrderStatusUpdate or similar)
2. Retrieve order mapping (PrestaShop order ID → loyalty transactions)
3. Determine which transactions to reverse (earn and/or redeem)
4. Call backend API to create reversal transactions
5. Include idempotency key (based on refund ID)
6. Handle partial refunds (out of scope, but gracefully reject)
7. Handle API failures gracefully
8. Log all refund operations
9. Notify customer of points adjustment
10. Test full refund flow
11. Document refund handling logic

Deliverables:
- [ ] Refund hook identified and registered
- [ ] Order mapping lookup working
- [ ] Reversal transactions created
- [ ] API call includes idempotency key
- [ ] Customer notified of adjustment
- [ ] Refund flow documented

Testing checklist:
- [ ] Full refund triggers reversal
- [ ] Earn transaction reversed correctly
- [ ] Redeem transaction reversed correctly
- [ ] Order mapping lookup succeeds
- [ ] API call succeeds
- [ ] Idempotency prevents duplicate reversals
- [ ] Customer notification sent
- [ ] Partial refund handled appropriately
```

---

# PHASE 5: MESSAGING AND NOTIFICATIONS

## Step 5.1: WhatsApp Balance Query Integration

```
I am implementing WhatsApp-based balance query for the Fidelity Points loyalty system.

Before I begin, I have read:
- 04_integrations/WHATSAPP_MESSAGING.md - WhatsApp integration
- 03_features/BALANCE_QUERY.md - Balance query feature
- 01_project/PROJECT_OVERVIEW.md - Language requirements (Spanish and Catalan)

Task:
1. Set up WhatsApp Business API integration
2. Create webhook endpoint for incoming messages
3. Implement message parsing (detect balance query intent)
4. Extract card UID or customer identifier from message
5. Lookup customer and calculate balance
6. Format balance response in Spanish or Catalan
7. Send response via WhatsApp API
8. Implement language selection logic (default Spanish)
9. Handle messaging API failures gracefully
10. Log all messages for audit and debugging
11. Test message delivery and response
12. Document WhatsApp integration setup

Deliverables:
- [ ] WhatsApp API integration working
- [ ] Balance query messages recognized
- [ ] Customer lookup successful
- [ ] Balance responses sent correctly
- [ ] Both languages supported
- [ ] Integration documented

Testing checklist:
- [ ] Incoming message triggers webhook
- [ ] Balance query intent detected
- [ ] Customer identified correctly
- [ ] Balance calculated accurately
- [ ] Spanish response correct
- [ ] Catalan response correct
- [ ] Language selection works
- [ ] API failure handled gracefully
- [ ] Messages logged for audit
```

## Step 5.2: Email Notifications

```
I am implementing email notifications for the Fidelity Points loyalty system.

Before I begin, I have read:
- 01_project/PROJECT_OVERVIEW.md - Email requirements
- 03_features/EARN_POINTS_ONLINE.md - Online earn notifications
- 03_features/REDEEM_POINTS_ONLINE.md - Online redeem notifications
- 03_features/REFUND_HANDLING.md - Refund notifications

Task:
1. Set up email service (SendGrid, SMTP, or similar)
2. Create email templates for earn notifications (Spanish and Catalan)
3. Create email templates for redeem notifications (Spanish and Catalan)
4. Create email templates for refund notifications (Spanish and Catalan)
5. Implement email sending function with language selection
6. Send earn notification after online order completion
7. Send redeem notification after online redemption
8. Send refund notification after refund processing
9. Include transaction details and current balance in emails
10. Handle email service failures gracefully
11. Log all sent emails for audit
12. Test all email templates and delivery
13. Document email templates and sending logic

Deliverables:
- [ ] Email service configured
- [ ] All templates created in both languages
- [ ] Emails sent for all relevant events
- [ ] Templates include all required information
- [ ] Email failures handled gracefully
- [ ] Email sending documented

Testing checklist:
- [ ] Earn email sent on order completion
- [ ] Redeem email sent on redemption
- [ ] Refund email sent on refund
- [ ] Spanish templates correct
- [ ] Catalan templates correct
- [ ] All data fields populated correctly
- [ ] Email service failure doesn't block transactions
- [ ] Emails delivered successfully
```

---

# PHASE 6: ADVANCED FEATURES

## Step 6.1: Points Expiration System

```
I am implementing the points expiration system for the Fidelity Points loyalty system.

Before I begin, I have read:
- 03_features/EXPIRATION.md - Expiration specification
- 05_data/LOYALTY_LEDGER.md - Ledger structure
- 02_architecture/CLOUD_BACKEND.md - Backend architecture

Task:
1. Implement expiration calculation logic (3-month rolling window)
2. Create scheduled job to process expirations daily
3. Create expiration transactions in ledger for expired points
4. Update balance calculation to account for expirations
5. Ensure expired points cannot be redeemed
6. Send notification to customers before points expire (7 days warning)
7. Send notification when points have expired
8. Handle timezone considerations
9. Log all expiration processing
10. Test expiration logic thoroughly
11. Test notification sending
12. Document expiration rules and process

Deliverables:
- [ ] Expiration calculation correct
- [ ] Scheduled job running daily
- [ ] Expiration transactions recorded
- [ ] Balance calculation includes expirations
- [ ] Notifications sent appropriately
- [ ] Expiration system documented

Testing checklist:
- [ ] Points expire after 3 months
- [ ] Expiration date calculated correctly
- [ ] Scheduled job runs reliably
- [ ] Expiration transactions recorded in ledger
- [ ] Balance calculation correct with expirations
- [ ] Warning notification sent 7 days before
- [ ] Expiration notification sent on expiration
- [ ] Timezone handling correct
```

## Step 6.2: Manual Balance Adjustments

```
I am implementing manual balance adjustment capability for the Fidelity Points loyalty system.

Before I begin, I have read:
- 03_features/MANUAL_ADJUSTMENTS.md - Manual adjustments specification
- 05_data/LOYALTY_LEDGER.md - Ledger structure
- 06_security/SECURITY_MODEL.md - Security requirements
- 06_security/AUTHENTICATION.md - Authentication

Task:
1. Create admin API endpoint for manual adjustments
2. Implement authentication and authorization (manager role required)
3. Validate adjustment amount and reason
4. Create adjustment transaction in ledger
5. Require reason/note for all adjustments
6. Log all adjustments with admin user identity
7. Create admin UI for making adjustments
8. Add audit report for all manual adjustments
9. Send notification to customer on adjustment
10. Test adjustment flow end-to-end
11. Test authorization (non-managers cannot adjust)
12. Document adjustment process and use cases

Deliverables:
- [ ] Adjustment API endpoint working
- [ ] Authorization enforced
- [ ] Adjustments recorded in ledger
- [ ] Reason required and logged
- [ ] Admin UI functional
- [ ] Audit report available
- [ ] Customer notified
- [ ] Feature documented

Testing checklist:
- [ ] Authorized user can make adjustment
- [ ] Unauthorized user cannot make adjustment
- [ ] Positive adjustment increases balance
- [ ] Negative adjustment decreases balance
- [ ] Reason required (cannot submit without)
- [ ] Adjustment recorded in ledger
- [ ] Audit log captures admin identity
- [ ] Customer notification sent
```

---

# PHASE 7: OFFLINE SYNC AND CONFLICT RESOLUTION

## Step 7.1: Offline Queue and Sync Implementation

```
I am implementing the offline queue and sync logic for the Fidelity Points loyalty system.

Before I begin, I have read:
- 02_architecture/SYNC_STRATEGY.md - Sync strategy
- 07_operations/OFFLINE_QUEUE.md - Queue management
- 06_security/IDEMPOTENCY.md - Duplicate prevention
- 02_architecture/WINDOWS_AGENT.md - Agent architecture

Task:
1. Implement queue persistence to local database/file
2. Create sync service that processes queue items
3. Ensure idempotency key sent with every request
4. Handle successful sync (remove from queue, update status)
5. Handle failed sync (retry with exponential backoff)
6. Handle conflict detection (timestamp comparison)
7. Implement sync status UI (progress, success, failures)
8. Add manual sync trigger button
9. Log all sync events for monitoring
10. Test with 100+ queued transactions
11. Test with intermittent network failures
12. Document sync logic and retry strategy

Deliverables:
- [ ] Queue persists reliably
- [ ] Sync service processes queue
- [ ] Idempotency prevents duplicates
- [ ] Retry logic works correctly
- [ ] Conflict detection functional
- [ ] Sync status visible to user
- [ ] Sync system documented

Testing checklist:
- [ ] Queue survives agent restart
- [ ] Successful sync removes item from queue
- [ ] Failed sync retries with backoff
- [ ] Idempotency prevents duplicates
- [ ] Large queue syncs in reasonable time
- [ ] Network failures don't cause data loss
- [ ] User informed of sync progress
- [ ] Manual sync trigger works
```

## Step 7.2: Conflict Resolution Implementation

```
I am implementing conflict resolution for the Fidelity Points loyalty system.

Before I begin, I have read:
- 02_architecture/CONFLICT_RESOLUTION.md - Resolution strategy
- 02_architecture/SYNC_STRATEGY.md - Sync context
- 05_data/LOYALTY_LEDGER.md - Ledger structure
- 07_operations/OFFLINE_QUEUE.md - Queue management

Task:
1. Detect conflicts during sync (same order processed multiple times)
2. Apply resolution rules from CONFLICT_RESOLUTION.md
3. Handle duplicate earn/redeem from POS vs online
4. Handle refund before original transaction synced
5. Log all conflicts and resolutions for audit
6. Notify operator if manual intervention needed
7. Update ledger with conflict resolution entries
8. Ensure ledger immutability preserved
9. Test all documented conflict scenarios
10. Document conflict handling in detail

Deliverables:
- [ ] Conflict detection working
- [ ] Resolution rules implemented
- [ ] Conflicts logged for audit
- [ ] Operator notification working
- [ ] Ledger remains consistent
- [ ] Conflict resolution documented

Testing checklist:
- [ ] Duplicate earn transaction detected
- [ ] Duplicate redeem transaction detected
- [ ] Resolution rule applied correctly
- [ ] Ledger remains consistent
- [ ] Operator notified if needed
- [ ] Audit trail complete
- [ ] All documented scenarios tested
```

---

# PHASE 8: TESTING, SECURITY, AND DEPLOYMENT

## Step 8.1: Comprehensive Integration Testing

```
I am implementing comprehensive integration tests for the Fidelity Points loyalty system.

Before I begin, I have read:
- All feature specifications in 03_features/
- All integration specifications in 04_integrations/
- 02_architecture/SYSTEM_ARCHITECTURE.md - Complete system architecture

Task:
1. Create end-to-end test suite for all features
2. Test earn points flow (POS and online)
3. Test redeem points flow (POS and online)
4. Test refund flow (POS and online)
5. Test card enrollment and assignment
6. Test balance query (WhatsApp and API)
7. Test offline scenarios (queue and sync)
8. Test conflict resolution scenarios
9. Test expiration processing
10. Test manual adjustments
11. Create test data generators
12. Document all test scenarios and expected outcomes
13. Set up continuous integration to run tests

Deliverables:
- [ ] Complete test suite implemented
- [ ] All features tested end-to-end
- [ ] Offline scenarios covered
- [ ] Test data generators available
- [ ] CI/CD runs tests automatically
- [ ] Test documentation complete

Testing checklist:
- [ ] All happy paths tested
- [ ] All error scenarios tested
- [ ] Offline scenarios tested
- [ ] Edge cases covered
- [ ] Performance acceptable
- [ ] Tests run reliably in CI/CD
```

## Step 8.2: Security Audit and Hardening

```
I am performing a security audit and hardening for the Fidelity Points loyalty system.

Before I begin, I have read:
- 06_security/SECURITY_MODEL.md - Overall security model
- 06_security/AUTHENTICATION.md - Authentication requirements
- 06_security/IDEMPOTENCY.md - Idempotency requirements
- 06_security/NFC_SECURITY.md - Card security considerations

Task:
1. Review all authentication and authorization implementations
2. Review all API endpoints for security vulnerabilities
3. Ensure no secrets in code or logs
4. Verify all communication uses TLS/SSL
5. Implement proper error messages (no info leakage)
6. Review idempotency implementation
7. Test for common vulnerabilities (injection, XSS, CSRF)
8. Implement rate limiting on all API endpoints
9. Review and harden database access
10. Implement security monitoring and alerting
11. Document all security controls
12. Create security runbook for incident response

Deliverables:
- [ ] Security audit complete
- [ ] All vulnerabilities addressed
- [ ] Security controls documented
- [ ] Monitoring and alerting configured
- [ ] Incident response plan documented

Testing checklist:
- [ ] Unauthorized access blocked
- [ ] Invalid credentials rejected
- [ ] Error messages don't leak info
- [ ] All communication encrypted
- [ ] Secrets not logged or exposed
- [ ] Rate limiting functional
- [ ] Injection attacks prevented
- [ ] Audit trail complete
```

## Step 8.3: Performance Testing and Optimization

```
I am performing performance testing and optimization for the Fidelity Points loyalty system.

Before I begin, I have read:
- 02_architecture/SYSTEM_ARCHITECTURE.md - System architecture
- 02_architecture/CLOUD_BACKEND.md - Backend architecture
- 05_data/DATA_MODEL.md - Database schema

Task:
1. Create performance test suite
2. Test API endpoint response times under load
3. Test database query performance
4. Optimize slow queries (add indexes, refactor)
5. Test sync performance with large queue
6. Test NFC card read performance
7. Profile memory usage
8. Optimize resource-intensive operations
9. Set up performance monitoring
10. Document performance benchmarks
11. Create performance degradation alerts
12. Document optimization decisions

Deliverables:
- [ ] Performance tests implemented
- [ ] All endpoints meet performance targets
- [ ] Database queries optimized
- [ ] Performance monitoring configured
- [ ] Benchmarks documented

Testing checklist:
- [ ] API responses < 200ms (95th percentile)
- [ ] Database queries optimized
- [ ] NFC reads < 2 seconds
- [ ] Sync processes efficiently
- [ ] Memory usage acceptable
- [ ] No performance regressions
```

## Step 8.4: Production Deployment and Documentation

```
I am preparing for production deployment of the Fidelity Points loyalty system.

Before I begin, I have read:
- 01_project/IMPLEMENTATION_PLAN.md - Implementation plan
- All documentation files across all sections

Task:
1. Create deployment runbook
2. Create database migration plan
3. Set up production environment
4. Configure production secrets and credentials
5. Set up backup and disaster recovery
6. Create monitoring dashboards
7. Set up alerting for critical errors
8. Create operations manual for staff
9. Create troubleshooting guide
10. Conduct staff training
11. Plan rollout strategy (pilot, full deployment)
12. Create rollback procedure
13. Update all documentation for production readiness
14. Conduct final security review
15. Conduct final performance review

Deliverables:
- [ ] Deployment runbook complete
- [ ] Production environment configured
- [ ] Backup and DR configured
- [ ] Monitoring and alerting working
- [ ] Operations manual complete
- [ ] Staff trained
- [ ] Rollback procedure tested

Testing checklist:
- [ ] Production environment tested
- [ ] Migrations tested on production-like data
- [ ] Monitoring captures all critical metrics
- [ ] Alerts trigger appropriately
- [ ] Backup and restore tested
- [ ] Rollback procedure works
- [ ] Staff comfortable with operations
```

---

# APPENDICES

## Appendix A: Documentation Quick Reference

### Project Level
- `00_meta/SESSION_START.md` - Start here every session
- `00_meta/DOCUMENTATION_RULES.md` - Documentation standards
- `01_project/PROJECT_OVERVIEW.md` - Complete project overview
- `01_project/IMPLEMENTATION_PLAN.md` - Current status and deviations
- `08_prompts/AGENT_WORKFLOW.md` - Required workflow for all work

### Architecture Level
- `02_architecture/SYSTEM_ARCHITECTURE.md` - Overall system design
- `02_architecture/CLOUD_BACKEND.md` - Backend API contracts
- `02_architecture/WINDOWS_AGENT.md` - POS agent architecture
- `02_architecture/SYNC_STRATEGY.md` - Offline sync strategy
- `02_architecture/CONFLICT_RESOLUTION.md` - Conflict handling

### Feature Level (03_features/)
- `EARN_POINTS_POS.md`, `EARN_POINTS_ONLINE.md` - Earning points
- `REDEEM_POINTS_POS.md`, `REDEEM_POINTS_ONLINE.md` - Redeeming points
- `CARD_ENROLLMENT.md` - Card registration
- `BALANCE_QUERY.md` - Balance queries
- `REFUND_HANDLING.md` - Refund processing
- `EXPIRATION.md` - Points expiration
- `MANUAL_ADJUSTMENTS.md` - Admin adjustments

### Integration Level (04_integrations/)
- `ANIWIN_POS_INTEGRATION.md` - POS integration
- `PRESTASHOP_MODULE.md` - E-commerce integration
- `NFC_HARDWARE.md` - NFC reader integration
- `WHATSAPP_MESSAGING.md` - Messaging integration

### Data Level (05_data/)
- `DATA_MODEL.md` - Complete database schema
- `LOYALTY_LEDGER.md` - Ledger structure and rules
- `CUSTOMER_MODEL.md`, `CARD_MODEL.md` - Entity specifications
- `ORDER_MAPPING.md` - Order tracking
- `CONSENT_RECORDS.md` - GDPR compliance

### Security Level (06_security/)
- `SECURITY_MODEL.md` - Overall security
- `AUTHENTICATION.md` - Auth requirements
- `IDEMPOTENCY.md` - Duplicate prevention
- `NFC_SECURITY.md` - Card security

### Operations Level (07_operations/)
- `OFFLINE_QUEUE.md` - Queue management
- `ERROR_HANDLING.md` - Error scenarios

## Appendix B: Common Patterns and Best Practices

### Always Follow These Patterns

1. **Ledger-First**: All loyalty transactions append to ledger, never modify
2. **Idempotency-Always**: Every transaction API call includes idempotency key
3. **Offline-First**: POS features work without internet, queue for sync
4. **Documentation-First**: Update docs before code, keep docs current
5. **Bilingual**: All POS UI in Spanish and Catalan
6. **No-Core-Modification**: PrestaShop module never modifies core files
7. **Audit-Everything**: Log all state changes with complete context

### Testing Requirements

1. **Happy Path**: Every feature tested in normal conditions
2. **Offline Path**: Every POS feature tested without internet
3. **Error Path**: All error scenarios tested
4. **Edge Cases**: Boundary conditions, zero values, negative values tested
5. **Idempotency**: Duplicate submissions tested
6. **Security**: Unauthorized access tested
7. **Performance**: Response times measured

### Documentation Requirements

1. **Update-As-You-Go**: Don't defer documentation
2. **Cross-Reference**: Link related documents bidirectionally
3. **Be-Specific**: Concrete examples, not generic descriptions
4. **Include-Rationale**: Explain why, not just what
5. **Track-Deviations**: Log in IMPLEMENTATION_PLAN.md
6. **Update-Diagrams**: Keep visual aids current

## Appendix C: Troubleshooting Common Issues

### Issue: Tests Failing After Code Change
- **Check**: Did you update affected documentation first?
- **Check**: Are you testing the documented behavior?
- **Fix**: Review documentation, ensure code matches spec

### Issue: Offline Mode Not Working
- **Check**: Is queue persisting to disk?
- **Check**: Are idempotency keys being generated offline?
- **Fix**: Review OFFLINE_QUEUE.md and SYNC_STRATEGY.md

### Issue: Duplicate Transactions
- **Check**: Is idempotency key being sent?
- **Check**: Is idempotency key unique per transaction?
- **Fix**: Review IDEMPOTENCY.md implementation

### Issue: PrestaShop Module Not Working
- **Check**: Did you modify core files? (Don't!)
- **Check**: Are hooks registered correctly?
- **Fix**: Review PRESTASHOP_MODULE.md and hook documentation

### Issue: NFC Reader Not Connecting
- **Check**: Is PC/SC service running?
- **Check**: Is reader compatible? (Check NFC_HARDWARE.md)
- **Fix**: Test with different reader or update drivers

### Issue: API Timeout
- **Check**: Are database queries optimized?
- **Check**: Are indexes in place?
- **Fix**: Review DATA_MODEL.md, add missing indexes

## Appendix D: Session Workflow Reminder

Every work session should follow this flow:

1. ✅ Read SESSION_START.md checklist
2. ✅ Read all relevant documentation
3. ✅ Verify documentation is current
4. ✅ Plan documentation updates needed
5. ✅ Update documentation first
6. ✅ Write code following documentation
7. ✅ Test code matches documentation
8. ✅ Update documentation if needed during coding
9. ✅ Run tests (unit, integration, end-to-end)
10. ✅ Complete pre-commit checklist
11. ✅ Complete PR checklist
12. ✅ Submit PR with documentation links

**Never skip steps. Never assume. Always document.**

---

## Next Steps After Completing This Sequence

Once all phases are complete:

1. Conduct final system review against PROJECT_OVERVIEW.md
2. Verify all goals and constraints are met
3. Conduct user acceptance testing with real staff
4. Deploy to production following deployment runbook
5. Monitor production for 2 weeks closely
6. Document lessons learned
7. Plan future enhancements

---

**Remember**: This is a production system for a real business. Quality, reliability, and attention to detail are paramount. Follow the documentation, follow the workflow, and build something excellent.
