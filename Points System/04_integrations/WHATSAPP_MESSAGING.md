# WhatsApp Messaging Integration

**Version**: 1.0  
**Status**: Draft  
**Last Updated**: 2024-02-13

---

## Purpose

Define the integration strategy for WhatsApp Business API to enable automated customer notifications (points earned, balance updates) and two-way communication (balance queries via keyword "Saldo") in Spanish and Catalan languages.

## Scope

### In Scope
- WhatsApp Business API setup and configuration
- Message templates for notifications (points earned, redemption, expiration)
- Balance query automation (keyword "Saldo" or "Saldo")
- Multi-language support (Spanish, Catalan, English)
- Message delivery tracking and error handling
- Customer opt-in/opt-out management
- Integration with PrestaShop module
- Webhook handling for inbound messages
- Rate limiting and queue management

### Out of Scope
- WhatsApp Marketing Platform (separate from Business API)
- Chatbot with natural language processing
- Customer support ticketing system
- Order placement via WhatsApp
- Payment processing via WhatsApp
- Media messages (images, videos, documents)
- Group messaging

---

## Inputs

### From PrestaShop Events
1. **Points Earned Event**
   - Customer ID
   - Points awarded
   - Order reference
   - Transaction timestamp
   - New balance

2. **Points Redeemed Event**
   - Customer ID
   - Points redeemed
   - Discount value
   - Cart rule code
   - New balance

3. **Points Expiring Soon Event**
   - Customer ID
   - Points expiring
   - Expiration date
   - Current balance

### From Customer (Inbound Messages)
1. **Balance Query**
   - WhatsApp phone number
   - Message text: "Saldo", "Saldo", "Balance", "Puntos"
   - Message timestamp

2. **Opt-out Request**
   - Message text: "STOP", "BAJA", "PARAR"

### Configuration Parameters
- WhatsApp Business Account ID
- Phone Number ID (WhatsApp assigned)
- Access Token (Meta Business)
- Webhook verification token
- Default language per customer
- Message templates (approved by Meta)
- Rate limits (messages per minute)

---

## Outputs

### To Customer (WhatsApp)
1. **Points Earned Notification**
   ```
   🎉 ¡Felicidades! Has ganado 45 puntos.
   
   Compra: #PS000123
   Tu saldo: 320 puntos
   
   ¡Gracias por tu compra!
   ```

2. **Points Redeemed Notification**
   ```
   ✅ Has canjeado 100 puntos por un descuento de 5€.
   
   Código: FIDEL12345678
   Válido hasta: 15/03/2024
   Tu saldo: 220 puntos
   ```

3. **Balance Response**
   ```
   💳 Tu saldo de puntos:
   
   Puntos disponibles: 320
   Próxima expiración: 50 puntos el 30/04/2024
   
   🛒 ¡Canjea tus puntos en nuestra tienda!
   [URL]
   ```

4. **Expiration Warning**
   ```
   ⚠️ Tus puntos están por expirar
   
   50 puntos expirarán el 30/04/2024
   Saldo actual: 320 puntos
   
   ¡No los pierdas! Canjea ahora:
   [URL]
   ```

### To PrestaShop Database
1. **Message Log**
   ```sql
   CREATE TABLE IF NOT EXISTS ps_fidelitypoints_whatsapp_log (
     id_message INT(11) NOT NULL AUTO_INCREMENT,
     id_customer INT(11),
     phone_number VARCHAR(20),
     direction ENUM('outbound','inbound'),
     message_type VARCHAR(50), -- 'points_earned', 'balance_query', etc.
     message_body TEXT,
     whatsapp_message_id VARCHAR(100),
     status VARCHAR(20), -- 'sent', 'delivered', 'read', 'failed'
     error_message TEXT,
     date_add DATETIME NOT NULL,
     date_delivered DATETIME,
     date_read DATETIME,
     PRIMARY KEY (id_message),
     KEY customer_date (id_customer, date_add),
     KEY phone (phone_number)
   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
   ```

