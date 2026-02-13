# Cloud Backend Architecture

## Purpose

This document describes the architecture, API contracts, and implementation requirements for the cloud-based loyalty backend service.

## Scope

Covers:
- Backend technology stack
- REST API endpoints and contracts
- Database interactions
- Business logic implementation
- Background jobs
- Scalability and deployment

Does not cover:
- Data model details (see `05_data/DATA_MODEL.md`)
- Integration with specific clients (see integration docs)
- Operational procedures (see operations docs)

## Technology Stack (PENDING DECISION)

### Option A: Node.js + TypeScript (DEFAULT)

**Framework**: Express or Fastify
- Express: Mature, extensive middleware ecosystem
- Fastify: Better performance, TypeScript-first

**ORM**: TypeORM or Prisma
- TypeORM: Mature, supports migrations, decorator-based
- Prisma: Modern, excellent TypeScript support, auto-generated client

**Testing**: Jest
- Unit tests with mocks
- Integration tests with test database
- API tests with supertest

**Validation**: Zod or class-validator
- Request/response schema validation
- Type-safe validation

**Documentation**: OpenAPI/Swagger
- Auto-generated from code
- Interactive API explorer

### Option B: Python FastAPI

**Framework**: FastAPI
- Built-in OpenAPI documentation
- Excellent performance (async)
- Type hints and Pydantic validation

**ORM**: SQLAlchemy or Tortoise ORM
- SQLAlchemy: Industry standard, mature
- Tortoise ORM: Async-first, similar to TypeORM

**Testing**: pytest
- Unit tests with mocks
- Integration tests with test database
- API tests with TestClient

**Validation**: Pydantic (built into FastAPI)
- Request/response models
- Type-safe validation

### Common Components

**Database**: PostgreSQL 14+
**Migration Tool**: Flyway, Liquibase, or ORM migrations
**Logging**: Structured JSON logs (for cloud ingestion)
**Monitoring**: Prometheus metrics + Grafana OR cloud provider metrics
**Authentication**: JWT tokens or API keys
**Rate Limiting**: Redis-backed rate limiter

## REST API Specification

### Base URL

```
Production: https://api.loyalty.example.com/v1
Development: https://api-dev.loyalty.example.com/v1
```

### Authentication

**Method**: API Key in header

```http
Authorization: Bearer {API_KEY}
X-Terminal-ID: {TERMINAL_ID}  (for POS requests)
X-Module-ID: {MODULE_ID}      (for PrestaShop requests)
```

Each terminal and PrestaShop installation has unique credentials.

### Idempotency

All state-changing requests (POST, PUT, PATCH) require an idempotency key:

```http
Idempotency-Key: {UNIQUE_REQUEST_ID}
```

- Format: UUID v4 recommended
- Stored for 24 hours minimum
- Same key + same request = same response (no duplicate operation)
- Different key + same data = new operation

### Common Response Format

**Success Response:**
```json
{
  "status": "success",
  "data": { ... },
  "meta": {
    "timestamp": "2026-02-13T12:34:56Z",
    "request_id": "uuid"
  }
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": {
    "code": "INSUFFICIENT_BALANCE",
    "message": "Customer has insufficient balance",
    "details": {
      "requested": 10.00,
      "available": 5.50
    }
  },
  "meta": {
    "timestamp": "2026-02-13T12:34:56Z",
    "request_id": "uuid"
  }
}
```

### API Endpoints

#### 1. Card Lookup

**Endpoint**: `GET /cards/{uid}`

**Purpose**: Look up customer by NFC card UID

**Request:**
```http
GET /cards/04A1B2C3D4E5F6
Authorization: Bearer {API_KEY}
X-Terminal-ID: TERM-001
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "card_id": "uuid",
    "card_uid": "04A1B2C3D4E5F6",
    "card_number": "LC-00001234",
    "status": "active",
    "customer": {
      "customer_id": "uuid",
      "name": "Juan García",
      "phone": "+34612345678",
      "email": "juan@example.com",
      "prestashop_customer_id": 123
    }
  }
}
```

**Error Codes:**
- `404 CARD_NOT_FOUND` - Card UID not registered
- `403 CARD_INACTIVE` - Card exists but is deactivated

#### 2. Get Balance

**Endpoint**: `GET /customers/{customer_id}/balance`

**Purpose**: Query current loyalty balance

**Request:**
```http
GET /customers/{uuid}/balance
Authorization: Bearer {API_KEY}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "customer_id": "uuid",
    "balance_euros": 12.50,
    "balance_points": 125000,
    "transactions_count": 42,
    "last_transaction": "2026-02-10T15:30:00Z",
    "expiring_soon": {
      "amount_euros": 2.00,
      "expiry_date": "2026-03-15"
    }
  }
}
```

