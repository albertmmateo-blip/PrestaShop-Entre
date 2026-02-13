# System Architecture Overview

## Purpose

This document describes the overall architecture of the Fidelity Points loyalty system, including all major components and their interactions.

## Scope

Covers:
- High-level system components
- Component interactions
- Technology choices
- Deployment architecture
- Integration points

Does not cover:
- Detailed component internals (see component-specific docs)
- Specific business rules (see feature docs)
- Detailed data models (see data docs)

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CUSTOMERS                                │
│  ┌──────────────────┐              ┌──────────────────────────┐ │
│  │ Physical Store   │              │  Online Store            │ │
│  │ NFC Card Tap     │              │  PrestaShop 9.1.0        │ │
│  └────────┬─────────┘              └──────────┬───────────────┘ │
└───────────┼────────────────────────────────────┼─────────────────┘
            │                                    │
            │                                    │
┌───────────▼──────────────────┐    ┌───────────▼──────────────┐
│  Windows Terminal (POS)      │    │  PrestaShop Module       │
│  ┌────────────────────────┐  │    │  (Loyalty Plugin)        │
│  │  Windows Agent/Service │  │    └──────────┬───────────────┘
│  │  - NFC Reader Driver   │  │               │
│  │  - Offline Queue       │  │               │ REST API
│  │  - Local UI            │  │               │ (Always Online)
│  │  - Aniwin Integration  │  │               │
│  └───────┬────────────────┘  │               │
│          │ REST API           │               │
│          │ (Offline Capable)  │               │
└──────────┼────────────────────┘               │
           │                                    │
           │     ┌──────────────────────────────┘
           │     │
┌──────────▼─────▼──────────────────────────────────────────┐
│              CLOUD LOYALTY BACKEND                         │
│  ┌───────────────────────────────────────────────────────┐│
│  │  REST API (Node.js/TypeScript or Python FastAPI)      ││
│  │  - Earn Points                                         ││
│  │  - Redeem Points                                       ││
│  │  - Refund/Reverse                                      ││
│  │  - Balance Query                                       ││
│  │  - Card Management                                     ││
│  │  - Manual Adjustments                                  ││
│  │  - Idempotency Management                              ││
│  └───────────────────────────────────────────────────────┘│
│  ┌───────────────────────────────────────────────────────┐│
│  │  PostgreSQL Database                                   ││
│  │  - Customers                                           ││
│  │  - Cards (NFC UIDs)                                    ││
│  │  - Loyalty Accounts                                    ││
│  │  - Immutable Ledger                                    ││
│  │  - Order Mapping                                       ││
│  │  - Idempotency Keys                                    ││
│  └───────────────────────────────────────────────────────┘│
│  ┌───────────────────────────────────────────────────────┐│
│  │  Background Jobs                                       ││
│  │  - Expiration Processing (nightly)                     ││
│  │  - Notification Sending                                ││
│  └───────────────────────────────────────────────────────┘│
└────────────────────┬───────────────────┬───────────────────┘
                     │                   │
              ┌──────▼────────┐    ┌────▼──────────┐
              │  Email        │    │  WhatsApp     │
              │  Service      │    │  Business API │
              │  (SendGrid/   │    │               │
              │   SES)        │    │               │
              └───────────────┘    └───────────────┘