2. **Opt-out Tracking**
   ```sql
   CREATE TABLE IF NOT EXISTS ps_fidelitypoints_whatsapp_optout (
     id_optout INT(11) NOT NULL AUTO_INCREMENT,
     id_customer INT(11),
     phone_number VARCHAR(20),
     opted_out TINYINT(1) DEFAULT 1,
     date_add DATETIME NOT NULL,
     date_upd DATETIME,
     PRIMARY KEY (id_optout),
     UNIQUE KEY phone (phone_number)
   ) ENGINE=InnoDB;
   ```

### To Meta (WhatsApp Business API)
- Outbound message requests
- Message delivery status webhooks (acknowledgment)
- Read receipts

---

## Main Flows

### Flow 1: WhatsApp Business API Setup

```
┌─────────────────────────┐
│ Meta Business Manager   │
│ business.facebook.com   │
└────────────┬────────────┘
             │
             │ 1. Create WhatsApp Business Account
             │ 2. Add phone number
             │ 3. Verify phone number
             ▼
┌─────────────────────────┐
│ WhatsApp Business API   │
│ - Phone Number ID       │
│ - Access Token          │
│ - Webhook URL           │
└────────────┬────────────┘
             │
             │ 3. Create message templates
             │ 4. Submit for approval
             ▼
┌─────────────────────────┐
│ Meta Review Process     │
│ (24-48 hours)           │
└────────────┬────────────┘
             │
             │ Approved templates
             ▼
┌─────────────────────────┐
│ PrestaShop Integration  │
│ - Store credentials     │
│ - Configure webhook     │
│ - Test messaging        │
└─────────────────────────┘
```

**Setup Steps**:

1. **Create Meta Business Account**
   - Go to https://business.facebook.com
   - Create business account or use existing
   - Add WhatsApp Business API product

2. **Register Phone Number**
   - Use a dedicated business phone number (not personal)
   - Format: +34 XXX XXX XXX (Spain)
   - Verify via SMS or voice call
   - **Important**: Once registered, cannot receive SMS/calls normally

3. **Get API Credentials**
   ```
   Phone Number ID: 123456789012345
   WhatsApp Business Account ID: 234567890123456
   Access Token: EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

4. **Configure Webhook** (for inbound messages)
   - Webhook URL: `https://yourstore.com/module/fidelitypoints/whatsapp-webhook`
   - Verification Token: `your_secret_verification_token`
   - Subscribe to: `messages`, `message_deliveries`, `message_reads`

### Flow 2: Send Points Earned Notification

