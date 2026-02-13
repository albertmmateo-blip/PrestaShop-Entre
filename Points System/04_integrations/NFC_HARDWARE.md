# NFC Hardware Integration

**Version**: 1.0  
**Status**: Draft  
**Last Updated**: 2024-02-13

---

## Purpose

Define technical specifications, security requirements, and integration methods for NFC cards and readers used in the Fidelity Points System for customer identification at both POS terminals and web-based card registration.

## Scope

### In Scope
- NFC card specifications (MIFARE, NTAG, ISO14443A)
- Reader hardware recommendations (PC/SC compatible)
- UID extraction and validation
- Reader-to-system communication protocols
- Security considerations (cloning, relay attacks)
- Card registration workflow
- Multi-reader support (POS + customer self-service)
- Browser-based NFC reading (Web NFC API)

### Out of Scope
- Payment processing via NFC (this is for identification only)
- NFC-enabled smartphones as virtual cards (future feature)
- Secure element programming
- Custom card printing/encoding services
- Physical card design/branding

---

## Inputs

### From NFC Card
1. **Card UID (Unique Identifier)**
   - 4-byte (8 hex characters): MIFARE Classic
   - 7-byte (14 hex characters): MIFARE Ultralight, NTAG
   - Example: `04A1B2C3D4E5F6` (7-byte UID)

2. **Card Type** (optional, for validation)
   - ATR (Answer To Reset) string
   - Example: `3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 01 00 00 00 00 6A`

### From NFC Reader
1. **Reader Status**
   - Connected/Disconnected
   - Card present/absent
   - Read success/failure
   - Error codes

2. **Reader Information**
   - Manufacturer
   - Model name
   - Firmware version
   - Supported protocols (ISO14443A/B, ISO15693)

### Configuration Parameters
- Accepted card types (whitelist/blacklist)
- UID validation rules (length, format)
- Duplicate card detection threshold
- Reader timeout settings

---

## Outputs

### To PrestaShop Database
1. **NFC Card Registration**
   ```sql
   UPDATE ps_fidelitypoints_customer
   SET nfc_uid = :card_uid,
       nfc_registered_date = NOW(),
       date_upd = NOW()
   WHERE id_customer = :customer_id;
   ```

2. **Card Usage Log**
   ```sql
   CREATE TABLE IF NOT EXISTS ps_fidelitypoints_nfc_log (
     id_log INT(11) NOT NULL AUTO_INCREMENT,
     nfc_uid VARCHAR(20) NOT NULL,
     reader_id VARCHAR(50),
     action VARCHAR(50), -- 'register', 'purchase', 'query'
     id_customer INT(11),
     success TINYINT(1),
     error_message TEXT,
     ip_address VARCHAR(45),
     date_add DATETIME NOT NULL,
     PRIMARY KEY (id_log),
     KEY nfc_date (nfc_uid, date_add)
   ) ENGINE=InnoDB;
   ```

### To POS Integration Service
- Customer ID mapped from NFC UID
- Customer name and balance (for display)
- Error messages for unregistered cards

### To Customer
- Confirmation message upon successful registration
- Warning if card already registered to another account
- Balance display upon card scan

---

## Main Flows

### Flow 1: NFC Reader Setup (POS Terminal)

**Hardware**: ACR122U USB NFC Reader (recommended)

```
┌─────────────────┐
│ Windows POS PC  │
│ (Aniwin system) │
└────────┬────────┘
         │
         │ USB connection
         ▼
┌─────────────────┐
│ ACR122U Reader  │
│ (PC/SC driver)  │
└────────┬────────┘
         │
         │ PC/SC API calls
         ▼
┌─────────────────┐
│ NFC Service     │
│ (Python/C#)     │
│ - Read UID      │
│ - Validate      │
│ - Send to API   │
└────────┬────────┘
         │
         │ HTTP POST
         ▼
┌─────────────────┐
│ PrestaShop API  │
│ /api/fidelity/  │
│ customer-lookup │
└─────────────────┘
```

**Installation Steps**:

1. **Install PC/SC Driver**
   ```bash
   # Windows: Included in OS
   # Linux: Install pcscd
   sudo apt-get install pcscd pcsc-tools libpcsclite-dev
   
   # macOS: Included in OS
   ```

