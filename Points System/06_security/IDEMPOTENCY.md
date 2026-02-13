# Idempotency: Duplicate Transaction Prevention

## Purpose

Define the idempotency mechanism that prevents duplicate transactions caused by network retries, user double-clicks, or system errors. Ensure each unique business operation executes exactly once, even if the API request is repeated.

## Scope

### In Scope
- Idempotency key concept and requirements
- Key format and generation rules
- Key storage and retention (48-hour window)
- Request payload hashing for conflict detection
- Idempotent endpoint list
- Conflict detection and response
- Edge cases (key collision, expired keys, parameter changes)
- Integration with POS agent and PrestaShop module

### Out of Scope
- General API security (see `SECURITY_MODEL.md`)
- Authentication mechanisms (see `AUTHENTICATION.md`)
- Transaction processing logic (see `03_features/`)
- Database transaction isolation (separate concern)

## Idempotency Concept

### Definition
**Idempotency**: Property where an operation can be applied multiple times without changing the result beyond the initial application.

**Example**:
- `balance = 100` is idempotent (setting balance to 100 multiple times still results in 100)
- `balance += 10` is NOT idempotent (adding 10 three times results in 130, not 110)

### Why Needed

#### Problem 1: Network Retry
```
Client: POST /earn (50 EUR earn transaction)
  → Network timeout (no response received)
Client: Retry POST /earn (same 50 EUR transaction)
  → If not idempotent: Customer earns 100 EUR (double credit)
```

#### Problem 2: User Double-Click
```
Manager: Click "Approve Adjustment"
  → Server processing (takes 2 seconds)
Manager: Click again (impatient)
  → If not idempotent: Adjustment applied twice
```

#### Problem 3: Offline Queue Sync
```
POS offline: Create earn transaction (queued locally)
POS online: Sync queue → send transaction
Network error: Retry sync → send transaction again
  → If not idempotent: Transaction duplicated
```

### Solution: Idempotency Keys
Client generates unique key for each business operation. Server stores key + result for 48 hours. If duplicate request received, server returns cached result.

## Idempotent Endpoints

### Endpoints Requiring Idempotency Keys

| Endpoint | Mutating? | Idempotency Required |
|----------|-----------|---------------------|
| `POST /transactions/earn` | ✅ Yes | ✅ **REQUIRED** |
| `POST /transactions/redeem` | ✅ Yes | ✅ **REQUIRED** |
| `POST /transactions/adjustment` | ✅ Yes | ✅ **REQUIRED** |
| `POST /transactions/refund` | ✅ Yes | ✅ **REQUIRED** |
| `GET /balance` | ❌ No (read-only) | ❌ Not required |
| `GET /transactions` | ❌ No (read-only) | ❌ Not required |
| `POST /enrollment` | ✅ Yes | ✅ **REQUIRED** |
| `POST /terminals/provision` | ✅ Yes | ✅ **REQUIRED** |

### Idempotency Header
```http
X-Idempotency-Key: <unique_key>
```

**Example Request**:
```http
POST /api/v1/transactions/earn HTTP/1.1
Host: loyalty-api.prestashop-entre.com
Authorization: Bearer loyalty_prod_POS-TERMINAL-001_k9m2n5...
Content-Type: application/json
X-Idempotency-Key: earn_04A1B2C3D4E5F6_1708012800_POS-TERMINAL-001

{
  "card_uid": "04A1B2C3D4E5F6",
  "order_id": "PS-ORD-12345",
  "order_amount": 50.00,
  "points_earned": 500000,
  "timestamp": "2025-02-15T14:30:00Z"
}
```

## Idempotency Key Format

### Structure
```
<operation_type>_<entity_identifier>_<unix_timestamp>_<terminal_id>
```

### Components