```php
// File: modules/fidelitypoints/classes/WhatsAppService.php

class WhatsAppService
{
    private $phoneNumberId;
    private $accessToken;
    private $apiUrl = 'https://graph.facebook.com/v18.0';

    public function __construct()
    {
        $this->phoneNumberId = Configuration::get('WHATSAPP_PHONE_NUMBER_ID');
        $this->accessToken = Configuration::get('WHATSAPP_ACCESS_TOKEN');
    }

    public function sendPointsEarnedNotification($customer, $points, $orderRef, $newBalance)
    {
        // Check if customer opted out
        if ($this->isOptedOut($customer->id)) {
            return false;
        }

        // Get customer phone number
        $phone = $this->formatPhoneNumber($customer);
        if (!$phone) {
            Logger::addLog("WhatsApp: No phone number for customer {$customer->id}", 2);
            return false;
        }

        // Get customer language
        $language = $this->getCustomerLanguage($customer);

        // Use message template
        $templateName = 'points_earned_' . $language; // e.g., 'points_earned_es'
        
        $messageData = [
            'messaging_product' => 'whatsapp',
            'to' => $phone,
            'type' => 'template',
            'template' => [
                'name' => $templateName,
                'language' => [
                    'code' => $this->getWhatsAppLanguageCode($language)
                ],
                'components' => [
                    [
                        'type' => 'body',
                        'parameters' => [
                            ['type' => 'text', 'text' => (string)$points],
                            ['type' => 'text', 'text' => $orderRef],
                            ['type' => 'text', 'text' => (string)$newBalance]
                        ]
                    ]
                ]
            ]
        ];

        return $this->sendMessage($messageData, $customer->id, 'points_earned');
    }

    private function sendMessage($messageData, $customerId, $messageType)
    {
        $url = "{$this->apiUrl}/{$this->phoneNumberId}/messages";
        
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($messageData));
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Authorization: Bearer ' . $this->accessToken,
            'Content-Type: application/json'
        ]);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        $responseData = json_decode($response, true);
        
        if ($httpCode == 200 && isset($responseData['messages'][0]['id'])) {
            // Log successful send
            $this->logMessage(
                $customerId,
                $messageData['to'],
                'outbound',
                $messageType,
                json_encode($messageData),
                $responseData['messages'][0]['id'],
                'sent'
            );
            return true;
        } else {
            // Log error
            $errorMsg = $responseData['error']['message'] ?? 'Unknown error';
            $this->logMessage(
                $customerId,
                $messageData['to'],
                'outbound',
                $messageType,
                json_encode($messageData),
                null,
                'failed',
                $errorMsg
            );
            Logger::addLog("WhatsApp send failed: {$errorMsg}", 3);
            return false;
        }
    }

    private function formatPhoneNumber($customer)
    {
        // Assumes phone stored in addresses table
        $address = new Address((int)Address::getFirstCustomerAddressId($customer->id));
        
        if (!Validate::isLoadedObject($address) || !$address->phone_mobile) {
            return null;
        }

        $phone = $address->phone_mobile;
        
        // Remove all non-digit characters
        $phone = preg_replace('/[^0-9]/', '', $phone);
        
        // Add country code if missing (assume Spain +34)
        if (strlen($phone) == 9 && $phone[0] == '6' || $phone[0] == '7') {
            $phone = '34' . $phone;
        }
        
        // Ensure it has country code
        if (!str_starts_with($phone, '34')) {
            // Try to detect country from address
            if ($address->id_country == 6) { // Spain
                $phone = '34' . $phone;
            }
        }
        
        return $phone;
    }

    private function getCustomerLanguage($customer)
    {
        $langId = $customer->id_lang;
        $lang = new Language($langId);
        
        // Map PrestaShop language to our supported languages
        $isoCode = strtolower($lang->iso_code);
        
        if ($isoCode == 'es') return 'es';
        if ($isoCode == 'ca') return 'ca';
        return 'en'; // default
    }

    private function getWhatsAppLanguageCode($language)
    {
        // WhatsApp language codes
        $codes = [
            'es' => 'es',      // Spanish
            'ca' => 'ca',      // Catalan
            'en' => 'en_US'    // English
        ];
        
        return $codes[$language] ?? 'es';
    }

    private function logMessage($customerId, $phone, $direction, $type, $body, $waMessageId, $status, $error = null)
    {
        Db::getInstance()->insert('fidelitypoints_whatsapp_log', [
            'id_customer' => (int)$customerId,
            'phone_number' => pSQL($phone),
            'direction' => pSQL($direction),
            'message_type' => pSQL($type),
            'message_body' => pSQL($body),
            'whatsapp_message_id' => pSQL($waMessageId),
            'status' => pSQL($status),
            'error_message' => pSQL($error),
            'date_add' => date('Y-m-d H:i:s')
        ]);
    }

    private function isOptedOut($customerId)
    {
        $result = Db::getInstance()->getValue(
            'SELECT opted_out FROM ' . _DB_PREFIX_ . 'fidelitypoints_whatsapp_optout
             WHERE id_customer = ' . (int)$customerId
        );
        
        return $result == 1;
    }
}
```

### Flow 3: Handle Balance Query (Inbound Message)

