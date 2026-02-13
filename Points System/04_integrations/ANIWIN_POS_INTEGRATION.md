# Aniwin POS Integration

**Version**: 1.0  
**Status**: Draft  
**Last Updated**: 2024-02-13

---

## Purpose

Define the integration strategy between the Fidelity Points System and Aniwin.net POS to automatically detect in-store purchases and award points to customers without manual intervention by cashiers.

## Scope

### In Scope
- Real-time sale detection from Aniwin POS
- Automatic point calculation and award
- Customer identification via NFC card
- Multiple integration methods (database, file, receipt)
- Order data synchronization to PrestaShop
- Transaction reconciliation
- Error handling and retry mechanisms

### Out of Scope
- Modifications to Aniwin POS core software
- POS hardware replacement
- Direct payment processing
- Inventory management
- Employee training materials
- Receipt printer configuration

---

## Inputs

### From Aniwin POS
1. **Sale Transaction Data**
   - Transaction ID (unique identifier)
   - Timestamp (ISO 8601 format)
   - Total amount (EUR, with VAT)
   - Items purchased (SKU, quantity, unit price, name)
   - Payment method (cash, card, mixed)
   - Cashier ID
   - Store location ID

2. **Customer Identification**
   - NFC card UID (read at payment terminal)
   - Alternative: Manual customer ID entry
   - Alternative: Phone number lookup

3. **Transaction Status**
   - Completed (finalized sale)
   - Voided (cancelled transaction)
   - Refunded (return processed)

### Configuration Parameters
- Database connection string (if using DB hook method)
- Export file path (if using file export method)
- Receipt format specifications (if using receipt intercept)
- Points conversion rate (e.g., 1 point per 10€)
- Minimum purchase amount for points
- Excluded product categories

---

## Outputs

### To PrestaShop Database
1. **Order Creation**
   ```sql
   INSERT INTO ps_orders (
     id_customer,
     id_cart,
     reference,
     current_state,
     payment,
     total_paid,
     total_products,
     date_add,
     source
   ) VALUES (
     :customer_id,
     :cart_id,
     'POS-' || :aniwin_transaction_id,
     2, -- Payment accepted
     :payment_method,
     :total_amount,
     :products_total,
     :transaction_time,
     'aniwin_pos'
   );
   ```

2. **Points Award**
   ```sql
   INSERT INTO ps_fidelitypoints_transactions (
     id_customer,
     points,
     id_order,
     transaction_type,
     description,
     date_add
   ) VALUES (
     :customer_id,
     :calculated_points,
     :order_id,
     'purchase',
     'In-store purchase at ' || :store_name,
     :transaction_time
   );
   ```

3. **Synchronization Log**
   - Transaction ID mapping
   - Sync status (success/failure)
   - Error messages if any
   - Retry count

### To Customer
- WhatsApp notification (via integration, see WHATSAPP_MESSAGING.md)
- Points balance update visible in PrestaShop account
- Optional: Email receipt with points earned

---

## Main Flows

### Flow 1: Database Hook Method (Recommended)

**Description**: Direct database monitoring of Aniwin POS transactions table.

```
┌──────────────┐
│ Aniwin POS   │
│ (Sale Made)  │
└──────┬───────┘
       │
       │ INSERT INTO sales_transactions
       ▼
┌──────────────────┐
│ Aniwin Database  │
│ (SQL Server)     │
└──────┬───────────┘
       │
       │ Database Trigger or
       │ Polling Service
       ▼
┌──────────────────┐
│ Integration      │
│ Service          │
│ (PHP/Python)     │
└──────┬───────────┘
       │
       │ 1. Validate transaction
       │ 2. Map customer (NFC UID)
       │ 3. Calculate points
       │ 4. Create PrestaShop order
       ▼
┌──────────────────┐
│ PrestaShop DB    │
│ (ps_orders,      │
│  ps_fidelity*)   │
└──────────────────┘
```

**Implementation Steps**:

1. **Database Access Setup**
   - Request read-only credentials for Aniwin database
   - Identify sales transaction table (e.g., `ventas`, `transacciones`)
   - Map required fields to PrestaShop data model

