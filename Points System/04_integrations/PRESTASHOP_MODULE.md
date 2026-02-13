# PrestaShop Fidelity Module Implementation

**Version**: 1.0  
**Status**: Draft  
**Last Updated**: 2024-02-13  
**PrestaShop Version**: 9.1.0

---

## Purpose

Define the technical implementation of the Fidelity Points System as a PrestaShop module, ensuring no modifications to PrestaShop core files while providing full functionality for earning, redeeming, and managing customer loyalty points.

## Scope

### In Scope
- Module architecture and file structure
- Database table creation and management
- Hook integration (actionValidateOrder, displayCustomerAccount, etc.)
- Cart rule generation for point redemption
- Customer account integration
- Admin panel for configuration and reporting
- Compatibility with PrestaShop 9.1.0
- Upgrade/uninstall procedures
- Translation support (Spanish, Catalan, English)

### Out of Scope
- Core PrestaShop modifications (forbidden)
- Theme-specific customizations
- Third-party module integration (handled separately)
- POS hardware integration (see ANIWIN_POS_INTEGRATION.md)
- WhatsApp API implementation (see WHATSAPP_MESSAGING.md)

---

## Inputs

### From PrestaShop Core
1. **Order Events** (via hooks)
   - `actionValidateOrder`: New order placed
   - `actionOrderStatusPostUpdate`: Order status changed
   - `actionOrderReturn`: Product returned
   - Order data: total, customer ID, products, payment status

2. **Customer Actions**
   - Point redemption request (via form submission)
   - Balance inquiry (via customer account page)
   - NFC card registration (via profile page)

3. **Admin Configuration**
   - Points per euro spent (e.g., 1 point per 10€)
   - Minimum order amount for points
   - Point expiration period (days)
   - Excluded product categories/manufacturers
   - Redemption rate (e.g., 100 points = 5€ discount)
   - Minimum points for redemption

### From Integration Services
- In-store purchases (see ANIWIN_POS_INTEGRATION.md)
- Manual point adjustments (admin)
- Bulk import operations

---

## Outputs

### To PrestaShop Database
1. **Custom Tables** (prefix: `ps_`)
   ```sql
   -- Main transactions table
   CREATE TABLE IF NOT EXISTS `PREFIX_fidelitypoints_transactions` (
     `id_transaction` INT(11) NOT NULL AUTO_INCREMENT,
     `id_customer` INT(11) NOT NULL,
     `points` INT(11) NOT NULL COMMENT 'Positive for earn, negative for redeem',
     `id_order` INT(11) DEFAULT NULL,
     `id_cart_rule` INT(11) DEFAULT NULL,
     `transaction_type` ENUM('purchase','redeem','adjustment','expire','void') NOT NULL,
     `description` VARCHAR(255),
     `source` VARCHAR(50) DEFAULT 'prestashop' COMMENT 'prestashop, aniwin_pos, manual',
     `admin_note` TEXT,
     `date_add` DATETIME NOT NULL,
     `date_upd` DATETIME,
     PRIMARY KEY (`id_transaction`),
     KEY `customer_date` (`id_customer`, `date_add`),
     KEY `order_ref` (`id_order`)
   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

   -- Customer balance cache
   CREATE TABLE IF NOT EXISTS `PREFIX_fidelitypoints_customer` (
     `id_customer` INT(11) NOT NULL,
     `total_points` INT(11) NOT NULL DEFAULT 0,
     `points_earned` INT(11) NOT NULL DEFAULT 0 COMMENT 'Lifetime earned',
     `points_redeemed` INT(11) NOT NULL DEFAULT 0 COMMENT 'Lifetime redeemed',
     `nfc_uid` VARCHAR(20) DEFAULT NULL COMMENT 'NFC card unique ID',
     `nfc_registered_date` DATETIME DEFAULT NULL,
     `last_transaction_date` DATETIME,
     `date_upd` DATETIME,
     PRIMARY KEY (`id_customer`),
     UNIQUE KEY `nfc_uid` (`nfc_uid`)
   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

   -- Configuration table
   CREATE TABLE IF NOT EXISTS `PREFIX_fidelitypoints_config` (
     `id_config` INT(11) NOT NULL AUTO_INCREMENT,
     `config_key` VARCHAR(100) NOT NULL,
     `config_value` TEXT,
     `date_upd` DATETIME,
     PRIMARY KEY (`id_config`),
     UNIQUE KEY `config_key` (`config_key`)
   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

   -- Pending transactions (for unregistered NFC cards)
   CREATE TABLE IF NOT EXISTS `PREFIX_fidelitypoints_pending` (
     `id_pending` INT(11) NOT NULL AUTO_INCREMENT,
     `nfc_uid` VARCHAR(20) NOT NULL,
     `points` INT(11) NOT NULL,
     `order_reference` VARCHAR(50),
     `source` VARCHAR(50),
     `date_add` DATETIME NOT NULL,
     `claimed` TINYINT(1) DEFAULT 0,
     `claimed_date` DATETIME DEFAULT NULL,
     PRIMARY KEY (`id_pending`),
     KEY `nfc_unclaimed` (`nfc_uid`, `claimed`)
   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
   ```

