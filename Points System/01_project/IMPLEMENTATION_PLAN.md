# Implementation Plan: Fidelity Points Loyalty System

**This document is a living document and must reflect the current reality of the system at all times.**

Every change to scope, timeline, architecture, or approach must be recorded here.

## Current Status

**Phase**: Planning and Documentation  
**Status**: Documentation framework creation in progress  
**Last Updated**: 2026-02-13

## Technology Stack Decision

**Status**: PENDING USER CHOICE

Choose technology stack:
- **Option A**: Node.js + TypeScript + PostgreSQL
- **Option B**: Python FastAPI + PostgreSQL

**Default**: If no answer provided, proceed with Node.js + TypeScript + PostgreSQL

This decision affects:
- `02_architecture/CLOUD_BACKEND.md`
- `02_architecture/WINDOWS_AGENT.md`
- Development timeline
- Deployment requirements

## Milestones and Phases

### Phase 0: Planning and Architecture (Week 1-2)
**Status**: In Progress

- [x] Document project overview and scope
- [x] Document business requirements
- [ ] Finalize technology stack selection
- [ ] Define complete architecture
- [ ] Design data model
- [ ] Define REST API contracts
- [ ] Create sequence diagrams for all major flows
- [ ] Hardware procurement specification

**Deliverables**:
- Complete documentation framework
- Architecture diagrams
- API specification
- Hardware requirements document

**Exit Criteria**:
- All documentation reviewed and approved
- Technology stack confirmed
- Hardware ordered
- Database schema validated

### Phase 1: Core Backend (Week 3-4)
**Status**: Not Started

- [ ] Set up PostgreSQL database
- [ ] Implement data model (customers, cards, ledger)
- [ ] Implement ledger append-only logic
- [ ] Implement balance calculation
- [ ] Create REST API endpoints (earn, redeem, query)
- [ ] Implement idempotency mechanism
- [ ] Unit tests for core business logic
- [ ] API integration tests

**Deliverables**:
- Working cloud backend with REST API
- Database migrations
- API documentation
- Unit and integration tests

**Exit Criteria**:
- All API endpoints tested and working
- Idempotency verified
- Load testing passed (100 concurrent requests)
- API documentation complete

### Phase 2: Windows Agent for POS (Week 5-6)
**Status**: Not Started

- [ ] Implement local Windows service/agent
- [ ] Integrate with USB NFC reader (PC/SC)
- [ ] Implement offline queue persistence
- [ ] Implement sync logic with cloud backend
- [ ] Detect Aniwin.net sales (database hook or file export)
- [ ] Automatic points earning on sale
- [ ] UI for card enrollment
- [ ] UI for manual redemption
- [ ] UI for balance query
- [ ] Sync status indicator

**Deliverables**:
- Windows agent installer
- NFC reader drivers and configuration
- Offline queue implementation
- User manual for cashiers (Spanish + Catalan)

**Exit Criteria**:
- Agent runs as Windows service
- Offline mode tested (24h without internet)
- Sync tested with 100+ queued transactions
- UI tested with real NFC cards
- Integration with Aniwin.net verified

### Phase 3: PrestaShop Module (Week 7-8)
**Status**: Not Started

- [ ] Create PrestaShop 9.1.0 module skeleton
- [ ] Implement REST API client for loyalty backend
- [ ] Hook into order completion (earn points)
- [ ] Create voucher/cart rule for redemption
- [ ] Display balance on customer account page
- [ ] Hook into refund (reverse points)
- [ ] Admin UI for loyalty configuration
- [ ] Test with PrestaShop test store

**Deliverables**:
- PrestaShop module package
- Installation and configuration guide
- Admin user manual
- Customer-facing documentation

**Exit Criteria**:
- Module installs cleanly on PS 9.1.0
- Earn/redeem/refund flows tested end-to-end
- No core PrestaShop modifications required
- Module passes PrestaShop validator

### Phase 4: Sync and Conflict Resolution (Week 9)
**Status**: Not Started

- [ ] Implement conflict detection algorithms
- [ ] Implement conflict resolution rules
- [ ] Add sync retry logic with exponential backoff
- [ ] Add sync monitoring and alerting
- [ ] Test edge cases (network failures, duplicates)
- [ ] Test large sync backlogs
- [ ] Document all conflict scenarios

**Deliverables**:
- Conflict resolution implementation
- Sync monitoring dashboard (basic)
- Runbook for common sync issues
- Test report for edge cases

**Exit Criteria**:
- All conflict scenarios handled correctly
- No transaction loss in any test scenario
- Sync completes in < 5 minutes for 1000 transactions

