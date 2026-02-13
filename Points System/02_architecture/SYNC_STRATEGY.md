# Synchronization Strategy

## Purpose

This document defines how offline transactions are synchronized between Windows terminals and the cloud backend to ensure data consistency and prevent duplicates.

## Scope

Covers:
- Sync triggers and frequency
- Sync algorithm
- Idempotency implementation
- Network resilience
- Conflict detection

Does not cover:
- Conflict resolution rules (see `CONFLICT_RESOLUTION.md`)
- Queue implementation details (see `07_operations/OFFLINE_QUEUE.md`)

## Sync Overview

### Goals

1. **Zero Data Loss**: Every transaction must eventually reach the backend
2. **No Duplicates**: Each transaction processed exactly once
3. **Eventual Consistency**: All terminals eventually have consistent view
4. **Network Resilience**: Handle intermittent connectivity gracefully
5. **Performance**: Minimize sync latency while avoiding excessive API calls

### Non-Goals

- **Real-Time Sync**: Not required; eventual consistency is acceptable
- **Strong Consistency**: Cross-terminal consistency not real-time
- **Guaranteed Order**: Transactions may sync out of chronological order

## Sync Triggers

### Automatic Triggers

1. **Periodic Poll** (Primary)
   - Frequency: Every 60 seconds when queue not empty
   - Frequency: Every 300 seconds when queue empty
   - Runs in background service

2. **After Transaction** (Opportunistic)
   - Immediately after enqueueing new transaction
   - Only if online
   - Non-blocking (background)

3. **On Connection Restore**
   - When internet connection detected after offline period
   - Immediate sync attempt

4. **On Application Start**
   - When Windows agent starts
   - Check queue and sync if online

### Manual Triggers

1. **Manual Sync Button**
   - User-initiated from UI
   - Force sync even if recently synced
   - Provides immediate feedback

2. **Admin Command**
   - Command-line tool for troubleshooting
   - Can sync specific transaction or all

## Sync Algorithm

### High-Level Flow

```
SYNC_PROCESS:
  1. Check internet connectivity
  2. If offline: Exit (retry later)
  3. If online:
     a. Lock queue for reading
     b. Get oldest pending transaction
     c. Unlock queue
     d. If no pending: Exit
     e. Send transaction to backend
     f. Process response
     g. Update queue status
     h. Repeat from step 3a
```

### Detailed Algorithm

```python
def sync_queue():
    if not is_online():
        log("Offline - skipping sync")
        return
    
    while True:
        # Get next pending transaction
        transaction = get_next_pending_from_queue()
        
        if transaction is None:
            log("Queue empty - sync complete")
            break
        
        # Mark as syncing (prevents duplicate processing)
        mark_transaction_syncing(transaction.id)
        
        try:
            # Call backend API with idempotency key
            response = call_backend_api(
                endpoint=transaction.endpoint,
                payload=transaction.payload,
                idempotency_key=transaction.idempotency_key
            )
            
            if response.status == 200:
                # Success - mark synced and remove from queue
                mark_transaction_synced(transaction.id)
                update_local_cache(response.data)
                log_success(transaction, response)
                
                # Continue to next transaction
                continue
                
            elif response.status == 409 and response.error == 'IDEMPOTENCY_KEY_CONFLICT':
                # Already processed - safe to mark synced
                mark_transaction_synced(transaction.id)
                log_duplicate_prevented(transaction)
                continue
                
            elif response.error in RESOLVABLE_CONFLICTS:
                # Conflict that can be auto-resolved
                resolution = apply_conflict_resolution(transaction, response)
                mark_transaction_resolved(transaction.id, resolution)
                log_conflict_resolved(transaction, resolution)
                continue
                
            else:
                # Unrecoverable error - mark failed and move on
                mark_transaction_failed(transaction.id, response.error)
                log_failure(transaction, response)
                
                # Don't block queue on one failure
                if should_continue_despite_error(response):
                    continue
                else:
                    break  # Stop sync to investigate
        
        except NetworkError as e:
            # Network error - don't mark failed, retry later
            mark_transaction_pending(transaction.id)
            log_network_error(transaction, e)
            schedule_retry(transaction.id)
            break  # Stop sync, wait for connection
        
        except Exception as e:
            # Unexpected error - mark failed for investigation
            mark_transaction_failed(transaction.id, str(e))
            log_unexpected_error(transaction, e)
            continue  # Try next transaction
```

## Idempotency Implementation

### Idempotency Key Format