2. **Install Reader Hardware**
   - Connect ACR122U to USB port
   - Verify driver installation:
     ```bash
     # Windows
     certutil -scinfo
     
     # Linux
     pcsc_scan
     
     # macOS
     system_profiler SPUSBDataType
     ```

3. **Test Card Reading**
   ```python
   # Python example using pyscard
   from smartcard.System import readers
   from smartcard.util import toHexString
   
   r = readers()
   print("Available readers:", r)
   
   connection = r[0].createConnection()
   connection.connect()
   
   # Get UID for MIFARE card
   GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
   data, sw1, sw2 = connection.transmit(GET_UID)
   
   if sw1 == 0x90:
       uid = toHexString(data).replace(' ', '')
       print(f"Card UID: {uid}")
   else:
       print(f"Error: {sw1:02X} {sw2:02X}")
   ```

### Flow 2: Card Registration (Customer Self-Service)

**Scenario**: Customer registers their NFC card in their PrestaShop account.

```
┌─────────────────┐
│ Customer        │
│ (logged in)     │
└────────┬────────┘
         │
         │ Navigate to My Account > NFC Card
         ▼
┌─────────────────────────┐
│ PrestaShop Page         │
│ "Register Your Card"    │
│                         │
│ [Scan Card] button      │
└────────┬────────────────┘
         │
         │ Click "Scan Card"
         ▼
┌─────────────────────────┐
│ Web NFC API             │
│ (Chrome Android/PC)     │
│ navigator.nfc.scan()    │
└────────┬────────────────┘
         │
         │ Card detected
         ▼
┌─────────────────────────┐
│ JavaScript              │
│ - Extract UID           │
│ - Validate format       │
│ - Submit to server      │
└────────┬────────────────┘
         │
         │ AJAX POST /module/fidelitypoints/register-nfc
         ▼
┌─────────────────────────┐
│ PHP Controller          │
│ - Check UID uniqueness  │
│ - Link to customer      │
│ - Return success        │
└─────────────────────────┘
```

**Web Implementation** (Web NFC API):

```html
<!-- views/templates/front/nfc_register.tpl -->
<div id="nfc-register">
    <h2>{l s='Register Your NFC Card' mod='fidelitypoints'}</h2>
    
    <div class="alert alert-info">
        {l s='Place your NFC card on the reader to register it to your account.' mod='fidelitypoints'}
    </div>
    
    <button id="scan-btn" class="btn btn-primary">
        <i class="material-icons">nfc</i>
        {l s='Scan Card' mod='fidelitypoints'}
    </button>
    
    <div id="nfc-status"></div>
</div>

<script>
document.getElementById('scan-btn').addEventListener('click', async () => {
    if ('NDEFReader' in window) {
        try {
            const ndef = new NDEFReader();
            await ndef.scan();
            
            console.log("NFC scan started");
            
            ndef.addEventListener("reading", ({ message, serialNumber }) => {
                // serialNumber is the UID
                const uid = serialNumber.toUpperCase();
                console.log("Card detected:", uid);
                
                registerCard(uid);
            });
            
            ndef.addEventListener("readingerror", () => {
                document.getElementById('nfc-status').innerHTML = 
                    '<div class="alert alert-danger">Read error. Try again.</div>';
            });
            
        } catch (error) {
            console.error("NFC scan failed:", error);
            document.getElementById('nfc-status').innerHTML = 
                '<div class="alert alert-danger">' + error + '</div>';
        }
    } else {
        // Fallback: Manual UID entry or USB reader
        alert('Web NFC not supported. Use a compatible browser or enter UID manually.');
    }
});

function registerCard(uid) {
    fetch('/module/fidelitypoints/register-nfc', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ nfc_uid: uid })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('nfc-status').innerHTML = 
                '<div class="alert alert-success">' + data.message + '</div>';
        } else {
            document.getElementById('nfc-status').innerHTML = 
                '<div class="alert alert-danger">' + data.error + '</div>';
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
</script>
```

**PHP Controller**:

```php
// modules/fidelitypoints/controllers/front/registernfc.php

class FidelityPointsRegisterNFCModuleFrontController extends ModuleFrontController
{
    public function postProcess()
    {
        $this->ajax = true;
        
        if (!$this->context->customer->isLogged()) {
            $this->ajaxDie(json_encode([
                'success' => false,
                'error' => 'Not authenticated'
            ]));
        }
        
        $nfcUid = Tools::getValue('nfc_uid');
        
        // Validate UID format
        if (!$this->validateUID($nfcUid)) {
            $this->ajaxDie(json_encode([
                'success' => false,
                'error' => 'Invalid card UID format'
            ]));
        }
        
        // Check if UID already registered
        $existingCustomer = Db::getInstance()->getValue(
            'SELECT id_customer FROM ' . _DB_PREFIX_ . 'fidelitypoints_customer 
             WHERE nfc_uid = "' . pSQL($nfcUid) . '"'
        );
        
        if ($existingCustomer && $existingCustomer != $this->context->customer->id) {
            $this->ajaxDie(json_encode([
                'success' => false,
                'error' => 'This card is already registered to another account'
            ]));
        }
        
        // Register card
        $result = Db::getInstance()->update(
            'fidelitypoints_customer',
            [
                'nfc_uid' => pSQL($nfcUid),
                'nfc_registered_date' => date('Y-m-d H:i:s'),
                'date_upd' => date('Y-m-d H:i:s')
            ],
            'id_customer = ' . (int)$this->context->customer->id
        );
        
        if ($result) {
            // Log registration
            $this->module->logNFCAction(
                $nfcUid,
                'register',
                $this->context->customer->id,
                true
            );
            
            // Check for pending transactions
            $pendingPoints = $this->module->claimPendingPoints(
                $nfcUid,
                $this->context->customer->id
            );
            
            $message = 'Card registered successfully!';
            if ($pendingPoints > 0) {
                $message .= ' You have been awarded ' . $pendingPoints . ' pending points!';
            }
            
            $this->ajaxDie(json_encode([
                'success' => true,
                'message' => $message,
                'pending_points' => $pendingPoints
            ]));
        } else {
            $this->ajaxDie(json_encode([
                'success' => false,
                'error' => 'Database error. Please try again.'
            ]));
        }
    }
    
    private function validateUID($uid)
    {
        // Remove any separators
        $uid = str_replace([':', '-', ' '], '', $uid);
        
        // Check if hexadecimal
        if (!ctype_xdigit($uid)) {
            return false;
        }
        
        // Check length (4-byte or 7-byte UID)
        $length = strlen($uid);
        if ($length != 8 && $length != 14) {
            return false;
        }
        
        return true;
    }
}
```

### Flow 3: Customer Identification at POS

**Scenario**: Customer presents NFC card at checkout to earn points.

```python
# pos_nfc_service.py
# Runs on POS terminal, monitors NFC reader

import time
import requests
from smartcard.System import readers
from smartcard.util import toHexString

API_URL = "https://yourstore.com/api/fidelity/customer-lookup"
API_KEY = "your_api_key_here"

def read_card_uid(reader):
    """Read UID from NFC card"""
    try:
        connection = reader.createConnection()
        connection.connect()
        
        # Get UID command for MIFARE
        GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
        data, sw1, sw2 = connection.transmit(GET_UID)
        
        if sw1 == 0x90:
            uid = toHexString(data).replace(' ', '')
            return uid
        else:
            return None
    except Exception as e:
        print(f"Card read error: {e}")
        return None

def lookup_customer(uid):
    """Query PrestaShop API for customer info"""
    try:
        response = requests.post(
            API_URL,
            json={'nfc_uid': uid},
            headers={'Authorization': f'Bearer {API_KEY}'},
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"API error: {e}")
        return None

def main():
    # Get available readers
    reader_list = readers()
    if not reader_list:
        print("No NFC readers found")
        return
    
    reader = reader_list[0]
    print(f"Using reader: {reader}")
    
    last_uid = None
    
    while True:
        try:
            # Check if card present
            uid = read_card_uid(reader)
            
            if uid and uid != last_uid:
                print(f"\n=== Card detected: {uid} ===")
                
                # Lookup customer
                customer = lookup_customer(uid)
                
                if customer:
                    print(f"Customer: {customer['name']}")
                    print(f"Points Balance: {customer['points']}")
                    
                    # Display on POS screen (implementation depends on POS system)
                    # display_customer_info(customer)
                else:
                    print("Card not registered")
                    # display_message("Card not registered. Please register at our website.")
                
                last_uid = uid
            
            elif not uid and last_uid:
                # Card removed
                last_uid = None
                print("Card removed")
            
            time.sleep(0.5)
            
        except KeyboardInterrupt:
            print("\nStopping NFC service")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
```