```php
// File: modules/fidelitypoints/controllers/front/whatsappwebhook.php

class FidelityPointsWhatsAppWebhookModuleFrontController extends ModuleFrontController
{
    public function postProcess()
    {
        // Verify webhook (GET request from Meta)
        if ($_SERVER['REQUEST_METHOD'] === 'GET') {
            $this->verifyWebhook();
            return;
        }

        // Handle incoming message (POST request)
        $input = file_get_contents('php://input');
        $data = json_decode($input, true);
        
        // Log raw webhook data
        Logger::addLog('WhatsApp webhook: ' . $input, 1);
        
        if (!isset($data['entry'][0]['changes'][0]['value'])) {
            return;
        }
        
        $value = $data['entry'][0]['changes'][0]['value'];
        
        // Handle different webhook types
        if (isset($value['messages'])) {
            foreach ($value['messages'] as $message) {
                $this->handleIncomingMessage($message, $value['metadata']);
            }
        }
        
        if (isset($value['statuses'])) {
            foreach ($value['statuses'] as $status) {
                $this->handleStatusUpdate($status);
            }
        }
        
        // Always return 200 OK to Meta
        http_response_code(200);
        die('OK');
    }

    private function verifyWebhook()
    {
        $mode = Tools::getValue('hub_mode');
        $token = Tools::getValue('hub_verify_token');
        $challenge = Tools::getValue('hub_challenge');
        
        $verifyToken = Configuration::get('WHATSAPP_VERIFY_TOKEN');
        
        if ($mode === 'subscribe' && $token === $verifyToken) {
            echo $challenge;
            die();
        } else {
            http_response_code(403);
            die('Forbidden');
        }
    }

    private function handleIncomingMessage($message, $metadata)
    {
        $from = $message['from']; // Phone number
        $messageType = $message['type'];
        $messageId = $message['id'];
        
        // Only handle text messages
        if ($messageType !== 'text') {
            return;
        }
        
        $messageText = strtolower(trim($message['text']['body']));
        
        // Find customer by phone number
        $customer = $this->findCustomerByPhone($from);
        
        if (!$customer) {
            // Send error message
            $this->sendTextMessage(
                $from,
                "No encontramos tu cuenta. Por favor, registra tu número en nuestra tienda online."
            );
            return;
        }
        
        // Process commands
        if (in_array($messageText, ['saldo', 'balance', 'puntos', 'points'])) {
            $this->handleBalanceQuery($customer, $from);
        } elseif (in_array($messageText, ['stop', 'baja', 'parar', 'unsubscribe'])) {
            $this->handleOptOut($customer, $from);
        } elseif (in_array($messageText, ['start', 'alta', 'subscribe'])) {
            $this->handleOptIn($customer, $from);
        } else {
            // Unknown command
            $this->sendTextMessage(
                $from,
                "Comandos disponibles:\n• Saldo - Ver puntos\n• STOP - Dejar de recibir mensajes"
            );
        }
        
        // Log inbound message
        $this->module->whatsappService->logMessage(
            $customer->id,
            $from,
            'inbound',
            'customer_message',
            $messageText,
            $messageId,
            'received'
        );
    }

    private function handleBalanceQuery($customer, $phone)
    {
        // Get customer balance
        $balance = $this->module->getCustomerBalance($customer->id);
        
        // Get expiring points
        $expiringPoints = $this->module->getExpiringPoints($customer->id, 30);
        
        // Get customer language
        $language = $this->module->whatsappService->getCustomerLanguage($customer);
        
        // Build response message
        if ($language == 'ca') {
            $message = "💳 El teu saldo de punts:\n\n";
            $message .= "Punts disponibles: {$balance}\n";
            if ($expiringPoints['points'] > 0) {
                $message .= "Propera caducitat: {$expiringPoints['points']} punts el {$expiringPoints['date']}\n";
            }
            $message .= "\n🛒 Bescanvia els teus punts aquí:\n";
        } else {
            $message = "💳 Tu saldo de puntos:\n\n";
            $message .= "Puntos disponibles: {$balance}\n";
            if ($expiringPoints['points'] > 0) {
                $message .= "Próxima expiración: {$expiringPoints['points']} puntos el {$expiringPoints['date']}\n";
            }
            $message .= "\n🛒 Canjea tus puntos aquí:\n";
        }
        
        $message .= Configuration::get('PS_SHOP_URL') . '/module/fidelitypoints/account';
        
        $this->sendTextMessage($phone, $message);
    }

    private function handleOptOut($customer, $phone)
    {
        // Mark customer as opted out
        Db::getInstance()->insert('fidelitypoints_whatsapp_optout', [
            'id_customer' => (int)$customer->id,
            'phone_number' => pSQL($phone),
            'opted_out' => 1,
            'date_add' => date('Y-m-d H:i:s'),
            'date_upd' => date('Y-m-d H:i:s')
        ], false, true, Db::ON_DUPLICATE_KEY); // Update if exists
        
        // Send confirmation
        $this->sendTextMessage(
            $phone,
            "Has sido dado de baja. No recibirás más notificaciones.\n\nPara volver a suscribirte, envía START."
        );
    }

    private function handleOptIn($customer, $phone)
    {
        // Mark customer as opted in
        Db::getInstance()->update('fidelitypoints_whatsapp_optout', [
            'opted_out' => 0,
            'date_upd' => date('Y-m-d H:i:s')
        ], 'id_customer = ' . (int)$customer->id);
        
        // Send confirmation
        $this->sendTextMessage(
            $phone,
            "¡Bienvenido de nuevo! Recibirás notificaciones de tus puntos de fidelidad.\n\nConsulta tu saldo con: SALDO"
        );
    }

    private function sendTextMessage($to, $text)
    {
        $phoneNumberId = Configuration::get('WHATSAPP_PHONE_NUMBER_ID');
        $accessToken = Configuration::get('WHATSAPP_ACCESS_TOKEN');
        
        $url = "https://graph.facebook.com/v18.0/{$phoneNumberId}/messages";
        
        $data = [
            'messaging_product' => 'whatsapp',
            'to' => $to,
            'type' => 'text',
            'text' => [
                'body' => $text
            ]
        ];
        
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Authorization: Bearer ' . $accessToken,
            'Content-Type: application/json'
        ]);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        
        $response = curl_exec($ch);
        curl_close($ch);
        
        return json_decode($response, true);
    }

    private function handleStatusUpdate($status)
    {
        $messageId = $status['id'];
        $statusType = $status['status']; // 'sent', 'delivered', 'read', 'failed'
        
        $updateData = ['status' => pSQL($statusType)];
        
        if ($statusType == 'delivered') {
            $updateData['date_delivered'] = date('Y-m-d H:i:s', $status['timestamp']);
        } elseif ($statusType == 'read') {
            $updateData['date_read'] = date('Y-m-d H:i:s', $status['timestamp']);
        } elseif ($statusType == 'failed' && isset($status['errors'])) {
            $updateData['error_message'] = pSQL(json_encode($status['errors']));
        }
        
        Db::getInstance()->update(
            'fidelitypoints_whatsapp_log',
            $updateData,
            'whatsapp_message_id = "' . pSQL($messageId) . '"'
        );
    }

    private function findCustomerByPhone($phone)
    {
        // Try exact match first
        $sql = 'SELECT DISTINCT c.id_customer
                FROM ' . _DB_PREFIX_ . 'customer c
                INNER JOIN ' . _DB_PREFIX_ . 'address a ON a.id_customer = c.id_customer
                WHERE a.phone_mobile = "' . pSQL($phone) . '"
                OR a.phone_mobile = "+' . pSQL($phone) . '"';
        
        $customerId = Db::getInstance()->getValue($sql);
        
        if ($customerId) {
            return new Customer($customerId);
        }
        
        // Try without country code
        if (strlen($phone) > 9) {
            $phoneShort = substr($phone, -9); // Last 9 digits
            $sql = 'SELECT DISTINCT c.id_customer
                    FROM ' . _DB_PREFIX_ . 'customer c
                    INNER JOIN ' . _DB_PREFIX_ . 'address a ON a.id_customer = c.id_customer
                    WHERE a.phone_mobile LIKE "%' . pSQL($phoneShort) . '"';
            
            $customerId = Db::getInstance()->getValue($sql);
            
            if ($customerId) {
                return new Customer($customerId);
            }
        }
        
        return null;
    }
}
```