2. **Cart Rules** (PrestaShop native table)
   - Generated dynamically for point redemption
   - Single-use, customer-specific codes
   - Automatic cleanup after use or expiration

### To Customer
- Points balance displayed on:
  - Customer account dashboard
  - Order confirmation page
  - My account > Fidelity Points page
- Transaction history table
- Redemption form and generated discount codes

### To Admin
- Configuration page (`/admin/configure/modules/fidelitypoints`)
- Reports page with:
  - Total points in circulation
  - Points awarded/redeemed per period
  - Top customers by points
  - Liability estimation (points as currency value)
- Customer detail page (points tab)

---

## Main Flows

### Flow 1: Module Installation

```php
// File: modules/fidelitypoints/fidelitypoints.php

class FidelityPoints extends Module
{
    public function __construct()
    {
        $this->name = 'fidelitypoints';
        $this->tab = 'loyalty_customer_engagement';
        $this->version = '1.0.0';
        $this->author = 'Your Company';
        $this->need_instance = 0;
        $this->ps_versions_compliancy = ['min' => '9.0.0', 'max' => '9.99.99'];
        $this->bootstrap = true;

        parent::__construct();

        $this->displayName = $this->l('Fidelity Points System');
        $this->description = $this->l('Complete loyalty program with points earning and redemption');
        $this->confirmUninstall = $this->l('Are you sure? All points data will be deleted.');
    }

    public function install()
    {
        return parent::install()
            && $this->createTables()
            && $this->registerHooks()
            && $this->installTabs()
            && $this->setDefaultConfiguration();
    }

    private function registerHooks()
    {
        return $this->registerHook('actionValidateOrder')
            && $this->registerHook('actionOrderStatusPostUpdate')
            && $this->registerHook('actionOrderReturn')
            && $this->registerHook('displayCustomerAccount')
            && $this->registerHook('displayCustomerAccountForm')
            && $this->registerHook('displayOrderConfirmation')
            && $this->registerHook('displayHeader')
            && $this->registerHook('displayBackOfficeHeader')
            && $this->registerHook('actionCustomerAccountAdd')
            && $this->registerHook('actionObjectCustomerDeleteAfter');
    }

    private function setDefaultConfiguration()
    {
        Configuration::updateValue('FIDELITY_POINTS_PER_EURO', 1);
        Configuration::updateValue('FIDELITY_MIN_ORDER_AMOUNT', 0);
        Configuration::updateValue('FIDELITY_EXPIRATION_DAYS', 365);
        Configuration::updateValue('FIDELITY_REDEMPTION_RATE', 100); // 100 points = 5€
        Configuration::updateValue('FIDELITY_REDEMPTION_VALUE', 5);
        Configuration::updateValue('FIDELITY_MIN_REDEEM_POINTS', 100);
        Configuration::updateValue('FIDELITY_ENABLED', 1);
        
        return true;
    }
}
```

