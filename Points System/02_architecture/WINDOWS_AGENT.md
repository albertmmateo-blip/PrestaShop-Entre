# Windows Agent Architecture

## Purpose

This document describes the architecture and implementation requirements for the Windows-based loyalty agent that runs on POS terminals.

## Scope

Covers:
- Windows agent architecture
- NFC integration
- Offline queue management
- UI requirements
- Aniwin POS integration
- Sync logic

## Technology Stack (depends on backend choice)

### Option A: C# .NET 6+ (Recommended for Windows)

**Advantages**:
- Native Windows integration
- Excellent PC/SC NFC support
- Windows Service support built-in
- WPF for rich UI
- Entity Framework for local database

**Stack**:
- .NET 6+ Windows Service
- WPF or WinForms for UI
- SQLite for offline queue
- PC/SC drivers for NFC
- HttpClient for REST API calls

### Option B: Electron + Node.js

**Advantages**:
- Code reuse with Node.js backend
- Cross-platform (if needed later)
- Familiar web technologies
- Hot reload during development

**Stack**:
- Electron application
- React or Vue for UI
- SQLite for offline queue
- node-pcsclite for NFC
- axios for REST API calls

### Option C: Python + PyQt

**Advantages**:
- Code reuse with Python backend
- PyQt for native-looking UI
- Simple deployment

**Stack**:
- Python 3.11+ application
- PyQt6 for UI
- SQLite for offline queue
- pyscard for NFC (PC/SC)
- requests for REST API calls

## Architecture Diagram

```
┌──────────────────────────────────────────────────────┐
│              Windows Terminal (POS)                   │
│                                                       │
│  ┌────────────────────────────────────────────────┐  │
│  │         Loyalty Windows Agent                  │  │
│  │                                                 │  │
│  │  ┌──────────────┐      ┌──────────────────┐   │  │
│  │  │  UI Layer    │      │  Sync Service    │   │  │
│  │  │  (WPF/Elect.)│      │  (Background)    │   │  │
│  │  │  - Balance   │      │  - Queue Proc.   │   │  │
│  │  │  - Enroll    │      │  - API Calls     │   │  │
│  │  │  - Redeem    │      │  - Conflict Res. │   │  │
│  │  │  - Status    │      │  - Retry Logic   │   │  │
│  │  └──────┬───────┘      └─────────┬────────┘   │  │
│  │         │                        │            │  │
│  │  ┌──────▼────────────────────────▼─────────┐  │  │
│  │  │      Business Logic Layer                │  │  │
│  │  │  - Transaction Management                │  │  │
│  │  │  - Offline Queue Management              │  │  │
│  │  │  - Idempotency Key Generation            │  │  │
│  │  └──────┬───────────────────┬──────────────┘  │  │
│  │         │                   │                  │  │
│  │  ┌──────▼──────┐     ┌──────▼──────────────┐  │  │
│  │  │ NFC Driver  │     │ Local SQLite DB     │  │  │
│  │  │ (PC/SC)     │     │ (Offline Queue)     │  │  │
│  │  └──────┬──────┘     └─────────────────────┘  │  │
│  │         │                                      │  │
│  └─────────┼──────────────────────────────────────┘  │
│            │                                         │
│  ┌─────────▼──────┐                                  │
│  │ USB NFC Reader │                                  │
│  └────────────────┘                                  │
│                                                       │
│  ┌──────────────────────────────────────┐            │
│  │  Aniwin.net POS                      │            │
│  │  (Separate Application)              │            │
│  └──────────────────────────────────────┘            │
│            │                                          │
│            │ Database/File/Receipt                    │
│            │ Integration                              │
│            ▼                                          │
│  ┌──────────────────────────────────────┐            │
│  │  Aniwin Database / Export Files      │            │
│  └──────────────────────────────────────┘            │
└───────────────────────────┬──────────────────────────┘
                            │
                            │ Internet (when available)
                            │
                  ┌─────────▼─────────┐
                  │  Cloud Backend    │
                  │  REST API         │
                  └───────────────────┘
```

## Component Architecture

### 1. UI Layer

**Purpose**: Cashier-facing interface for loyalty operations

**Screens**:

1. **Main Dashboard**
   - Current customer (after card tap)
   - Balance display (prominent)
   - Quick actions (Enroll, Redeem, History)
   - Sync status indicator (online/offline/syncing)
   - Last sync time

2. **Card Enrollment**
   - Customer name (required)
   - Phone number (required, validated)
   - Email address (required, validated)
   - Consent checkboxes (loyalty, marketing)
   - Language selection (Spanish/Catalan)
   - Card tap prompt
   - Confirmation screen

3. **Balance Query**
   - Card tap prompt
   - Balance display (EUR and points)
   - Recent transactions (last 5)
   - Points expiring soon