```

## Core Components

### 1. Cloud Loyalty Backend

**Technology**: Node.js + TypeScript + PostgreSQL (default) OR Python FastAPI + PostgreSQL  
**Hosting**: Cloud (AWS, Azure, DigitalOcean, etc.)  
**Purpose**: Central loyalty transaction processing and data storage

**Responsibilities**:
- Process earn, redeem, refund, adjustment transactions
- Maintain immutable loyalty ledger
- Compute balances from ledger
- Enforce business rules
- Manage idempotency (prevent duplicates)
- Provide REST API for Windows agent and PrestaShop module
- Execute background jobs (expiration, notifications)
- Send emails and WhatsApp messages

**Key Characteristics**:
- Stateless API (horizontal scalability)
- Idempotent operations (safe retries)
- Append-only ledger (audit trail)
- Balance computed on-demand (not stored directly)

**See**: `02_architecture/CLOUD_BACKEND.md` for details

### 2. Windows Agent / Service

**Technology**: C# .NET OR Electron + Node.js OR Python (TBD based on stack choice)  
**Deployment**: Runs on Windows terminal at POS  
**Purpose**: Offline-capable loyalty operations at physical store

**Responsibilities**:
- Read NFC cards via USB reader (PC/SC)
- Display balance and transaction UI (Spanish + Catalan)
- Queue transactions when offline
- Sync queued transactions when online
- Integrate with Aniwin.net POS (detect sales, earn points)
- Handle manual redemptions at POS
- Provide sync status feedback to cashier

**Key Characteristics**:
- Offline-first design (can operate with no internet)
- Persistent queue (survives restarts)
- Automatic sync when connection available
- Clear UI feedback for offline/sync status

**See**: `02_architecture/WINDOWS_AGENT.md` for details

### 3. PrestaShop Module

**Technology**: PHP (PrestaShop module)  
**Deployment**: Installed on PrestaShop 9.1.0  
**Purpose**: Loyalty integration for e-commerce

**Responsibilities**:
- Call cloud backend API on order completion (earn points)
- Create cart rules/vouchers for redemptions (redeem points)
- Display customer balance on account page
- Handle refunds (reverse points)
- Admin UI for loyalty configuration
- No core PrestaShop modifications

**Key Characteristics**:
- Always online (no offline requirement)
- Uses standard PrestaShop hooks
- REST API client to loyalty backend
- Handles API failures gracefully

**See**: `04_integrations/PRESTASHOP_MODULE.md` for details

### 4. PostgreSQL Database

**Technology**: PostgreSQL 14+  
**Deployment**: Cloud (managed service recommended)  
**Purpose**: Central data storage

**Key Tables**:
- `customers` - Customer master data
- `cards` - NFC card UIDs and assignments
- `loyalty_accounts` - Account metadata
- `loyalty_ledger` - Immutable transaction log (append-only)
- `order_mapping` - POS ↔ PrestaShop order mapping
- `consent_records` - GDPR consent tracking
- `idempotency_keys` - Duplicate prevention

**Key Characteristics**:
- Ledger table is append-only (no updates, no deletes)
- Balances computed via SUM aggregate, not stored
- Foreign key constraints for referential integrity
- Indexes for performance

**See**: `05_data/DATA_MODEL.md` for schema details

### 5. Integration Points

#### Aniwin.net POS
**Type**: One-way read integration (POS → Loyalty)  
**Method**: TBD (database hook, file export, or receipt intercept)  
**Purpose**: Detect completed sales, award points automatically

**See**: `04_integrations/ANIWIN_POS_INTEGRATION.md`

#### NFC Hardware
**Type**: USB NFC reader (PC/SC protocol)  
**Cards**: MIFARE Classic or compatible (UID-only)  
**Purpose**: Customer identification via card tap

**See**: `04_integrations/NFC_HARDWARE.md`

#### Email Service
**Type**: Transactional email API  
**Provider**: SendGrid, Amazon SES, or similar  
**Purpose**: Send receipts, notifications, balance info

#### WhatsApp Business API
**Type**: WhatsApp Cloud API or provider  
**Purpose**: Balance queries via "Saldo" keyword

**See**: `04_integrations/WHATSAPP_MESSAGING.md`

## Data Flow

### Earn Points Flow (Physical Store)

```
1. Customer makes purchase in Aniwin POS
2. Sale recorded in Aniwin database/file
3. Windows Agent detects new sale
4. Windows Agent reads customer card (NFC tap)
5. Windows Agent calls Backend API: POST /transactions/earn
   - If offline: queued locally
   - If online: immediate API call
6. Backend validates, appends to ledger
7. Backend returns new balance
8. Windows Agent displays confirmation
9. Receipt printed with points earned
```

### Redeem Points Flow (Physical Store)

```
1. Cashier initiates redemption in Windows Agent
2. Customer taps NFC card
3. Windows Agent calls Backend API: GET /customers/{uid}/balance
4. Balance displayed to cashier
5. Cashier enters redemption amount
6. Windows Agent calls Backend API: POST /transactions/redeem
   - If offline: queued locally (with current balance check)
   - If online: immediate API call
7. Backend validates balance, appends to ledger
8. Backend returns new balance
9. Windows Agent applies discount in Aniwin POS
10. Receipt printed with points redeemed
```

### Earn Points Flow (Online)

```
1. Customer completes order in PrestaShop
2. PrestaShop triggers order completion hook
3. PrestaShop Module calls Backend API: POST /transactions/earn
4. Backend validates, appends to ledger
5. Backend returns new balance
6. Customer receives email with points earned
```

### Redeem Points Flow (Online)

```
1. Customer requests redemption on cart page
2. PrestaShop Module calls Backend API: GET /customers/{prestashop_id}/balance
3. Balance displayed to customer
4. Customer enters redemption amount
5. PrestaShop Module calls Backend API: POST /transactions/redeem
6. Backend validates balance, appends to ledger, returns voucher code
7. PrestaShop Module creates cart rule with voucher code
8. Discount applied to cart
9. Order completed
10. Customer receives email with points redeemed
```

### Offline Sync Flow

```
1. Windows Agent periodically checks internet connectivity
2. If online and queue not empty:
   a. Read next queued transaction
   b. Call Backend API with idempotency key
   c. If success: remove from queue
   d. If failure: retry with exponential backoff
   e. If conflict: apply resolution rules
   f. Update sync status UI