### Flow 4: Message Template Creation (Meta Business Manager)

**Template Name**: `points_earned_es` (Spanish)

**Category**: UTILITY (for transactional messages)

**Header**: None

**Body**:
```
🎉 ¡Felicidades! Has ganado {{1}} puntos.

Compra: {{2}}
Tu saldo: {{3}} puntos

¡Gracias por tu compra!
```

**Footer**: None

**Buttons**: None (or optional: [Canjear puntos] → URL)

**Template Name**: `points_earned_ca` (Catalan)

**Body**:
```
🎉 Felicitats! Has guanyat {{1}} punts.

Compra: {{2}}
El teu saldo: {{3}} punts

Gràcies per la teva compra!
```

**Submission**:
1. Go to WhatsApp Manager → Message Templates
2. Click "Create Template"
3. Fill in template details
4. Submit for Meta approval (usually 24-48 hours)
5. Once approved, use template name in API calls

---

## Edge Cases

### 1. Customer Has No Phone Number
**Scenario**: Customer registered without mobile phone.

**Handling**:
- Skip WhatsApp notification
- Log: "WhatsApp skipped: no phone number"
- Fall back to email notification

### 2. Invalid Phone Number Format
**Scenario**: Phone stored in wrong format (letters, too short, etc.).

**Handling**:
```php
private function isValidPhoneNumber($phone)
{
    // Remove all non-digit
    $digits = preg_replace('/[^0-9]/', '', $phone);
    
    // Must be 11-15 digits (with country code)
    if (strlen($digits) < 11 || strlen($digits) > 15) {
        return false;
    }
    
    return true;
}
```