```
Format: {TERMINAL_ID}-{YYYYMMDD}-{COUNTER}-{UUID4}
Example: TERM-001-20260213-00042-a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Components**:
- **TERMINAL_ID**: Unique terminal identifier (e.g., TERM-001)
- **YYYYMMDD**: Date when transaction created (local time)
- **COUNTER**: Daily counter (resets each day, zero-padded to 5 digits)
- **UUID4**: Random UUID for additional uniqueness

**Properties**:
- Globally unique across all terminals and time
- Sortable (chronologically within terminal)
- Human-readable (can identify terminal and date)
- Collision-resistant (UUID component)

### Backend Idempotency Checking

```python
def process_transaction_idempotent(request, idempotency_key):
    # Check if this idempotency key was seen before
    existing = db.idempotency_keys.get(idempotency_key)
    
    if existing:
        # Key exists - check if request matches
        request_hash = hash_request(request)
        
        if existing.request_hash == request_hash:
            # Exact same request - return cached response
            return existing.response_data
        else:
            # Same key, different request - conflict!
            raise IdempotencyKeyConflictError(
                "Key already used with different request"
            )
    
    # New key - process transaction
    response = process_new_transaction(request)
    
    # Store idempotency record (expires in 48 hours)
    db.idempotency_keys.insert({
        "key": idempotency_key,
        "request_hash": request_hash,
        "response_data": response,
        "created_at": now(),
        "expires_at": now() + timedelta(hours=48)
    })
    
    return response
