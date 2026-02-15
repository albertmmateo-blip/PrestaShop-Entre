/**
 * Entretelas Theme - Main JavaScript Entry Point
 * This file is the main entry for webpack compilation
 */

// Import jQuery (available globally from PrestaShop)
import $ from 'jquery';

// Import base theme functionality
// Note: Core theme.js functionality is handled by PrestaShop core
// This file is for Entretelas-specific enhancements

/**
 * Entretelas Theme Initialization
 */
(function() {
  'use strict';

  // Initialize when DOM is ready
  $(document).ready(function() {
    console.log('Entretelas theme initialized');
    
    // Add any Entretelas-specific JavaScript functionality here
    initEntretelasFunctionality();
  });

  /**
   * Initialize Entretelas-specific features
   */
  function initEntretelasFunctionality() {
    // Custom animations, interactions, or enhancements
    // for the Entretelas theme can be added here
    
    // Example: Enhanced product card interactions
    $('.product-miniature').hover(
      function() {
        $(this).addClass('product-hover');
      },
      function() {
        $(this).removeClass('product-hover');
      }
    );

    // Add smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(e) {
      const target = $(this.getAttribute('href'));
      if (target.length) {
        e.preventDefault();
        $('html, body').stop().animate({
          scrollTop: target.offset().top - 100
        }, 500);
      }
    });
  }

  // Export for use in other modules if needed
  window.EntreterasTheme = {
    init: initEntretelasFunctionality
  };

})();