### Flow 2: Points Awarding on Order

```php
public function hookActionValidateOrder($params)
{
    // Check if points system is enabled
    if (!Configuration::get('FIDELITY_ENABLED')) {
        return;
    }

    $order = $params['order'];
    $customer = new Customer($order->id_customer);

    // Check if customer is valid and not guest
    if (!Validate::isLoadedObject($customer) || $customer->is_guest) {
        return;
    }

    // Get order total (excluding shipping and already redeemed points)
    $orderTotal = $order->total_paid_tax_incl;
    $minAmount = (float)Configuration::get('FIDELITY_MIN_ORDER_AMOUNT');

    if ($orderTotal < $minAmount) {
        return; // Order too small
    }

    // Check for excluded products
    $orderProducts = $order->getProducts();
    $eligibleAmount = $this->calculateEligibleAmount($orderProducts);

    // Calculate points
    $pointsPerEuro = (int)Configuration::get('FIDELITY_POINTS_PER_EURO');
    $pointsEarned = floor($eligibleAmount / 10 * $pointsPerEuro);

    if ($pointsEarned <= 0) {
        return;
    }

    // Award points
    $this->addTransaction(
        $customer->id,
        $pointsEarned,
        $order->id,
        'purchase',
        sprintf(
            $this->l('Order %s - Earned %d points'),
            $order->reference,
            $pointsEarned
        ),
        'prestashop'
    );

    // Send notification
    $this->notifyCustomer($customer, 'points_earned', [
        'points' => $pointsEarned,
        'order_ref' => $order->reference,
        'new_balance' => $this->getCustomerBalance($customer->id)
    ]);
}

private function calculateEligibleAmount($products)
{
    $excludedCategories = json_decode(
        Configuration::get('FIDELITY_EXCLUDED_CATEGORIES'),
        true
    ) ?: [];
    
    $eligibleTotal = 0;

    foreach ($products as $product) {
        $productObj = new Product($product['product_id']);
        $categories = $productObj->getCategories();
        
        // Check if product is in excluded category
        $isExcluded = !empty(array_intersect($categories, $excludedCategories));
        
        if (!$isExcluded) {
            $eligibleTotal += $product['total_price_tax_incl'];
        }
    }

    return $eligibleTotal;
}
```

### Flow 3: Point Redemption

```php
// File: modules/fidelitypoints/controllers/front/redeem.php

class FidelityPointsRedeemModuleFrontController extends ModuleFrontController
{
    public $ssl = true;
    public $auth = true; // Require login

    public function postProcess()
    {
        $customerId = $this->context->customer->id;
        $pointsToRedeem = (int)Tools::getValue('points_to_redeem');

        // Validate points amount
        $currentBalance = $this->module->getCustomerBalance($customerId);
        $minRedeem = (int)Configuration::get('FIDELITY_MIN_REDEEM_POINTS');

        if ($pointsToRedeem < $minRedeem) {
            $this->errors[] = sprintf(
                $this->module->l('Minimum redemption is %d points'),
                $minRedeem
            );
            return;
        }

        if ($pointsToRedeem > $currentBalance) {
            $this->errors[] = $this->module->l('Insufficient points balance');
            return;
        }

        // Calculate discount value
        $redemptionRate = (int)Configuration::get('FIDELITY_REDEMPTION_RATE');
        $redemptionValue = (float)Configuration::get('FIDELITY_REDEMPTION_VALUE');
        $discountAmount = ($pointsToRedeem / $redemptionRate) * $redemptionValue;

        // Create cart rule
        $cartRule = new CartRule();
        $cartRule->id_customer = $customerId;
        $cartRule->date_from = date('Y-m-d H:i:s');
        $cartRule->date_to = date('Y-m-d H:i:s', strtotime('+30 days'));
        $cartRule->description = sprintf(
            'Fidelity Points Redemption: %d points',
            $pointsToRedeem
        );
        $cartRule->quantity = 1;
        $cartRule->quantity_per_user = 1;
        $cartRule->priority = 1;
        $cartRule->partial_use = 0;
        $cartRule->code = $this->generateUniqueCode();
        $cartRule->minimum_amount = 0;
        $cartRule->minimum_amount_tax = 1;
        $cartRule->minimum_amount_currency = (int)$this->context->currency->id;
        $cartRule->minimum_amount_shipping = 0;
        $cartRule->reduction_amount = $discountAmount;
        $cartRule->reduction_tax = 1;
        $cartRule->reduction_currency = (int)$this->context->currency->id;
        $cartRule->active = 1;

        // Set names for all languages
        $languages = Language::getLanguages(true);
        foreach ($languages as $lang) {
            $cartRule->name[$lang['id_lang']] = sprintf(
                'Fidelity Points (%d pts)',
                $pointsToRedeem
            );
        }

        if ($cartRule->add()) {
            // Deduct points
            $this->module->addTransaction(
                $customerId,
                -$pointsToRedeem,
                null,
                $cartRule->id,
                'redeem',
                sprintf('Redeemed %d points for %s€ discount', $pointsToRedeem, $discountAmount),
                'prestashop'
            );

            // Redirect to cart with code applied
            $cartUrl = $this->context->link->getPageLink('cart', true, null, [
                'action' => 'show',
                'addDiscount' => 1,
                'discount_name' => $cartRule->code
            ]);
            Tools::redirect($cartUrl);
        } else {
            $this->errors[] = $this->module->l('Error creating discount. Please try again.');
        }
    }

    private function generateUniqueCode()
    {
        do {
            $code = 'FIDEL' . strtoupper(Tools::passwdGen(8));
            $exists = CartRule::getIdByCode($code);
        } while ($exists);

        return $code;
    }
}
```

