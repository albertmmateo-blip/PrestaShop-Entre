# API Authentication: Terminal and Module Credentials

## Purpose

Define all authentication mechanisms for the loyalty points system, including terminal authentication (API keys), PrestaShop module authentication, future JWT token implementation, credential management, rotation procedures, rate limiting, and IP whitelisting.

## Scope

### In Scope
- Terminal authentication (POS Windows Agent)
- API key format and generation
- API key storage and transmission
- PrestaShop module authentication
- JWT token design (future implementation)
- API key rotation procedures
- Rate limiting per terminal
- IP whitelisting (optional feature)
- Credential revocation
- Authentication failure handling

### Out of Scope
- Authorization and role-based access control (see `SECURITY_MODEL.md`)
- Manager authentication for manual adjustments (see `SECURITY_MODEL.md`)
- NFC card security (see `NFC_SECURITY.md`)
- Idempotency keys (see `IDEMPOTENCY.md`)

## Authentication Methods Overview

| Component | Authentication Method | Status | Use Case |
|-----------|----------------------|--------|----------|
| **POS Windows Agent** | API Key + Terminal ID | ✅ Implemented | All POS transactions |
| **PrestaShop Module** | PrestaShop API Credentials | ✅ Implemented | Module configuration, admin access |
| **Mobile App (Future)** | JWT Token | 🔮 Future | Customer self-service |
| **Admin Panel** | PrestaShop Session | ✅ Implemented | Admin management |

## Terminal Authentication: API Keys

### Overview
Each POS terminal has unique API key tied to specific terminal ID. This credentials pair authenticates all API requests from that terminal.

### API Key Format

#### Structure
```
loyalty_<environment>_<terminal_id>_<random_32_chars>
```

#### Example
```
loyalty_prod_POS-TERMINAL-001_k9m2n5p8q1r4s7t0u3v6w9x2y5z8
```

#### Components
- **Prefix**: `loyalty_` (identifies system)
- **Environment**: `prod`, `staging`, `dev`
- **Terminal ID**: Unique terminal identifier (e.g., `POS-TERMINAL-001`)
- **Random String**: 32-character cryptographically random string (alphanumeric)

#### Generation Algorithm
```python
import secrets
import string

def generate_api_key(environment: str, terminal_id: str) -> str:
    """Generate secure API key for terminal."""
    alphabet = string.ascii_lowercase + string.digits
    random_part = ''.join(secrets.choice(alphabet) for _ in range(32))
    return f"loyalty_{environment}_{terminal_id}_{random_part}"

# Example
api_key = generate_api_key("prod", "POS-TERMINAL-001")
# loyalty_prod_POS-TERMINAL-001_k9m2n5p8q1r4s7t0u3v6w9x2y5z8
```

### API Key Properties
- **Length**: 70-80 characters (varies by terminal ID length)
- **Character Set**: Lowercase letters and digits (no special chars for compatibility)
- **Entropy**: 160 bits (32 chars × 5 bits/char)
- **Collision Probability**: Negligible (2^160 possible keys)
- **Human-Readable**: Partially (environment and terminal ID visible)

### API Key Generation Process

#### Step 1: Provision New Terminal
**When**: New POS terminal added to system

**Process**:
1. Admin logs into PrestaShop admin panel
2. Navigate to Loyalty Module → Terminals
3. Click "Add New Terminal"
4. Enter terminal details:
   - Terminal ID (e.g., `POS-TERMINAL-001`)
   - Location (e.g., "Main Store - Checkout 1")
   - Manager assigned (e.g., "manager_maria")
5. Click "Generate API Key"
6. System generates API key using cryptographically secure random
7. API key displayed ONE TIME ONLY: 
   ```
   API Key: loyalty_prod_POS-TERMINAL-001_k9m2n5p8q1r4s7t0u3v6w9x2y5z8
   
   ⚠️ SAVE THIS KEY SECURELY. IT WILL NOT BE SHOWN AGAIN.
   ```
