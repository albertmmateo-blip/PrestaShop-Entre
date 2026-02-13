# Session Prompts: Component-Specific Workflows

## Important: See BUILD_SEQUENCE.md First

**If you are building the project from scratch or need an orderly sequence of steps**, see `BUILD_SEQUENCE.md` for a comprehensive, copy-and-paste ready guide that walks through the entire project implementation in order.

This document (SESSION_PROMPTS.md) contains component-specific prompts for working on individual features after the initial project structure is in place.

## Purpose

This document contains well-structured prompts that agents must use when working on specific components of the Fidelity Points loyalty system.

Each prompt references the documentation files that must be read before working.

## Backend Development

### Prompt: Implementing Backend API Endpoint

```
I am implementing [ENDPOINT_NAME] API endpoint for the Fidelity Points loyalty system.

Before I begin, I have read:
- 02_architecture/CLOUD_BACKEND.md - Backend architecture
- 02_architecture/SYNC_STRATEGY.md - Sync requirements
- 05_data/DATA_MODEL.md - Database schema
- 05_data/LOYALTY_LEDGER.md - Ledger append-only requirements
- 06_security/AUTHENTICATION.md - Authentication requirements
- 06_security/IDEMPOTENCY.md - Idempotency requirements
- 03_features/[RELEVANT_FEATURE].md - Feature specification

Task:
1. Review the existing API contract in CLOUD_BACKEND.md
2. Implement the endpoint following ledger-append-only principle
3. Implement idempotency using idempotency keys
4. Add proper error handling for all failure modes
5. Add validation for all inputs
6. Add audit logging for all state changes
7. Write unit tests covering happy path and edge cases
8. Write integration tests with test database
9. Update API documentation if contract changed
10. Update IMPLEMENTATION_PLAN.md if any deviations occurred

Specific considerations for [ENDPOINT_NAME]:
- [List specific requirements]
```

### Prompt: Implementing Business Rule

```
I am implementing [BUSINESS_RULE] for the Fidelity Points loyalty system.

Before I begin, I have read:
- 01_project/PROJECT_OVERVIEW.md - Business requirements
- 03_features/[RELEVANT_FEATURE].md - Feature specification
- 05_data/LOYALTY_LEDGER.md - How to record transactions
- [OTHER RELEVANT DOCS]

The rule is: [DESCRIBE RULE]

Task:
1. Implement calculation logic with proper rounding
2. Handle edge cases: [LIST EDGE CASES FROM DOCS]
3. Ensure rule is applied consistently across POS and PrestaShop
4. Add comprehensive unit tests for all scenarios
5. Update documentation if implementation reveals necessary changes

Testing checklist:
- [ ] Boundary values tested
- [ ] Rounding behavior verified
- [ ] Zero-value edge case handled
- [ ] Negative-value edge case handled (if applicable)
- [ ] Expiration interaction tested (if applicable)
```

## Windows Agent Development

### Prompt: Implementing Windows Agent Feature

```
I am implementing [FEATURE_NAME] in the Windows agent for the Fidelity Points loyalty system.

Before I begin, I have read:
- 02_architecture/WINDOWS_AGENT.md - Agent architecture
- 02_architecture/SYNC_STRATEGY.md - Sync requirements
- 07_operations/OFFLINE_QUEUE.md - Offline queue requirements
- 07_operations/ERROR_HANDLING.md - Error handling requirements
- 04_integrations/ANIWIN_POS_INTEGRATION.md - POS integration
- 04_integrations/NFC_HARDWARE.md - NFC reader integration
- 03_features/[RELEVANT_FEATURE].md - Feature specification

Task:
1. Implement feature with offline-first mindset
2. Queue transactions with idempotency key
3. Persist queue to disk before acknowledging operation
4. Handle NFC reader connection failures gracefully
5. Provide clear UI feedback in Spanish and Catalan
6. Update sync logic to handle this transaction type
7. Test offline scenario (disconnect network)
8. Test sync scenario (reconnect and verify sync)
9. Test conflict scenarios (if applicable)
10. Update documentation if design changed

Offline testing checklist:
- [ ] Feature works with no internet connection
- [ ] Transaction queued correctly
- [ ] Queue persists across agent restart
- [ ] Sync completes successfully when connection restored
- [ ] No duplicate transactions after sync
- [ ] User informed of offline status
```