### 3. Message Template Rejected by Meta
**Scenario**: Template violates WhatsApp policies.

**Handling**:
- Review Meta's rejection reason
- Revise template (remove promotional language, shorten, etc.)
- Resubmit
- Meanwhile, use fallback text messages (lower quality limits)

### 4. Customer Queries Balance from Unregistered Number
**Scenario**: Customer sends "Saldo" from phone not in system.

**Handling**:
- Reply: "No encontramos tu cuenta. Registra tu número aquí: [URL]"
- Provide link to phone number update page in PrestaShop

### 5. Rate Limit Exceeded
**Scenario**: Too many messages sent too quickly (Meta limits: 1000/day for new accounts).

**Handling**:
- Queue messages in database:
  ```sql
  CREATE TABLE ps_fidelitypoints_whatsapp_queue (
    id_queue INT AUTO_INCREMENT PRIMARY KEY,
    id_customer INT,
    phone_number VARCHAR(20),
    message_data TEXT,
    priority INT DEFAULT 5,
    attempts INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    date_add DATETIME,
    date_sent DATETIME,
    KEY status_priority (status, priority, date_add)
  );
  ```
- Cron job processes queue at safe rate (e.g., 10 messages/minute)

### 6. Webhook Replay Attack
**Scenario**: Malicious actor resends webhook payload.

**Handling**:
- Store processed message IDs in cache (Redis/Memcached)
- Check if message ID already processed:
  ```php
  $cacheKey = 'whatsapp_msg_' . $messageId;
  if (Cache::getInstance()->get($cacheKey)) {
      return; // Already processed
  }
  Cache::getInstance()->set($cacheKey, 1, 3600); // 1 hour TTL
  ```

---

## Failure Modes

### 1. WhatsApp API Unavailable
**Symptoms**: All message sends return 5xx errors.

**Impact**: High - No notifications sent.

**Detection**:
- Monitor API response codes
- Alert if consecutive failures > 5

**Mitigation**:
- Queue messages for retry
- Exponential backoff: 1m, 5m, 15m, 1h, 6h
- Fallback to email after 24h
- Display Meta status page: https://developers.facebook.com/status/

### 2. Access Token Expired
**Symptoms**: 401 Unauthorized errors.

