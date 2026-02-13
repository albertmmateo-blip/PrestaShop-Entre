# Security Model: Loyalty Points System

## Purpose

Define the complete security architecture for the PrestaShop loyalty points system, including authentication, authorization, threat modeling, risk acceptance, compliance requirements, and security controls across all system components.

## Scope

### In Scope
- Overall security architecture and design principles
- Threat model and risk assessment
- Accepted security risks and mitigations
- Authentication mechanisms (API keys, terminals)
- Authorization model (role-based access control)
- Transport layer security (TLS/HTTPS)
- Audit logging and monitoring
- Data protection and privacy (GDPR compliance)
- Attack scenarios and defensive measures
- Physical security considerations
- Incident response procedures

### Out of Scope
- Detailed NFC security (see `NFC_SECURITY.md`)
- API authentication implementation details (see `AUTHENTICATION.md`)
- Idempotency mechanisms (see `IDEMPOTENCY.md`)
- PrestaShop core security (separate system)
- Payment card industry (PCI) compliance (no payment data stored)

## Security Principles

### 1. Defense in Depth
- Multiple layers of security controls
- No single point of failure
- Compensating controls for accepted risks

### 2. Least Privilege
- Minimum necessary permissions for each role
- Cashiers: read balance, create transactions
- Managers: all cashier permissions + manual adjustments
- Admins: full system access via PrestaShop panel

### 3. Audit Everything
- All transactions logged immutably
- All authentication attempts logged
- All authorization failures logged
- All manual adjustments logged with justification

### 4. Fail Secure
- Authentication failures block access
- Authorization failures deny operation
- Validation failures reject transaction
- Network failures queue transactions locally (offline mode)

### 5. Privacy by Design
- No sensitive personal data on NFC cards
- Minimal PII in transaction logs
- Customer consent for data processing
- Right to be forgotten support

## Threat Model

### Assets to Protect

| Asset | Sensitivity | Impact if Compromised |
|-------|-------------|----------------------|
| Customer point balances | High | Financial loss, reputation damage |
| Transaction history | Medium | Privacy violation, audit trail loss |
| API credentials | High | Unauthorized access, fraud |
| Customer PII | High | Privacy violation, GDPR fines |
| System availability | Medium | Business disruption |

### Threat Actors

#### 1. Malicious Customer
**Motivation**: Gain free points or products  
**Capabilities**: Physical access to own card, limited technical knowledge  
**Threats**:
- Clone NFC card to duplicate balance
- Replay captured transactions
- Social engineering cashiers
- Exploit race conditions (parallel redemptions)

#### 2. Dishonest Employee (Cashier/Manager)
**Motivation**: Theft, help friends/family  
**Capabilities**: System access, knowledge of procedures, physical access  
**Threats**:
- Create fraudulent earn transactions
- Approve unauthorized redemptions
- Manual adjustments for friends
- Share API credentials
- Manipulate offline transactions

#### 3. External Attacker (Hacker)
**Motivation**: Financial gain, data theft, disruption  
**Capabilities**: Technical sophistication, remote access attempts  
**Threats**:
- API credential theft
- Man-in-the-middle attacks
- Database compromise
- DDoS attacks
- Exploit software vulnerabilities

#### 4. Insider with Admin Access
**Motivation**: Fraud, corporate espionage  
**Capabilities**: Full system access, database access  
**Threats**:
- Mass point manipulation
- Customer data exfiltration
- System sabotage
- Audit log tampering

### Attack Scenarios and Mitigations

#### Scenario 1: NFC Card Cloning
**Attack**: Customer clones UID, creates duplicate card with same balance

**Risk Level**: **ACCEPTED** (Low financial impact)

**Why Accepted**:
- Cost of encryption/authentication exceeds loss potential
- Average balance: 20 EUR
- Detection possible via unusual activity patterns
- Customer service can resolve disputes