2. **Polling Service** (if triggers not possible)
   ```php
   // Check every 30 seconds for new transactions
   while (true) {
       $newSales = $aniwinDB->query("
           SELECT * FROM ventas 
           WHERE fecha >= :last_sync 
           AND estado = 'completada'
           AND NOT EXISTS (
               SELECT 1 FROM sync_log 
               WHERE aniwin_id = ventas.id
           )
       ");
       
       foreach ($newSales as $sale) {
           try {
               processSale($sale);
               logSync($sale->id, 'success');
           } catch (Exception $e) {
               logSync($sale->id, 'error', $e->getMessage());
           }
       }
       
       sleep(30);
   }
   ```

3. **Transaction Processing**
   - Validate customer mapping (NFC UID → PrestaShop customer ID)
   - Create order in PrestaShop with `source = 'aniwin_pos'`
   - Calculate points: `floor(total_amount / 10)`
   - Award points to customer account
   - Update sync status

### Flow 2: File Export Method

**Description**: Aniwin exports transaction data to CSV/XML file, integration service processes periodically.

```
┌──────────────┐
│ Aniwin POS   │
│              │
└──────┬───────┘
       │
       │ Export at end of day or hourly
       ▼
┌──────────────────┐
│ Shared Folder    │
│ /exports/sales/  │
│ sales_20240213.  │
│ csv              │
└──────┬───────────┘
       │
       │ SFTP/SMB/Local
       ▼
┌──────────────────┐
│ Integration      │
│ Service          │
│ (Cron Job)       │
└──────┬───────────┘
       │
       │ Parse, validate, process
       ▼
┌──────────────────┐
│ PrestaShop       │
└──────────────────┘
```

**File Format Example** (CSV):
```csv
transaction_id,date_time,customer_nfc,total_eur,items,payment_method,status
TX20240213001,2024-02-13T10:15:30,04A1B2C3D4E5,45.60,"SKU123:2:15.30,SKU456:1:14.00",card,completed
TX20240213002,2024-02-13T10:22:15,04F6G7H8I9J0,12.50,"SKU789:1:12.50",cash,completed
```

**Cron Configuration**:
```bash
# Process new sales files every hour
0 * * * * /usr/bin/php /var/www/prestashop/scripts/process_aniwin_sales.php
```

### Flow 3: Receipt Intercept Method (Alternative)

**Description**: Capture receipt data via thermal printer output or Z-report.

**Pros**: No database access needed  
**Cons**: Complex parsing, potential data loss

- Parse receipt text format
- Extract transaction details via regex
- Higher error rate due to format variations

---

## Edge Cases

### 1. Customer Not Registered
**Scenario**: NFC card presented but not linked to PrestaShop account.

**Handling**:
- Log transaction with NFC UID
- Create "pending points" entry
- Send WhatsApp message (if phone number known): "Card not registered. Visit [URL] to claim your points."
- Manual reconciliation tool in admin panel

### 2. Duplicate Transaction Detection
**Scenario**: Same transaction ID appears twice (retry, export duplication).

**Handling**:
```php
$existing = Order::getByReference('POS-' . $transactionId);
if ($existing) {
    Logger::log("Duplicate transaction ignored: " . $transactionId);
    return; // Skip processing
}
```

### 3. Transaction Voided After Points Awarded
**Scenario**: Sale cancelled but points already given.

**Handling**:
- Monitor void/refund status in Aniwin
- Reverse point transaction:
  ```sql
  INSERT INTO ps_fidelitypoints_transactions (
    id_customer, points, transaction_type, description
  ) VALUES (
    :customer_id, -:points, 'void', 'Sale cancelled: POS-XXX'
  );
  ```
- Update order status to cancelled

### 4. Mixed Payment with Redeemed Points
**Scenario**: Customer pays partially with PrestaShop points, partially with cash at POS.

**Handling**:
- Not supported in v1.0
- TODO: Implement QR code redemption at POS (see Open Questions)

### 5. Network Outage During Processing
**Scenario**: Connection to PrestaShop lost mid-transaction.

**Handling**:
- Queue transactions locally (SQLite or file-based queue)
- Retry with exponential backoff: 1m, 5m, 15m, 1h
- Admin alert if queue size > 100 or age > 24h