8. Admin copies key to secure password manager

#### Step 2: Install API Key on Terminal
**When**: Initial POS agent installation or key rotation

**Process**:
1. IT staff opens POS Windows Agent
2. Navigate to Settings → Authentication
3. Paste API key into "API Key" field
4. Enter Terminal ID: `POS-TERMINAL-001`
5. Click "Test Connection" (validates key with API)
6. If successful: Key saved to Windows Credential Manager (encrypted)
7. Agent restarts with new credentials

### API Key Storage

#### Server-Side Storage (Cloud API)
**Database Table**: `terminal_credentials`

```sql
CREATE TABLE terminal_credentials (
  id SERIAL PRIMARY KEY,
  terminal_id VARCHAR(50) UNIQUE NOT NULL,
  api_key_hash VARCHAR(64) NOT NULL,  -- SHA-256 hash of API key
  location VARCHAR(200),
  manager_assigned VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW(),
  last_used_at TIMESTAMP,
  rotation_due_date TIMESTAMP,
  status VARCHAR(20) DEFAULT 'active', -- active, revoked, expired
  created_by VARCHAR(100),
  ip_whitelist TEXT[]  -- Optional: array of allowed IPs
);

-- Index for fast lookup
CREATE INDEX idx_terminal_id ON terminal_credentials(terminal_id);
CREATE INDEX idx_status ON terminal_credentials(status);
```

**Security**:
- API keys never stored in plaintext
- Only SHA-256 hash stored
- Rainbow table attack prevented by unique keys

**Hash Verification**:
```python
import hashlib

def hash_api_key(api_key: str) -> str:
    """Hash API key for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()

def verify_api_key(api_key: str, stored_hash: str) -> bool:
    """Verify API key against stored hash."""
    return hash_api_key(api_key) == stored_hash
```

#### Client-Side Storage (POS Agent)
**Location**: Windows Credential Manager

**Storage Process**:
```csharp
using System.Security.Cryptography;
using Windows.Security.Credentials;

public class CredentialStorage
{
    private const string ResourceName = "LoyaltySystem.ApiKey";
    
    public void SaveApiKey(string terminalId, string apiKey)
    {
        var vault = new PasswordVault();
        var credential = new PasswordCredential(
            ResourceName,
            terminalId,  // Username field
            apiKey       // Password field
        );
        vault.Add(credential);
    }
    
    public string RetrieveApiKey(string terminalId)
    {
        var vault = new PasswordVault();
        var credential = vault.Retrieve(ResourceName, terminalId);
        credential.RetrievePassword();
        return credential.Password;
    }
}
```

**Security**:
- Encrypted by Windows using DPAPI (Data Protection API)
- Only accessible by user account that stored it (typically SYSTEM)
- Cannot be extracted without admin access to terminal
- Survives application reinstall (stored in Windows, not app folder)

### API Key Transmission

#### HTTP Header Format
```
Authorization: Bearer loyalty_prod_POS-TERMINAL-001_k9m2n5p8q1r4s7t0u3v6w9x2y5z8
```

#### Complete Request Example
```http
POST /api/v1/transactions/earn HTTP/1.1
Host: loyalty-api.prestashop-entre.com
Authorization: Bearer loyalty_prod_POS-TERMINAL-001_k9m2n5p8q1r4s7t0u3v6w9x2y5z8
Content-Type: application/json
X-Terminal-ID: POS-TERMINAL-001
X-Idempotency-Key: earn_04A1B2C3D4E5F6_1708012800_POS-TERMINAL-001

{
  "card_uid": "04A1B2C3D4E5F6",
  "order_id": "PS-ORD-12345",
  "order_amount": 50.00,
  "points_earned": 500000,
  "timestamp": "2025-02-15T14:30:00Z"
}
```

#### Security Requirements
- **TLS 1.3 Only**: API key transmitted over HTTPS
- **Never Logged**: API keys never appear in logs (redacted)
- **Never Cached**: API keys not stored in HTTP caches
- **No GET Params**: API keys never in URL parameters (only Authorization header)

