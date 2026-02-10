# Meter-Based Product Quantities (CONDITIONAL)

## Overview

This feature allows PrestaShop to handle product quantities in meters with decimal precision (multiples of 0.05 meters) while maintaining full compatibility with PrestaShop's integer-based internal processing.

**IMPORTANT**: This feature is **conditional** and only applies to products explicitly marked as meter-based. Standard products continue to work with regular integer quantities.

## Enabling Meter-Based Quantities

The meter conversion system only activates for products that are marked with one of these indicators:

### Method 1: Data Attribute on Quantity Input
Add `data-unity="m"` to the quantity input:
```html
<input type="number" id="quantity_wanted" data-unity="m" value="1" />
```

### Method 2: Data Attribute on Product Form
Add `data-unity="m"` to the product form:
```html
<form data-unity="m">
  <input type="number" id="quantity_wanted" value="1" />
</form>
```

### Method 3: CSS Class on Quantity Input
Add the class `quantity-meters` to the quantity input:
```html
<input type="number" id="quantity_wanted" class="quantity-meters" value="1" />
```

### Method 4: CSS Class on Product Form
Add the class `product-meters` to the product form:
```html
<form class="product-meters">
  <input type="number" id="quantity_wanted" value="1" />
</form>
```

### Method 5: Data Attribute Anywhere on Page
Add `data-product-unity="m"` anywhere on the product page:
```html
<div data-product-unity="m">
  <!-- Product details -->
</div>
```

## Product Types

### Meter-Based Products
Products marked with any of the above indicators will:
- Display quantities in meters (1.00, 1.25, 2.75)
- Round user input UP to nearest 0.05 meters
- Store quantities as centimeters (100, 125, 275)
- Convert between meters and centimeters automatically

### Standard Products
Products **without** any meter indicators will:
- Display quantities as regular integers (1, 2, 3)
- Use standard PrestaShop quantity handling
- Store quantities as entered (1, 2, 3)
- Work exactly as PrestaShop normally does

## How It Works

### User Interface (Frontend)
- **Display**: Users see and input quantities in meters (e.g., 1.00, 1.25, 2.75)
- **Input Validation**: Quantities are automatically rounded to the nearest 0.05 meters (5 centimeters)
  - Example: 2.71 → 2.75
  - Example: 2.76 → 2.80
  - Example: 2.23 → 2.25
- **Minimum Step**: 0.05 meters (5 centimeters)
- **Minimum Quantity**: 0.05 meters (5 centimeters)

### Backend Processing
- **Storage**: Quantities are stored as integers representing centimeters
  - 1.00 meters → 100 (centimeters)
  - 1.25 meters → 125 (centimeters)
  - 2.75 meters → 275 (centimeters)
- **Processing**: All PrestaShop operations (cart, orders, stock, invoices, payments) work with these integer values
- **No Infrastructure Changes**: The system continues to work exactly as before, just with larger integer values

## Implementation Details

### JavaScript Module
Location: `themes/_core/js/quantity-meters.js`

This module handles:
1. **Display Conversion**: Converts stored centimeter values to meters for display
2. **Input Validation**: Rounds user input to nearest 0.05 meters
3. **Submission Conversion**: Converts meter input to centimeters before sending to backend
4. **AJAX Interception**: Intercepts PrestaShop AJAX calls to ensure centimeter values are sent
5. **Response Handling**: Converts backend responses back to meters for display

### Key Functions

```javascript
roundToMeterStep(meters)
```
Rounds a meter value to the nearest 0.05.

```javascript
metersToCentimeters(meters)
```
Converts meters to centimeters (integer).

```javascript
centimetersToMeters(centimeters)
```
Converts centimeters to meters (decimal).

### Heuristic for Compatibility

To maintain compatibility with existing PrestaShop installations:
- Values < 50: Treated as meters (e.g., quantity=1 displayed as 1.00 meters → stored as 100 centimeters)
- Values >= 50: Treated as centimeters already (e.g., quantity=125 displayed as 1.25 meters)

This allows the system to work with both:
- Existing products with small quantities (1, 2, 3)
- New products with centimeter-based quantities (100, 125, 275)

## Usage Example

### For Customers
1. Visit a product page
2. See quantity input showing "1.00" meters (default)
3. Enter desired quantity: "2.75" meters
4. System automatically validates and rounds to nearest 0.05
5. Add to cart
6. System processes order with quantity=275 (centimeters)

### For Administrators
- No special configuration required
- Set product minimal quantity as usual:
  - Set to 1 → Displayed as 1.00 meters → Stored as 100 centimeters
  - Set to 100 → Displayed as 1.00 meters
  - Set to 125 → Displayed as 1.25 meters

## Technical Notes

### Input Attributes
The quantity input field is enhanced with:
- `step="0.05"` - Allows 0.05 meter increments
- `min="0.05"` - Minimum of 0.05 meters
- `type="number"` - Native browser number input

### Event Handling
- **change/blur events**: Validate and round user input
- **submit events**: Convert meters to centimeters
- **AJAX events**: Intercept and convert quantities
- **updatedProduct events**: Convert backend responses to meters

### Data Storage
- Uses jQuery `.data()` to store centimeter values temporarily
- Stores `centimeters` and `is-meters-mode` flags on input element

## Building the JavaScript

To rebuild the JavaScript after making changes:

```bash
cd themes/
npm install  # First time only
npm run build
```

Build output will be generated in `themes/core.js` and related chunk files.

## Testing

### Manual Testing Checklist
1. ✓ Open a product page
2. ✓ Verify quantity shows as meter value (e.g., "1.00")
3. ✓ Try entering: 2.71 → Should become 2.75
4. ✓ Try entering: 2.76 → Should become 2.80
5. ✓ Try entering: 2.23 → Should become 2.25
6. ✓ Add product to cart
7. ✓ Verify cart shows correct quantity
8. ✓ Update cart quantity
9. ✓ Complete checkout
10. ✓ Verify order shows correct quantity

### Browser Compatibility
- Modern browsers with ES6 support
- jQuery 3.x
- Webpack-bundled code supports wide range of browsers

## Maintenance

### Updating the Rounding Logic
To change the rounding increment (currently 0.05):

1. Edit `themes/_core/js/quantity-meters.js`
2. Change the `METER_STEP` constant
3. Rebuild: `npm run build`

### Debugging
- Check browser console for errors
- Verify `quantity_wanted` parameter in network requests
- Should see large integers (100, 125, etc.) being sent to backend

## Compatibility

### PrestaShop Version
- Tested with PrestaShop 1.7.x+
- Compatible with core PrestaShop quantity handling
- Works with standard themes and modules

### No Breaking Changes
- Existing products continue to work
- No database schema changes required
- No modification to payment or order processing
- Full backward compatibility

## Security Considerations

- Input validation ensures only valid meter values
- Conversion to integers prevents decimal-related precision issues
- No SQL injection risk (uses PrestaShop's built-in parameter handling)
- Client-side validation supplemented by server-side integer casting

## Future Enhancements

Possible improvements:
1. Add configuration option to enable/disable per product
2. Add custom product attribute for meter-based products
3. Support different units (feet, yards, etc.)
4. Admin panel configuration for default unit
5. Display unit label next to quantity input

## Support

For issues or questions:
1. Check browser console for JavaScript errors
2. Verify JavaScript build completed successfully
3. Check network tab to see values being sent
4. Review PrestaShop logs for backend errors