#### 3. Earn Points

**Endpoint**: `POST /transactions/earn`

**Purpose**: Award points for a purchase

**Request:**
```http
POST /transactions/earn
Authorization: Bearer {API_KEY}
X-Terminal-ID: TERM-001
Idempotency-Key: {UUID}
Content-Type: application/json

{
  "customer_id": "uuid",
  "order_id": "POS-2026021312345",
  "order_source": "aniwin_pos",
  "terminal_id": "TERM-001",
  "order_amount_euros": 100.00,
  "order_timestamp": "2026-02-13T12:34:56Z",
  "metadata": {
    "items_count": 5
  }
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "transaction_id": "uuid",
    "customer_id": "uuid",
    "transaction_type": "earn",
    "amount_euros": 1.50,
    "amount_points": 15000,
    "order_id": "POS-2026021312345",
    "new_balance_euros": 14.00,
    "new_balance_points": 140000,
    "timestamp": "2026-02-13T12:34:56Z"
  }
}
```

**Business Rule**: amount_euros = order_amount_euros * 0.015

**Error Codes:**
- `400 INVALID_ORDER_AMOUNT` - Order amount must be positive
- `404 CUSTOMER_NOT_FOUND` - Customer does not exist
- `409 DUPLICATE_TRANSACTION` - Idempotency key already used with different data

#### 4. Redeem Points

**Endpoint**: `POST /transactions/redeem`

**Purpose**: Redeem points for discount

**Request:**
```http
POST /transactions/redeem
Authorization: Bearer {API_KEY}
X-Terminal-ID: TERM-001
Idempotency-Key: {UUID}
Content-Type: application/json

{
  "customer_id": "uuid",
  "redemption_amount_euros": 10.00,
  "order_id": "POS-2026021312346",
  "order_source": "aniwin_pos",
  "terminal_id": "TERM-001",
  "order_timestamp": "2026-02-13T12:45:00Z"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "transaction_id": "uuid",
    "customer_id": "uuid",
    "transaction_type": "redeem",
    "amount_euros": -10.00,
    "amount_points": -100000,
    "order_id": "POS-2026021312346",
    "new_balance_euros": 4.00,
    "new_balance_points": 40000,
    "voucher_code": "LOYALTY-ABC123",
    "timestamp": "2026-02-13T12:45:00Z"
  }
}
```

**Validation**:
- redemption_amount_euros must be positive
- redemption_amount_euros must be <= current balance

**Error Codes:**
- `400 INSUFFICIENT_BALANCE` - Not enough points
- `400 INVALID_REDEMPTION_AMOUNT` - Amount must be positive

#### 5. Refund / Reverse

**Endpoint**: `POST /transactions/refund`

**Purpose**: Reverse points for refunded order

**Request:**
```http
POST /transactions/refund
Authorization: Bearer {API_KEY}
X-Terminal-ID: TERM-001
Idempotency-Key: {UUID}
Content-Type: application/json

{
  "original_order_id": "POS-2026021312345",
  "refund_timestamp": "2026-02-14T10:00:00Z",
  "reason": "Customer return"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "reversal_transactions": [
      {
        "transaction_id": "uuid",
        "customer_id": "uuid",
        "transaction_type": "reversal_earn",
        "amount_euros": -1.50,
        "amount_points": -15000,
        "original_transaction_id": "uuid",
        "timestamp": "2026-02-14T10:00:00Z"
      }
    ],
    "new_balance_euros": 12.50,
    "new_balance_points": 125000
  }
}
```

**Logic**:
- Find all transactions (earn, redeem) for original_order_id
- Create reversal transaction for each (inverse amount)
- If balance goes negative, allow it (customer owes points)

**Error Codes:**
- `404 ORDER_NOT_FOUND` - Original order not found
- `409 ALREADY_REFUNDED` - Order already refunded

#### 6. Manual Adjustment

**Endpoint**: `POST /transactions/adjust`

**Purpose**: Manually adjust customer balance (manager only)

**Request:**
```http
POST /transactions/adjust
Authorization: Bearer {MANAGER_API_KEY}
X-Terminal-ID: TERM-001
Idempotency-Key: {UUID}
Content-Type: application/json

{
  "customer_id": "uuid",
  "adjustment_amount_euros": 5.00,
  "reason_code": "GOODWILL",
  "reason_description": "Compensation for service issue",
  "operator": "Manager Maria"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "transaction_id": "uuid",
    "customer_id": "uuid",
    "transaction_type": "adjustment",
    "amount_euros": 5.00,
    "amount_points": 50000,
    "new_balance_euros": 17.50,
    "new_balance_points": 175000,
    "reason": "Compensation for service issue",
    "timestamp": "2026-02-14T11:00:00Z"
  }
}
```