### Prompt: Integrating with Aniwin POS

```
I am working on the integration between the Windows agent and Aniwin.net POS.

Before I begin, I have read:
- 04_integrations/ANIWIN_POS_INTEGRATION.md - Integration specification
- 02_architecture/WINDOWS_AGENT.md - Agent architecture
- 03_features/EARN_POINTS_POS.md - Earn points flow
- 05_data/ORDER_MAPPING.md - Order mapping requirements

Integration approach: [DATABASE_HOOK | FILE_EXPORT | RECEIPT_INTERCEPT]

Task:
1. Implement detection mechanism for new sales
2. Extract order ID, amount, timestamp, customer
3. Create loyalty transaction with proper idempotency key
4. Handle cases where customer not identified (skip quietly)
5. Handle Aniwin database/file unavailability gracefully
6. Log all integration events for debugging
7. Test with Aniwin test environment
8. Document any assumptions about Aniwin behavior
9. Document recovery procedure if integration fails

Testing checklist:
- [ ] New sale detected within [TIME] seconds
- [ ] Order mapping correctly stored
- [ ] Points awarded correctly
- [ ] Multiple rapid sales handled correctly
- [ ] Aniwin offline/error handled gracefully
- [ ] No crashes if Aniwin data format changes
```

## PrestaShop Module Development

### Prompt: Implementing PrestaShop Module Feature

```
I am implementing [FEATURE_NAME] in the PrestaShop module for the Fidelity Points loyalty system.

Before I begin, I have read:
- 04_integrations/PRESTASHOP_MODULE.md - Module specification
- 02_architecture/CLOUD_BACKEND.md - API contracts
- 03_features/[RELEVANT_FEATURE].md - Feature specification
- 05_data/ORDER_MAPPING.md - Order mapping requirements

Task:
1. Identify correct PrestaShop hook for this feature
2. Implement REST API call to loyalty backend
3. Handle API failures gracefully (retry logic)
4. Ensure no core PrestaShop files are modified
5. Add admin configuration UI for settings
6. Add customer-facing UI (if applicable)
7. Test on PrestaShop 9.1.0 clean install
8. Ensure module passes PrestaShop validator
9. Document all hooks used
10. Update module installation guide

PrestaShop integration checklist:
- [ ] Correct hook identified and documented
- [ ] API call includes idempotency key
- [ ] API timeout handled gracefully
- [ ] API error displayed to admin (if applicable)
- [ ] No PrestaShop core modifications
- [ ] Module installs cleanly
- [ ] Module uninstalls cleanly
- [ ] Compatible with PS 9.1.0
```

### Prompt: Implementing Voucher/Cart Rule for Redemption

```
I am implementing the redemption voucher/cart rule mechanism in the PrestaShop module.

Before I begin, I have read:
- 04_integrations/PRESTASHOP_MODULE.md - Module specification
- 03_features/REDEEM_POINTS_ONLINE.md - Redemption flow
- 03_features/REFUND_HANDLING.md - Refund reversal flow
- 05_data/LOYALTY_LEDGER.md - Ledger requirements

Task:
1. Create programmatic cart rule when redemption requested
2. Set cart rule properties (amount, validity, single-use)
3. Apply cart rule to current cart
4. Handle insufficient balance gracefully
5. Ensure cart rule is deleted if order fails
6. Hook into refund to reverse redemption
7. Test redemption flow end-to-end
8. Test refund reversal flow
9. Document cart rule lifecycle

Testing checklist:
- [ ] Cart rule created with correct amount
- [ ] Cart rule applied to cart successfully
- [ ] Order completion recorded in ledger
- [ ] Insufficient balance displays error
- [ ] Failed order doesn't consume points
- [ ] Refund correctly reverses redemption
- [ ] Partial payment (points + money) works
```

## Data Layer Development

### Prompt: Modifying Data Model

