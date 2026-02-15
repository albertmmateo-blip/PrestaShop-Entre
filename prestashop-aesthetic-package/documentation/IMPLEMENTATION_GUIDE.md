# 🎨 Entretelas Aesthetic Implementation Guide for PrestaShop 9.1.0

## 📋 Overview

This package contains the aesthetic and design system from the Entretelas static website to help you create a **standalone "Entretelas" theme** for your PrestaShop 9.1.0 store.

**🎯 THEME APPROACH:**
This guide will help you create a **THIRD theme option** for PrestaShop:
1. **Classic** (PrestaShop's legacy theme)
2. **Hummingbird** (PrestaShop 9.1.0 default theme)
3. **Entretelas** (Your new custom theme - DOES NOT modify Hummingbird)

This approach means you can:
- Keep Hummingbird intact and unmodified
- Switch between themes anytime in PrestaShop admin
- Update Hummingbird without losing customizations
- Develop safely without affecting the default theme

**⚠️ IMPORTANT DISCLAIMER:**
- These files are provided as **INSPIRATION and REFERENCE** only
- **DO NOT** directly replace PrestaShop core files with these files
- **BE CONSERVATIVE** with changes to avoid breaking e-commerce functionality
- Always test changes on a staging/development environment first
- Keep backups before making any modifications

---

## 🎨 Design System Overview

### Brand Identity - Entretelas
This aesthetic is designed for a traditional Spanish haberdashery (mercería) business with warm, earthy tones and a classic feel.

### Color Palette

```css
/* Primary Brand Colors */
--logo-brown: #542e26;     /* Deep brown - main brand color */
--logo-orange: #e87722;    /* Vibrant orange - accent */
--logo-red: #cb2c30;       /* Bold red - secondary accent */
--dark-brown: #3e221c;     /* Darker brown variant */

/* UI & Background */
--soft-tan: #f1e5d6;       /* Warm tan background */
--white: #ffffff;
--border-light: #ddd;

/* Text Colors */
--text-main: var(--logo-brown);
--text-secondary: #555;

/* Functional Colors */
--color-success: #28a745;
--color-error: #dc3545;
```

### Typography

**Display Font (Headings):**
- Font: `Pump Trid Regular` (included in `/fonts/`)
- Usage: Hero text, large titles, decorative elements

**Heading Font:**
- Font: `Quagmire Extended Bold` (included in `/fonts/`)
- Usage: Section headings, navigation, product titles
- Style: Uppercase, bold, extended

**Body Font:**
- Font: Standard sans-serif (system fonts)
- Usage: Body text, descriptions, content

### Design Characteristics
- **Warm earthy color scheme** (browns, oranges, tans)
- **Traditional/classic aesthetic** suitable for textile/craft business
- **Clean layouts** with good whitespace
- **Striped navigation** with gradient (brown → orange → red)
- **Rounded corners** (4px-30px depending on element)
- **High contrast** for readability

---

## 🏗️ Creating a Standalone "Entretelas" Theme for PrestaShop 9.1.0

### Understanding PrestaShop 9.1.0 Theme Structure

PrestaShop 9.1.0 uses the **Hummingbird theme** by default. We'll use it as a **BASE** to create your new "Entretelas" theme:

```
/themes/
├── classic/                   # Legacy PrestaShop theme
├── hummingbird/               # Default PS 9.1.0 theme (UNTOUCHED)
└── entretelas/                # YOUR NEW THEME (we'll create this)
    ├── assets/
    │   ├── css/
    │   │   ├── theme.css      # Hummingbird base styles
    │   │   ├── entretelas-custom.css  # Your customizations
    │   │   └── components/    # Component-specific styles
    │   ├── js/
    │   ├── img/
    │   └── fonts/             # Custom fonts (Pump Trid, Quagmire)
    ├── templates/
    │   ├── catalog/           # Product pages
    │   ├── checkout/          # Checkout flow
    │   ├── cms/               # CMS pages
    │   └── _partials/         # Reusable components
    └── config/
        └── theme.yml          # Theme configuration
```

**Key Point:** Hummingbird remains completely unchanged. You can switch between themes anytime.

---

## 📝 Step-by-Step Implementation Plan

### Phase 1: Preparation (CRITICAL - Don't Skip!)

#### 1.1 Backup Your Store
```bash
# Backup your entire PrestaShop installation
cp -r /path/to/prestashop /path/to/prestashop-backup-$(date +%Y%m%d)

# Backup database
mysqldump -u username -p database_name > prestashop_backup_$(date +%Y%m%d).sql
```

#### 1.2 Enable Developer Mode
In PrestaShop Admin:
1. Go to **Advanced Parameters > Performance**
2. Set **Debug mode** to **Yes** (for development)
3. Clear cache after changes: **Advanced Parameters > Performance > Clear cache**

#### 1.3 Create Your New "Entretelas" Theme
**This creates a THIRD theme option without modifying Hummingbird:**

```bash
# Navigate to themes directory
cd /path/to/prestashop/themes/

# Copy Hummingbird as base for new theme
cp -r hummingbird entretelas

# Enter new theme directory
cd entretelas
```

#### 1.4 Configure the New Theme
Edit `themes/entretelas/config/theme.yml`:

```yaml
name: entretelas
display_name: Entretelas
version: 1.0.0
author:
  name: "Entretelas Team"
  email: "your-email@example.com"
  url: "https://www.entretelas.cat"

meta:
  compatibility:
    from: 9.0.0
  available_layouts:
    layout-full-width:
      name: Full width layout
      description: No side columns
    layout-both-columns:
      name: Three columns layout
      description: One column on each side
    layout-left-column:
      name: Two columns, left sidebar
    layout-right-column:
      name: Two columns, right sidebar

theme_settings:
  default_layout: layout-full-width

assets:
  css:
    all:
      - id: theme-main
        path: assets/css/theme.css
        priority: 50
      - id: entretelas-custom
        path: assets/css/entretelas-custom.css
        priority: 100  # Load after main theme CSS
  js:
    all:
      - id: theme-main
        path: assets/js/theme.js
```

#### 1.5 Add Custom Fonts
```bash
# Create fonts directory
mkdir -p themes/entretelas/assets/fonts/

# Copy font files from this package
cp /path/to/package/fonts/*.{ttf,otf} themes/entretelas/assets/fonts/
```

#### 1.6 Activate Your New Theme
In PrestaShop Admin:
1. Go to **Design > Theme & Logo**
2. You should see three themes: **Classic**, **Hummingbird**, and **Entretelas**
3. Click **Use this theme** on **Entretelas**
4. PrestaShop will activate your new theme

**Important:** You can switch back to Hummingbird or Classic anytime!

---

### Phase 2: Color Scheme Integration

#### 2.1 Create Custom CSS File
Create: `/themes/entretelas/assets/css/entretelas-custom.css`

```css
/* Entretelas Custom Styles for PrestaShop Hummingbird */
:root {
  /* Override Hummingbird's default colors */
  --primary: #542e26;           /* Brown replaces default primary */
  --secondary: #e87722;         /* Orange for accents */
  --accent: #cb2c30;            /* Red for highlights */
  
  /* Background colors */
  --body-bg: #f1e5d6;           /* Warm tan instead of white/gray */
  --card-bg: #ffffff;
  
  /* Text colors */
  --text-primary: #542e26;
  --text-secondary: #555;
  
  /* Border and UI elements */
  --border-color: #ddd;
  --border-radius: 8px;
}

/* Apply warm tan background to body */
body {
  background-color: var(--body-bg);
  color: var(--text-primary);
}

/* Update primary buttons */
.btn-primary,
.add-to-cart {
  background-color: var(--primary);
  border-color: var(--primary);
}

.btn-primary:hover,
.add-to-cart:hover {
  background-color: var(--secondary);
  border-color: var(--secondary);
}

/* Update links */
a {
  color: var(--primary);
}

a:hover {
  color: var(--secondary);
}
```

#### 2.2 Verify CSS Registration
The custom CSS should already be registered in `themes/entretelas/config/theme.yml`:

```yaml
assets:
  css:
    all:
      - id: entretelas-custom
        path: assets/css/entretelas-custom.css
        priority: 100  # Load after base theme CSS
```

After making CSS changes:
```bash
# Clear cache
php bin/console cache:clear

# Regenerate assets
php bin/console prestashop:generate:assets
```

---

### Phase 3: Typography Integration

#### 3.1 Upload Custom Fonts
Upload fonts to: `/themes/hummingbird/assets/fonts/`

- `PumpTriD Regular.ttf`
- `Quagmire Extended Bold.otf`

#### 3.2 Add @font-face Declarations
In `/themes/entretelas/assets/css/entretelas-custom.css`:

```css
@font-face {
  font-family: 'Pump Trid';
  src: url('../fonts/PumpTriD Regular.ttf') format('truetype');
  font-display: swap;
  font-weight: normal;
  font-style: normal;
}

@font-face {
  font-family: 'Quagmire';
  src: url('../fonts/Quagmire Extended Bold.otf') format('opentype');
  font-display: swap;
  font-weight: bold;
  font-style: normal;
}

/* Apply to headings */
h1, h2, h3, .h1, .h2, .h3,
.product-title,
.category-title {
  font-family: 'Quagmire', sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Hero/display text (use sparingly) */
.hero-title,
.page-header h1 {
  font-family: 'Pump Trid', sans-serif;
}
```

---

### Phase 4: Navigation Styling (Conservative Approach)

⚠️ **CAUTION:** Navigation is critical for e-commerce functionality. Test thoroughly!

#### 4.1 Understanding the Original Design
The Entretelas site has a distinctive **three-striped navigation** (brown, orange, red). 

#### 4.2 Adapting to PrestaShop
**Option A: Subtle Adaptation (Recommended)**
```css
/* Add colored accent bar above main navigation */
#header {
  border-top: 12px solid transparent;
  border-image: linear-gradient(
    to right, 
    #542e26 0%, #542e26 33%, 
    #e87722 33%, #e87722 66%, 
    #cb2c30 66%, #cb2c30 100%
  ) 1;
}

#header .header-nav {
  background-color: #542e26;
}

#header .header-nav a {
  color: #ffffff;
  font-family: 'Quagmire', sans-serif;
}
```

**Option B: Full Recreation (Advanced - Test Carefully)**
```css
/* Only use if you're comfortable with CSS and testing */
#header {
  background: linear-gradient(
    to bottom,
    #542e26 0%, #542e26 33%,
    #e87722 33%, #e87722 66%,
    #cb2c30 66%, #cb2c30 100%
  );
  height: 80px;
}

/* Ensure cart, search, and user links still work! */
#header .header-nav,
#header .search-widget,
#header .blockcart {
  /* Preserve functionality while styling */
}
```

**⚠️ DO NOT remove or hide:**
- Search widget
- Shopping cart
- User account links
- Mobile menu toggle
- Language/Currency selectors

---

### Phase 5: Product Page Styling

#### 5.1 Product Cards
The `product-detail.css` file contains extensive product card styling. Adapt selectively:

```css
/* Product miniature cards (catalog pages) */
.product-miniature {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(84, 46, 38, 0.1);
  transition: transform 0.2s ease;
}

.product-miniature:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 8px rgba(84, 46, 38, 0.15);
}

/* Product titles */
.product-miniature .product-title {
  color: #542e26;
  font-family: 'Quagmire', sans-serif;
  font-size: 1.1rem;
}

/* Price styling */
.product-price {
  color: #e87722;
  font-weight: bold;
  font-size: 1.2rem;
}
```

#### 5.2 Product Detail Page
**Conservative additions only:**

```css
/* Product page main container */
.product-container {
  background: #ffffff;
  padding: 2rem;
  border-radius: 8px;
}

/* Add to cart button */
.product-add-to-cart .btn-primary {
  background-color: #542e26;
  border: none;
  padding: 12px 30px;
  font-size: 1.1rem;
  text-transform: uppercase;
  font-family: 'Quagmire', sans-serif;
}

.product-add-to-cart .btn-primary:hover {
  background-color: #e87722;
}
```

---

### Phase 6: Testing Checklist

After implementing changes, **THOROUGHLY TEST** the following:

#### Critical E-commerce Functions
- [ ] Add products to cart
- [ ] Update cart quantities
- [ ] Remove items from cart
- [ ] Proceed to checkout
- [ ] Complete a test order (use test mode!)
- [ ] User registration/login
- [ ] Search functionality
- [ ] Category filtering
- [ ] Mobile responsiveness
- [ ] Cross-browser compatibility (Chrome, Firefox, Safari, Edge)

#### Visual/UI Verification
- [ ] All text is readable (good contrast)
- [ ] Navigation works on all devices
- [ ] Images load correctly
- [ ] Buttons are clickable and properly sized
- [ ] Forms are functional
- [ ] Modals/popups work correctly
- [ ] No layout breaking on different screen sizes

#### Performance Check
- [ ] Page load times acceptable (<3 seconds)
- [ ] Images optimized
- [ ] No console errors in browser developer tools
- [ ] CSS doesn't conflict with PrestaShop modules

---

## ⚠️ Critical Warnings

### DO NOT:
1. ❌ Modify the Hummingbird or Classic themes directly
2. ❌ Replace PrestaShop core files
3. ❌ Delete existing CSS classes/IDs needed for functionality
4. ❌ Hide or remove checkout elements
5. ❌ Break mobile navigation
6. ❌ Disable JavaScript needed for cart/checkout
7. ❌ Remove accessibility features (ARIA labels, keyboard navigation)
8. ❌ Use `!important` excessively (max 5-10 instances)
9. ❌ Make changes directly on live/production site

### DO:
1. ✅ Create a separate "Entretelas" theme (as described in this guide)
2. ✅ Work in a staging/development environment
3. ✅ Use CSS custom properties (variables) for easy adjustments
4. ✅ Test after every change
5. ✅ Keep PrestaShop's responsive breakpoints
6. ✅ Preserve all form functionality
7. ✅ Maintain WCAG accessibility standards
8. ✅ Use browser DevTools to inspect before modifying
9. ✅ Document your changes
10. ✅ Version control your customizations (Git)
11. ✅ Keep Hummingbird and Classic themes untouched (you can switch between themes anytime)

---

## 📚 Reference Files in This Package

### `/css/` Directory

1. **`variables.css`** - Design tokens (colors, fonts, spacing)
   - **USE FOR:** Reference color codes and spacing values
   - **SIZE:** 35 lines - easy to reference

2. **`style.css`** - Main stylesheet from static site
   - **USE FOR:** Understanding overall design system
   - **WARNING:** 1,657 lines - don't copy wholesale!
   - **EXTRACT:** Navigation styles, typography, layout patterns

3. **`product-detail.css`** - Product page styles
   - **USE FOR:** Product card design, detail page layouts
   - **WARNING:** 2,996 lines - highly specific to static site
   - **EXTRACT:** Color schemes, spacing, hover effects

4. **`portal.css`** - Client portal styles
   - **USE FOR:** Inspiration for user account area
   - **NOTE:** 4,345 lines - most may not apply

5. **`product-detail-critical.css`** - Critical above-fold styles
   - **USE FOR:** Performance optimization ideas
   - **SIZE:** 277 lines - prioritized styles for fast rendering

6. **`wishlists.css`** - Wishlist feature styles
   - **USE FOR:** If implementing wishlist functionality
   - **SIZE:** 706 lines

7. **`shortcutbar.css`** - Quick navigation bar
   - **USE FOR:** Optional shortcut menu styling
   - **SIZE:** 327 lines

8. **`merceria-search.css`** - Custom search widget
   - **USE FOR:** Search functionality styling ideas
   - **SIZE:** 128 lines

### `/fonts/` Directory
- `PumpTriD Regular.ttf` - Display font for large text
- `Quagmire Extended Bold.otf` - Heading font (uppercase style)

### `/assets/images-samples/` Directory
Sample images showing the visual style and color usage in context

---

## 🎯 Recommended Implementation Strategy

### Week 1: Foundation
1. Set up child theme
2. Implement color variables only
3. Test all critical functions

### Week 2: Typography
1. Upload and register fonts
2. Apply to headings only
3. Check readability on all pages

### Week 3: Components
1. Style buttons and links
2. Update product cards
3. Adjust forms

### Week 4: Navigation & Polish
1. Carefully update header/navigation
2. Fine-tune spacing and layouts
3. Mobile optimization

### Week 5: Testing & Refinement
1. Comprehensive testing
2. Fix bugs and issues
3. Performance optimization
4. User acceptance testing

---

## 🔧 Useful PrestaShop 9.1.0 Commands

```bash
# Clear cache (do this after CSS changes)
php bin/console cache:clear

# Regenerate assets
php bin/console prestashop:generate:assets

# Enable maintenance mode (for testing)
php bin/console prestashop:maintenance:enable

# Disable maintenance mode
php bin/console prestashop:maintenance:disable
```

---

## 📖 Additional Resources

### PrestaShop Documentation
- [Hummingbird Theme Guide](https://devdocs.prestashop-project.org/8/themes/)
- [Theme Development](https://devdocs.prestashop-project.org/8/themes/getting-started/)
- [Asset Management](https://devdocs.prestashop-project.org/8/themes/assets/)

### CSS Best Practices
- Use CSS custom properties for maintainability
- Follow BEM naming convention where possible
- Keep specificity low (avoid deep nesting)
- Mobile-first responsive design

### Testing Tools
- Chrome DevTools (inspect elements, test responsiveness)
- [Google Lighthouse](https://developers.google.com/web/tools/lighthouse) (performance)
- [WAVE](https://wave.webaim.org/) (accessibility testing)

---

## 🆘 Troubleshooting

### Problem: CSS changes not appearing
**Solution:**
1. Clear PrestaShop cache (Advanced Parameters > Performance)
2. Clear browser cache (Ctrl+Shift+Delete)
3. Hard refresh page (Ctrl+Shift+R or Cmd+Shift+R)
4. Check file permissions (should be 644 for CSS files)

### Problem: Fonts not loading
**Solution:**
1. Verify font files are in `/themes/hummingbird/assets/fonts/`
2. Check @font-face path is correct (relative to CSS file)
3. Ensure font files have proper permissions (644)
4. Check browser console for 404 errors
5. Verify font formats are supported by target browsers

### Problem: Layout breaking on mobile
**Solution:**
1. Don't override PrestaShop's responsive breakpoints
2. Test with browser DevTools mobile emulation
3. Use `max-width: 100%` on all images
4. Preserve existing media queries
5. Test on actual devices, not just emulator

### Problem: Checkout not working after styling
**Solution:**
1. Check browser console for JavaScript errors
2. Ensure no form elements are hidden or removed
3. Verify button click handlers still work
4. Remove recent CSS that might affect z-index or pointer-events
5. Roll back changes and apply one at a time to identify culprit

### Problem: Conflicts with PrestaShop modules
**Solution:**
1. Use more specific CSS selectors
2. Namespace your styles (e.g., `.entretelas-custom-class`)
3. Check module-specific CSS and adjust accordingly
4. Consider using CSS scope/layer (modern browsers)
5. Contact module developer for compatibility

---

## 📞 Support & Questions

If you encounter issues:

1. **Check PrestaShop forums:** [PrestaShop Community Forums](https://www.prestashop.com/forums/)
2. **Developer documentation:** [PrestaShop DevDocs](https://devdocs.prestashop-project.org/)
3. **Theme customization:** Consider hiring a PrestaShop developer for complex changes
4. **Test, test, test:** Always test on staging before production!

---

## 📝 Final Notes

This aesthetic package is designed to **inspire** your PrestaShop customization, not to be a drop-in replacement. The static site generator and PrestaShop are fundamentally different systems:

- **Static site:** Full control over HTML/CSS, no e-commerce requirements
- **PrestaShop:** Dynamic, database-driven, complex e-commerce functionality

**Take your time.** Rushing customization can break critical shopping cart functionality. A conservative, tested approach will lead to a better result than trying to replicate everything at once.

**Good luck with your PrestaShop customization!** 🎨✨

---

*Package prepared: February 2024*
*For PrestaShop 9.1.0 with Hummingbird Theme*
*Source: Entretelas Static Site (Web-Mateo-Fork)*
