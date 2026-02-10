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

import $ from 'jquery';
import prestashop from 'prestashop';

/**
 * Quantity Meters Handler
 * 
 * Handles product quantities in meters with decimal precision (multiples of 0.05).
 * Converts meters to centimeters for backend processing while maintaining
 * user-friendly meter-based interface.
 */

const METER_STEP = 0.05; // Minimum step for meters (5 centimeters)
const METER_TO_CM = 100; // Conversion factor

/**
 * Round a meter value UP to the nearest multiple of 0.05
 * Examples: 2.71 -> 2.75, 2.76 -> 2.80, 2.23 -> 2.25
 * 
 * @param {number} meters - The meter value to round
 * @return {number} The rounded meter value
 */
function roundToMeterStep(meters) {
  // Round UP to nearest 0.05 (5 centimeters)
  return Math.ceil(meters / METER_STEP) * METER_STEP;
}

/**
 * Convert meters to centimeters (integer)
 * 
 * @param {number} meters - The meter value
 * @return {number} The centimeter value as integer
 */
function metersToCentimeters(meters) {
  return Math.round(meters * METER_TO_CM);
}

/**
 * Convert centimeters to meters
 * 
 * @param {number} centimeters - The centimeter value
 * @return {number} The meter value
 */
function centimetersToMeters(centimeters) {
  return centimeters / METER_TO_CM;
}

/**
 * Format meter value for display (2 decimal places)
 * 
 * @param {number} meters - The meter value
 * @return {string} The formatted meter value
 */
function formatMeters(meters) {
  return meters.toFixed(2);
}

/**
 * Initialize meter-based quantity handling
 */
function initQuantityMeters() {
  const $quantityInput = $(prestashop.selectors.quantityWanted);
  
  if ($quantityInput.length === 0) {
    return;
  }

  // Get initial value
  let initialValue = parseInt($quantityInput.val(), 10) || 1;
  let initialMeters;
  
  // Heuristic: if value < 50, treat as meters; if >= 50, treat as centimeters
  // This allows compatibility with existing PrestaShop installations
  if (initialValue < 50) {
    initialMeters = initialValue; // Treat as meters
  } else {
    initialMeters = centimetersToMeters(initialValue); // Already in centimeters
  }
  
  // Set input attributes for meter input
  $quantityInput.attr('step', METER_STEP);
  $quantityInput.attr('min', METER_STEP);
  $quantityInput.attr('type', 'number');
  
  // Store centimeter value
  const initialCentimeters = metersToCentimeters(initialMeters);
  $quantityInput.data('centimeters', initialCentimeters);
  $quantityInput.data('is-meters-mode', true);
  
  // Display in meters
  $quantityInput.val(formatMeters(initialMeters));

  /**
   * Handle input changes - validate and round to meter step
   */
  $quantityInput.on('change blur', function() {
    let meters = parseFloat($(this).val());
    
    // Validate input
    if (isNaN(meters) || meters < METER_STEP) {
      meters = METER_STEP; // Minimum 0.05 meters (5 cm)
    }
    
    // Round to nearest step
    meters = roundToMeterStep(meters);
    
    // Update display value
    $(this).val(formatMeters(meters));
    
    // Store centimeter value
    const centimeters = metersToCentimeters(meters);
    $(this).data('centimeters', centimeters);
  });

  /**
   * Intercept form submission to convert meters to centimeters
   */
  const $form = $quantityInput.closest('form');
  
  // Store original form submit handler
  const originalSubmit = $form[0].submit;
  
  // Override form submit
  $form.on('submit', function(e) {
    const meters = parseFloat($quantityInput.val());
    const centimeters = metersToCentimeters(roundToMeterStep(meters));
    $quantityInput.val(centimeters);
  });

  /**
   * Intercept AJAX calls to convert meters to centimeters
   */
  $(document).ajaxSend(function(event, jqxhr, settings) {
    // Check if this is a product-related AJAX call
    if (settings.data && typeof settings.data === 'string' && settings.data.includes('quantity_wanted')) {
      const meters = parseFloat($quantityInput.val());
      const roundedMeters = roundToMeterStep(meters);
      const centimeters = metersToCentimeters(roundedMeters);
      
      // Replace the quantity_wanted parameter with centimeter value
      settings.data = settings.data.replace(
        /quantity_wanted=[^&]*/,
        `quantity_wanted=${centimeters}`
      );
    }
  });

  /**
   * Convert response data from centimeters back to meters for display
   */
  prestashop.on('updatedProduct', function(data) {
    if (data.product_minimal_quantity) {
      let minQuantity = parseInt(data.product_minimal_quantity, 10);
      
      // Apply same heuristic: < 50 means meters, >= 50 means centimeters
      let minMeters;
      if (minQuantity < 50) {
        minMeters = minQuantity;
      } else {
        minMeters = centimetersToMeters(minQuantity);
      }
      
      $quantityInput.attr('min', formatMeters(minMeters));
    }
    
    // Update displayed value to meters
    const currentCentimeters = $quantityInput.data('centimeters');
    if (currentCentimeters) {
      const currentMeters = centimetersToMeters(currentCentimeters);
      $quantityInput.val(formatMeters(currentMeters));
    }
  });

  /**
   * Handle add to cart - ensure we send centimeters
   */
  $(document).on('click', prestashop.selectors.product.addToCart + ', [data-button-action="add-to-cart"]', function(e) {
    const meters = parseFloat($quantityInput.val());
    const roundedMeters = roundToMeterStep(meters);
    const centimeters = metersToCentimeters(roundedMeters);
    
    // Temporarily set centimeter value for the add to cart action
    $quantityInput.data('display-meters', $quantityInput.val());
    $quantityInput.val(centimeters);
    
    // Restore meter display after a short delay
    setTimeout(function() {
      const displayMeters = $quantityInput.data('display-meters');
      if (displayMeters) {
        $quantityInput.val(displayMeters);
      }
    }, 100);
  });
}

// Initialize when DOM is ready
$(() => {
  initQuantityMeters();
});

export { 
  roundToMeterStep, 
  metersToCentimeters, 
  centimetersToMeters, 
  formatMeters 
};