3. Repeat until queue empty or connection lost
```

## Technology Stack

### Backend (PENDING DECISION)

**Option A: Node.js + TypeScript**
- Framework: Express or Fastify
- ORM: TypeORM or Prisma
- Testing: Jest
- API Documentation: OpenAPI/Swagger

**Option B: Python FastAPI**
- Framework: FastAPI
- ORM: SQLAlchemy or Tortoise ORM
- Testing: pytest
- API Documentation: OpenAPI (built-in)

### Database
- PostgreSQL 14+ (required for all options)
- Migration tool: Flyway, Liquibase, or ORM migrations

### Windows Agent (depends on backend choice)
- Option A: C# .NET 6+ (best Windows integration)
- Option B: Electron + Node.js (reuse backend code)
- Option C: Python + PyQt (if Python backend)

### PrestaShop Module
- PHP 7.4+ (PrestaShop 9.1.0 requirement)
- PrestaShop module framework
- Guzzle HTTP client (for REST API calls)

### Infrastructure
- Cloud hosting: AWS, Azure, or DigitalOcean
- Database: Managed PostgreSQL service
- Load balancer: Cloud-provided
- TLS: Let's Encrypt or cloud-provided certificates
- Backups: Automated daily database backups

## Deployment Architecture

### Production Environment

```
┌──────────────────────────────────────────────────┐
│  Cloud Provider (AWS/Azure/DigitalOcean)         │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │  Load Balancer (TLS Termination)            │ │
│  └─────────────┬───────────────────────────────┘ │
│                │                                  │
│  ┌─────────────▼────────────┬─────────────────┐ │
│  │  Backend API Server 1    │  Server 2 (opt) │ │
│  │  (Stateless, Auto-scale) │                  │ │
│  └──────────────────────────┴─────────────────┘ │
│                │                                  │
│  ┌─────────────▼──────────────────────────────┐ │
│  │  Managed PostgreSQL Database                │ │
│  │  - Primary + Standby                        │ │
│  │  - Automated Backups                        │ │
│  │  - Point-in-time Recovery                   │ │
│  └────────────────────────────────────────────┘ │
│                                                   │
│  ┌────────────────────────────────────────────┐ │
│  │  Background Job Runner (optional separate) │ │
│  │  - Expiration Job                          │ │
│  │  - Notification Queue                      │ │
│  └────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘

┌──────────────────┐       ┌────────────────────┐
│  Email Service   │       │  WhatsApp Provider │
│  (SendGrid/SES)  │       │  (Twilio/etc)      │
└──────────────────┘       └────────────────────┘
```

### On-Premises Environment

```
┌─────────────────────────────────────┐
│  Physical Store                     │
│                                      │
│  ┌────────────────────────────────┐ │
│  │  Windows Terminal              │ │
│  │  ┌──────────────────────────┐  │ │
│  │  │  Windows Agent           │  │ │
│  │  │  - Offline Queue DB      │  │ │
│  │  └──────────────────────────┘  │ │
│  │  ┌──────────────────────────┐  │ │
│  │  │  Aniwin POS              │  │ │
│  │  └──────────────────────────┘  │ │
│  │  ┌──────────────────────────┐  │ │
│  │  │  USB NFC Reader          │  │ │
│  │  └──────────────────────────┘  │ │
│  └────────────────────────────────┘ │
│             │                        │
│             │ Internet (when         │
│             │ available)             │
└─────────────┼──────────────────────┘
              │
              ▼
        Cloud Backend