### Flow 4: Customer Account Display

```php
public function hookDisplayCustomerAccount($params)
{
    $customerId = $this->context->customer->id;
    $balance = $this->getCustomerBalance($customerId);

    $this->context->smarty->assign([
        'points_balance' => $balance,
        'points_link' => $this->context->link->getModuleLink(
            'fidelitypoints',
            'account'
        )
    ]);

    return $this->display(__FILE__, 'views/templates/hook/customer_account.tpl');
}

// Template: views/templates/hook/customer_account.tpl
{literal}
<li class="fidelity-points-account">
    <a href="{$points_link}" title="{l s='My Fidelity Points' mod='fidelitypoints'}">
        <i class="material-icons">&#xe8d3;</i>
        <span>
            {l s='My Fidelity Points' mod='fidelitypoints'}
            <em class="points-badge">{$points_balance}</em>
        </span>
    </a>
</li>
{/literal}
```

### Flow 5: Admin Configuration Page

```php
// File: modules/fidelitypoints/controllers/admin/AdminFidelityPointsController.php

class AdminFidelityPointsController extends ModuleAdminController
{
    public function __construct()
    {
        $this->bootstrap = true;
        $this->table = 'fidelitypoints_transactions';
        $this->className = 'FidelityTransaction';
        $this->lang = false;

        parent::__construct();

        $this->fields_list = [
            'id_transaction' => ['title' => 'ID', 'width' => 50],
            'id_customer' => ['title' => 'Customer'],
            'points' => ['title' => 'Points', 'class' => 'fixed-width-xs'],
            'transaction_type' => ['title' => 'Type'],
            'description' => ['title' => 'Description'],
            'date_add' => ['title' => 'Date', 'type' => 'datetime']
        ];

        $this->addRowAction('view');
        $this->addRowAction('delete');
    }

    public function renderForm()
    {
        // Configuration form
        $fields_form = [
            'legend' => ['title' => $this->l('Fidelity Points Settings')],
            'input' => [
                [
                    'type' => 'switch',
                    'label' => $this->l('Enable Points System'),
                    'name' => 'FIDELITY_ENABLED',
                    'values' => [
                        ['id' => 'active_on', 'value' => 1, 'label' => $this->l('Yes')],
                        ['id' => 'active_off', 'value' => 0, 'label' => $this->l('No')]
                    ]
                ],
                [
                    'type' => 'text',
                    'label' => $this->l('Points per 10€ spent'),
                    'name' => 'FIDELITY_POINTS_PER_EURO',
                    'class' => 'fixed-width-xs',
                    'desc' => $this->l('Example: 1 = 1 point per 10€')
                ],
                [
                    'type' => 'text',
                    'label' => $this->l('Minimum order amount'),
                    'name' => 'FIDELITY_MIN_ORDER_AMOUNT',
                    'class' => 'fixed-width-sm',
                    'suffix' => '€',
                    'desc' => $this->l('Orders below this amount will not earn points')
                ],
                [
                    'type' => 'text',
                    'label' => $this->l('Redemption rate'),
                    'name' => 'FIDELITY_REDEMPTION_RATE',
                    'class' => 'fixed-width-xs',
                    'desc' => $this->l('How many points equal the redemption value')
                ],
                [
                    'type' => 'text',
                    'label' => $this->l('Redemption value'),
                    'name' => 'FIDELITY_REDEMPTION_VALUE',
                    'class' => 'fixed-width-xs',
                    'suffix' => '€',
                    'desc' => $this->l('Discount value for redemption rate (e.g., 100 points = 5€)')
                ]
            ],
            'submit' => ['title' => $this->l('Save')]
        ];

        // ... additional rendering logic
    }
}
```