| Component | Description | Example |
|-----------|-------------|---------|
| **operation_type** | Type of operation | `earn`, `redeem`, `adjustment`, `refund` |
| **entity_identifier** | Unique identifier for entity | `04A1B2C3D4E5F6` (card UID) or `txn_abc123` (transaction ID) |
| **unix_timestamp** | Unix epoch timestamp (seconds) | `1708012800` |
| **terminal_id** | Terminal or source identifier | `POS-TERMINAL-001`, `module_shop001` |

### Examples

#### Earn Transaction
```
earn_04A1B2C3D4E5F6_1708012800_POS-TERMINAL-001
```
- Operation: earn
- Card UID: 04A1B2C3D4E5F6
- Timestamp: 1708012800 (2025-02-15 14:30:00 UTC)
- Terminal: POS-TERMINAL-001

#### Redemption Transaction
```
redeem_04A1B2C3D4E5F6_1708014600_POS-TERMINAL-002
```
- Operation: redeem
- Card UID: 04A1B2C3D4E5F6
- Timestamp: 1708014600 (2025-02-15 15:00:00 UTC)
- Terminal: POS-TERMINAL-002

#### Manual Adjustment
```
adjustment_04A1B2C3D4E5F6_1708016400_manager_maria
```
- Operation: adjustment
- Card UID: 04A1B2C3D4E5F6
- Timestamp: 1708016400 (2025-02-15 15:30:00 UTC)
- Source: manager_maria

#### Refund Transaction
```
refund_txn_abc123_1708018200_module_shop001
```
- Operation: refund
- Original transaction: txn_abc123
- Timestamp: 1708018200 (2025-02-15 16:00:00 UTC)
- Source: module_shop001 (PrestaShop module)

### Key Generation (Client-Side)

#### POS Agent (C#)
```csharp
using System;

public class IdempotencyKeyGenerator
{
    public static string GenerateEarnKey(string cardUid, string terminalId)
    {
        long timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
        return $"earn_{cardUid}_{timestamp}_{terminalId}";
    }
    
    public static string GenerateRedeemKey(string cardUid, string terminalId)
    {
        long timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
        return $"redeem_{cardUid}_{timestamp}_{terminalId}";
    }
    
    public static string GenerateAdjustmentKey(string cardUid, string managerId)
    {
        long timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
        return $"adjustment_{cardUid}_{timestamp}_{managerId}";
    }
}

// Usage
string key = IdempotencyKeyGenerator.GenerateEarnKey("04A1B2C3D4E5F6", "POS-TERMINAL-001");
// earn_04A1B2C3D4E5F6_1708012800_POS-TERMINAL-001
```

#### PrestaShop Module (PHP)
```php
class LoyaltyIdempotencyKey
{
    public static function generateRefundKey(string $transactionId, string $shopId): string
    {
        $timestamp = time();
        return sprintf('refund_%s_%d_module_%s', $transactionId, $timestamp, $shopId);
    }
    
    public static function generateEarnKey(string $cardUid, string $orderId, string $shopId): string
    {
        $timestamp = time();
        return sprintf('earn_%s_%d_module_%s_order_%s', $cardUid, $timestamp, $shopId, $orderId);
    }
}

// Usage
$key = LoyaltyIdempotencyKey::generateEarnKey('04A1B2C3D4E5F6', 'PS-ORD-12345', 'shop001');
// earn_04A1B2C3D4E5F6_1708012800_module_shop001_order_PS-ORD-12345
```

### Key Properties
- **Uniqueness**: Combination of operation type, entity, timestamp, source ensures uniqueness
- **Determinism**: Same parameters always generate same key (within same second)
- **Human-Readable**: Key components visible for debugging
- **Length**: ~80-120 characters (depends on identifiers)
- **Character Set**: Alphanumeric + underscore (URL-safe)

## Idempotency Storage

### Database Schema