```
I am modifying the data model for [ENTITY/TABLE] in the Fidelity Points loyalty system.

Before I begin, I have read:
- 05_data/DATA_MODEL.md - Overall data model
- 05_data/[ENTITY]_MODEL.md - Specific entity documentation
- 05_data/LOYALTY_LEDGER.md - Ledger immutability requirements
- 02_architecture/CLOUD_BACKEND.md - How backend uses data
- 02_architecture/SYNC_STRATEGY.md - Sync implications

Proposed changes: [DESCRIBE CHANGES]

Task:
1. Verify ledger immutability is preserved (if touching ledger)
2. Create database migration script
3. Test migration on copy of production-like data
4. Test rollback procedure
5. Update all code that queries this entity
6. Update documentation for this entity
7. Update DATA_MODEL.md with schema changes
8. Check all components that use this entity
9. Add database indexes if needed for performance
10. Update IMPLEMENTATION_PLAN.md if this is a deviation

Migration checklist:
- [ ] Migration script tested with data
- [ ] Rollback script tested
- [ ] All queries updated
- [ ] All foreign keys preserved
- [ ] All constraints preserved
- [ ] Indexes optimized
- [ ] Documentation updated
```

## NFC Layer Development

### Prompt: Implementing NFC Card Handling

```
I am implementing NFC card handling for [OPERATION] in the Fidelity Points loyalty system.

Before I begin, I have read:
- 04_integrations/NFC_HARDWARE.md - NFC hardware specification
- 06_security/NFC_SECURITY.md - Security considerations
- 03_features/CARD_ENROLLMENT.md - Enrollment flow
- 05_data/CARD_MODEL.md - Card data model

Task:
1. Implement PC/SC interface with USB NFC reader
2. Read card UID reliably
3. Handle reader not connected gracefully
4. Handle card read failures gracefully
5. Provide clear UI feedback (Spanish + Catalan)
6. Test with multiple card types (MIFARE, etc.)
7. Test rapid successive reads
8. Test reader disconnect during operation
9. Document tested card models
10. Update NFC_HARDWARE.md with findings

Testing checklist:
- [ ] Card read success rate >99%
- [ ] Read completes in <2 seconds
- [ ] Reader not found displays clear error
- [ ] Card read error displays clear error
- [ ] Multiple rapid taps handled correctly
- [ ] Works with documented card models
```

## Offline Sync Development

### Prompt: Implementing Sync Logic

```
I am implementing sync logic for [TRANSACTION_TYPE] in the Fidelity Points loyalty system.

Before I begin, I have read:
- 02_architecture/SYNC_STRATEGY.md - Sync strategy
- 02_architecture/CONFLICT_RESOLUTION.md - Conflict resolution
- 07_operations/OFFLINE_QUEUE.md - Queue management
- 06_security/IDEMPOTENCY.md - Duplicate prevention
- 03_features/[RELEVANT_FEATURE].md - Feature specification

Task:
1. Implement queue processing for this transaction type
2. Ensure idempotency key sent with every request
3. Handle successful sync (remove from queue)
4. Handle failed sync (retry with exponential backoff)
5. Handle conflict detection
6. Implement conflict resolution per CONFLICT_RESOLUTION.md
7. Log all sync events for monitoring
8. Update sync status UI
9. Test with 100+ queued transactions
10. Test with intermittent network failures

Sync testing checklist:
- [ ] Successful sync removes item from queue
- [ ] Failed sync retries with backoff
- [ ] Idempotency prevents duplicates
- [ ] Conflicts detected correctly
- [ ] Conflicts resolved correctly
- [ ] Large queue syncs in reasonable time
- [ ] Network failures don't cause data loss
- [ ] User informed of sync progress
```

### Prompt: Implementing Conflict Resolution

```
I am implementing conflict resolution for [CONFLICT_SCENARIO] in the Fidelity Points loyalty system.

Before I begin, I have read:
- 02_architecture/CONFLICT_RESOLUTION.md - Resolution strategy
- 02_architecture/SYNC_STRATEGY.md - Sync context
- 05_data/LOYALTY_LEDGER.md - Ledger structure

Conflict scenario: [DESCRIBE SCENARIO]

Task:
1. Detect this conflict type during sync
2. Apply resolution rule from CONFLICT_RESOLUTION.md
3. Log conflict and resolution for audit
4. Notify operator if manual intervention needed
5. Update all affected ledger entries
6. Ensure ledger immutability preserved
7. Test conflict scenario thoroughly
8. Document resolution in detail

Testing checklist:
- [ ] Conflict correctly detected
- [ ] Resolution rule applied correctly
- [ ] Ledger remains consistent
- [ ] Operator notified if needed
- [ ] Audit trail is complete
```