### Phase 5: Messaging and Notifications (Week 10)
**Status**: Not Started

- [ ] Implement email sending (welcome, transaction, balance)
- [ ] Integrate WhatsApp API for balance queries
- [ ] Implement receipt formatting logic
- [ ] Configure email templates (Spanish + Catalan)
- [ ] Configure WhatsApp message templates
- [ ] Test message delivery
- [ ] Test WhatsApp keyword parsing

**Deliverables**:
- Email service integration
- WhatsApp integration
- Message templates
- Test results

**Exit Criteria**:
- All message types deliver successfully
- WhatsApp responds to "Saldo" within 5 seconds
- Messages correctly formatted in both languages

### Phase 6: Business Rules and Expiration (Week 11)
**Status**: Not Started

- [ ] Implement expiration batch job
- [ ] Implement earn rate calculation
- [ ] Implement redemption validation
- [ ] Implement manual adjustment with audit log
- [ ] Schedule nightly expiration job
- [ ] Test expiration logic thoroughly
- [ ] Test edge cases (same-day earn/expire, etc.)

**Deliverables**:
- Business rule engine
- Expiration job implementation
- Scheduled job configuration
- Test results for all rule edge cases

**Exit Criteria**:
- Expiration job runs nightly without errors
- All earn/redeem calculations verified correct
- Manual adjustment audit trail verified

### Phase 7: Hardware Setup and Testing (Week 12)
**Status**: Not Started

- [ ] Receive and test NFC cards
- [ ] Receive and test USB NFC readers
- [ ] Set up card printing (or order printed cards)
- [ ] Test end-to-end with real hardware
- [ ] Train staff on hardware usage
- [ ] Create quick reference guides

**Deliverables**:
- Tested hardware
- Printed cards
- Hardware setup documentation
- Quick reference guides (laminated)

**Exit Criteria**:
- NFC reader reads cards reliably (>99% success rate)
- Cards print with correct customer information
- Staff successfully complete test transactions

### Phase 8: Integration Testing and Pilot (Week 13-14)
**Status**: Not Started

- [ ] End-to-end testing in test environment
- [ ] Performance testing under load
- [ ] Offline scenario testing
- [ ] Disaster recovery testing
- [ ] Security testing
- [ ] Pilot with 10-20 customers
- [ ] Collect feedback from staff and customers
- [ ] Fix critical issues discovered in pilot

**Deliverables**:
- Test report (all scenarios)
- Performance test results
- Pilot feedback report
- Bug fixes from pilot

**Exit Criteria**:
- All critical bugs fixed
- Performance targets met
- Staff comfortable with system
- Pilot customers successfully enrolled and transacting

### Phase 9: Production Deployment (Week 15)
**Status**: Not Started

- [ ] Deploy backend to production cloud environment
- [ ] Configure production database with backups
- [ ] Install Windows agent on production terminal
- [ ] Install PrestaShop module on production site
- [ ] Configure monitoring and alerting
- [ ] Create runbooks for operations
- [ ] Final staff training session
- [ ] Go-live

**Deliverables**:
- Production system live
- Monitoring dashboards configured
- Operations runbooks
- Support contact information

**Exit Criteria**:
- System live and processing real transactions
- Monitoring confirms healthy operation
- Staff successfully onboarded
- Support procedures in place

### Phase 10: Post-Launch Support (Week 16+)
**Status**: Not Started

- [ ] Monitor for issues
- [ ] Respond to support requests
- [ ] Tune performance based on real usage
- [ ] Collect enhancement requests
- [ ] Plan next iteration

**Deliverables**:
- Support log
- Performance optimization results
- Enhancement backlog

## Deviations from Original Plan

### Deviation Log

*No deviations yet - project is in planning phase.*

When deviations occur, log them here with:
- Date
- Original plan
- Actual implementation
- Reason for deviation
- Risks introduced
- Mitigation plan

**Example Format**:

> **Date**: 2026-03-15  
> **Component**: Aniwin POS Integration  
> **Original Plan**: Use database hook to detect sales  
> **Actual Implementation**: Use file export polling  
> **Reason**: Database access not available due to Aniwin security policy  
> **Risks**: 30-second delay in points award, potential missed transactions if file corrupted  
> **Mitigation**: Add file validation, add retry logic, add manual reconciliation report  
> **Documentation Updated**: `04_integrations/ANIWIN_POS_INTEGRATION.md`

## Technical Debt

### Current Technical Debt

*No technical debt yet - project is in planning phase.*