```sql
CREATE TABLE idempotency_keys (
  id SERIAL PRIMARY KEY,
  idempotency_key VARCHAR(200) UNIQUE NOT NULL,
  request_hash VARCHAR(64) NOT NULL,  -- SHA-256 hash of request body
  endpoint VARCHAR(100) NOT NULL,     -- e.g., '/transactions/earn'
  http_method VARCHAR(10) NOT NULL,   -- e.g., 'POST'
  response_status INTEGER NOT NULL,   -- e.g., 201
  response_body TEXT NOT NULL,        -- Cached response
  terminal_id VARCHAR(50),
  card_uid VARCHAR(20),
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP NOT NULL,      -- created_at + 48 hours
  request_metadata JSONB              -- Additional context
);

-- Index for fast lookup
CREATE UNIQUE INDEX idx_idempotency_key ON idempotency_keys(idempotency_key);

-- Index for cleanup (delete expired keys)
CREATE INDEX idx_expires_at ON idempotency_keys(expires_at);

-- Index for analytics
CREATE INDEX idx_terminal_id ON idempotency_keys(terminal_id);
CREATE INDEX idx_created_at ON idempotency_keys(created_at);
```

### Storage Example

**First Request**:
```json
{
  "idempotency_key": "earn_04A1B2C3D4E5F6_1708012800_POS-TERMINAL-001",
  "request_hash": "a3b5c7d9e1f3g5h7i9j1k3l5m7n9o1p3q5r7s9t1u3v5w7x9y1z3a5b7c9d1e3f5",
  "endpoint": "/transactions/earn",
  "http_method": "POST",
  "response_status": 201,
  "response_body": "{\"success\": true, \"transaction_id\": \"txn_xyz123\", ...}",
  "terminal_id": "POS-TERMINAL-001",
  "card_uid": "04A1B2C3D4E5F6",
  "created_at": "2025-02-15T14:30:00Z",
  "expires_at": "2025-02-17T14:30:00Z",
  "request_metadata": {
    "order_id": "PS-ORD-12345",
    "order_amount": 50.00,
    "client_ip": "192.168.1.100"
  }
}
```

**Retry Request** (duplicate):
- Server looks up `idempotency_key`
- Key found → return cached `response_body` with status 201
- No duplicate transaction created

### Retention Policy
- **Duration**: 48 hours from creation
- **Cleanup**: Automated job runs hourly to delete expired keys
- **Rationale**: 48 hours covers network retry windows, offline sync delays

```sql
-- Cleanup job (runs hourly)
DELETE FROM idempotency_keys
WHERE expires_at < NOW();
```

## Request Payload Hashing

### Purpose
Detect if client retries request with **different parameters** but **same idempotency key**.

### Example Conflict
```
Request 1: Idempotency-Key = earn_04A1B2_1708012800_POS-001
           Body = {"amount": 50.00, "points": 500000}
           
Request 2: Idempotency-Key = earn_04A1B2_1708012800_POS-001  (SAME KEY)
           Body = {"amount": 75.00, "points": 750000}         (DIFFERENT PARAMS)
```

**Problem**: Same key, different transaction details → which is correct?

**Solution**: Hash request body. If hash differs, return error (conflict).

### Hash Calculation

#### Server-Side (Python)
```python
import hashlib
import json

def hash_request_body(body: dict) -> str:
    """
    Generate SHA-256 hash of request body for idempotency conflict detection.
    
    Args:
        body: Request body dictionary
    
    Returns: Hex-encoded SHA-256 hash
    """
    # Sort keys for deterministic hash
    canonical_json = json.dumps(body, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical_json.encode()).hexdigest()

# Example
body1 = {"card_uid": "04A1B2C3D4E5F6", "amount": 50.00, "points": 500000}
body2 = {"amount": 50.00, "card_uid": "04A1B2C3D4E5F6", "points": 500000}  # Same data, different order
body3 = {"card_uid": "04A1B2C3D4E5F6", "amount": 75.00, "points": 750000}  # Different data

hash1 = hash_request_body(body1)  # abc123...
hash2 = hash_request_body(body2)  # abc123... (SAME - order doesn't matter)
hash3 = hash_request_body(body3)  # def456... (DIFFERENT)
```