### API Key Validation (Server-Side)

#### Validation Flow
```
┌──────────┐     ┌────────────┐     ┌──────────┐     ┌──────────┐
│ POS Agent│     │  API Gateway│     │   Auth   │     │ Database │
│          │     │  (Nginx)    │     │ Service  │     │          │
└────┬─────┘     └──────┬─────┘     └────┬─────┘     └────┬─────┘
     │                  │                 │                 │
     │ 1. POST /earn    │                 │                 │
     │ + API key        │                 │                 │
     ├─────────────────>│                 │                 │
     │                  │                 │                 │
     │                  │ 2. Extract key  │                 │
     │                  ├────────┐        │                 │
     │                  │        │        │                 │
     │                  │<───────┘        │                 │
     │                  │                 │                 │
     │                  │ 3. Validate key │                 │
     │                  ├────────────────>│                 │
     │                  │                 │                 │
     │                  │                 │ 4. Lookup hash  │
     │                  │                 ├────────────────>│
     │                  │                 │                 │
     │                  │                 │ 5. Return hash  │
     │                  │                 │<────────────────┤
     │                  │                 │                 │
     │                  │                 │ 6. Hash + compare
     │                  │                 ├────────┐        │
     │                  │                 │        │        │
     │                  │                 │<───────┘        │
     │                  │                 │                 │
     │                  │ 7. Valid = true │                 │
     │                  │<────────────────┤                 │
     │                  │                 │                 │
     │                  │ 8. Forward req  │                 │
     │                  │ + terminal_id   │                 │
     │                  ├────────────────────────────────────>
     │                  │                 │                 │
```

#### Validation Checks
```python
from typing import Optional, Tuple
import hashlib
import time

class AuthService:
    def authenticate_terminal(self, api_key: str, terminal_id: str) -> Tuple[bool, Optional[str]]:
        """
        Authenticate terminal API key.
        
        Returns: (is_valid, error_message)
        """
        # 1. Format validation
        if not api_key.startswith("loyalty_"):
            return False, "Invalid API key format"
        
        parts = api_key.split("_")
        if len(parts) != 4:
            return False, "Invalid API key structure"
        
        _, environment, key_terminal_id, random_part = parts
        
        # 2. Environment check
        if environment != self.current_environment:
            return False, f"API key for {environment}, but running in {self.current_environment}"
        
        # 3. Terminal ID match
        if key_terminal_id != terminal_id:
            return False, "API key terminal ID does not match request terminal ID"
        
        # 4. Database lookup
        credential = self.db.get_terminal_credential(terminal_id)
        if not credential:
            return False, "Terminal not found"
        
        # 5. Status check
        if credential.status != "active":
            return False, f"Terminal credential status: {credential.status}"
        
        # 6. Expiration check
        if credential.rotation_due_date < time.time():
            return False, "API key expired. Rotation required."
        
        # 7. Hash comparison
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        if api_key_hash != credential.api_key_hash:
            return False, "Invalid API key"
        
        # 8. IP whitelist check (if configured)
        if credential.ip_whitelist:
            client_ip = self.get_client_ip()
            if client_ip not in credential.ip_whitelist:
                return False, f"IP {client_ip} not whitelisted for this terminal"
        
        # 9. Update last used timestamp
        self.db.update_last_used(terminal_id)
        
        return True, None
```

#### Authentication Failure Responses

**Invalid API Key**
```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "success": false,
  "error_code": "INVALID_CREDENTIALS",
  "error_message": "Authentication failed. Invalid API key.",
  "documentation_url": "https://docs.prestashop-entre.com/authentication"
}
```

**Expired API Key**
```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "success": false,
  "error_code": "CREDENTIALS_EXPIRED",
  "error_message": "API key expired. Please rotate credentials.",
  "rotation_due_date": "2025-02-01T00:00:00Z",
  "contact": "admin@prestashop-entre.com"
}
```