```

### Idempotency Storage

**Backend Database**:
```sql
CREATE TABLE idempotency_keys (
  idempotency_key VARCHAR(255) PRIMARY KEY,
  request_hash VARCHAR(64) NOT NULL,
  response_data JSONB NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_idempotency_expires ON idempotency_keys(expires_at);
```

**Retention**:
- Keep records for 48 hours minimum
- Purge expired records daily
- This allows safe retries for up to 2 days

## Network Resilience

### Connection Detection

**Method**: Periodic HTTP health check

```python
def is_online():
    try:
        response = requests.get(
            f"{BACKEND_URL}/health",
            timeout=5
        )
        return response.status_code == 200
    except:
        return False
```

**Frequency**:
- Check every 30 seconds when offline
- Check immediately after transaction when online
- Check before each sync batch

### Retry Strategy

**Exponential Backoff**:

| Attempt | Delay |
|---------|-------|
| 1 | Immediate |
| 2 | 1 minute |
| 3 | 5 minutes |
| 4 | 15 minutes |
| 5 | 30 minutes |
| 6+ | 1 hour |

**Max Attempts**: 20 attempts over ~20 hours

**After Max Attempts**: 
- Mark as "requires manual intervention"
- Alert admin via UI
- Log for investigation
- Don't auto-retry

### Timeout Configuration

```python
API_TIMEOUT_CONFIG = {
    "connect_timeout": 10,  # seconds to establish connection
    "read_timeout": 30,     # seconds to receive response
    "total_timeout": 45     # overall timeout
}
```

### Partial Failure Handling

**Scenario**: Sync succeeds for some transactions, fails for others

**Handling**:
1. Mark succeeded transactions as synced
2. Mark failed transactions for retry
3. Don't roll back successes
4. Continue with next batch

**Rationale**: Each transaction is independent; partial progress is acceptable

## Conflict Detection

### Conflict Types

1. **Idempotency Key Conflict**
   - Same key, different request data
   - Indicates client bug or corruption
   - Resolution: Log error, mark failed, investigate

2. **Insufficient Balance Conflict**
   - Redemption exceeds balance
   - Occurs when offline redemption used stale balance
   - Resolution: See `CONFLICT_RESOLUTION.md`

3. **Order Already Processed**
   - Earn/redeem for order_id that already exists
   - Indicates duplicate detection by order_id
   - Resolution: Check if amounts match; if yes, mark synced; if no, investigate

4. **Customer Not Found**
   - Customer deleted or never synced from enrollment
   - Resolution: Re-sync customer enrollment first

5. **Timestamp Out of Order**
   - Transaction timestamp older than last transaction
   - Acceptable (clock skew, offline delays)
   - Resolution: Process normally, ledger handles out-of-order

### Conflict Detection at Backend

```python
def validate_transaction(request):
    conflicts = []
    
    # Check customer exists
    customer = db.customers.get(request.customer_id)
    if not customer:
        conflicts.append({
            "type": "CUSTOMER_NOT_FOUND",
            "severity": "ERROR"
        })
    
    # Check balance for redemptions
    if request.type == "redeem":
        balance = compute_balance(request.customer_id)
        if balance < request.amount:
            conflicts.append({
                "type": "INSUFFICIENT_BALANCE",
                "severity": "WARNING",
                "details": {
                    "requested": request.amount,
                    "available": balance
                }
            })
    
    # Check for duplicate order_id
    existing = db.ledger.find(order_id=request.order_id)
    if existing:
        conflicts.append({
            "type": "DUPLICATE_ORDER_ID",
            "severity": "WARNING",
            "existing_transaction": existing
        })
    
    return conflicts
```

## Sync Monitoring

### Metrics to Track

1. **Queue Depth**
   - Current number of pending transactions
   - Alert if > 1000

2. **Sync Latency**
   - Time from transaction creation to sync completion
   - Alert if > 1 hour for any transaction

3. **Sync Success Rate**
   - Percentage of transactions synced successfully
   - Alert if < 95%

4. **Sync Throughput**
   - Transactions synced per minute
   - Target: >= 100/minute

5. **Failed Transaction Count**
   - Number of transactions marked failed
   - Alert if > 0

### Sync Status UI

**Terminal Dashboard Display**:

```
Sync Status: ● ONLINE
Last Sync: 14:32:15 (2 minutes ago)
Queue: 0 pending, 0 failed
Today: 127 synced, 0 conflicts
```

**Sync Log Viewer**:

```
14:35:00 - Sync started
14:35:01 - Synced transaction TERM-001-20260213-00042 (earn, 1.50 EUR)
14:35:02 - Synced transaction TERM-001-20260213-00043 (redeem, -10.00 EUR)
14:35:03 - Sync completed: 2 synced, 0 failed
```

## Edge Cases

### Clock Skew

**Problem**: Terminal clock differs from backend clock

**Impact**:
- Transaction timestamps may be out of order
- Expiration calculations may be off

**Mitigation**:
- Backend uses receive time, not client timestamp, for critical operations
- Ledger accepts out-of-order timestamps (sorted by sequence, not time)
- Expiration based on backend timestamp, not client timestamp

### Queue Corruption

**Problem**: SQLite database corrupted

**Detection**:
- SQLite integrity check on startup
- Catch database errors during queue operations

**Recovery**:
1. Backup corrupted database
2. Create new empty database
3. Log incident for manual recovery
4. Alert admin

**Data Loss**: Transactions in corrupted queue may be lost (acceptable rare risk)

### Duplicate Transactions

**Problem**: Same transaction enqueued twice

**Prevention**:
- Idempotency key uniqueness enforced in local database
- Backend idempotency checking

**Detection**:
- Backend returns 409 DUPLICATE for already-processed transactions
- Windows agent marks as synced (not an error)

### Network Partition

**Problem**: Some API endpoints reachable, others not

**Handling**:
- Treat as offline if any critical endpoint fails
- Don't partially sync
- Retry all transactions when fully online

## Performance Optimization

### Batch Sync (Future Enhancement)

Currently: One transaction per API call

Future: Batch up to 100 transactions per call

**Batch Endpoint**:
```
POST /transactions/batch
{
  "transactions": [
    { "idempotency_key": "...", "type": "earn", ... },
    { "idempotency_key": "...", "type": "redeem", ... }
  ]
}
```

**Response**:
```
{
  "results": [
    { "idempotency_key": "...", "status": "success", ... },
    { "idempotency_key": "...", "status": "conflict", ... }
  ]
}
```

**Benefits**:
- Fewer API calls
- Faster sync for large queues
- Reduced network overhead

**Complexity**: Higher; defer to post-MVP

### Connection Pooling

- Reuse HTTP connections across sync calls
- Reduces connection establishment overhead

### Compression

- Enable gzip compression for API requests/responses
- Reduces bandwidth usage

## Testing Strategy

### Unit Tests

- Idempotency key generation
- Conflict detection logic
- Retry schedule calculation
- Queue state transitions

### Integration Tests

- Sync with mock backend
- Offline/online transitions
- Retry on network failure
- Idempotency key collision handling

### End-to-End Tests

1. **Happy Path**
   - Queue transaction
   - Sync successfully
   - Verify backend received transaction

2. **Offline Scenario**
   - Disconnect network
   - Queue 10 transactions
   - Reconnect network
   - Verify all 10 sync

3. **Duplicate Prevention**
   - Queue same transaction twice (force duplicate)
   - Verify only one appears in backend

4. **Conflict Scenario**
   - Queue redemption with stale balance
   - Sync and verify conflict resolution

5. **Large Queue**
   - Queue 1000 transactions
   - Verify all sync within 10 minutes

## Related Documents

### Architecture
- `02_architecture/SYSTEM_ARCHITECTURE.md` - Overall architecture
- `02_architecture/CLOUD_BACKEND.md` - API contracts
- `02_architecture/WINDOWS_AGENT.md` - Windows agent details
- `02_architecture/CONFLICT_RESOLUTION.md` - Conflict resolution rules

### Operations
- `07_operations/OFFLINE_QUEUE.md` - Queue implementation
- `07_operations/ERROR_HANDLING.md` - Error handling
- `07_operations/SYNC_MONITORING.md` - Sync monitoring

### Security
- `06_security/IDEMPOTENCY.md` - Idempotency details