### Hash Storage
Stored alongside idempotency key in `idempotency_keys.request_hash` column.

### Conflict Detection Logic
```python
def check_idempotency(idempotency_key: str, request_body: dict) -> dict:
    """
    Check if request is idempotent retry or conflict.
    
    Returns:
        - If new key: {"status": "new", "should_process": True}
        - If retry (same hash): {"status": "duplicate", "cached_response": ...}
        - If conflict (different hash): {"status": "conflict", "error": ...}
    """
    # Lookup existing key
    existing = db.get_idempotency_key(idempotency_key)
    
    if not existing:
        # New request - process normally
        return {"status": "new", "should_process": True}
    
    # Check if expired
    if existing.expires_at < datetime.now():
        # Key expired - treat as new request (though client should have used new timestamp)
        return {"status": "expired", "should_process": True}
    
    # Calculate hash of current request
    current_hash = hash_request_body(request_body)
    
    # Compare hashes
    if current_hash == existing.request_hash:
        # Exact duplicate - return cached response
        return {
            "status": "duplicate",
            "cached_response": json.loads(existing.response_body),
            "original_timestamp": existing.created_at
        }
    else:
        # Conflict - same key, different parameters
        return {
            "status": "conflict",
            "error": "Idempotency key conflict: same key with different request parameters",
            "original_hash": existing.request_hash,
            "current_hash": current_hash
        }
```

## Server-Side Implementation Flow

### Complete Request Processing

```
┌────────────┐
│  Request   │
│  Received  │
└─────┬──────┘
      │
      ▼
┌──────────────────────┐
│ Extract Idempotency  │
│ Key from Header      │
└─────┬────────────────┘
      │
      ▼
┌──────────────────────┐
│ Key Present?         │◄─ NO ──┐
└─────┬────────────────┘        │
      │ YES                     │
      ▼                         ▼
┌──────────────────────┐   ┌────────────────┐
│ Lookup Key in DB     │   │ Return 400     │
└─────┬────────────────┘   │ "Key Required" │
      │                     └────────────────┘
      ▼
┌──────────────────────┐
│ Key Exists?          │
└─────┬────────────────┘
      │
      ├─ NO ──────────────────────────────┐
      │                                    │
      │ YES                                ▼
      ▼                             ┌──────────────────────┐
┌──────────────────────┐            │ Hash Request Body    │
│ Key Expired?         │            └─────┬────────────────┘
└─────┬────────────────┘                  │
      │                                    ▼
      ├─ YES ─────────────────────────────►┌──────────────────────┐
      │                                    │ Process Transaction  │
      │ NO                                 │ (Business Logic)     │
      ▼                                    └─────┬────────────────┘
┌──────────────────────┐                        │
│ Hash Request Body    │                        ▼
└─────┬────────────────┘                  ┌──────────────────────┐
      │                                    │ Save Idempotency Key │
      ▼                                    │ + Response to DB     │
┌──────────────────────┐                  └─────┬────────────────┘
│ Hash Matches         │                        │
│ Stored Hash?         │                        ▼
└─────┬────────────────┘                  ┌──────────────────────┐
      │                                    │ Return Response      │
      ├─ YES ─────────────────────────────►│ (201 Created)        │
      │                                    └──────────────────────┘
      │ NO
      ▼
┌──────────────────────┐
│ Return 409 Conflict  │
│ "Same key, different │
│  parameters"         │
└──────────────────────┘
      │
      ▼
┌──────────────────────┐
│ Return Cached        │
│ Response (200 OK)    │
└──────────────────────┘
```

### Python Implementation Example

