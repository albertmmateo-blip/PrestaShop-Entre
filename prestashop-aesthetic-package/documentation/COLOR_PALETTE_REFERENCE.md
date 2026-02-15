# 🎨 Color Palette Quick Reference

## Brand Colors

### Primary Brand Color - Deep Brown
```css
--logo-brown: #542e26;
```
- **RGB:** `rgb(84, 46, 38)`
- **Use for:** Primary buttons, headings, navigation background, main text
- **Personality:** Traditional, warm, earthy, reliable
- **Recommended opacity variants:**
  - 90%: `rgba(84, 46, 38, 0.9)`
  - 75%: `rgba(84, 46, 38, 0.75)`
  - 50%: `rgba(84, 46, 38, 0.5)`
  - 10%: `rgba(84, 46, 38, 0.1)`

### Secondary - Vibrant Orange
```css
--logo-orange: #e87722;
```
- **RGB:** `rgb(232, 119, 34)`
- **Use for:** Call-to-action buttons, links, hover states, accents
- **Personality:** Energetic, friendly, approachable
- **Works well with:** Browns, whites, tans
- **Accessibility note:** Ensure sufficient contrast with background

### Accent - Bold Red
```css
--logo-red: #cb2c30;
```
- **RGB:** `rgb(203, 44, 48)`
- **Use for:** Sale prices, urgent CTAs, error states, highlights
- **Personality:** Bold, urgent, attention-grabbing
- **Use sparingly:** High impact color

### Dark Variant - Darker Brown
```css
--dark-brown: #3e221c;
```
- **RGB:** `rgb(62, 34, 28)`
- **Use for:** Footer, dark mode elements, text on light backgrounds
- **Personality:** Sophisticated, grounding

---

## Background & UI Colors

### Soft Tan Background
```css
--soft-tan: #f1e5d6;
```
- **RGB:** `rgb(241, 229, 214)`
- **Use for:** Page background, card backgrounds, sections
- **Personality:** Warm, inviting, paper-like
- **Advantage:** Reduces eye strain vs. pure white

### Pure White
```css
--white: #ffffff;
```
- **RGB:** `rgb(255, 255, 255)`
- **Use for:** Cards, product boxes, input fields, content areas
- **Creates contrast** against soft-tan background

### Light Border
```css
--border-light: #ddd;
```
- **RGB:** `rgb(221, 221, 221)`
- **Use for:** Dividers, input borders, card outlines
- **Subtle and unobtrusive**

---

## Text Colors

### Main Text
```css
--text-main: var(--logo-brown); /* #542e26 */
```
- **Use for:** Body text, headings, primary content
- **Contrast ratio:** Excellent on white/tan backgrounds

### Secondary Text
```css
--text-secondary: #555;
```
- **RGB:** `rgb(85, 85, 85)`
- **Use for:** Metadata, captions, helper text, labels
- **Lower hierarchy** than main text

---

## Functional Colors

### Success Green
```css
--color-success: #28a745;
```
- **RGB:** `rgb(40, 167, 69)`
- **Use for:** Success messages, completed states, stock indicators
- **Standard Bootstrap success color**

### Error Red
```css
--color-error: #dc3545;
```
- **RGB:** `rgb(220, 53, 69)`
- **Use for:** Error messages, required fields, validation errors
- **Standard Bootstrap danger color**

---

## Color Combinations

### High Contrast Pairs (Best for Text)
| Foreground | Background | Contrast Ratio | WCAG AAA |
|------------|------------|----------------|----------|
| `#542e26` (brown) | `#ffffff` (white) | 10.36:1 | ✅ Pass |
| `#542e26` (brown) | `#f1e5d6` (tan) | 8.89:1 | ✅ Pass |
| `#3e221c` (dark brown) | `#ffffff` (white) | 14.82:1 | ✅ Pass |
| `#ffffff` (white) | `#542e26` (brown) | 10.36:1 | ✅ Pass |

### Accent Combinations
| Primary | Accent | Use Case |
|---------|--------|----------|
| `#542e26` (brown) | `#e87722` (orange) | Buttons, hover states |
| `#542e26` (brown) | `#cb2c30` (red) | Sale items, urgent CTAs |
| `#e87722` (orange) | `#ffffff` (white) | Orange buttons with white text |
| `#f1e5d6` (tan) | `#542e26` (brown) | Page backgrounds with brown text |

---

## Gradient Example (Navigation)

### Three-Stripe Gradient
```css
background: linear-gradient(
  to bottom,
  #542e26 0%,      /* Brown */
  #542e26 33.33%,
  #e87722 33.33%,  /* Orange */
  #e87722 66.66%,
  #cb2c30 66.66%,  /* Red */
  #cb2c30 100%
);
```