**Revoked API Key**
```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
  "success": false,
  "error_code": "CREDENTIALS_REVOKED",
  "error_message": "API key has been revoked. Contact administrator.",
  "terminal_id": "POS-TERMINAL-001"
}
```

### API Key Rotation

#### Rotation Policy
- **Frequency**: Every 90 days (configurable)
- **Trigger**: Automated reminder email to admin
- **Grace Period**: 7 days overlap (old and new keys both valid)
- **Emergency Rotation**: Immediate if compromise suspected

#### Rotation Process (Normal)

**Step 1: Admin Initiates Rotation (Day 0)**
1. Admin receives email: "API key rotation due for POS-TERMINAL-001"
2. Admin logs into PrestaShop admin panel
3. Navigate to Loyalty Module → Terminals → POS-TERMINAL-001
4. Click "Rotate API Key"
5. System generates new API key
6. System displays new key (one-time display)
7. Old key remains valid for 7 days

**Step 2: Update Terminal (Day 0-7)**
1. IT staff updates API key on terminal
2. POS agent tests new key (validates with API)
3. If successful: new key saved to Credential Manager
4. Old key still works during grace period

**Step 3: Old Key Expires (Day 7)**
1. System automatically revokes old key
2. Only new key accepted
3. If terminal not updated: authentication fails → must update immediately

#### Rotation Process (Emergency)

**Scenario**: API key compromise suspected

**Process**:
1. Admin clicks "Emergency Revoke" for terminal
2. Old key immediately revoked (no grace period)
3. New key generated and displayed
4. Terminal must be updated immediately
5. Until updated: terminal cannot make API calls (offline mode)

**Notification**:
- Email to admin: "Emergency key rotation for POS-TERMINAL-001"
- SMS/phone call if out of hours
- Store manager notified: terminal offline until updated

#### Automated Rotation (Future)

**Design**: Agent automatically fetches new key before expiration

**Flow**:
1. Agent checks key expiration daily
2. If expiration in < 14 days: request new key from API
3. API generates new key, returns to agent
4. Agent stores both old and new keys
5. On expiration date: switch to new key
6. Old key deleted

**Security Consideration**: Requires agent to have permission to generate own keys (risk of abuse)

**Status**: Future consideration (Phase 2)

## PrestaShop Module Authentication

### Authentication Method
PrestaShop module uses PrestaShop's built-in authentication mechanisms:

#### Admin Panel Access
- **Method**: PrestaShop admin session
- **Session Cookie**: `PrestaShop-<hash>`
- **Validation**: PrestaShop core validates session
- **Permissions**: Module checks admin has "Loyalty Module" permission

#### Module API Access (Module → Cloud API)
**Method**: Module-specific API credentials

**Format**:
```
loyalty_module_<shop_id>_<random_32_chars>
```

**Example**:
```
loyalty_module_shop001_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**Storage**:
- PrestaShop configuration table (encrypted)
- Accessed via PrestaShop Configuration class

**Usage**:
```php
use Configuration;

class LoyaltyModuleApi
{
    private function getModuleApiKey(): string
    {
        return Configuration::get('LOYALTY_MODULE_API_KEY');
    }
    
    public function syncOrderEarn(Order $order): array
    {
        $apiKey = $this->getModuleApiKey();
        
        $response = $this->httpClient->post('https://loyalty-api.prestashop-entre.com/api/v1/transactions/earn', [
            'headers' => [
                'Authorization' => 'Bearer ' . $apiKey,
                'Content-Type' => 'application/json',
            ],
            'json' => [
                'card_uid' => $order->getCustomerCardUid(),
                'order_id' => $order->reference,
                'order_amount' => $order->total_paid,
                'points_earned' => $this->calculatePoints($order),
                'timestamp' => date('c'),
            ],
        ]);
        
        return json_decode($response->getBody(), true);
    }
}
```

## JWT Tokens (Future Implementation)

### Use Case
Customer-facing mobile app or web portal (self-service balance check, transaction history)

### JWT Structure

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "customer_12345",
    "card_uid": "04A1B2C3D4E5F6",
    "name": "María García",
    "email": "maria@example.com",
    "role": "customer",
    "iat": 1708012800,
    "exp": 1708016400,
    "iss": "loyalty.prestashop-entre.com",
    "aud": "loyalty-api"
  },
  "signature": "..."
}
```