```python
from fastapi import FastAPI, Header, HTTPException, Request
from typing import Optional
import json

app = FastAPI()

@app.post("/api/v1/transactions/earn")
async def create_earn_transaction(
    request: Request,
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key")
):
    """Create earn transaction with idempotency protection."""
    
    # 1. Require idempotency key
    if not x_idempotency_key:
        raise HTTPException(
            status_code=400,
            detail="X-Idempotency-Key header required for this endpoint"
        )
    
    # 2. Parse request body
    body = await request.json()
    
    # 3. Check idempotency
    idempotency_result = check_idempotency(x_idempotency_key, body)
    
    if idempotency_result["status"] == "duplicate":
        # Return cached response
        return Response(
            content=json.dumps(idempotency_result["cached_response"]),
            status_code=200,
            headers={"X-Idempotency-Replay": "true"}
        )
    
    if idempotency_result["status"] == "conflict":
        # Conflict detected
        raise HTTPException(
            status_code=409,
            detail={
                "error_code": "IDEMPOTENCY_CONFLICT",
                "error_message": idempotency_result["error"],
                "original_hash": idempotency_result["original_hash"],
                "current_hash": idempotency_result["current_hash"]
            }
        )
    
    # 4. Process transaction (new or expired key)
    try:
        transaction = create_earn_transaction_logic(body)
        response_body = {
            "success": True,
            "transaction_id": transaction.id,
            "card_uid": body["card_uid"],
            "points_earned": body["points_earned"],
            "new_balance": transaction.new_balance,
            "timestamp": transaction.created_at.isoformat()
        }
        
        # 5. Save idempotency key + response
        save_idempotency_key(
            idempotency_key=x_idempotency_key,
            request_hash=hash_request_body(body),
            endpoint="/transactions/earn",
            http_method="POST",
            response_status=201,
            response_body=json.dumps(response_body),
            terminal_id=body.get("terminal_id"),
            card_uid=body.get("card_uid")
        )
        
        # 6. Return response
        return Response(
            content=json.dumps(response_body),
            status_code=201
        )
    
    except Exception as e:
        # Error occurred - do NOT save idempotency key
        # Client should retry with same key
        raise HTTPException(status_code=500, detail=str(e))
```

## Edge Cases

### Edge Case 1: Key Collision (Different Clients, Same Key)

**Scenario**:
- Terminal A generates: `earn_04A1B2_1708012800_POS-TERMINAL-001`
- Terminal B generates: `earn_04A1B2_1708012800_POS-TERMINAL-001` (same second, same card UID, same terminal ID)

**Probability**: Extremely low (requires exact same timestamp)

**Handling**:
- Second request sees key exists
- Hash comparison: If same parameters → return cached response (no harm)
- Hash comparison: If different parameters → return 409 Conflict

**Resolution**: Client retries with new timestamp (1 second later)

**Mitigation**: Include milliseconds in timestamp (future enhancement)

---

### Edge Case 2: Key Expiration During Processing

**Scenario**:
1. Client sends request with key (expires in 5 seconds)
2. Server processing takes 10 seconds
3. Key expires mid-processing
4. Client retries (same key)

**Handling**:
- First request: Key stored (even if takes long time)
- Retry request: Key found (not yet expired from client perspective)
- Return cached response

**Note**: Expiration based on creation time, not access time

---

### Edge Case 3: Client Changes Parameters Between Retries

**Scenario**:
1. Client sends: `{"amount": 50.00}` with key `earn_04A1B2_1708012800_POS-001`
2. Network timeout
3. Client changes amount to 75.00, retries with SAME key

**Handling**:
- Server detects hash mismatch
- Returns 409 Conflict
- Client must use NEW key (new timestamp) for different parameters

**Error Response**:
```json
{
  "success": false,
  "error_code": "IDEMPOTENCY_CONFLICT",
  "error_message": "Request parameters changed but idempotency key remained the same. Use a new key for different parameters.",
  "resolution": "Generate new idempotency key with current timestamp and retry."
}
```

---

### Edge Case 4: Offline Queue Sync (Same Transaction, Multiple Retries)

**Scenario**:
1. POS offline: Create earn transaction (queued)
2. POS online: Attempt sync → network error
3. Retry sync → network error
4. Retry sync → success