4. **Manual Redemption**
   - Card tap prompt
   - Current balance
   - Redemption amount input
   - Confirmation prompt
   - Success/failure message
   - Updated balance

5. **Sync Status**
   - Queue depth (transactions pending)
   - Last successful sync
   - Errors/warnings
   - Manual sync button

**Language Support**:
- All UI text in Spanish and Catalan
- Language switcher in settings
- Default language from Windows locale

**UI Requirements**:
- Large fonts for readability
- High contrast for visibility
- Touch-friendly (large buttons)
- Keyboard shortcuts for power users
- Clear error messages
- Progress indicators for slow operations

### 2. Business Logic Layer

**Responsibilities**:

#### Transaction Management
- Validate transaction requests
- Generate idempotency keys (UUID v4)
- Create transaction records
- Queue transactions for sync
- Update local cache

#### Offline Queue Management
- Persist transactions to SQLite
- Maintain queue order (FIFO)
- Track retry attempts
- Handle queue full scenario

#### Idempotency Key Generation
- Generate UUID v4 for each transaction
- Format: `{terminal_id}-{timestamp}-{counter}-{uuid}`
- Store with transaction in queue

#### Connection Management
- Monitor internet connectivity
- Trigger sync when online
- Notify UI of status changes
- Handle API timeouts

### 3. NFC Driver Integration

**Technology**: PC/SC (Personal Computer/Smart Card)

**Supported Readers**:
- ACR122U (USB NFC reader)
- Any PC/SC compliant reader

**Implementation**:

```csharp
// C# pseudocode
public class NfcReader {
  private SCardContext context;
  private string readerName;
  
  public async Task<string> ReadCardUid() {
    // Connect to reader
    // Send APDU command to get UID
    // Return UID as hex string (e.g., "04A1B2C3D4E5F6")
  }
  
  public bool IsReaderConnected() {
    // Check if reader is present
  }
  
  public event EventHandler<CardTappedEvent> CardTapped;
}
```

**Features**:
- Auto-detect reader on startup
- Poll for card presence (every 500ms)
- Read UID when card detected
- Fire event for card tap
- Handle reader disconnect gracefully
- Beep on successful read (if reader supports)

### 4. Local SQLite Database

**Purpose**: Offline queue and local cache

**Schema**:

```sql
-- Offline transaction queue
CREATE TABLE queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  idempotency_key TEXT UNIQUE NOT NULL,
  transaction_type TEXT NOT NULL, -- earn, redeem, refund, adjust
  customer_id TEXT,
  card_uid TEXT,
  payload JSON NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  retry_count INTEGER DEFAULT 0,
  last_retry_at TIMESTAMP,
  status TEXT DEFAULT 'pending', -- pending, syncing, failed, synced
  error_message TEXT
);

-- Local customer cache (for offline lookups)
CREATE TABLE customer_cache (
  customer_id TEXT PRIMARY KEY,
  card_uid TEXT UNIQUE,
  name TEXT,
  phone TEXT,
  email TEXT,
  balance_euros REAL,
  balance_points INTEGER,
  last_updated TIMESTAMP
);

-- Idempotency tracking (to prevent duplicate queue entries)
CREATE TABLE idempotency_local (
  idempotency_key TEXT PRIMARY KEY,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sync log (for debugging)
CREATE TABLE sync_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  event_type TEXT, -- sync_started, sync_completed, sync_failed, conflict
  details TEXT
);

CREATE INDEX idx_queue_status ON queue(status);
CREATE INDEX idx_customer_cache_uid ON customer_cache(card_uid);
```

**Operations**:

- **Enqueue**: Insert transaction with idempotency key
- **Dequeue**: Read oldest pending transaction
- **Mark Synced**: Update status to 'synced', delete after 24h
- **Mark Failed**: Increment retry_count, update error_message
- **Get Queue Depth**: Count pending transactions
- **Update Cache**: Update customer cache after successful sync

### 5. Sync Service

**Purpose**: Background service that syncs offline queue with cloud backend

**Sync Algorithm**:

```
WHILE true:
  IF internet_available AND queue_not_empty:
    transaction = dequeue_next_pending()
    
    TRY:
      response = call_backend_api(transaction)
      
      IF response.success:
        mark_transaction_synced(transaction)
        update_local_cache(response)
        log_sync_success(transaction)
      ELSE IF response.error == 'CONFLICT':
        apply_conflict_resolution(transaction, response)
      ELSE:
        mark_transaction_failed(transaction, response.error)
        schedule_retry(transaction)
    
    CATCH network_error:
      mark_transaction_failed(transaction, error)
      schedule_retry(transaction)
  
  ELSE IF internet_not_available:
    wait(30_seconds) // Check again later
  
  ELSE IF queue_empty:
    wait(60_seconds) // Poll less frequently
```