**Validation**:
- Requires manager-level API key
- adjustment_amount_euros can be positive or negative
- reason_code and reason_description are required

#### 7. Enroll Customer

**Endpoint**: `POST /customers`

**Purpose**: Create new customer and assign card

**Request:**
```http
POST /customers
Authorization: Bearer {API_KEY}
X-Terminal-ID: TERM-001
Idempotency-Key: {UUID}
Content-Type: application/json

{
  "name": "Juan García",
  "phone": "+34612345678",
  "email": "juan@example.com",
  "card_uid": "04A1B2C3D4E5F6",
  "prestashop_customer_id": null,
  "consent_loyalty": true,
  "consent_marketing": false,
  "language": "es"
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "data": {
    "customer_id": "uuid",
    "name": "Juan García",
    "phone": "+34612345678",
    "email": "juan@example.com",
    "card": {
      "card_id": "uuid",
      "card_uid": "04A1B2C3D4E5F6",
      "card_number": "LC-00001234",
      "status": "active",
      "issued_date": "2026-02-13"
    },
    "balance_euros": 0.00,
    "balance_points": 0,
    "created_at": "2026-02-13T12:00:00Z"
  }
}
```

**Error Codes:**
- `409 CARD_ALREADY_ASSIGNED` - Card UID already in use
- `400 INVALID_PHONE` - Phone format invalid
- `400 INVALID_EMAIL` - Email format invalid

#### 8. Transaction History

**Endpoint**: `GET /customers/{customer_id}/transactions`

**Purpose**: Get transaction history for customer

**Request:**
```http
GET /customers/{uuid}/transactions?limit=50&offset=0&type=all
Authorization: Bearer {API_KEY}
```

**Query Parameters:**
- `limit`: Results per page (default 50, max 100)
- `offset`: Pagination offset
- `type`: Filter by type (earn, redeem, adjustment, reversal, all)

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "transactions": [
      {
        "transaction_id": "uuid",
        "transaction_type": "earn",
        "amount_euros": 1.50,
        "amount_points": 15000,
        "order_id": "POS-2026021312345",
        "order_source": "aniwin_pos",
        "balance_after_euros": 14.00,
        "balance_after_points": 140000,
        "timestamp": "2026-02-13T12:34:56Z",
        "terminal_id": "TERM-001"
      }
    ],
    "pagination": {
      "total": 42,
      "limit": 50,
      "offset": 0,
      "has_more": false
    }
  }
}
```

## Implementation Architecture

### Layered Architecture

```
┌─────────────────────────────────────────┐
│         REST API Layer                  │
│  (Express/Fastify/FastAPI)              │
│  - Request validation                   │
│  - Authentication/Authorization         │
│  - Error handling                       │
│  - Response formatting                  │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Business Logic Layer            │
│  - Earn/Redeem/Refund logic             │
│  - Balance calculation                  │
│  - Expiration logic                     │
│  - Idempotency checking                 │
│  - Business rule validation             │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Data Access Layer               │
│  (ORM: TypeORM/Prisma/SQLAlchemy)       │
│  - CRUD operations                      │
│  - Query composition                    │
│  - Transaction management               │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         PostgreSQL Database             │
│  - Customers, Cards, Ledger, etc.       │
└─────────────────────────────────────────┘
```

### Key Implementation Patterns

#### Idempotency Implementation

```typescript
// Pseudocode
async function processTransaction(request, idempotencyKey) {
  // Check if idempotency key was used before
  const existing = await getIdempotencyRecord(idempotencyKey);
  
  if (existing) {
    // Same request seen before
    if (existing.request_hash === hash(request)) {
      // Exact same request - return cached response
      return existing.response;
    } else {
      // Same key, different request - conflict
      throw new Error('IDEMPOTENCY_KEY_CONFLICT');
    }
  }
  
  // New request - process it
  const response = await processNewTransaction(request);
  
  // Store idempotency record (expires in 24h)
  await storeIdempotencyRecord(idempotencyKey, hash(request), response, 24 * 3600);
  
  return response;
}
```

#### Ledger Append-Only Pattern

```typescript
// Pseudocode
async function earnPoints(customerId, orderAmount, orderId, terminalId) {
  // NEVER update existing ledger entries
  // ONLY insert new entries
  
  const earnAmount = orderAmount * 0.015; // Business rule
  
  await db.transaction(async (trx) => {
    // Append to ledger (INSERT only, never UPDATE/DELETE)
    const ledgerEntry = await trx.loyaltyLedger.insert({
      customer_id: customerId,
      transaction_type: 'earn',
      amount_euros: earnAmount,
      amount_points: earnAmount * 10000,
      order_id: orderId,
      terminal_id: terminalId,
      timestamp: now()
    });
    
    // Balance is computed, not stored
    const newBalance = await computeBalance(customerId, trx);
    
    return { ledgerEntry, newBalance };
  });
}
```

#### Balance Computation

```sql
-- Balance is always computed from ledger, never stored directly
SELECT 
  customer_id,
  SUM(amount_euros) as balance_euros,
  SUM(amount_points) as balance_points
