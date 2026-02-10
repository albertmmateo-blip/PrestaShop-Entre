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

use PrestaShop\PrestaShop\Adapter\Presenter\Product\ProductLazyArray;

/**
 * Override ProductController to handle meter-based quantities.
 * 
 * This override ensures that quantity values are properly handled as
 * centimeters internally while being presented as meters to users.
 */
class ProductController extends ProductControllerCore
{
    /**
     * Get the wanted quantity in centimeters.
     * 
     * The quantity_wanted comes from the frontend in centimeters.
     * This method ensures it's treated as an integer representing centimeters.
     *
     * @param ProductLazyArray|array $product
     * @return int Quantity in centimeters
     */
    public function getWantedQuantity(ProductLazyArray|array $product): int
    {
        // Get the quantity wanted from the request (in centimeters from frontend)
        $quantityWantedByTheCustomer = (int) Tools::getValue('quantity_wanted', 100);
        
        // Get minimal required quantity for purchase (also in centimeters)
        $requiredQuantityForPurchase = $this->getRequiredQuantity($product);
        
        // Ensure minimum is 5 centimeters (0.05 meters)
        if ($requiredQuantityForPurchase < 5) {
            $requiredQuantityForPurchase = 5;
        }
        
        // If the wanted quantity is lower than the required, we adjust it
        if ($quantityWantedByTheCustomer < $requiredQuantityForPurchase) {
            $quantityWantedByTheCustomer = $requiredQuantityForPurchase;
        }
        
        // Ensure minimum is 5 centimeters
        if ($quantityWantedByTheCustomer < 5) {
            $quantityWantedByTheCustomer = 5;
        }

        return $quantityWantedByTheCustomer;
    }
}