### Flow 4: Bulk Card Registration (Admin)

**Scenario**: Admin pre-registers cards for distribution to customers.

```php
// Admin controller for CSV import of pre-registered cards

public function processBulkUpload()
{
    $uploadedFile = $_FILES['nfc_csv'];
    
    if (!$uploadedFile || $uploadedFile['error'] !== UPLOAD_ERR_OK) {
        $this->errors[] = 'File upload failed';
        return;
    }
    
    $csvData = array_map('str_getcsv', file($uploadedFile['tmp_name']));
    $header = array_shift($csvData); // Remove header row
    
    $success = 0;
    $errors = [];
    
    foreach ($csvData as $row) {
        list($nfcUid, $email) = $row;
        
        // Find customer by email
        $customer = Customer::getByEmail($email);
        
        if (!$customer) {
            $errors[] = "Customer not found: $email";
            continue;
        }
        
        // Validate UID
        if (!$this->validateUID($nfcUid)) {
            $errors[] = "Invalid UID: $nfcUid";
            continue;
        }
        
        // Register card
        $result = Db::getInstance()->update(
            'fidelitypoints_customer',
            [
                'nfc_uid' => pSQL($nfcUid),
                'nfc_registered_date' => date('Y-m-d H:i:s')
            ],
            'id_customer = ' . (int)$customer->id
        );
        
        if ($result) {
            $success++;
        } else {
            $errors[] = "Database error for: $email";
        }
    }
    
    $this->confirmations[] = "$success cards registered successfully";
    if (!empty($errors)) {
        $this->errors = array_merge($this->errors, $errors);
    }
}
```

---

## Edge Cases

### 1. Card UID Collision (Extremely Rare)
**Scenario**: Two cards with identical UIDs (manufacturing defect or cloning).

**Handling**:
- First-come-first-served: First registration wins
- Log warning for manual review
- Display error to second registration attempt

### 2. Customer Loses Card
**Scenario**: Card lost/stolen, customer wants to de-register.

**Handling**:
```php
public function deregisterCard($customerId)
{
    // Unlink card from account
    Db::getInstance()->update(
        'fidelitypoints_customer',
        ['nfc_uid' => NULL, 'nfc_registered_date' => NULL],
        'id_customer = ' . (int)$customerId
    );
    
    // Log action
    Logger::addLog("NFC card deregistered for customer $customerId", 1);
    
    // Notify customer via email
    // ...
}
```

### 3. Multiple Cards Per Customer
**Scenario**: Customer wants to register multiple cards (family members, backup).

**Current**: Not supported (one card per customer)

**Future Enhancement**:
```sql
CREATE TABLE ps_fidelitypoints_customer_nfc (
  id INT AUTO_INCREMENT PRIMARY KEY,
  id_customer INT NOT NULL,
  nfc_uid VARCHAR(20) NOT NULL,
  card_label VARCHAR(50), -- 'Primary', 'Spouse', 'Backup'
  active TINYINT(1) DEFAULT 1,
  date_add DATETIME,
  UNIQUE KEY (nfc_uid),
  KEY (id_customer)
);
```

### 4. Card Read Failure at POS
**Scenario**: Card damaged, reader malfunction, interference.

**Handling**:
- Retry 3 times with 1-second delay
- Fallback: Manual customer ID entry by cashier
- Display error message: "Please try again or provide customer ID"

### 5. Web NFC Not Supported (Browser Limitation)
**Scenario**: Customer using unsupported browser (Safari, Firefox).

**Handling**:
- Feature detection:
  ```javascript
  if (!('NDEFReader' in window)) {
      // Show manual entry form
      document.getElementById('manual-entry').style.display = 'block';
  }
  ```
- Alternative: USB reader connected to customer's PC (if available)
- Alternative: Admin registers card on customer's behalf (in-store)

---

## Failure Modes

### 1. Reader Hardware Failure
**Symptoms**: Reader not detected, intermittent reads, constant errors.

**Impact**: High - Cannot identify customers at POS.

**Detection**:
- Monitor reader connectivity status
- Alert if no successful reads in 1 hour during business hours

**Mitigation**:
- Keep spare reader on-site
- Fallback to manual customer ID entry
- Document error for warranty claim

### 2. Driver Compatibility Issues
**Symptoms**: Reader detected but cannot communicate (Windows updates, OS change).