FROM loyalty_ledger
WHERE customer_id = $1
  AND expires_at > NOW()  -- Exclude expired points
GROUP BY customer_id;
```

## Background Jobs

### 1. Expiration Job

**Schedule**: Nightly at 2:00 AM (off-peak)

**Logic**:
1. Find all ledger entries where `earned_at + 3 months < NOW()` and not yet expired
2. For each entry with unexpired balance:
   - Insert expiration ledger entry (negative amount)
   - Update original entry's `expires_at` timestamp
3. Log expiration summary

**Idempotency**: Check if expiration entry already exists for each earn entry

### 2. Email Notification Job

**Schedule**: Every 5 minutes

**Logic**:
1. Read notification queue
2. For each pending email:
   - Render template with data
   - Send via email provider
   - Mark as sent or failed
   - Retry failed (max 3 attempts)

### 3. Database Backup Job

**Schedule**: Daily at 4:00 AM

**Logic**:
1. Trigger cloud provider backup
2. Verify backup completed
3. Log backup status
4. Alert if failed

## Deployment

### Container (Docker)

```dockerfile
FROM node:18-alpine  # or python:3.11-slim

WORKDIR /app

COPY package*.json ./  # or requirements.txt
RUN npm install --production  # or pip install -r requirements.txt

COPY . .

EXPOSE 3000

CMD ["npm", "start"]  # or ["uvicorn", "main:app"]
```

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/loyalty

# API
PORT=3000
API_KEY_SALT=random-secret-value
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# Email
EMAIL_PROVIDER=sendgrid  # or ses
EMAIL_API_KEY=secret

# WhatsApp
WHATSAPP_PROVIDER=twilio  # or messagebird
WHATSAPP_API_KEY=secret
WHATSAPP_PHONE_NUMBER=+34600000000

# Monitoring
LOG_LEVEL=info
SENTRY_DSN=https://...

# Background Jobs
ENABLE_BACKGROUND_JOBS=true
EXPIRATION_JOB_CRON=0 2 * * *
```

### Health Checks

**Endpoint**: `GET /health`

```json
{
  "status": "healthy",
  "checks": {
    "database": "ok",
    "email_service": "ok",
    "whatsapp_service": "ok"
  },
  "version": "1.0.0",
  "uptime_seconds": 3600
}
```

## Error Codes Reference

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `CARD_NOT_FOUND` | 404 | Card UID not registered |
| `CARD_INACTIVE` | 403 | Card is deactivated |
| `CUSTOMER_NOT_FOUND` | 404 | Customer does not exist |
| `INSUFFICIENT_BALANCE` | 400 | Not enough points to redeem |
| `INVALID_ORDER_AMOUNT` | 400 | Order amount must be positive |
| `INVALID_REDEMPTION_AMOUNT` | 400 | Redemption amount invalid |
| `ORDER_NOT_FOUND` | 404 | Order ID not found |
| `ALREADY_REFUNDED` | 409 | Order already refunded |
| `DUPLICATE_TRANSACTION` | 409 | Idempotency key conflict |
| `CARD_ALREADY_ASSIGNED` | 409 | Card already in use |
| `INVALID_PHONE` | 400 | Phone format invalid |
| `INVALID_EMAIL` | 400 | Email format invalid |
| `UNAUTHORIZED` | 401 | Invalid or missing API key |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |

## Open Questions

1. Node.js or Python backend? (Awaiting user decision)
2. Which ORM to use for chosen stack?
3. Which cloud provider for deployment?
4. Which email service provider?
5. Which WhatsApp Business API provider?

## Related Documents

### Architecture
- `02_architecture/SYSTEM_ARCHITECTURE.md` - Overall architecture
- `02_architecture/WINDOWS_AGENT.md` - Client implementation
- `02_architecture/SYNC_STRATEGY.md` - Offline sync design

### Features
- `03_features/EARN_POINTS_POS.md` - Earn flow
- `03_features/REDEEM_POINTS_POS.md` - Redeem flow
- `03_features/REFUND_HANDLING.md` - Refund flow

### Data
- `05_data/DATA_MODEL.md` - Database schema
- `05_data/LOYALTY_LEDGER.md` - Ledger design

### Security
- `06_security/AUTHENTICATION.md` - API authentication
- `06_security/IDEMPOTENCY.md` - Duplicate prevention