**Handling**:
- Same idempotency key used for all retries (generated when transaction created)
- First successful request: Transaction created
- Subsequent retries: Return cached response, no duplicate

**Implementation**:
```csharp
// POS Agent offline queue
public class OfflineTransaction
{
    public string IdempotencyKey { get; set; }  // Generated once at creation
    public string CardUid { get; set; }
    public decimal Amount { get; set; }
    public int SyncAttempts { get; set; }
    public DateTime CreatedAt { get; set; }
}

// Sync logic
public async Task<bool> SyncTransaction(OfflineTransaction txn)
{
    // Use original idempotency key (not regenerated)
    var response = await _apiClient.PostAsync("/transactions/earn", new
    {
        card_uid = txn.CardUid,
        amount = txn.Amount,
        // ... other fields
    }, idempotencyKey: txn.IdempotencyKey);  // SAME KEY on every retry
    
    if (response.IsSuccessStatusCode)
    {
        // Mark synced
        txn.SyncAttempts++;
        return true;
    }
    else
    {
        // Retry later
        txn.SyncAttempts++;
        return false;
    }
}
```

---

### Edge Case 5: Server Error After Processing

**Scenario**:
1. Client sends request
2. Server processes transaction successfully
3. Server saves idempotency key
4. **Server crashes before sending response**
5. Client retries (no response received)

**Handling**:
- Retry request finds idempotency key
- Returns cached response
- Transaction not duplicated

**Critical**: Idempotency key MUST be saved in same database transaction as business logic

```python
@transaction.atomic
def process_transaction_with_idempotency(key, body):
    """
    Process transaction and save idempotency key atomically.
    """
    # 1. Business logic
    txn = create_transaction(body)
    
    # 2. Save idempotency key
    save_idempotency_key(key, body, txn)
    
    # Both succeed or both fail (atomicity)
```

---

### Edge Case 6: Client Never Receives Response (Permanent Loss)

**Scenario**:
1. Client sends request
2. Server responds with 201 Created
3. Response lost in network
4. Client has no idea if transaction succeeded

**Handling**:
- Client retries with same idempotency key
- Server returns cached response
- Client now knows transaction succeeded

**Alternative**: Client queries transaction status by order ID or card UID

---

### Edge Case 7: Idempotency Key Cleanup Race Condition

**Scenario**:
1. Client sends request (key expires in 1 second)
2. Cleanup job deletes expired key (runs concurrently)
3. Server tries to save key → already gone

**Handling**:
- Use database transaction isolation
- Lock idempotency_keys row during processing
- Cleanup job skips locked rows

```sql
-- Cleanup with lock timeout
DELETE FROM idempotency_keys
WHERE expires_at < NOW()
  AND pg_try_advisory_lock(id);  -- Skip if locked
```

## Client Best Practices

### 1. Generate Key Once Per Operation
```csharp
// ✅ CORRECT
var key = GenerateIdempotencyKey();
await SendRequest(key);  // First try
// ... network error ...
await SendRequest(key);  // Retry with SAME KEY

// ❌ WRONG
await SendRequest(GenerateIdempotencyKey());  // First try
await SendRequest(GenerateIdempotencyKey());  // Retry with DIFFERENT KEY (duplicate)
```

### 2. Store Key with Transaction in Offline Queue
```csharp
// ✅ CORRECT
public class OfflineTransaction
{
    public string IdempotencyKey { get; set; }  // Generated once
    // ...
}
```

### 3. Retry with Same Key on Transient Errors
```csharp
// Transient errors: retry with same key
var transientErrors = new[] { 408, 429, 500, 502, 503, 504 };

if (transientErrors.Contains(response.StatusCode))
{
    await Task.Delay(1000);
    await SendRequest(sameKey);  // Retry
}
```

### 4. Use New Key for Different Parameters
```csharp
// User changes transaction amount
if (parameterChanged)
{
    var newKey = GenerateIdempotencyKey();  // NEW KEY
    await SendRequest(newKey);
}
```