**Impact**: Critical - All messages fail.

**Detection**:
- Check for 401 responses
- Immediate admin alert

**Mitigation**:
- Use long-lived tokens (60 days)
- Implement token refresh flow
- Admin dashboard warning 7 days before expiration

### 3. Phone Number Blocked/Suspended
**Symptoms**: 403 errors for specific phone numbers.

**Impact**: Medium - Cannot message specific customer.

**Detection**:
- Parse error response for "blocked" status

**Mitigation**:
- Log customer as unreachable
- Mark opt-out automatically
- Admin report for manual review

### 4. Webhook Not Receiving Events
**Symptoms**: No inbound messages processed, but messages visible in WhatsApp Manager.

**Impact**: Medium - Balance queries not working.

**Detection**:
- Test webhook with Meta's testing tool
- Monitor webhook request count

**Mitigation**:
- Check firewall/security rules
- Verify webhook URL accessible from internet
- Check server logs for errors
- Re-verify webhook subscription

### 5. Message Delivery Failure
**Symptoms**: Status stuck at "sent", never "delivered".

**Impact**: Low - Customer may not receive notification.

**Detection**:
- Monitor delivery rate
- Alert if < 90% delivery rate

**Mitigation**:
- Check if customer's WhatsApp number valid
- Retry once after 5 minutes
- Mark as failed after 2 attempts

---

## Offline Behavior

### PrestaShop Offline
**Impact**: Cannot send notifications, cannot receive balance queries.

**Behavior**:
- Messages queued in WhatsApp API (not our system)
- When PrestaShop back online, process backlog
- Balance queries: auto-retry from Meta (temporary failure)

### WhatsApp API Offline (Meta Outage)
**Impact**: No messaging possible.

**Behavior**:
- Queue messages locally in database
- Cron job retries every 15 minutes
- Admin notification of outage
- Check Meta status dashboard

---

## Security Considerations

### 1. Webhook Verification
```php
// Verify webhook signature (optional but recommended)
private function verifySignature()
{
    $signature = $_SERVER['HTTP_X_HUB_SIGNATURE_256'] ?? '';
    $payload = file_get_contents('php://input');
    $secret = Configuration::get('WHATSAPP_APP_SECRET');
    
    $expectedSignature = 'sha256=' . hash_hmac('sha256', $payload, $secret);
    
    if (!hash_equals($expectedSignature, $signature)) {
        http_response_code(403);
        die('Invalid signature');
    }
}
```

### 2. Access Token Protection
- **Never** hardcode in source code
- Store in encrypted configuration
- Use environment variables in production
- Rotate every 60 days (before expiration)
- Limit permissions to messaging only

### 3. Phone Number Privacy (GDPR)
- Phone numbers are personal data
- Log with customer consent (opt-in)
- Anonymize logs after 90 days
- Allow customer to request data deletion
- Include in GDPR export

### 4. Rate Limiting
```php
// Prevent abuse of balance query
private function rateLimitQuery($customerId)
{
    $cacheKey = 'whatsapp_query_' . $customerId;
    $count = Cache::getInstance()->get($cacheKey) ?: 0;
    
    if ($count > 10) {
        return false; // Too many queries
    }
    
    Cache::getInstance()->set($cacheKey, $count + 1, 3600); // 1 hour window
    return true;
}
```

### 5. Message Content Validation
- Sanitize dynamic content (customer names, amounts)
- Prevent injection of malicious links
- Validate template parameters before sending

### 6. Opt-out Compliance
- Must honor opt-out requests immediately
- Cannot send marketing messages after opt-out
- Transactional messages (order confirmation) may still be sent (check local laws)

---

## Related Documents