**Retry Strategy**:
- Attempt 1: Immediate
- Attempt 2: After 1 minute
- Attempt 3: After 5 minutes
- Attempt 4: After 15 minutes
- Attempt 5+: After 1 hour
- Max attempts: 20
- After max attempts: Mark as "manual intervention required"

**Conflict Resolution**:
- See `02_architecture/CONFLICT_RESOLUTION.md`
- Log all conflicts for review
- Apply automated resolution where possible
- Flag for manual review when needed

### 6. Aniwin POS Integration

**Challenge**: Aniwin.net has no plugin/API

**Integration Options**:

#### Option A: Database Hook (Preferred if available)
- Monitor Aniwin database for new sales
- Read: order_id, amount, timestamp, items
- Trigger: New row in sales table
- Method: Database trigger or polling

#### Option B: File Export
- Configure Aniwin to export completed sales
- File format: CSV or XML
- Location: Shared folder
- Agent polls folder every 30 seconds
- Process new files, archive after processing

#### Option C: Receipt Intercept
- Install virtual printer driver
- Intercept receipt prints
- Parse receipt text for order data
- Most fragile, last resort

**Earn Flow Integration**:

```
1. Aniwin POS sale completed
2. Agent detects new sale (via chosen integration method)
3. Agent prompts cashier: "Tap customer card to award points"
4. Customer taps card
5. Agent reads UID
6. Agent calls backend (or queues if offline): POST /transactions/earn
7. Agent displays confirmation: "1.50 EUR earned! New balance: 14.00 EUR"
8. Receipt prints with points info (if Aniwin supports custom fields)
```

**Redemption Flow Integration**:

Redemption happens BEFORE Aniwin sale:
```
1. Customer wants to redeem points
2. Cashier opens agent redemption UI
3. Customer taps card
4. Agent displays balance
5. Cashier enters redemption amount (e.g., 10.00 EUR)
6. Agent calls backend (or queues): POST /transactions/redeem
7. Agent displays confirmation
8. Cashier applies 10.00 EUR manual discount in Aniwin POS
9. Aniwin sale completes with discount
```

**See**: `04_integrations/ANIWIN_POS_INTEGRATION.md` for details

## Installation and Deployment

### Installer Requirements

**Windows Installer** (MSI or setup.exe):
- Install application files
- Install as Windows Service (auto-start)
- Install PC/SC NFC drivers (if not present)
- Create SQLite database in AppData folder
- Create desktop shortcut
- Add to Windows startup (optional)

**Configuration**:
- Backend API URL
- Terminal ID
- API Key (secure storage)
- Language preference

**Uninstaller**:
- Stop Windows Service
- Remove application files
- Preserve SQLite database (option to delete)

### Windows Service Configuration

**Service Name**: `FidelityPointsAgent`  
**Display Name**: `Fidelity Points Loyalty Agent`  
**Start Type**: Automatic  
**Recovery**: Restart on failure  

**Service Responsibilities**:
- Run sync service in background
- Monitor NFC reader
- Provide system tray icon
- Launch UI when clicked

### System Tray

**Icon States**:
- Green: Online, queue empty
- Yellow: Online, queue not empty (syncing)
- Red: Offline, queue not empty
- Gray: Service stopped

**Right-Click Menu**:
- Open Dashboard
- Manual Sync Now
- View Sync Log
- Settings
- Exit

## Offline Behavior

### Offline Capabilities

**What Works Offline**:
- Card reading (NFC UID)
- Transaction queuing (earn, redeem, adjust)
- Balance lookup (from local cache)
- Customer enrollment (queued for sync)

**What Doesn't Work Offline**:
- Real-time balance (uses cached balance + queued transactions)
- Balance validation (redemption validation uses estimated balance)
- Cross-terminal consistency (other terminals not synced)

### Offline Redemption

**Risk**: Customer redeems more than actual balance if cache is stale

**Mitigation**:
1. Display warning: "Offline mode - balance may not be current"
2. Limit redemption to cached balance minus queued redemptions
3. Log redemption for sync
4. Backend validates balance during sync
5. If insufficient balance, backend rejects (sync fails)
6. Agent alerts cashier of sync failure
7. Cashier issues refund in POS, or customer pays difference

**Policy Decision**: Accept occasional insufficient balance scenario rather than block all offline redemptions

### Queue Management

**Queue Full**:
- Queue limit: 10,000 transactions (configurable)
- If queue full: Refuse new transactions, display error
- Alert manager to sync issues

**Queue Corruption**:
- SQLite database corruption rare but possible
- If detected: Backup corrupt DB, create new DB
- Log incident for manual recovery

## UI Wireframes