### 5. Handle 409 Conflict Gracefully
```csharp
if (response.StatusCode == 409)
{
    // Generate new key and retry
    var newKey = GenerateIdempotencyKey();
    await SendRequest(newKey);
}
```

## Testing Idempotency

### Test Case 1: Duplicate Detection
```python
# Test: Same request twice returns same result
key = "earn_04A1B2_1708012800_POS-001"
body = {"card_uid": "04A1B2", "amount": 50.00}

response1 = client.post("/transactions/earn", json=body, headers={"X-Idempotency-Key": key})
assert response1.status_code == 201
txn_id_1 = response1.json()["transaction_id"]

response2 = client.post("/transactions/earn", json=body, headers={"X-Idempotency-Key": key})
assert response2.status_code == 200  # Cached response
assert response2.headers.get("X-Idempotency-Replay") == "true"
txn_id_2 = response2.json()["transaction_id"]

assert txn_id_1 == txn_id_2  # Same transaction
```

### Test Case 2: Conflict Detection
```python
# Test: Same key, different parameters returns 409
key = "earn_04A1B2_1708012800_POS-001"
body1 = {"card_uid": "04A1B2", "amount": 50.00}
body2 = {"card_uid": "04A1B2", "amount": 75.00}  # Different amount

response1 = client.post("/transactions/earn", json=body1, headers={"X-Idempotency-Key": key})
assert response1.status_code == 201

response2 = client.post("/transactions/earn", json=body2, headers={"X-Idempotency-Key": key})
assert response2.status_code == 409
assert response2.json()["error_code"] == "IDEMPOTENCY_CONFLICT"
```

### Test Case 3: Key Expiration
```python
# Test: Expired key treated as new request
key = "earn_04A1B2_1708012800_POS-001"
body = {"card_uid": "04A1B2", "amount": 50.00}

# Create request
response1 = client.post("/transactions/earn", json=body, headers={"X-Idempotency-Key": key})
assert response1.status_code == 201

# Wait for expiration (48 hours + 1 minute)
time.sleep(48 * 3600 + 60)

# Retry after expiration
response2 = client.post("/transactions/earn", json=body, headers={"X-Idempotency-Key": key})
assert response2.status_code == 201  # New transaction created
```

## Related Documents

### Dependencies
- `06_security/SECURITY_MODEL.md` - Overall security architecture
- `06_security/AUTHENTICATION.md` - API authentication mechanisms
- `02_architecture/CLOUD_BACKEND.md` - API implementation

### Related Features
- `03_features/OFFLINE_MODE.md` - Offline transaction queue and sync
- `03_features/EARN_POINTS_POS.md` - Earn transaction idempotency
- `03_features/REDEEM_POINTS_POS.md` - Redemption idempotency
- `03_features/MANUAL_ADJUSTMENTS.md` - Adjustment idempotency

## Open Questions / TODOs

### TODO: Millisecond Timestamps
**Status**: Future enhancement  
**Required by**: Phase 2  
**Description**: Include milliseconds in timestamp to reduce key collision probability

### TODO: Idempotency Key Metrics
**Status**: Monitoring needed  
**Required by**: Production launch  
**Description**: Track metrics: duplicate rate, conflict rate, key expiration distribution

### TODO: Distributed Lock for High Concurrency
**Status**: Future optimization  
**Required by**: High-traffic deployments  
**Description**: Use Redis distributed lock instead of database row lock

### Open Question: Idempotency for GET Requests
**Question**: Should GET requests have idempotency protection?  
**Context**: GET is already idempotent by HTTP specification  
**Impact**: Additional complexity for no benefit  
**Decision**: No (GET requests are naturally idempotent)

### Open Question: Custom Expiration Per Endpoint
**Question**: Should different endpoints have different expiration periods?  
**Context**: Adjustments may need longer retention than transactions  
**Impact**: More complex cleanup logic  
**Decision Required By**: Phase 2
