# PrestaShop 9.1.0 & Hummingbird Theme - Quick Reference

## 🏗️ Understanding PrestaShop 9.1.0 Structure

### File Locations

```
/your-prestashop-root/
├── themes/
│   └── hummingbird/              # Default theme for PS 9.1.0
│       ├── assets/
│       │   ├── css/              # Place custom CSS here
│       │   ├── js/               # JavaScript files
│       │   ├── img/              # Images
│       │   └── fonts/            # Custom fonts (create this)
│       ├── templates/
│       │   ├── catalog/          # Category & product pages
│       │   ├── checkout/         # Cart & checkout
│       │   ├── customer/         # Account pages
│       │   ├── cms/              # Content pages
│       │   └── _partials/        # Reusable components
│       ├── config/
│       │   └── theme.yml         # Theme configuration
│       └── preview.png
├── modules/                      # PrestaShop modules
├── override/                     # Core overrides (advanced)
└── var/cache/                    # Clear this after changes!
```

---

## 📁 Where to Put Custom Styles

### Option 1: Custom CSS File (Recommended)
**Location:** `/themes/hummingbird/assets/css/custom.css`

**Register in theme.yml:**
```yaml
# /themes/hummingbird/config/theme.yml
assets:
  css:
    all:
      - id: custom-entretelas
        path: assets/css/custom.css
        priority: 1000  # High priority = loads last = overrides others
```

**Pros:**
- Clean separation of custom code
- Easy to maintain and update
- Won't be lost on theme updates (if using child theme)

**Cons:**
- Requires editing theme.yml
- Need to regenerate assets after changes

### Option 2: Theme Configurator Module (Easiest)
**Location:** PrestaShop Admin Panel

**Steps:**
1. Go to **Design > Theme & Logo**
2. Click **Advanced Customization**
3. Add CSS in **Custom Code** section
4. Save

**Pros:**
- No file editing required
- Easy for non-technical users
- Changes visible immediately

**Cons:**
- Can get messy with lots of CSS
- Harder to version control
- May slow down admin panel

### Option 3: Child Theme (Most Professional)
**Location:** `/themes/entretelas-hummingbird/`

**Steps:**
```bash
# Copy entire hummingbird theme
cp -r themes/hummingbird themes/entretelas-hummingbird

# Edit config
nano themes/entretelas-hummingbird/config/theme.yml
```

**Update theme.yml:**
```yaml
name: entretelas-hummingbird
display_name: Entretelas Custom Theme
parent: hummingbird
version: 1.0.0
author:
  name: "Your Name"
```