---

## Edge Cases

### 1. Order Cancellation After Points Awarded
**Scenario**: Customer cancels order, points already in account.

**Handling**:
```php
public function hookActionOrderStatusPostUpdate($params)
{
    $newOrderStatus = $params['newOrderStatus'];
    $order = new Order($params['id_order']);

    // Check if order is cancelled or refunded
    if (in_array($newOrderStatus->id, [6, 7])) { // Cancelled, Refunded
        // Find original point transaction
        $sql = 'SELECT * FROM `' . _DB_PREFIX_ . 'fidelitypoints_transactions`
                WHERE `id_order` = ' . (int)$order->id . '
                AND `transaction_type` = "purchase"
                AND `points` > 0';
        
        $transaction = Db::getInstance()->getRow($sql);
        
        if ($transaction) {
            // Reverse points
            $this->addTransaction(
                $transaction['id_customer'],
                -$transaction['points'],
                $order->id,
                null,
                'void',
                'Order ' . $order->reference . ' cancelled',
                'prestashop'
            );
        }
    }
}
```

### 2. Cart Rule Already Used When Points Deducted
**Scenario**: Points redeemed, cart rule created, but customer never uses it (expires).

**Handling**:
- Cron job checks expired cart rules linked to point redemptions
- Refund points if cart rule never used:
```php
public function cronRefundExpiredRedemptions()
{
    $sql = 'SELECT cr.id_cart_rule, ft.id_customer, ft.points
            FROM `' . _DB_PREFIX_ . 'cart_rule` cr
            LEFT JOIN `' . _DB_PREFIX_ . 'fidelitypoints_transactions` ft
                ON cr.id_cart_rule = ft.id_cart_rule
            WHERE cr.date_to < NOW()
            AND cr.quantity = 1  -- Unused
            AND ft.transaction_type = "redeem"';
    
    $expiredRules = Db::getInstance()->executeS($sql);
    
    foreach ($expiredRules as $rule) {
        // Refund points
        $this->addTransaction(
            $rule['id_customer'],
            abs($rule['points']),
            null,
            null,
            'adjustment',
            'Refund for expired redemption',
            'system_cron'
        );
        
        // Mark cart rule as processed
        // ... (update logic)
    }
}
```

### 3. Concurrent Redemption Requests
**Scenario**: Customer clicks redeem button twice quickly.

**Handling**:
- Database-level locking:
```php
Db::getInstance()->execute('LOCK TABLES ' . _DB_PREFIX_ . 'fidelitypoints_customer WRITE');
$balance = $this->getCustomerBalance($customerId);
// ... process redemption
Db::getInstance()->execute('UNLOCK TABLES');
```
- Or use transactions:
```php
Db::getInstance()->execute('START TRANSACTION');
// ... check balance and deduct
Db::getInstance()->execute('COMMIT');
```