### Main Dashboard (Spanish)

```
┌──────────────────────────────────────────────────┐
│  Fidelity Points - Terminal 001        [ES] [CA] │
├──────────────────────────────────────────────────┤
│                                                   │
│  Estado: ● EN LÍNEA    Última sync: 14:32        │
│  Cola: 0 pendientes                              │
│                                                   │
│  ┌────────────────────────────────────────────┐  │
│  │  Presente la tarjeta del cliente           │  │
│  │                                             │  │
│  │          [🔲] Esperando tarjeta...         │  │
│  │                                             │  │
│  └────────────────────────────────────────────┘  │
│                                                   │
│  [ Inscribir Cliente ]  [ Canjear Puntos ]       │
│  [ Ver Historial ]      [ Configuración ]        │
│                                                   │
└──────────────────────────────────────────────────┘
```

### After Card Tap

```
┌──────────────────────────────────────────────────┐
│  Fidelity Points - Terminal 001        [ES] [CA] │
├──────────────────────────────────────────────────┤
│                                                   │
│  Cliente: Juan García                            │
│  Tarjeta: LC-00001234                            │
│                                                   │
│  ┌────────────────────────────────────────────┐  │
│  │         Saldo Actual                        │  │
│  │                                             │  │
│  │         14.00 €  /  140,000 puntos         │  │
│  │                                             │  │
│  │  Vence pronto: 2.00 € (15 Mar 2026)        │  │
│  └────────────────────────────────────────────┘  │
│                                                   │
│  Últimas transacciones:                          │
│  • 13 Feb 14:23 - Ganado: +1.50 €               │
│  • 10 Feb 11:05 - Ganado: +2.25 €               │
│  • 08 Feb 16:45 - Canjeado: -5.00 €             │
│                                                   │
│  [ Canjear Puntos ]  [ Ver Historial Completo ]  │
│                                                   │
└──────────────────────────────────────────────────┘
```

## Error Handling

### Error Scenarios

| Error | Cause | User Message | Resolution |
|-------|-------|--------------|------------|
| NFC reader not found | USB not connected | "Lector NFC no conectado" | Plug in USB reader, restart |
| Card read failed | Bad card or reader issue | "Error leyendo tarjeta, intente de nuevo" | Re-tap card |
| Card not registered | Unknown UID | "Tarjeta no registrada. ¿Inscribir cliente?" | Offer enrollment |
| API timeout | Network slow/down | "Transacción en cola, se sincronizará" | Queue transaction |
| Insufficient balance | Redemption > balance | "Saldo insuficiente: X€ disponible" | Reduce redemption |
| Queue full | Too many pending | "Cola llena. Contacte soporte." | Manual intervention |

### Logging

**Log Levels**:
- ERROR: System errors, API failures, sync failures
- WARN: Reader disconnected, offline mode, retry attempts
- INFO: Transactions, sync events, UI actions
- DEBUG: Detailed API calls, NFC reads (dev only)

**Log Files**:
- Location: `%AppData%\FidelityPoints\logs\`
- Rotation: Daily, keep 30 days
- Format: JSON for machine parsing

**Log Example**:
```json
{
  "timestamp": "2026-02-13T14:32:15.123Z",
  "level": "INFO",
  "event": "transaction_queued",
  "terminal_id": "TERM-001",
  "transaction_type": "earn",
  "customer_id": "uuid",
  "amount_euros": 1.50,
  "idempotency_key": "TERM-001-20260213-001-uuid"
}
```

## Testing Requirements

### Unit Tests
- NFC reader communication (mocked reader)
- Queue management (SQLite operations)
- Sync logic (mocked API)
- Business logic (earn/redeem calculations)

### Integration Tests
- Real NFC reader reading test cards
- Real SQLite database operations
- Real API calls to test backend
- Offline/online transitions

### End-to-End Tests
- Complete earn flow (POS sale → card tap → points awarded)
- Complete redeem flow (card tap → balance check → redemption)
- Offline scenario (disconnect internet, queue, reconnect, sync)
- Error scenarios (reader disconnect, API down, etc.)

## Related Documents

### Architecture
- `02_architecture/SYSTEM_ARCHITECTURE.md` - Overall architecture
- `02_architecture/CLOUD_BACKEND.md` - API contracts
- `02_architecture/SYNC_STRATEGY.md` - Sync details
- `02_architecture/CONFLICT_RESOLUTION.md` - Conflict handling

### Integrations
- `04_integrations/ANIWIN_POS_INTEGRATION.md` - POS integration
- `04_integrations/NFC_HARDWARE.md` - NFC hardware details

### Operations
- `07_operations/OFFLINE_QUEUE.md` - Queue management details
- `07_operations/ERROR_HANDLING.md` - Error handling