### 6. Time Zone Mismatch
**Scenario**: Aniwin POS in UTC, PrestaShop in Europe/Madrid.

**Handling**:
```php
$transactionTime = new DateTime($sale->fecha, new DateTimeZone('UTC'));
$transactionTime->setTimezone(new DateTimeZone('Europe/Madrid'));
$timestamp = $transactionTime->format('Y-m-d H:i:s');
```

---

## Failure Modes

### 1. Database Connection Failure
**Symptoms**: Polling service cannot connect to Aniwin database.

**Impact**: High - No points awarded for in-store purchases.

**Detection**: 
- Connection timeout exceptions
- Health check endpoint fails

**Mitigation**:
- Retry connection with backoff
- Alert admin via email/Slack after 3 failures
- Fall back to file export method if available

### 2. Customer Mapping Failure
**Symptoms**: NFC UID not found in customer mapping table.

**Impact**: Medium - Points not awarded, customer dissatisfaction.

**Detection**: 
- `customer_id = NULL` in processing log

**Mitigation**:
- Store unmapped transactions in `ps_fidelity_pending_transactions`
- Admin panel to manually map and award points
- Customer notification with claim link

### 3. Invalid Transaction Data
**Symptoms**: Missing required fields (amount, timestamp, etc.).

**Impact**: Low - Single transaction affected.

**Detection**: 
- Data validation exceptions
- Required field NULL checks fail

**Mitigation**:
```php
if (!isset($sale->total_amount) || $sale->total_amount <= 0) {
    Logger::error("Invalid sale amount", ['sale_id' => $sale->id]);
    markForManualReview($sale->id);
    return;
}
```

### 4. PrestaShop Order Creation Failed
**Symptoms**: Database constraint violation, duplicate key, etc.

**Impact**: Medium - Points not awarded, order not synced.

**Detection**: 
- SQL exception during INSERT
- Order ID not returned

**Mitigation**:
- Log full error with stack trace
- Add to retry queue (up to 5 attempts)
- Mark transaction for manual review after max retries

### 5. Point Calculation Error
**Symptoms**: Wrong points awarded (negative, zero, excessive).

**Impact**: High - Financial discrepancy, customer trust issues.

**Detection**: 
```php
assert($calculatedPoints >= 0 && $calculatedPoints < $saleAmount * 10);
```

**Mitigation**:
- Strict validation rules before awarding
- Daily reconciliation report comparing total sales vs. total points
- Admin alert if discrepancy > 5%

---

## Offline Behavior

### Aniwin POS Offline
**Impact**: Sales continue at POS, but no real-time sync.

**Behavior**:
- Aniwin stores transactions locally
- Integration service continues attempting to connect
- Once online, batch process all pending transactions
- Points awarded retroactively with original transaction timestamp

### PrestaShop Database Offline
**Impact**: Cannot create orders or award points.

**Behavior**:
- Integration service queues transactions locally
- SQLite-based queue:
  ```sql
  CREATE TABLE pending_sync (
    id INTEGER PRIMARY KEY,
    aniwin_transaction_id TEXT,
    transaction_data TEXT, -- JSON
    attempts INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    last_attempt TIMESTAMP
  );
  ```
- Process queue when connection restored
- Admin notification if offline > 1 hour

### Network Partition
**Impact**: POS and PrestaShop both online but cannot communicate.

**Behavior**:
- Similar to PrestaShop offline
- Integration service must be strategically placed (same network as PrestaShop recommended)

---

## Security Considerations

### 1. Database Credentials Protection
- Store Aniwin DB credentials in encrypted configuration file
- Use read-only database user with minimal privileges
- Rotate credentials quarterly
- Never log credentials in plaintext

### 2. SQL Injection Prevention
```php
// Always use parameterized queries
$stmt = $aniwinDB->prepare("
    SELECT * FROM ventas WHERE id = :id
");
$stmt->execute(['id' => $transactionId]);
```

### 3. Data in Transit
- Use TLS for database connections (SQL Server: `Encrypt=yes`)
- SFTP (not FTP) for file transfers
- VPN tunnel between POS network and PrestaShop server if crossing internet