### Internal References
- [../01_project/REQUIREMENTS.md](../01_project/REQUIREMENTS.md) - Project requirements
- [./ANIWIN_POS_INTEGRATION.md](./ANIWIN_POS_INTEGRATION.md) - POS integration (for in-store notifications)
- [./PRESTASHOP_MODULE.md](./PRESTASHOP_MODULE.md) - Module integration points
- [../03_features/NOTIFICATIONS.md](../03_features/NOTIFICATIONS.md) - Notification rules
- [../05_data/CUSTOMER_DATA.md](../05_data/CUSTOMER_DATA.md) - Phone number storage
- [../06_security/DATA_PROTECTION.md](../06_security/DATA_PROTECTION.md) - GDPR compliance

### External References
- **WhatsApp Business API Docs**: https://developers.facebook.com/docs/whatsapp/cloud-api
- **Message Templates Guide**: https://developers.facebook.com/docs/whatsapp/message-templates
- **Webhooks Setup**: https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks
- **WhatsApp Business Policy**: https://www.whatsapp.com/legal/business-policy
- **Meta Business Manager**: https://business.facebook.com

---

## Open Questions / TODOs

### High Priority
- [ ] **WhatsApp Business Account**: Create or use existing?
  - New account recommended for dedicated support number
  - Requires business verification (documents, 1-3 days)

- [ ] **Phone Number**: Acquire dedicated business line
  - Spain: +34 XXX XXX XXX
  - Provider: Twilio, Vonage, local telecom
  - Cost: ~€5-15/month

- [ ] **Message Templates**: Create and submit all templates
  - Points earned (ES, CA, EN)
  - Points redeemed (ES, CA, EN)
  - Points expiring (ES, CA, EN)
  - Welcome message
  - Balance response

- [ ] **Messaging Tier**: Confirm Meta messaging limits
  - New accounts: 1,000 conversations/24h
  - After 7 days: increases to 10,000, then 100,000
  - Expect ~50-100 messages/day initially

### Medium Priority
- [ ] **Rich Media Messages**: Add product images?
  - Currently text-only
  - Future: Send product image with points notification
  - Requires template with header image

- [ ] **Interactive Messages**: Button-based replies
  - Quick reply buttons: [Ver Saldo] [Canjear]
  - Simplifies customer interaction
  - Requires different template structure

- [ ] **Delivery Analytics**: Dashboard for message stats
  - Sent/Delivered/Read rates
  - Average response time for balance queries
  - Opt-out rate tracking

- [ ] **Multi-language Auto-detection**: 
  - Currently based on PrestaShop language setting
  - Future: Detect from customer message language
  - Use language detection API or simple keyword matching

### Low Priority
- [ ] **Chatbot Integration**: AI-powered responses
  - Handle FAQs beyond balance query
  - "How do I redeem points?" → Auto-response
  - DialogFlow or Rasa integration

- [ ] **Order Updates**: Extend to shipping notifications?
  - "Your order #XXX has shipped"
  - May require separate message templates
  - Check if this fits loyalty program scope

- [ ] **Promotional Messages**: Opt-in marketing campaigns
  - "Double points this weekend!"
  - Separate opt-in from transactional messages
  - Must comply with anti-spam regulations

---

**Supported Languages**

| Language | WhatsApp Code | Greeting | Balance Query Keywords |
|----------|---------------|----------|----------------------|
| Spanish | `es` | ¡Hola! | saldo, puntos, balance |
| Catalan | `ca` | Hola! | saldo, punts |
| English | `en_US` | Hello! | balance, points |

---

**Rate Limits & Costs**

| Item | Limit/Cost | Notes |
|------|------------|-------|
| **Initial Tier** | 1,000 conversations/day | New accounts |
| **Tier 1** | 10,000/day | After ~7 days |
| **Tier 2** | 100,000/day | After sustained usage |
| **Service Conversations** | €0.0018-0.0090 per conversation | Utility messages (our case) |
| **Marketing Conversations** | €0.0250-0.0500 per conversation | Promotional (not used) |
| **Conversation Window** | 24 hours | Free messages within window |

*Costs as of 2024, Spain market. Check latest pricing: https://developers.facebook.com/docs/whatsapp/pricing*

---

**Document Owner**: Communications Team  
**Review Cycle**: Quarterly or when Meta updates API  
**Feedback**: [Create issue in project repository]