### 4. Customer Deletion
**Scenario**: Customer account deleted (GDPR right to erasure).

**Handling**:
```php
public function hookActionObjectCustomerDeleteAfter($params)
{
    $customerId = $params['object']->id;
    
    // Anonymize transaction history (keep for accounting)
    Db::getInstance()->update(
        'fidelitypoints_transactions',
        ['id_customer' => 0, 'description' => 'Customer account deleted'],
        'id_customer = ' . (int)$customerId
    );
    
    // Delete customer balance record
    Db::getInstance()->delete(
        'fidelitypoints_customer',
        'id_customer = ' . (int)$customerId
    );
    
    // Cancel active cart rules
    $cartRules = CartRule::getCustomerCartRules(
        $this->context->language->id,
        $customerId
    );
    foreach ($cartRules as $rule) {
        $cartRule = new CartRule($rule['id_cart_rule']);
        $cartRule->active = 0;
        $cartRule->update();
    }
}
```

### 5. Module Upgrade with Schema Changes
**Scenario**: Module updated from v1.0 to v1.1 with new database fields.

**Handling**:
```php
public function upgrade_module_1_1_0($module)
{
    // Add new column if not exists
    $sql = 'ALTER TABLE `' . _DB_PREFIX_ . 'fidelitypoints_customer`
            ADD COLUMN `tier_level` VARCHAR(20) DEFAULT "bronze"';
    
    try {
        Db::getInstance()->execute($sql);
    } catch (Exception $e) {
        // Column already exists, skip
    }
    
    return true;
}
```

---

## Failure Modes

### 1. Database Transaction Failure
**Symptoms**: Points transaction recorded but customer balance not updated.

**Impact**: High - Data inconsistency.

**Mitigation**:
- Use database transactions for atomic operations
- Daily reconciliation job compares sum of transactions vs. cached balance
- Alert admin if discrepancies found

### 2. Hook Not Triggering
**Symptoms**: Order placed but no points awarded.

**Impact**: High - Customer dissatisfaction.

**Detection**:
- Monitor hook execution logs
- Check for conflicts with other modules

**Mitigation**:
- Fallback: Cron job checks orders from last 24h without point transactions
- Retry point award for missed orders

### 3. Cart Rule Generation Error
**Symptoms**: Points deducted but no discount code created.

**Impact**: Critical - Customer loses points with no benefit.

**Mitigation**:
```php
Db::getInstance()->execute('START TRANSACTION');
try {
    // Deduct points
    $this->addTransaction(...);
    
    // Create cart rule
    if (!$cartRule->add()) {
        throw new Exception('Cart rule creation failed');
    }
    
    Db::getInstance()->execute('COMMIT');
} catch (Exception $e) {
    Db::getInstance()->execute('ROLLBACK');
    Logger::addLog('Point redemption failed: ' . $e->getMessage(), 3);
    // Show error to customer
}
```

### 4. Module Uninstall Data Loss
**Symptoms**: Module uninstalled, all data deleted permanently.

**Impact**: Critical if accidental.

**Mitigation**:
- Export feature before uninstall
- Confirmation dialog with warning
- Soft delete option (disable module, keep data)

---

## Offline Behavior

**Not Applicable** - PrestaShop module operates only when store is online. For offline POS integration, see ANIWIN_POS_INTEGRATION.md.

---

## Security Considerations

### 1. SQL Injection Prevention
```php
// Always use parameterized queries or PrestaShop Db methods
$sql = 'SELECT * FROM ' . _DB_PREFIX_ . 'fidelitypoints_transactions 
        WHERE id_customer = ' . (int)$customerId;  // Force type casting

// Or use pSQL()
$search = pSQL(Tools::getValue('search'));
```

### 2. CSRF Protection
```php
// In controller
if (!$this->module->active) {
    die('Module not active');
}

if (!Tools::getToken(false)) {
    die('Invalid token');
}
```