**Mitigations**:
- Anomaly detection: multiple simultaneous redemptions from same UID
- Velocity limits: max 3 redemptions per day per card
- Location tracking: flag if same card used at distant terminals within short time
- Manual investigation for suspicious patterns
- Negative balance prevention (balance can't be over-redeemed)

**Residual Risk**: Customer may redeem ~20 EUR fraudulently before detection

---

#### Scenario 2: Dishonest Cashier Creates Fake Earn Transactions
**Attack**: Cashier scans own card, creates fake purchase transactions to earn points

**Risk Level**: **HIGH** (Not accepted)

**Mitigations**:
- Earn transactions require order ID from PrestaShop
- Order ID validated against PrestaShop database (API call)
- Audit reports: flag employees earning points at own register
- Manager review: daily report of employee transactions
- Separation of duties: employees cannot create orders and process points in same terminal session

**Detection**:
- Daily audit report: "Employee cards scanned at own terminals"
- Automated alert: if employee card earns > 50 EUR in one day
- Monthly manager review of all employee loyalty accounts

---

#### Scenario 3: API Key Theft and Abuse
**Attack**: Attacker steals terminal API key, makes unauthorized API calls

**Risk Level**: **HIGH** (Not accepted)

**Mitigations**:
- API keys stored encrypted in Windows Credential Manager
- TLS 1.3 for all API communication
- API key tied to specific terminal ID
- IP whitelisting (optional, for fixed POS locations)
- Rate limiting: 100 requests/minute per terminal
- Anomalous behavior detection: flag if terminal makes unusual API calls
- API key rotation every 90 days (automated reminder)
- Immediate revocation capability

**Detection**:
- Monitor for API calls from unexpected IPs
- Alert on unusual request patterns (e.g., 1000 balance checks in 1 minute)
- Audit log review: weekly check of API usage patterns

**Response**:
- Immediately revoke compromised API key
- Issue new API key to affected terminal
- Investigate: which transactions occurred during compromise window
- Review transactions for fraud, reverse if necessary

---

#### Scenario 4: Man-in-the-Middle (MITM) Attack
**Attack**: Attacker intercepts network traffic between POS and Cloud API

**Risk Level**: **MEDIUM** (Mitigated by TLS)

**Mitigations**:
- TLS 1.3 mandatory for all HTTPS connections
- Certificate pinning in POS agent (validates cloud API certificate)
- No HTTP fallback (HTTPS only)
- HSTS (HTTP Strict Transport Security) headers
- Regular TLS configuration audits

**Residual Risk**: Minimal if TLS properly configured

---

#### Scenario 5: Database Compromise
**Attack**: Attacker gains direct access to cloud database

**Risk Level**: **CRITICAL** (Not accepted)

**Mitigations**:
- Database credentials stored in secret manager (not code)
- Database firewall: only cloud API server can connect
- Encrypted connections to database (TLS)
- Encrypted fields for sensitive data (customer PII)
- Database audit logging enabled
- Regular security patches
- Principle of least privilege: API service account has minimal DB permissions

**Detection**:
- Database access logs monitored 24/7
- Alert on unexpected connections or queries
- Regular penetration testing

**Response**:
- Incident response plan activated
- Forensic analysis to determine scope
- Customer notification if PII compromised (GDPR requirement)
- System hardening and patching

---

#### Scenario 6: Offline Transaction Manipulation
**Attack**: Attacker modifies queued offline transactions in local SQLite database

**Risk Level**: **MEDIUM** (Requires physical access to POS terminal)

**Mitigations**:
- SQLite database file encrypted (Windows DPAPI)
- File permissions: only SYSTEM account can access
- Transaction signatures: HMAC of transaction data with terminal secret
- Cloud API validates signatures during sync
- Tampered transactions rejected

**Detection**:
- Signature validation failures logged and alerted
- Manual investigation of repeated failures from same terminal

**Response**:
- Quarantine affected terminal
- Manual review of all transactions from that terminal
- Reinstall POS agent if compromised

---

#### Scenario 7: Race Condition - Parallel Redemptions
**Attack**: Customer attempts simultaneous redemptions at multiple terminals

**Risk Level**: **MEDIUM** (Can cause over-redemption)

**Mitigations**:
- Database row-level locking on customer balance
- Idempotency keys for all redemption requests
- Transaction serialization: second redemption waits for first to complete
- Eventual consistency: offline redemptions may succeed locally, fail on sync
- Negative balance prevention

**Residual Risk**: Small window for duplicate redemption if both terminals offline

---

#### Scenario 8: Social Engineering - Manager Approval Bypass
**Attack**: Attacker convinces manager to approve large fraudulent adjustment

**Risk Level**: **MEDIUM** (Human factor)

**Mitigations**:
- Manager training on fraud indicators
- Dual approval for adjustments > 100 EUR
- Audit trail with justification required
- Monthly review of all manual adjustments by senior management
- Anomaly detection: flag managers with unusual adjustment patterns

**Detection**:
- Manager-specific adjustment reports
- Customer complaints trigger investigation

**Response**:
- Employee disciplinary action
- Reverse fraudulent adjustments
- Improve training and procedures

## Authentication

### Terminal Authentication
- **Method**: API key + Terminal ID
- **Format**: `Bearer <api_key>` in Authorization header
- **Scope**: Per-terminal credentials
- **Rotation**: Every 90 days (manual, reminder email)
- **Storage**: Windows Credential Manager (encrypted)
- **Transmission**: HTTPS only, never logged

See `AUTHENTICATION.md` for implementation details.

### Manager Authentication (Manual Adjustments)
- **Method**: Windows login PIN or PrestaShop admin session
- **Requirement**: Re-authentication before adjustment (even if already logged in)
- **Lockout**: 3 failed attempts = 15-minute lockout
- **Audit**: All authentication attempts logged

### PrestaShop Module Authentication
- **Method**: PrestaShop API credentials (OAuth 2.0 or API key)
- **Scope**: Module can read/write loyalty data
- **Validation**: Module signature verified by PrestaShop core

## Authorization

### Role-Based Access Control (RBAC)

| Role | Permissions |
|------|-------------|
| **Cashier** | - Read customer balance<br>- Create earn transactions<br>- Create redemption transactions<br>- View transaction history |
| **Manager** | - All cashier permissions<br>- Create manual adjustments (< 100 EUR)<br>- View audit reports<br>- Export transaction data |
| **Senior Manager** | - All manager permissions<br>- Approve manual adjustments (>= 100 EUR)<br>- Access approval dashboard |
| **Admin** | - Full system access via PrestaShop admin panel<br>- Configure module settings<br>- View all audit logs<br>- Manage API keys |
| **System** | - Cloud API service account<br>- Database access (read/write loyalty data only)<br>- No direct customer PII access |

### Authorization Checks
- Every API request validates role permissions
- Terminal role: only allowed to create transactions for own terminal ID
- Manager role: validated before displaying adjustment interface
- Approval role: validated before allowing approval actions

### Authorization Failures
- HTTP 403 Forbidden returned
- Failure logged with username, attempted action, timestamp
- Repeated failures trigger alert (potential attack)

## Transport Layer Security (TLS)

### Requirements
- **Protocol**: TLS 1.3 (TLS 1.2 minimum)
- **Ciphers**: Only strong ciphers (AEAD: AES-GCM, ChaCha20-Poly1305)
- **Certificates**: Valid certificates from trusted CA (Let's Encrypt or commercial)
- **HSTS**: Enabled with max-age=31536000 (1 year)
- **No Downgrade**: HTTPS only, no HTTP fallback

### Certificate Management
- Certificates auto-renewed via Let's Encrypt
- Expiration monitoring: alert 30 days before expiry
- Certificate pinning in POS agent (validates API certificate thumbprint)

### Network Security
- API exposed only via HTTPS (port 443)
- No direct database access from internet
- Database accessible only from cloud API server (firewall rule)

## Audit Logging

### Logged Events

#### Transaction Events
```json
{
  "event_type": "TRANSACTION_CREATED",
  "timestamp": "2025-02-15T14:30:00Z",
  "transaction_id": "txn_abc123",
  "transaction_type": "earn",
  "card_uid": "04A1B2C3D4E5F6",
  "customer_id": 12345,
  "amount": 50.00,
  "points": 500000,
  "terminal_id": "POS-TERMINAL-001",
  "cashier": "cashier_maria",
  "order_id": "PS-ORD-9876",
  "ip_address": "192.168.1.100"
}
```

#### Authentication Events
```json
{
  "event_type": "AUTH_FAILURE",
  "timestamp": "2025-02-15T14:35:00Z",
  "username": "manager_juan",
  "auth_method": "pin",
  "reason": "invalid_credentials",
  "ip_address": "192.168.1.105",
  "terminal_id": "POS-TERMINAL-002",
  "attempt_number": 2
}
```

#### Authorization Events
```json
{
  "event_type": "AUTHORIZATION_DENIED",
  "timestamp": "2025-02-15T14:40:00Z",
  "username": "cashier_ana",
  "attempted_action": "manual_adjustment",
  "required_role": "manager",
  "user_role": "cashier",
  "ip_address": "192.168.1.110",
  "terminal_id": "POS-TERMINAL-003"
}
```

#### Manual Adjustment Events
```json
{
  "event_type": "MANUAL_ADJUSTMENT",
  "timestamp": "2025-02-15T16:45:00Z",
  "transaction_id": "txn_adj_xyz",
  "adjustment_type": "credit",
  "adjustment_amount": 15.00,
  "adjustment_points": 150000,
  "reason_code": "customer_service_gesture",
  "reason_detail": "Apology for long wait time",
  "card_uid": "04A1B2C3D4E5F6",
  "balance_before": 50000,
  "balance_after": 200000,
  "adjusted_by": "manager_maria",
  "approved_by": null,
  "terminal_id": "POS-TERMINAL-001",
  "ip_address": "192.168.1.100"
}
```

### Log Storage
- **Retention**: 7 years (GDPR compliance)
- **Storage**: Immutable audit log database
- **Access**: Read-only for most users, admin can export
- **Format**: JSON structured logs
- **Indexing**: Indexed by timestamp, card_uid, transaction_id, event_type

### Log Protection
- Audit logs cannot be modified or deleted
- Separate database from transactional data
- Regular backups to separate storage
- Integrity checks: periodic hash verification

### No Sensitive Data in Logs
**Prohibited**:
- Full card UIDs are logged (acceptable, not secret)
- API keys (never logged)
- Passwords or PINs (never logged)
- Full customer PII (only customer ID, not names/addresses)

**Anonymization**:
- Customer names replaced with customer IDs in audit logs
- Only link customer ID to PII when explicitly needed (admin report)

## GDPR Compliance

### Data Minimization
- Only collect necessary data for loyalty program
- No sensitive personal data (race, religion, health, etc.)
- NFC card contains only UID (no PII)

### Legal Basis
- **Legitimate Interest**: Transaction processing for loyalty program
- **Consent**: Customer enrolls voluntarily
- **Contract**: Loyalty program terms and conditions accepted

### Customer Rights

#### Right to Access (Data Portability)
- Customer can download transaction history (CSV/JSON)
- Export includes: transaction dates, types, amounts, points, balances
- Available via PrestaShop customer account dashboard

#### Right to Erasure ("Right to be Forgotten")
- Customer can request account deletion
- Process:
  1. Final balance redemption or forfeiture
  2. Transaction history anonymized (replace card_uid with `DELETED_<customer_id>`)
  3. Customer PII removed from PrestaShop
  4. Audit logs retained (legal requirement) but anonymized

#### Right to Rectification
- Customer can correct personal information via PrestaShop account
- Transaction data cannot be modified (audit integrity)

#### Right to Object
- Customer can opt-out of promotional emails
- Cannot opt-out of transactional emails (required for program operation)

### Data Retention
- **Active accounts**: No limit (ongoing relationship)
- **Inactive accounts**: 3 years without activity → account suspended
- **Suspended accounts**: 1 year → account deleted (anonymized)
- **Audit logs**: 7 years (legal/tax requirement)

### Data Breach Response
1. Detect and contain breach within 24 hours
2. Assess: what data exposed, how many customers affected
3. Notify supervisory authority within 72 hours (GDPR requirement)
4. Notify affected customers if high risk to rights/freedoms
5. Document breach and response in incident log
6. Implement additional security measures to prevent recurrence

### Data Processing Agreement (DPA)
- Cloud provider (AWS/Azure/GCP) has signed DPA
- Data processed within EU (GDPR compliance)
- Subprocessors disclosed to customers

## Attack Scenarios - Summary Table

| Attack | Risk Level | Accepted? | Primary Mitigation |
|--------|-----------|-----------|-------------------|
| NFC card cloning | Low | **YES** | Anomaly detection, velocity limits |
| Dishonest cashier | High | NO | Order ID validation, audit reports |
| API key theft | High | NO | Encryption, IP whitelisting, rotation |
| Man-in-the-middle | Medium | NO | TLS 1.3, certificate pinning |
| Database compromise | Critical | NO | Firewall, encryption, least privilege |
| Offline manipulation | Medium | NO | Transaction signatures, validation |
| Race condition | Medium | NO | Row-level locking, idempotency |
| Social engineering | Medium | NO | Dual approval, manager training |

## Physical Security

### POS Terminals
- **Location**: Store premises (physical security by store)
- **Access**: Restricted to employees
- **Device Security**: Windows login required (BitLocker encryption recommended)

### NFC Cards
- **Distribution**: Provided to customers at enrollment
- **Replacement**: Available at customer service desk (free)
- **Lost/Stolen**: Customer reports, card deactivated, new card issued
- **No Lock**: Cards do not lock or expire (acceptable risk)

### NFC Readers
- **Tamper Resistance**: Standard USB readers (no special security)
- **Theft**: Reader theft does not compromise system (no secrets stored)

## Incident Response

### Security Incident Types
1. **API key compromise**: Revoke key, issue new key, audit transactions
2. **Data breach**: Forensic analysis, customer notification, regulatory reporting
3. **Fraud detection**: Investigate, reverse fraudulent transactions, employee action
4. **DDoS attack**: Rate limiting, CDN protection, contact hosting provider

### Incident Response Plan
1. **Detection**: Automated alerts or manual report
2. **Containment**: Isolate affected systems, revoke credentials
3. **Investigation**: Determine root cause, scope, affected data
4. **Remediation**: Fix vulnerability, restore service
5. **Documentation**: Incident report with timeline, actions, lessons learned
6. **Follow-up**: Improve security controls, update procedures

### Escalation Path
- **Level 1**: POS support team (operational issues)
- **Level 2**: IT security team (security incidents)
- **Level 3**: Management and legal (data breaches, regulatory)

## Monitoring and Alerting

### Real-Time Alerts
- Authentication failures (> 5 in 1 minute)
- Authorization failures (> 10 in 1 hour)
- Unusual API usage (> 500 requests in 1 minute from one terminal)
- Large manual adjustments (> 50 EUR)
- Transaction signature validation failures
- Database connection failures

### Daily Reports
- Employee transactions at own terminals
- Manual adjustments summary
- API key usage by terminal
- Failed authentication attempts

### Weekly Reports
- Security audit summary
- Transaction anomalies
- System performance

## Compliance Checklist

- [x] GDPR compliance (EU data protection)
- [x] Audit logging (7-year retention)
- [x] Data encryption in transit (TLS 1.3)
- [x] Data encryption at rest (database, local files)
- [x] Access control (RBAC)
- [x] Incident response plan
- [ ] PCI DSS compliance (not required - no payment card data)
- [ ] ISO 27001 certification (future consideration)
- [ ] Penetration testing (annual, recommended)

## Related Documents

### Dependencies
- `02_architecture/CLOUD_BACKEND.md` - Cloud API security implementation
- `02_architecture/WINDOWS_AGENT.md` - POS agent security controls
- `04_integrations/PRESTASHOP_MODULE.md` - Module authentication
- `05_data/CUSTOMER.md` - Customer data model and PII

### Security Details
- `06_security/NFC_SECURITY.md` - NFC-specific security considerations
- `06_security/AUTHENTICATION.md` - API authentication mechanisms
- `06_security/IDEMPOTENCY.md` - Duplicate transaction prevention

### Related Features
- `03_features/MANUAL_ADJUSTMENTS.md` - Manager adjustment security
- `03_features/OFFLINE_MODE.md` - Offline transaction security

## Open Questions / TODOs

### TODO: Penetration Testing
**Status**: Not yet performed  
**Required by**: Before production launch  
**Description**: Annual penetration testing by third-party security firm

### TODO: Bug Bounty Program
**Status**: Under consideration  
**Required by**: Phase 2  
**Description**: Public bug bounty for responsible disclosure of vulnerabilities

### TODO: Security Training
**Status**: Materials needed  
**Required by**: Employee onboarding  
**Description**: Security awareness training for all cashiers and managers

### Open Question: Biometric Authentication
**Question**: Should managers use biometric authentication (fingerprint) instead of PINs?  
**Context**: Improved security, but hardware requirements  
**Impact**: POS hardware requirements, implementation complexity  
**Decision Required By**: Phase 2

### Open Question: Two-Factor Authentication (2FA)
**Question**: Should admin access require 2FA (SMS or authenticator app)?  
**Context**: Additional security for high-privilege accounts  
**Impact**: User experience, support burden  
**Decision Required By**: Phase 2
