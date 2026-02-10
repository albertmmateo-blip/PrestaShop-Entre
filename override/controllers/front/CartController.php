<?php
/**
 * Copyright since 2007 PrestaShop SA and Contributors
 * PrestaShop is an International Registered Trademark & Property of PrestaShop SA
 *
 * NOTICE OF LICENSE
 *
 * This source file is subject to the Open Software License (OSL 3.0)
 * that is bundled with this package in the file LICENSE.md.
 * It is also available through the world-wide-web at this URL:
 * https://opensource.org/licenses/OSL-3.0
 * If you did not receive a copy of the license and are unable to
 * obtain it through the world-wide-web, please send an email
 * to license@prestashop.com so we can send you a copy immediately.
 *
 * DISCLAIMER
 *
 * Do not edit or add to this file if you wish to upgrade PrestaShop to newer
 * versions in the future. If you wish to customize PrestaShop for your
 * needs please refer to https://devdocs.prestashop.com/ for more information.
 *
 * @author    PrestaShop SA and Contributors <contact@prestashop.com>
 * @copyright Since 2007 PrestaShop SA and Contributors
 * @license   https://opensource.org/licenses/OSL-3.0 Open Software License (OSL 3.0)
 */

/**
 * Override CartController to handle meter-based quantities.
 * 
 * This override allows the system to work with centimeters internally
 * while presenting meters to the user. Quantities are received in
 * centimeters from the frontend and processed as such.
 */
class CartController extends CartControllerCore
{
    /**
     * Initialize cart controller.
     * 
     * Overrides parent to ensure quantity values from the frontend
     * (which are in centimeters) are properly handled as integers.
     *
     * @see FrontController::init()
     */
    public function init(): void
    {
        parent::init();

        // The qty value comes in as centimeters from the frontend JavaScript
        // We ensure it's treated as an integer (centimeters)
        // The conversion from meters to centimeters happens in the frontend
        $this->qty = abs((int) Tools::getValue('qty', 1));
        
        // Ensure minimum quantity is at least 5 centimeters (0.05 meters)
        if ($this->qty < 5) {
            $this->qty = 5;
        }
    }

    /**
     * Process AJAX add to cart action.
     * 
     * Ensures quantity is properly handled as centimeters.
     */
    public function processAdd(): void
    {
        // Ensure qty is set correctly before processing
        $qty = abs((int) Tools::getValue('qty', 1));
        
        // Minimum quantity is 5 centimeters
        if ($qty < 5) {
            $qty = 5;
        }
        
        $_GET['qty'] = $qty;
        $_POST['qty'] = $qty;
        $this->qty = $qty;
        
        parent::processAdd();
    }

    /**
     * Process AJAX update action for cart quantities.
     * 
     * Ensures quantity is properly handled as centimeters.
     */
    public function processUpdate(): void
    {
        // Ensure qty is set correctly before processing
        $qty = abs((int) Tools::getValue('qty', 1));
        
        // Minimum quantity is 5 centimeters
        if ($qty < 5) {
            $qty = 5;
        }
        
        $_GET['qty'] = $qty;
        $_POST['qty'] = $qty;
        $this->qty = $qty;
        
        parent::processUpdate();
    }
}