**Impact**: High - System inoperable.

**Mitigation**:
- Pin driver version, avoid automatic updates
- Test driver compatibility before OS upgrades
- Keep offline driver installer backup

### 3. UID Read Corruption
**Symptoms**: Invalid UID format returned (non-hex, wrong length).

**Impact**: Medium - Single transaction affected.

**Detection**:
```python
def is_valid_uid(uid):
    if not uid:
        return False
    uid_clean = uid.replace(':', '').replace('-', '')
    if not all(c in '0123456789ABCDEFabcdef' for c in uid_clean):
        return False
    if len(uid_clean) not in [8, 14]:
        return False
    return True
```

**Mitigation**:
- Retry read immediately
- Log corrupted UIDs for pattern analysis
- Replace card if persistent issue

### 4. Database Connection Failure During Registration
**Symptoms**: Card scanned but not saved to database.

**Impact**: Medium - Registration fails, customer must retry.

**Mitigation**:
- Show clear error message to customer
- Implement retry logic with exponential backoff
- Queue registration for offline processing if API unavailable

### 5. Cloned Card Used (Security)
**Symptoms**: Same UID used at multiple locations simultaneously or in rapid succession.

**Impact**: Critical - Fraudulent point earning.

**Detection**:
```sql
-- Alert if same card used at different stores within 1 hour
SELECT nfc_uid, COUNT(DISTINCT reader_id) as locations
FROM ps_fidelitypoints_nfc_log
WHERE date_add > DATE_SUB(NOW(), INTERVAL 1 HOUR)
GROUP BY nfc_uid
HAVING locations > 1;
```

**Mitigation**:
- Freeze account automatically
- Admin review and contact customer
- Issue replacement card with new UID

---

## Offline Behavior

### POS Reader Offline (No Internet)
**Impact**: Cannot validate customer or award points.

**Behavior**:
- Continue sale without points (standard POS operation)
- Log card UID locally for later reconciliation
- Customer receives points when system reconnects

### Customer Registration Offline
**Impact**: Cannot register card immediately.

**Behavior**:
- Show "Service temporarily unavailable" message
- Allow manual UID entry to queue registration
- Process queued registrations when online

---

## Security Considerations

### 1. Card Cloning Risk
**Threat**: MIFARE Classic UID is not secure, can be cloned easily.

**Mitigation**:
- **Accept risk**: Low-value system (loyalty points, not payment)
- Monitor for suspicious patterns (same card, multiple locations)
- Consider upgrading to MIFARE DESFire for high-security needs
- Rate limiting: Max 10 transactions per card per day

**MIFARE Classic vs. DESFire**:
| Feature | Classic 1K | DESFire EV2 |
|---------|------------|-------------|
| Security | Low (UID easily cloned) | High (crypto, secure element) |
| Cost | ~$0.20/card | ~$2.50/card |
| Use Case | Identification | Payment/Access Control |
| Recommended | Yes (for loyalty) | Overkill for this system |

### 2. Relay Attacks
**Threat**: Attacker intercepts NFC communication, replays to another reader.

**Mitigation**:
- Use timestamp validation in API calls
- Implement nonce/challenge-response (overkill for v1.0)
- Physical security: POS terminal in controlled environment

### 3. UID Enumeration
**Threat**: Attacker systematically tests UIDs to find valid cards.

**Mitigation**:
- Rate limiting on API: Max 10 lookups per IP per minute
- Log and alert on excessive failed lookups
- Implement CAPTCHA on web registration page

### 4. Reader Tampering
**Threat**: Malicious reader installed to capture UIDs.

**Mitigation**:
- Physical security: Tamper-evident seals on reader
- Regular hardware audits
- Use readers with LED indicators (visible when active)

### 5. Man-in-the-Middle (API Communication)
**Threat**: Interception of API calls with customer data.

**Mitigation**:
- **Mandatory TLS/HTTPS** for all API communication
- Certificate pinning for POS integration service
- API authentication tokens, rotate monthly

### 6. Privacy Concerns (GDPR)
**Issue**: NFC UID is persistent identifier linked to customer.

**Compliance**:
- Obtain explicit consent during registration
- Allow customer to de-register card anytime
- Anonymize UID in logs after 90 days
- Include in GDPR data export requests

---

## Related Documents