### Token Lifecycle
1. **Login**: Customer enters email + password (PrestaShop account)
2. **Issue Token**: API returns JWT (valid 1 hour)
3. **Refresh Token**: Separate refresh token (valid 30 days)
4. **Use Token**: Mobile app includes JWT in Authorization header
5. **Expire Token**: After 1 hour, must refresh

### Token Validation
```python
import jwt
from datetime import datetime

def validate_jwt(token: str) -> dict:
    """Validate and decode JWT token."""
    try:
        payload = jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            audience="loyalty-api",
            issuer="loyalty.prestashop-entre.com"
        )
        
        # Additional checks
        if payload['exp'] < datetime.now().timestamp():
            raise ValueError("Token expired")
        
        return payload
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token: {e}")
```

### Status
- **Current**: Not implemented (no customer mobile app yet)
- **Timeline**: Phase 2 (6-12 months)

## Rate Limiting

### Per-Terminal Limits

| Endpoint | Limit | Window | Behavior on Exceed |
|----------|-------|--------|-------------------|
| `/transactions/earn` | 100 requests | 1 minute | HTTP 429, retry after 60s |
| `/transactions/redeem` | 100 requests | 1 minute | HTTP 429, retry after 60s |
| `/balance` | 200 requests | 1 minute | HTTP 429, retry after 60s |
| `/transactions/adjustment` | 10 requests | 1 hour | HTTP 429, contact admin |

### Implementation: Token Bucket Algorithm

```python
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self):
        self.buckets = defaultdict(lambda: {"tokens": 100, "last_refill": time.time()})
    
    def allow_request(self, terminal_id: str, limit: int = 100, window: int = 60) -> bool:
        """
        Check if request allowed under rate limit.
        
        Args:
            terminal_id: Terminal making request
            limit: Max requests in window
            window: Time window in seconds
        
        Returns: True if allowed, False if rate limited
        """
        bucket = self.buckets[terminal_id]
        now = time.time()
        
        # Refill tokens based on time elapsed
        elapsed = now - bucket["last_refill"]
        refill_rate = limit / window  # tokens per second
        bucket["tokens"] = min(limit, bucket["tokens"] + elapsed * refill_rate)
        bucket["last_refill"] = now
        
        # Check if token available
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True
        else:
            return False
```

### Rate Limit Response

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 60

{
  "success": false,
  "error_code": "RATE_LIMIT_EXCEEDED",
  "error_message": "Rate limit exceeded. Max 100 requests per minute.",
  "retry_after": 60,
  "limit": 100,
  "window": "1 minute",
  "terminal_id": "POS-TERMINAL-001"
}
```

### Rate Limit Headers (Response)
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1708012860
```

## IP Whitelisting (Optional)

### Use Case
Fixed POS terminals with static IPs (e.g., restaurant with dedicated internet)

### Configuration

**Enable for Terminal**:
```sql
UPDATE terminal_credentials
SET ip_whitelist = ARRAY['192.168.1.100', '192.168.1.101', '10.0.0.50']
WHERE terminal_id = 'POS-TERMINAL-001';
```

**Validation**:
- If `ip_whitelist` is NULL: Allow from any IP
- If `ip_whitelist` is set: Only allow from listed IPs

### Mobile/Dynamic IP Handling
- **Do NOT use** IP whitelisting for terminals with dynamic IPs (e.g., mobile POS)
- Use API key authentication only

## Credential Revocation