Technical debt items will be tracked here with:
- Description of the shortcut taken
- Why it was necessary
- Impact on system
- Plan to resolve
- Target date for resolution

**Example Format**:

> **Item**: Basic conflict resolution only  
> **Description**: Implemented "last-write-wins" for conflicts instead of sophisticated CRDT  
> **Reason**: Time constraint for MVP  
> **Impact**: Rare edge case where offline terminal with stale data can cause incorrect balance  
> **Resolution Plan**: Implement proper CRDT or operational transformation  
> **Target**: Post-MVP iteration 2  
> **Risk**: Low - only occurs if terminal offline for >24h then syncs overlapping transaction

## Postponed Items

### Features Postponed from MVP

Items explicitly deferred to post-MVP:

1. **Customer Web Portal**
   - Reason: Can use PrestaShop account page initially
   - Target: Iteration 2 (Q2 2026)

2. **Points Expiration Notifications**
   - Reason: Email infrastructure in place, but notification logic postponed
   - Target: Iteration 1 (Q1 2026)

3. **Advanced Fraud Detection**
   - Reason: Acceptable risk for MVP based on business context
   - Target: Review after 6 months of operation

4. **Multi-Terminal Support**
   - Reason: Only 1 terminal currently; architecture supports multiple but not tested
   - Target: When second terminal purchased (TBD)

5. **QR Code Fallback**
   - Reason: NFC is primary; QR code can be added if NFC issues arise
   - Target: Only if needed

6. **Partial Refund Handling**
   - Reason: Business only does full refunds; manual adjustment can handle edge cases
   - Target: Only if business process changes

## Architectural Changes

### Change Log

*No architectural changes yet - project is in planning phase.*

When architecture changes, document:
- Original architecture decision
- New architecture decision
- Reason for change
- Components affected
- Migration required (if any)
- Documentation updated

## Risks Discovered During Implementation

### Risk Register

*No implementation risks yet - project is in planning phase.*

As implementation progresses, log risks discovered:

| Risk | Likelihood | Impact | Mitigation | Owner | Status |
|------|-----------|---------|-----------|-------|--------|
| Example: Aniwin.net no database access | Medium | High | Use file export | Tech Lead | Open |

## Open Questions

### Critical Questions (Blocking)

*None currently*

### Important Questions (Not Blocking)

1. **NFC Card Vendor**: Need to select specific card and reader models
2. **Card Printing**: In-house printer or pre-printed cards from vendor?
3. **WhatsApp API Provider**: Which WhatsApp Business API provider to use?
4. **Hosting Provider**: AWS, Azure, DigitalOcean, or other?
5. **Email Provider**: SendGrid, Amazon SES, or other?

## Dependencies

### External Dependencies

- **Aniwin.net**: POS integration method must be determined
- **PrestaShop**: Version 9.1.0 compatibility must be verified
- **Hardware Vendors**: NFC cards and readers must be sourced
- **WhatsApp Provider**: API access must be obtained
- **Hosting Provider**: Cloud infrastructure must be provisioned

### Internal Dependencies

- Technology stack decision affects all development work
- Backend must be complete before Windows agent can fully integrate
- Windows agent must be stable before PrestaShop integration testing
- Hardware must arrive before end-to-end testing

## Success Metrics

### MVP Success Criteria

- [ ] System deployed to production
- [ ] At least 10 customers enrolled
- [ ] 100% of transactions in pilot period successful
- [ ] Offline mode tested with 24h disconnect
- [ ] Zero data loss in all testing
- [ ] Staff trained and comfortable
- [ ] No critical bugs in production

### Long-Term Success Metrics

- **Customer Adoption**: >50% of regular customers enrolled within 6 months
- **Transaction Speed**: <5 seconds added to checkout time
- **System Uptime**: >99% uptime for cloud backend
- **Sync Reliability**: >99.9% of offline transactions sync successfully
- **Customer Satisfaction**: >80% of loyalty customers satisfied with program

## Related Documents

### Planning Documents
- `01_project/PROJECT_OVERVIEW.md` - Overall project scope and goals
- `00_meta/SESSION_START.md` - Session workflow checklist
- `08_prompts/AGENT_WORKFLOW.md` - Agent workflow guidelines

### Architecture Documents
- `02_architecture/SYSTEM_ARCHITECTURE.md` - Overall system design
- All files in `02_architecture/` - Component-specific architecture

### Feature Documents
- All files in `03_features/` - Feature specifications

### Integration Documents
- All files in `04_integrations/` - Integration specifications