### Horizontal Stripe
```css
background: linear-gradient(
  to right,
  #542e26 0%, #542e26 33%,
  #e87722 33%, #e87722 66%,
  #cb2c30 66%, #cb2c30 100%
);
```

---

## PrestaShop Hummingbird Variable Mapping

Map Entretelas colors to Hummingbird's CSS variables:

```css
:root {
  /* Primary colors */
  --primary: #542e26;           /* Brown - main brand */
  --secondary: #e87722;         /* Orange - accents */
  --success: #28a745;           /* Keep standard green */
  --danger: #dc3545;            /* Keep standard red */
  --warning: #ffc107;           /* Standard warning */
  --info: #17a2b8;              /* Standard info */
  
  /* Body & backgrounds */
  --body-bg: #f1e5d6;           /* Warm tan */
  --body-color: #542e26;        /* Brown text */
  
  /* Links */
  --link-color: #542e26;        /* Brown */
  --link-hover-color: #e87722;  /* Orange on hover */
  
  /* Buttons */
  --btn-primary-bg: #542e26;
  --btn-primary-hover-bg: #e87722;
  --btn-secondary-bg: #cb2c30;
  
  /* Borders */
  --border-color: #ddd;
  
  /* Components */
  --card-bg: #ffffff;
  --card-border-color: #ddd;
}
```

---

## Color Usage Guidelines

### DO:
✅ Use brown (`#542e26`) as primary brand color  
✅ Use orange (`#e87722`) for hover states and CTAs  
✅ Use tan background (`#f1e5d6`) for warmth  
✅ Maintain high contrast for text (WCAG AA/AAA)  
✅ Use red (`#cb2c30`) sparingly for emphasis  

### DON'T:
❌ Use orange and red together too frequently (can be overwhelming)  
❌ Place orange or red text on tan background (poor contrast)  
❌ Use light colors for primary text  
❌ Forget to test color blindness accessibility  
❌ Override success/error colors unless necessary  

---

## Accessibility Notes

### Contrast Requirements (WCAG 2.1)
- **Level AA (minimum):**
  - Normal text: 4.5:1 contrast ratio
  - Large text (18pt+): 3:1 contrast ratio
  
- **Level AAA (enhanced):**
  - Normal text: 7:1 contrast ratio
  - Large text: 4.5:1 contrast ratio

### All primary combinations in this palette meet WCAG AAA standards! ✅

### Color Blindness Considerations
- Brown and orange may appear similar to some users
- Always use additional indicators beyond color:
  - Icons for success/error states
  - Text labels on buttons
  - Patterns or textures where appropriate

---

## Testing Colors

### Online Tools
- **Contrast Checker:** https://webaim.org/resources/contrastchecker/
- **Color Blindness Simulator:** https://www.color-blindness.com/coblis-color-blindness-simulator/
- **Coolors:** https://coolors.co/ (palette exploration)

### Browser DevTools
```javascript
// Test color contrast in browser console
// Using Chrome/Edge DevTools
// 1. Inspect element
// 2. Look for contrast ratio indicator in Color Picker
// 3. Adjust until meeting WCAG standards
```

---

## Export Formats

### Sass/SCSS
```scss
$logo-brown: #542e26;
$logo-orange: #e87722;
$logo-red: #cb2c30;
$dark-brown: #3e221c;
$soft-tan: #f1e5d6;
$white: #ffffff;
$border-light: #ddd;
$text-main: $logo-brown;
$text-secondary: #555;
$color-success: #28a745;
$color-error: #dc3545;
```

### Less
```less
@logo-brown: #542e26;
@logo-orange: #e87722;
@logo-red: #cb2c30;
@dark-brown: #3e221c;
@soft-tan: #f1e5d6;
@white: #ffffff;
@border-light: #ddd;
@text-main: @logo-brown;
@text-secondary: #555;
@color-success: #28a745;
@color-error: #dc3545;
```

### JavaScript Object
```javascript
const colors = {
  logoBrown: '#542e26',
  logoOrange: '#e87722',
  logoRed: '#cb2c30',
  darkBrown: '#3e221c',
  softTan: '#f1e5d6',
  white: '#ffffff',
  borderLight: '#ddd',
  textMain: '#542e26',
  textSecondary: '#555',
  colorSuccess: '#28a745',
  colorError: '#dc3545'
};
```

---

## Visual Palette

```
████████  #542e26  Logo Brown (Primary)
████████  #e87722  Logo Orange (Secondary)
████████  #cb2c30  Logo Red (Accent)
████████  #3e221c  Dark Brown
████████  #f1e5d6  Soft Tan (Background)
████████  #ffffff  White
████████  #dddddd  Border Light
████████  #555555  Text Secondary
████████  #28a745  Success Green
████████  #dc3545  Error Red
```

---

*For more details, see `IMPLEMENTATION_GUIDE.md`*