### Revocation Triggers
1. **Security Incident**: API key compromise suspected
2. **Terminal Decommission**: POS terminal retired
3. **Employee Termination**: Manager who had access leaves
4. **Audit Finding**: Unused terminal detected

### Revocation Process

**Immediate Revocation**:
```sql
UPDATE terminal_credentials
SET status = 'revoked',
    revoked_at = NOW(),
    revoked_by = 'admin_juan',
    revocation_reason = 'Security incident - API key exposed in logs'
WHERE terminal_id = 'POS-TERMINAL-001';
```

**Effect**:
- All API requests from that terminal immediately fail with 403 Forbidden
- Terminal must provision new API key to restore access

**Logging**:
```json
{
  "event_type": "CREDENTIAL_REVOKED",
  "timestamp": "2025-02-15T18:00:00Z",
  "terminal_id": "POS-TERMINAL-001",
  "revoked_by": "admin_juan",
  "reason": "Security incident - API key exposed in logs",
  "new_key_issued": true
}
```

## Authentication Monitoring and Alerts

### Monitored Events
- **Failed Authentication Attempts**: > 5 in 1 minute from same terminal
- **Authentication from Unexpected IP**: Terminal authenticates from new IP
- **API Key Reuse**: Same API key used from multiple IPs simultaneously
- **Expired Key Usage Attempts**: Repeated attempts with expired key

### Automated Alerts

**Alert: Repeated Authentication Failures**
```json
{
  "alert_type": "REPEATED_AUTH_FAILURES",
  "terminal_id": "POS-TERMINAL-001",
  "failure_count": 12,
  "time_window": "1 minute",
  "last_failure_time": "2025-02-15T18:05:00Z",
  "action_taken": "Terminal temporarily blocked (15 minutes)",
  "notification_sent_to": ["admin@prestashop-entre.com", "security@prestashop-entre.com"]
}
```

**Alert: API Key Used from Multiple IPs**
```json
{
  "alert_type": "API_KEY_MULTI_IP",
  "terminal_id": "POS-TERMINAL-001",
  "ip_addresses": ["192.168.1.100", "203.0.113.45"],
  "time_window": "5 minutes",
  "detection_time": "2025-02-15T18:10:00Z",
  "action_taken": "Admin notified for review",
  "potential_issue": "API key theft or misconfiguration"
}
```

## Related Documents

### Dependencies
- `06_security/SECURITY_MODEL.md` - Overall security architecture
- `02_architecture/CLOUD_BACKEND.md` - API implementation details
- `02_architecture/WINDOWS_AGENT.md` - Client-side credential storage

### Related Security
- `06_security/NFC_SECURITY.md` - Card authentication (UID-based, no credentials)
- `06_security/IDEMPOTENCY.md` - Request de-duplication

### Features
- `03_features/MANUAL_ADJUSTMENTS.md` - Manager authentication requirements
- `03_features/OFFLINE_MODE.md` - Offline credential handling

## Open Questions / TODOs

### TODO: Automated Key Rotation
**Status**: Future enhancement  
**Required by**: Phase 2  
**Description**: Agent automatically fetches new keys before expiration

### TODO: Hardware Security Module (HSM)
**Status**: Under evaluation  
**Required by**: High-security deployments  
**Description**: Store API key hashes in HSM instead of database

### TODO: OAuth 2.0 for Module
**Status**: Future consideration  
**Required by**: Phase 3  
**Description**: Replace module API key with OAuth 2.0 client credentials flow

### Open Question: Multi-Factor Authentication for Admins
**Question**: Should admin access to terminal credential management require 2FA?  
**Context**: Additional security for high-privilege operations  
**Impact**: Admin user experience, security posture  
**Decision Required By**: Phase 2

### Open Question: API Key Versioning
**Question**: Should API keys include version number for future changes?  
**Context**: Allows backward-incompatible changes to key format  
**Impact**: Key generation, validation logic  
**Decision Required By**: Before launch (if needed)