**Pros:**
- Future-proof (won't lose changes on updates)
- Full control
- Professional approach

**Cons:**
- More initial setup
- Need to maintain both themes
- Larger file size

---

## 🎨 Hummingbird CSS Variables

Hummingbird uses CSS custom properties. You can override these:

### Core Variables (to override)
```css
:root {
  /* Layout */
  --body-bg: #f1e5d6;              /* Change background */
  --body-color: #542e26;           /* Change text color */
  
  /* Brand colors */
  --primary: #542e26;              /* Main brand color */
  --secondary: #6c757d;            /* Secondary actions */
  --success: #28a745;              /* Success states */
  --danger: #dc3545;               /* Errors/warnings */
  --warning: #ffc107;              /* Warnings */
  --info: #17a2b8;                 /* Info messages */
  
  /* Typography */
  --font-family-base: sans-serif;
  --font-size-base: 1rem;
  --line-height-base: 1.5;
  --headings-font-family: 'Quagmire', sans-serif;
  
  /* Spacing */
  --spacer: 1rem;
  
  /* Components */
  --border-radius: 0.25rem;
  --card-border-radius: 0.5rem;
  --btn-border-radius: 0.25rem;
  
  /* Links */
  --link-color: #542e26;
  --link-hover-color: #e87722;
  
  /* Buttons */
  --btn-padding-y: 0.375rem;
  --btn-padding-x: 0.75rem;
  --btn-font-size: 1rem;
}
```

---

## 🔑 Important Hummingbird Selectors

### Navigation
```css
/* Main header */
#header {
  /* Top bar with logo, search, cart */
}

#header .header-top {
  /* Logo and language/currency switchers */
}

#header .header-nav {
  /* Main navigation menu */
}

/* Mobile menu */
.mobile-menu {
  /* Hamburger menu on mobile */
}
```

### Product Listings
```css
/* Product grid */
.products {
  /* Container for product cards */
}

.product-miniature {
  /* Individual product card */
}

.product-thumbnail {
  /* Product image wrapper */
}

.product-title {
  /* Product name */
}

.product-price-and-shipping {
  /* Price display */
}

.product-flags {
  /* "New", "Sale" badges */
}
```

### Product Page
```css
/* Main product container */
.product-container {
  /* Product detail page wrapper */
}

.product-cover {
  /* Main product image */
}

.product-images {
  /* Image gallery/thumbnails */
}

.product-information {
  /* Product details, description */
}

.product-actions {
  /* Add to cart, quantity selector */
}

.product-add-to-cart {
  /* Add to cart button */
}
```

### Cart & Checkout
```css
/* Shopping cart */
#cart {
  /* Cart page */
}

.cart-grid {
  /* Cart layout */
}

.cart-items {
  /* List of cart items */
}

.cart-summary {
  /* Order summary, totals */
}

/* Checkout */
#checkout {
  /* Checkout page */
}

.checkout-step {
  /* Individual checkout step */
}
```

---

## 🛠️ Common Customizations

### 1. Change Primary Button Color
```css
.btn-primary {
  background-color: #542e26;
  border-color: #542e26;
}

.btn-primary:hover {
  background-color: #e87722;
  border-color: #e87722;
}
```

### 2. Update Add to Cart Button
```css
.product-add-to-cart .btn {
  background-color: #542e26;
  font-family: 'Quagmire', sans-serif;
  text-transform: uppercase;
  padding: 12px 30px;
}

.product-add-to-cart .btn:hover {
  background-color: #e87722;
}
```

### 3. Style Product Cards
```css
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

.product-title a {
  color: #542e26;
  font-family: 'Quagmire', sans-serif;
}

.product-price {
  color: #e87722;
  font-weight: bold;
  font-size: 1.2rem;
}
```

### 4. Customize Navigation
```css
#header .header-nav {
  background-color: #542e26;
}

#header .header-nav .nav-link {
  color: #ffffff;
  font-family: 'Quagmire', sans-serif;
  text-transform: uppercase;
}

#header .header-nav .nav-link:hover {
  color: #e87722;
}
```

### 5. Change Page Background
```css
body {
  background-color: #f1e5d6;
}

/* Keep content areas white */
.page-content,
.product-container,
.cart-container {
  background-color: #ffffff;
  padding: 2rem;
  border-radius: 8px;
}
```

---

## 🔄 After Making Changes

### 1. Clear PrestaShop Cache
```bash
# Via command line
php bin/console cache:clear

# Or in admin panel
# Advanced Parameters > Performance > Clear cache
```

### 2. Regenerate Assets
```bash
# Compile and minify assets
php bin/console prestashop:generate:assets
```

### 3. Clear Browser Cache
- **Chrome/Edge:** Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)
- **Hard Refresh:** Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

### 4. Test in Incognito/Private Mode
Ensures you're seeing fresh version without cached files

---

## 🧪 Testing Checklist

After applying custom styles, test:

### Critical Functions
- [ ] Homepage loads correctly
- [ ] Category pages display products
- [ ] Product detail pages show images and info
- [ ] Search function works
- [ ] Add product to cart
- [ ] View cart
- [ ] Update cart quantities
- [ ] Proceed to checkout
- [ ] Complete test order (in test mode!)
- [ ] User login/registration
- [ ] Account pages accessible

### Visual Check
- [ ] All text is readable (good contrast)
- [ ] Buttons are visible and clickable
- [ ] Images load properly
- [ ] No layout overflow or breaking
- [ ] Colors applied consistently

### Responsive Check
- [ ] Desktop (1920px, 1366px, 1024px)
- [ ] Tablet (768px, 834px)
- [ ] Mobile (375px, 414px, 390px)
- [ ] Navigation menu on mobile
- [ ] Cart/checkout on mobile

### Browser Check
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge

---

## 🚨 Common Issues & Fixes

### Issue: Styles Not Applying

**Causes & Solutions:**

1. **Cache not cleared**
   ```bash
   php bin/console cache:clear
   rm -rf var/cache/*
   ```

2. **CSS specificity too low**
   ```css
   /* Instead of: */
   .btn { color: #542e26; }
   
   /* Use: */
   .btn-primary.btn { color: #542e26; }
   ```

3. **CSS file not loaded**
   - Check `theme.yml` has correct path
   - Regenerate assets: `php bin/console prestashop:generate:assets`
   - Check browser Network tab for 404 errors

4. **Wrong selector**
   - Use browser DevTools to inspect element
   - Copy exact selector from inspector

### Issue: Layout Breaking

**Causes & Solutions:**