### 4. Audit Trail
- Log every transaction processing attempt
- Store: timestamp, transaction ID, customer ID, points awarded, status
- Retention: 7 years (tax compliance)
- Tamper-proof logging (append-only)

### 5. NFC Card Security
- Validate UID format before processing (see NFC_HARDWARE.md)
- Check for suspicious patterns (sequential UIDs indicating cloning)
- Rate limiting: Max 5 transactions per card per hour
- Alert on duplicate simultaneous use (same card, different locations)

### 6. Access Control
- Integration service runs as dedicated system user
- No direct admin access to PrestaShop database
- Use PrestaShop API where possible
- Principle of least privilege

### 7. Transaction Integrity
- Checksum validation for file exports
- Idempotent processing (duplicate transaction IDs ignored)
- Atomic operations (order + points in database transaction)
- Rollback mechanism for partial failures

---

## Related Documents

### Internal References
- [../02_architecture/DATA_FLOW.md](../02_architecture/DATA_FLOW.md) - Overall system data flow
- [../03_features/POINTS_CALCULATION.md](../03_features/POINTS_CALCULATION.md) - Point calculation rules
- [./NFC_HARDWARE.md](./NFC_HARDWARE.md) - NFC card/reader specifications
- [./PRESTASHOP_MODULE.md](./PRESTASHOP_MODULE.md) - PrestaShop module implementation
- [./WHATSAPP_MESSAGING.md](./WHATSAPP_MESSAGING.md) - Customer notifications
- [../05_data/CUSTOMER_MAPPING.md](../05_data/CUSTOMER_MAPPING.md) - NFC UID to customer mapping
- [../05_data/ORDER_SCHEMA.md](../05_data/ORDER_SCHEMA.md) - PrestaShop order structure
- [../06_security/DATA_PROTECTION.md](../06_security/DATA_PROTECTION.md) - GDPR compliance
- [../07_operations/MONITORING.md](../07_operations/MONITORING.md) - System monitoring

### External References
- Aniwin POS Documentation: https://aniwin.net/docs
- PrestaShop Order API: https://devdocs.prestashop-project.org/8/webservice/
- PC/SC Reader Integration: https://pcsclite.apdu.fr/
- SQL Server Connection Strings: https://www.connectionstrings.com/sql-server/

---

## Open Questions / TODOs

### High Priority
- [ ] **Aniwin Database Schema**: Request complete table schema from Aniwin support
  - Transaction table name and fields
  - Customer identifier field (if any)
  - Status codes for void/refund
  - Access method: Direct DB or API?

- [ ] **Integration Method Selection**: Decide between DB hook, file export, or hybrid
  - Schedule meeting with Aniwin reseller
  - Test environment access needed
  - Performance testing (handle 100 transactions/day)

- [ ] **NFC Reader at POS**: Which readers are compatible with Aniwin?
  - Current hardware: [TO BE DETERMINED]
  - USB or serial connection?
  - Driver installation required?

### Medium Priority
- [ ] **Points Redemption at POS**: How to handle PrestaShop points used in-store?
  - QR code shown in PrestaShop account
  - Cashier scans code to apply discount
  - Bidirectional sync needed

- [ ] **Refund Handling**: Detailed workflow for returns
  - Automatic point reversal
  - Time limit (30 days?)
  - Partial refunds calculation

- [ ] **Multi-Store Support**: If multiple physical locations
  - Store identification in transaction data
  - Separate point pools or unified?
  - Location-specific promotions

### Low Priority
- [ ] **Historical Data Import**: Import past sales for retroactive points
  - Data format from Aniwin
  - Mapping old transactions to customers
  - One-time script or ongoing reconciliation?

- [ ] **Performance Optimization**: 
  - Batch processing vs. real-time per transaction
  - Caching strategies for customer mapping
  - Database indexing recommendations

- [ ] **Fallback UI**: Manual point award interface for cashiers
  - When NFC fails or card forgotten
  - Receipt number lookup
  - Require manager approval?

---

**Document Owner**: Integration Team  
**Review Cycle**: Quarterly or before major POS updates  
**Feedback**: [Create issue in project repository]