## Messaging Development

### Prompt: Implementing Messaging Feature

```
I am implementing [MESSAGE_TYPE] messaging for the Fidelity Points loyalty system.

Before I begin, I have read:
- 04_integrations/WHATSAPP_MESSAGING.md - WhatsApp integration
- 03_features/BALANCE_QUERY.md - Balance query feature
- 01_project/PROJECT_OVERVIEW.md - Language requirements

Message type: [EMAIL | WHATSAPP | RECEIPT]

Task:
1. Implement message template in Spanish
2. Implement message template in Catalan
3. Implement language selection logic
4. Include all required information per feature spec
5. Handle messaging API failures gracefully
6. Log all sent messages for audit
7. Test message delivery
8. Test message content accuracy
9. Test both languages
10. Document message templates

Testing checklist:
- [ ] Spanish template correct
- [ ] Catalan template correct
- [ ] Language selection works
- [ ] All data fields populated
- [ ] API failure handled gracefully
- [ ] Messages delivered successfully
- [ ] Message content verified by native speaker
```

## Security Development

### Prompt: Implementing Security Feature

```
I am implementing [SECURITY_FEATURE] for the Fidelity Points loyalty system.

Before I begin, I have read:
- 06_security/SECURITY_MODEL.md - Overall security model
- 06_security/AUTHENTICATION.md - Authentication requirements
- 06_security/IDEMPOTENCY.md - Idempotency requirements
- [OTHER RELEVANT SECURITY DOCS]

Task:
1. Implement security control per specification
2. Ensure no secrets in code or logs
3. Ensure secure communication (TLS)
4. Implement proper error messages (no info leak)
5. Add security-relevant audit logging
6. Test security control effectiveness
7. Test security failure scenarios
8. Document security assumptions
9. Update SECURITY_MODEL.md if needed

Security testing checklist:
- [ ] Unauthorized access blocked
- [ ] Invalid credentials rejected
- [ ] Error messages don't leak info
- [ ] All communication encrypted
- [ ] Secrets not logged
- [ ] Audit trail complete
- [ ] Attack scenarios tested
```

## Component-Specific Reminders

### For All Backend Work
- Read CLOUD_BACKEND.md, IDEMPOTENCY.md, LOYALTY_LEDGER.md
- Never modify ledger entries (append-only)
- Always use idempotency keys
- Always audit log state changes

### For All Windows Agent Work
- Read WINDOWS_AGENT.md, OFFLINE_QUEUE.md, SYNC_STRATEGY.md
- Always design offline-first
- Always persist before acknowledging
- Always provide Spanish and Catalan UI

### For All PrestaShop Work
- Read PRESTASHOP_MODULE.md, CLOUD_BACKEND.md
- Never modify PrestaShop core
- Always handle API failures gracefully
- Always test on PS 9.1.0

### For All Data Work
- Read DATA_MODEL.md and entity-specific docs
- Never break ledger immutability
- Always create migrations
- Always test migrations and rollbacks

### For All Integration Work
- Read specific integration doc
- Always document external system assumptions
- Always handle external system failures
- Always log integration events

## Related Documents

### Process Documents
- `08_prompts/AGENT_WORKFLOW.md` - Overall workflow
- `00_meta/SESSION_START.md` - Session start checklist
- `00_meta/DOCUMENTATION_RULES.md` - Documentation rules

### Architecture Documents
- All files in `02_architecture/` - Component architecture

### Feature Documents
- All files in `03_features/` - Feature specifications

### Integration Documents
- All files in `04_integrations/` - Integration specifications

### Data Documents
- All files in `05_data/` - Data model and entities

### Security Documents
- All files in `06_security/` - Security requirements

### Operations Documents
- All files in `07_operations/` - Operational requirements