1. **Overriding grid/flex properties**
   ```css
   /* Be careful with: */
   display: block; /* May break flex layouts */
   width: 100%;    /* May break grids */
   float: left;    /* Old technique, avoid */
   ```

2. **Incorrect box-sizing**
   ```css
   * {
     box-sizing: border-box; /* Ensure this is set */
   }
   ```

3. **Z-index conflicts**
   ```css
   /* Check existing z-index values */
   /* Dropdown: ~1000 */
   /* Modal: ~1050 */
   /* Use appropriate values */
   ```

### Issue: Mobile Menu Not Working

**Causes & Solutions:**

1. **Don't override mobile menu CSS!**
   ```css
   /* DON'T do this: */
   .mobile-menu { display: none !important; }
   
   /* Check these are working: */
   .mobile-menu-toggle { /* Hamburger button */ }
   .mobile-menu-panel { /* Slide-out menu */ }
   ```

2. **JavaScript conflict**
   - Check browser console for errors
   - Ensure jQuery is loaded
   - Don't override `.js-mobile-menu` classes

### Issue: Checkout Not Working

**Causes & Solutions:**

1. **Hidden form elements**
   ```css
   /* DON'T hide form inputs */
   input[type="hidden"] { display: none; } /* OK */
   input[type="text"] { display: none; }   /* BAD */
   ```

2. **Disabled buttons**
   ```css
   /* Make sure buttons are clickable */
   .btn {
     pointer-events: auto; /* Not 'none' */
     cursor: pointer;
   }
   ```

3. **Z-index covering clickable elements**
   ```css
   /* Check overlapping elements */
   /* Reduce z-index if blocking buttons */
   ```

---

## 📊 Performance Tips

### 1. Optimize Font Loading
```css
@font-face {
  font-family: 'Quagmire';
  src: url('../fonts/Quagmire Extended Bold.otf') format('opentype');
  font-display: swap; /* Important for performance */
  font-weight: bold;
  font-style: normal;
}
```

### 2. Minimize Custom CSS
- Remove unused styles
- Combine similar rules
- Use shorthand properties
- Minify for production

### 3. Use CSS Variables
```css
/* More maintainable */
:root {
  --brand-primary: #542e26;
}

.btn { background: var(--brand-primary); }
.heading { color: var(--brand-primary); }
```

### 4. Avoid !important
```css
/* Instead of: */
.btn { color: red !important; }

/* Use higher specificity: */
.page-content .btn.btn-primary { color: red; }
```

---

## 🔗 Useful Resources

### Official Documentation
- **PrestaShop DevDocs:** https://devdocs.prestashop-project.org/
- **Hummingbird Theme:** https://devdocs.prestashop-project.org/8/themes/
- **Theme Development:** https://devdocs.prestashop-project.org/8/themes/getting-started/

### Tools
- **Browser DevTools:** Inspect and test CSS in real-time
- **GTmetrix:** Test page speed and performance
- **Google Lighthouse:** Audit performance, accessibility, SEO
- **WAVE:** Check accessibility compliance

### Community
- **PrestaShop Forums:** https://www.prestashop.com/forums/
- **PrestaShop Slack:** https://prestashop.com/slack
- **GitHub Issues:** https://github.com/PrestaShop/PrestaShop/issues

---

## 💡 Pro Tips

1. **Use Browser DevTools**
   - Right-click > Inspect to see applied styles
   - Edit CSS in real-time to test
   - Copy working CSS to your file

2. **Version Control**
   ```bash
   git init
   git add themes/hummingbird/assets/css/custom.css
   git commit -m "Add custom Entretelas styling"
   ```

3. **Document Your Changes**
   - Keep a changelog of modifications
   - Comment complex CSS rules
   - Note any PrestaShop-specific workarounds

4. **Test Payment Gateway**
   - Use test/sandbox mode
   - Complete full order flow
   - Verify styling doesn't break payment forms

5. **Mobile-First Approach**
   ```css
   /* Start with mobile styles */
   .product-card {
     width: 100%;
   }
   
   /* Add desktop styles with media queries */
   @media (min-width: 768px) {
     .product-card {
       width: 50%;
     }
   }
   ```

---

## ✅ Final Checklist Before Go-Live

- [ ] All custom CSS validated (no errors)
- [ ] Performance tested (Lighthouse score >90)
- [ ] Cross-browser tested
- [ ] Mobile responsive verified
- [ ] All e-commerce functions working
- [ ] Test orders completed successfully
- [ ] No console errors in DevTools
- [ ] Accessibility checked (WCAG AA minimum)
- [ ] Backup created
- [ ] Staging environment tested
- [ ] Client/stakeholder approval received

---

*Good luck with your PrestaShop customization!*