```

## Non-Functional Requirements

### Performance
- API response time: < 500ms (p95)
- NFC card read to balance display: < 2 seconds
- Offline transaction queue: handle 1000+ transactions
- Sync throughput: 100 transactions per minute minimum

### Availability
- Cloud backend: 99% uptime target
- POS operations: 100% uptime (via offline mode)
- PrestaShop operations: Depends on PrestaShop hosting (no offline)

### Scalability
- Support 1-10 terminals initially
- Support 10,000+ customers
- Support 100,000+ transactions per year
- Horizontal scaling of backend API servers

### Security
- TLS for all API communication
- API authentication via per-terminal credentials
- No sensitive data in logs
- Audit trail for all transactions
- GDPR compliance for customer data

### Reliability
- No data loss (even in offline scenarios)
- Idempotent operations (safe retries)
- Conflict resolution for sync edge cases
- Automatic recovery from transient failures

### Maintainability
- Comprehensive documentation
- Automated tests (unit, integration, e2e)
- Logging and monitoring
- Clear error messages
- Runbooks for common issues

## Constraints

### Technical Constraints
1. **No POS Modification** - Aniwin.net cannot be modified; integration via database/file/receipt
2. **Windows Only** - POS terminals run Windows; agent must be Windows-compatible
3. **PrestaShop 9.1.0** - Must work with this specific version
4. **Offline Requirement** - POS must function without internet
5. **Ledger Immutability** - Ledger entries cannot be modified or deleted

### Business Constraints
1. **Budget** - Hardware budget limited to 1000 EUR
2. **UID-Only Cards** - Must work with simple UID-only NFC cards (cloneable)
3. **No PIN** - No PIN or password verification for redemptions
4. **Full Refunds Only** - System only handles full order refunds
5. **Single Currency** - EUR only

### Operational Constraints
1. **Minimal Training** - Staff must be able to use system with < 30 minutes training
2. **Fast Transactions** - Loyalty transaction adds < 5 seconds to checkout
3. **Self-Service** - System should require minimal IT support
4. **Languages** - POS UI must support Spanish and Catalan

## Failure Modes and Mitigations

| Failure | Impact | Mitigation |
|---------|--------|------------|
| Backend API down | POS can't sync | Offline queue; operations continue |
| Internet connection lost | POS can't sync | Offline queue; auto-reconnect |
| NFC reader failure | Can't read cards | Manual card number entry (fallback) |
| Aniwin POS down | No sales detection | Manual reconciliation when POS restored |
| Database failure | Backend unavailable | Database standby failover; backups |
| Duplicate transaction | Points awarded twice | Idempotency keys prevent duplicates |
| Sync conflict | Inconsistent state | Conflict resolution rules applied |
| PrestaShop down | E-commerce unavailable | POS unaffected; e-commerce independent |

## Security Model

### Authentication
- **Terminal Authentication**: Per-terminal API keys
- **PrestaShop Authentication**: Module-specific API key
- **Customer Identification**: NFC card UID (no additional auth)

### Authorization
- **Terminals**: Can earn, redeem, query for their customers
- **PrestaShop**: Can earn, redeem, query for PrestaShop customers
- **Managers**: Can manual-adjust (no permission system in MVP)

### Data Protection
- **In Transit**: TLS 1.2+ for all API calls
- **At Rest**: Database encryption (cloud provider)
- **PII**: Customer names, emails, phones encrypted (future enhancement)
- **Audit**: All operations logged with timestamp, terminal, operator

### Threat Model
- **Acceptable Risks**: UID cloning, no cashier fraud prevention
- **Not Acceptable**: SQL injection, XSS, data breach, transaction tampering

**See**: `06_security/SECURITY_MODEL.md` for complete threat model

## Monitoring and Observability

### Metrics to Track
- API request rate and latency
- Database query performance
- Sync queue depth per terminal
- Sync failure rate
- Transaction success rate
- NFC read success rate
- Background job execution time

### Logging
- All API requests (timestamp, terminal, endpoint, status)
- All ledger appends (transaction details)
- All sync events (success, failure, conflict)
- All errors (with stack traces)

### Alerting
- Backend API down
- Database down
- Sync queue depth > 1000 transactions
- Sync failures > 10% over 1 hour
- Expiration job failed

## Open Questions

1. **Technology Stack**: Node.js or Python? (PENDING USER CHOICE)
2. **Windows Agent Tech**: C#, Electron, or Python?
3. **Cloud Provider**: AWS, Azure, or DigitalOcean?
4. **Email Provider**: SendGrid, Amazon SES, or other?
5. **WhatsApp Provider**: Twilio, MessageBird, or other?
6. **NFC Card Model**: Exact card specifications?
7. **NFC Reader Model**: Exact reader model?
8. **Aniwin Integration Method**: Database, file, or receipt?

## Related Documents

### Component Details
- `02_architecture/CLOUD_BACKEND.md` - Backend API details
- `02_architecture/WINDOWS_AGENT.md` - Windows agent details
- `02_architecture/SYNC_STRATEGY.md` - Sync logic details
- `02_architecture/CONFLICT_RESOLUTION.md` - Conflict handling

### Integrations
- `04_integrations/ANIWIN_POS_INTEGRATION.md` - POS integration
- `04_integrations/PRESTASHOP_MODULE.md` - PrestaShop integration
- `04_integrations/NFC_HARDWARE.md` - NFC hardware
- `04_integrations/WHATSAPP_MESSAGING.md` - WhatsApp integration

### Data
- `05_data/DATA_MODEL.md` - Database schema
- `05_data/LOYALTY_LEDGER.md` - Ledger design

### Security
- `06_security/SECURITY_MODEL.md` - Security details
- `06_security/IDEMPOTENCY.md` - Duplicate prevention

### Operations
- `07_operations/OFFLINE_QUEUE.md` - Offline queue details
- `07_operations/ERROR_HANDLING.md` - Error handling