### Internal References
- [../01_project/REQUIREMENTS.md](../01_project/REQUIREMENTS.md) - Project requirements
- [./ANIWIN_POS_INTEGRATION.md](./ANIWIN_POS_INTEGRATION.md) - POS system integration
- [./PRESTASHOP_MODULE.md](./PRESTASHOP_MODULE.md) - Module implementation
- [../05_data/CUSTOMER_MAPPING.md](../05_data/CUSTOMER_MAPPING.md) - NFC UID to customer mapping
- [../06_security/FRAUD_PREVENTION.md](../06_security/FRAUD_PREVENTION.md) - Anti-fraud measures
- [../07_operations/HARDWARE_MAINTENANCE.md](../07_operations/HARDWARE_MAINTENANCE.md) - Reader maintenance

### External References
- **PC/SC Workgroup**: https://www.pcscworkgroup.com/
- **PC/SC Lite (Linux)**: https://pcsclite.apdu.fr/
- **pyscard Documentation**: https://pyscard.sourceforge.io/
- **Web NFC API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_NFC_API
- **MIFARE Specifications**: https://www.nxp.com/products/rfid-nfc/mifare-hf/mifare-classic:MC_41863
- **ACR122U Manual**: https://www.acs.com.hk/en/products/3/acr122u-usb-nfc-reader/

---

## Open Questions / TODOs

### High Priority
- [ ] **Reader Model Selection**: Confirm ACR122U or alternative
  - Budget: €30-50 per reader
  - Quantity needed: [TBD based on store count]
  - Supplier: Amazon, AliExpress, or official distributor?

- [ ] **Card Procurement**: Order NFC cards
  - Type: MIFARE Classic 1K (recommended)
  - Quantity: 1000 cards for initial rollout
  - Custom printing with company logo?
  - Pre-encoding UIDs to database before distribution?

- [ ] **Browser Compatibility Testing**: Web NFC API support
  - Test on Chrome Android (primary)
  - Test on Chrome Desktop with USB reader
  - Fallback UI for unsupported browsers

### Medium Priority
- [ ] **Multi-Reader Setup**: If multiple POS terminals
  - USB hub compatibility
  - Reader ID assignment for transaction logging
  - Interference testing (readers too close together)

- [ ] **Card Lifetime**: Expected durability
  - Test card read reliability after 1000 scans
  - Replacement policy for worn cards
  - Customer notification for failing cards

- [ ] **Alternative Card Types**: Evaluate other options
  - NTAG213/215/216 (lower cost, similar UID security)
  - ISO14443B or ISO15693 for reduced interference
  - Dual-frequency cards (HF + UHF) for future expansion

### Low Priority
- [ ] **NFC Stickers/Keychains**: Alternative form factors
  - Easier to carry than card
  - Same UID technology
  - Test adhesive durability on phone cases

- [ ] **Virtual Card (Mobile)**: NFC from smartphone
  - Android HCE (Host Card Emulation)
  - iOS Wallet integration (Apple Pay framework)
  - Security: Rotating UIDs vs. static

- [ ] **Backup Identification Methods**: If NFC fails
  - QR code printed on card (UID encoded)
  - Phone number lookup
  - Email address verification

- [ ] **Reader Diagnostics Dashboard**: Web interface
  - Real-time reader status
  - Read success rate metrics
  - Card type distribution statistics

---

**Hardware Specifications Summary**

| Component | Specification | Notes |
|-----------|---------------|-------|
| **Recommended Reader** | ACR122U | USB, PC/SC, €30-40 |
| **Alternative Readers** | ACR1252U, HID Omnikey 5022 | Higher cost, more features |
| **Card Type** | MIFARE Classic 1K | 4-byte or 7-byte UID |
| **Card Alternative** | NTAG213 | Cheaper, NFC Forum Type 2 |
| **Interface** | USB 2.0 | Full-speed (12 Mbps) |
| **Protocol** | ISO/IEC 14443 Type A | 13.56 MHz |
| **Read Range** | 0-5 cm | Typical 3 cm optimal |
| **Read Speed** | < 100ms | UID extraction time |
| **Compatibility** | Windows 7+, Linux, macOS | PC/SC drivers |
| **Power** | USB bus-powered | No external adapter needed |

---

**Document Owner**: Infrastructure Team  
**Review Cycle**: Semi-annually or before hardware purchases  
**Feedback**: [Create issue in project repository]