### 3. Access Control
- Customer can only view/redeem their own points
- Admin permissions for manual adjustments
```php
if ($this->context->customer->id != $requestedCustomerId && 
    !$this->context->employee) {
    Tools::redirect('index.php?controller=authentication');
}
```

### 4. Point Manipulation Prevention
- Server-side validation for all point operations
- Audit log for manual adjustments
```php
if (Tools::getValue('points') != $this->calculatePoints($order)) {
    Logger::addLog('Point manipulation attempt detected', 4);
    die('Invalid request');
}
```

### 5. Cart Rule Abuse Prevention
- One-time use codes
- Customer-specific
- Expiration date (30 days)
- Monitor redemption patterns for fraud

### 6. NFC UID Security
- Validate UID format (see NFC_HARDWARE.md)
- Prevent duplicate registration
```php
$existing = Db::getInstance()->getValue(
    'SELECT id_customer FROM ' . _DB_PREFIX_ . 'fidelitypoints_customer
     WHERE nfc_uid = "' . pSQL($nfcUid) . '"'
);
if ($existing && $existing != $customerId) {
    throw new Exception('NFC card already registered');
}
```

---

## Related Documents

### Internal References
- [../01_project/REQUIREMENTS.md](../01_project/REQUIREMENTS.md) - Project requirements
- [../02_architecture/MODULE_STRUCTURE.md](../02_architecture/MODULE_STRUCTURE.md) - Module file organization
- [../03_features/POINTS_CALCULATION.md](../03_features/POINTS_CALCULATION.md) - Point calculation rules
- [../03_features/POINTS_REDEMPTION.md](../03_features/POINTS_REDEMPTION.md) - Redemption logic
- [./ANIWIN_POS_INTEGRATION.md](./ANIWIN_POS_INTEGRATION.md) - POS integration
- [./NFC_HARDWARE.md](./NFC_HARDWARE.md) - NFC card integration
- [../05_data/DATABASE_SCHEMA.md](../05_data/DATABASE_SCHEMA.md) - Complete schema
- [../06_security/MODULE_SECURITY.md](../06_security/MODULE_SECURITY.md) - Security best practices

### External References
- PrestaShop 9.1 Module Development: https://devdocs.prestashop-project.org/9/modules/
- Hook Reference: https://devdocs.prestashop-project.org/9/modules/concepts/hooks/
- Cart Rule API: https://devdocs.prestashop-project.org/9/development/components/cart-rule/
- Database Best Practices: https://devdocs.prestashop-project.org/9/development/database/

---

## Open Questions / TODOs

### High Priority
- [ ] **Module Namespace**: Confirm final module name (fidelitypoints vs. loyaltypoints)
- [ ] **PrestaShop Validator**: Submit to official validator for compliance check
- [ ] **Theme Compatibility**: Test with default theme and top 5 popular themes
- [ ] **Performance Testing**: Load test with 10,000+ customers and 100,000+ transactions

### Medium Priority
- [ ] **Multi-Currency Support**: How to handle points in different currencies?
  - Award points based on base currency conversion
  - Or separate point pools per currency?

- [ ] **B2B Mode**: Should business customers earn points?
  - Separate calculation rules?
  - Volume-based bonuses?

- [ ] **Point Expiration**: Implement automatic expiration
  - Cron job to expire old points
  - Email notification 30 days before expiration

- [ ] **Tier System**: VIP customers earn more points
  - Bronze, Silver, Gold tiers based on lifetime spend
  - Multiplier: Bronze 1x, Silver 1.5x, Gold 2x

### Low Priority
- [ ] **Import/Export Tool**: For data migration or backup
- [ ] **API Endpoint**: REST API for mobile app integration
- [ ] **GraphQL Support**: For modern frontend frameworks
- [ ] **Referral Program**: Earn points for referring friends
- [ ] **Social Sharing Bonus**: Points for sharing purchases on social media

---

**Document Owner**: Development Team  
**Review Cycle**: Before each major release  
**Feedback**: [Create issue in project repository]
