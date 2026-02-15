# Entretelas Theme Implementation Notes

## Overview
This document details all non-UI/stylistic changes made to create the Entretelas theme for PrestaShop. The theme is based on Hummingbird and follows PrestaShop 9.1.0 theme structure.

---

## 1. Repository Configuration Changes

### 1.1 Git Configuration (.gitignore)
**File Modified:** `.gitignore` (root directory)

**Change Made:**
```diff
themes/*/
themes/classic
!themes/_core
!themes/_libraries
+!themes/entretelas
```

**Line Number:** 163

**Reason:** 
PrestaShop's default `.gitignore` excludes all theme directories (`themes/*/`) to prevent accidental commits of third-party themes. We added an exception for `!themes/entretelas` to allow version control of our custom theme while keeping other themes excluded.

**Impact:** 
- Allows the Entretelas theme to be tracked in Git
- Maintains exclusion of other themes (e.g., downloaded themes, Classic theme)
- Follows the existing pattern used for `_core` and `_libraries` directories

---

## 2. Theme Directory Structure

### 2.1 Theme Creation
**Source:** `tests/Resources/themes/hummingbird/`  
**Destination:** `themes/entretelas/`

**Method:**
```bash
cp -r tests/Resources/themes/hummingbird themes/entretelas
```

**Reason:**
- PrestaShop 9.1.0 uses Hummingbird as the default theme
- The test resources contain a minimal but complete Hummingbird theme structure
- Copying provides all necessary template files and base structure
- Creates a standalone theme that doesn't modify the original Hummingbird

### 2.2 Complete Directory Structure Created
```
themes/entretelas/
├── assets/
│   ├── css/
│   │   ├── theme.css                    # Base Hummingbird styles (copied)
│   │   └── entretelas-custom.css        # NEW: Custom Entretelas styles
│   ├── fonts/                           # NEW: Custom fonts directory
│   │   ├── PumpTriD Regular.ttf         # NEW: Display font
│   │   └── Quagmire Extended Bold.otf   # NEW: Heading font
│   └── js/
│       └── theme.js                     # Base theme JavaScript (copied)
├── config/
│   └── theme.yml                        # MODIFIED: Theme configuration
├── preview.png                          # Theme preview image (copied)
└── templates/                           # All template files (copied from Hummingbird)
    ├── _partials/
    ├── catalog/
    ├── checkout/
    ├── cms/
    ├── contact.tpl
    ├── customer/
    ├── errors/
    └── index.tpl
```

**Files Created:** 36 total files
- **2 new CSS files** (1 base + 1 custom)
- **2 new font files**
- **1 new JavaScript file** (base theme)
- **1 configuration file** (modified)
- **1 preview image**
- **29 template files** (all copied unchanged from Hummingbird)

---

## 3. Theme Configuration Changes

### 3.1 Theme Metadata (theme.yml)
**File:** `themes/entretelas/config/theme.yml`

#### 3.1.1 Theme Identity
**Lines Modified:** 1-7

**Original (Hummingbird):**
```yaml
name: hummingbird
display_name: Hummingbird
version: 1.0.1
author:
  name: "PrestaShop Team"
  email: "pub@prestashop.com"
  url: "https://www.prestashop-project.org/"
```

**Changed to (Entretelas):**
```yaml
name: entretelas
display_name: Entretelas
version: 1.0.0
author:
  name: "Entretelas"
  email: "info@entretelas.com"
  url: "https://www.entretelas.com/"
```

**Fields Changed:**
- `name`: `hummingbird` → `entretelas` (internal identifier, must be unique)
- `display_name`: `Hummingbird` → `Entretelas` (displayed in admin panel)
- `version`: `1.0.1` → `1.0.0` (new theme starts at 1.0.0)
- `author.name`: Changed to theme owner
- `author.email`: Changed to business email
- `author.url`: Changed to business website

**Why These Changes Matter:**
- `name` is used by PrestaShop to identify the theme in database and file system
- `display_name` appears in the admin panel theme selector
- Proper versioning allows tracking theme updates
- Author information provides attribution and support contact

#### 3.1.2 Asset Registration
**Lines Modified:** 29-34

**Original (Commented Out):**
```yaml
assets:
# If you're using this theme as child and you want to load
# the parent theme assets, uncomment this line.
#  use_parent_assets: true

# The following lines are showing how to load assets in your page
# Uncomment and change value to start loading css or js files
#  css:
#    all:
#      - id: custom-lib-style
#        path: assets/css/custom-lib.css
#    product:
#      - id: product-style
#        path: assets/css/product.css
#        media: all
#        priority: 200
#  js:
#    cart:
#      - id: cat-extra-lib
#        path: assets/js/cart-lib.js
```

**Changed to:**
```yaml
assets:
  css:
    all:
      - id: entretelas-custom
        path: assets/css/entretelas-custom.css
        priority: 100
```

**Configuration Details:**

| Parameter | Value | Explanation |
|-----------|-------|-------------|
| `css.all` | Array of CSS files | Loads on all pages |
| `id` | `entretelas-custom` | Unique identifier for this CSS asset |
| `path` | `assets/css/entretelas-custom.css` | Relative path from theme root |
| `priority` | `100` | Load order (higher = later, allows overriding base styles) |

**Loading Order:**
1. PrestaShop core CSS (priority 0-50)
2. Base theme CSS (`theme.css`) (priority 50-99)
3. **Entretelas custom CSS** (priority 100) ← Loads last, can override everything

**Why This Configuration:**
- Loads custom styles on **all pages** (not just specific pages)
- Priority 100 ensures our custom styles override base Hummingbird styles
- Uses relative path (no domain/URL needed)
- Single CSS file approach keeps customizations maintainable

#### 3.1.3 Unchanged Sections
The following sections were **copied unchanged** from Hummingbird:

**Meta Configuration (lines 9-27):**
- `compatibility`: Works with PrestaShop 8.1.0+
- `framework`: Bootstrap v5.2.0
- `available_layouts`: Four layout options (full-width, three-column, two-column variants)

**Global Settings (lines 37-64):**
- `configuration`: Image quality settings
- `modules`: Modules to enable (`ps_apiresources`)
- `hooks`: Module placement on pages
  - `displayHome`: Featured products and banner
  - `displayOrderConfirmation2`: Featured products on order confirmation

**Image Types (lines 65-129):**
- Standard PrestaShop image sizes (cart_default, small_default, etc.)
- Product and category image dimensions
- Retina display support (2x variants)

**Theme Settings (lines 132-143):**
- `rtl_generation`: false (no right-to-left support)
- `default_layout`: layout-full-width
- Page-specific layouts (category, best-sales, new-products, etc. use left column)

**Why Keep These Unchanged:**
- Maintains compatibility with PrestaShop core
- Preserves all Hummingbird functionality
- Ensures modules and images work correctly
- Allows easy theme switching (Hummingbird ↔ Entretelas)

---

## 4. Asset Integration

### 4.1 Custom Fonts
**Source:** `prestashop-aesthetic-package/fonts/`  
**Destination:** `themes/entretelas/assets/fonts/`

**Files Copied:**
1. `PumpTriD Regular.ttf` (89KB)
   - Display font for hero/large text
   - TrueType format
   - Normal weight

2. `Quagmire Extended Bold.otf` (25KB)
   - Heading font (uppercase style)
   - OpenType format
   - Bold weight, extended style

**Method:**
```bash
cp prestashop-aesthetic-package/fonts/*.ttf prestashop-aesthetic-package/fonts/*.otf themes/entretelas/assets/fonts/
```

**Integration in CSS:**
Fonts are loaded via `@font-face` declarations in `entretelas-custom.css` (lines 6-20):
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
```

**Path Resolution:**
- CSS file location: `themes/entretelas/assets/css/entretelas-custom.css`
- Font file location: `themes/entretelas/assets/fonts/`
- Relative path: `../fonts/` (up one directory from css to assets, then into fonts)

**Performance Considerations:**
- `font-display: swap` ensures text remains visible during font loading
- Font files are reasonably sized (total 114KB)
- Modern browsers cache fonts after first load

### 4.2 Custom CSS File
**File:** `themes/entretelas/assets/css/entretelas-custom.css`

**Purpose:** Contains all Entretelas brand styling (colors, typography, components)

**Structure:**
1. Font declarations (@font-face rules)
2. CSS custom properties (:root variables)
3. Global styles (body, typography)
4. Component styles (buttons, forms, products, etc.)
5. Responsive adjustments (media queries)

**Total Size:** 485 lines of CSS

**Note:** See separate section on UI/stylistic changes for CSS content details.

---

## 5. PrestaShop Theme Requirements

### 5.1 Minimum Required Files (All Present)
✅ `config/theme.yml` - Theme configuration  
✅ `preview.png` - Theme preview image (139KB)  
✅ `templates/` directory - Template files  
✅ `assets/` directory - CSS, JS, images, fonts  

### 5.2 Template Files Compatibility
All 29 template files copied from Hummingbird maintain:
- Smarty template syntax
- PrestaShop variable usage
- Bootstrap 5.2.0 structure
- Module hook compatibility
- Form handling
- Customer account functionality
- Checkout/cart functionality

**No template modifications were made** - all customization is CSS-only.

**Advantage:** Theme updates can be applied by updating template files without losing customizations.

---

## 6. Installation & Activation

### 6.1 Theme Detection by PrestaShop
PrestaShop detects themes by:
1. Scanning `themes/` directory for subdirectories
2. Looking for `config/theme.yml` in each subdirectory
3. Reading `name` and `display_name` from theme.yml
4. Checking `preview.png` for theme preview image

**Entretelas meets all requirements:**
- Located in `themes/entretelas/`
- Valid `theme.yml` with unique name
- Preview image present

### 6.2 How to Activate (Admin Panel)
1. Navigate to **Design > Theme & Logo**
2. Three themes should appear:
   - Classic (PrestaShop legacy)
   - Hummingbird (PrestaShop 9.x default)
   - **Entretelas** (new custom theme)
3. Click **"Use this theme"** on Entretelas card
4. PrestaShop activates the theme

### 6.3 Cache Clearing
After activation or CSS changes:
```bash
php bin/console cache:clear
```

If assets aren't loading:
```bash
php bin/console prestashop:generate:assets
```

---

## 7. Technical Specifications

### 7.1 PrestaShop Compatibility
- **Target Version:** PrestaShop 9.1.0
- **Minimum Version:** PrestaShop 8.1.0 (per theme.yml)
- **Framework:** Bootstrap v5.2.0
- **Base Theme:** Hummingbird

### 7.2 Browser Compatibility
Inherited from Hummingbird:
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Bootstrap 5.2.0 compatibility matrix
- CSS custom properties support required
- @font-face support required

### 7.3 PHP Requirements
No PHP code in theme - inherits from PrestaShop core:
- PHP 8.1+ (PrestaShop 9.x requirement)
- Smarty template engine

### 7.4 File Encoding
- All files: UTF-8 encoding
- Line endings: Unix (LF)
- No BOM (Byte Order Mark)

---

## 8. Maintenance & Updates

### 8.1 Updating Theme Styles
**To modify colors/styling:**
1. Edit `themes/entretelas/assets/css/entretelas-custom.css`
2. Clear PrestaShop cache: `php bin/console cache:clear`
3. Refresh browser (Ctrl+Shift+R to bypass cache)

**Variables to modify** (lines 23-48 of entretelas-custom.css):
```css
:root {
  --entretelas-brown: #542e26;      /* Primary brand color */
  --entretelas-orange: #e87722;     /* Secondary/accent */
  --entretelas-red: #cb2c30;        /* Calls-to-action */
  --entretelas-soft-tan: #f1e5d6;   /* Background */
  /* ... more variables ... */
}
```

### 8.2 Adding New CSS Files
If you need additional CSS files:

1. Create file: `themes/entretelas/assets/css/[filename].css`
2. Edit `themes/entretelas/config/theme.yml`
3. Add to assets section:
```yaml
assets:
  css:
    all:
      - id: entretelas-custom
        path: assets/css/entretelas-custom.css
        priority: 100
      - id: new-css-file          # Add this
        path: assets/css/[filename].css
        priority: 110              # Higher priority loads later
```
4. Clear cache

### 8.3 Template Customization
**Current state:** All templates are unchanged from Hummingbird

**To customize templates:**
1. Locate template: `themes/entretelas/templates/[path]/[file].tpl`
2. Edit using Smarty template syntax
3. Test thoroughly - template errors break pages
4. Clear cache after changes

**Recommendation:** Keep template changes minimal to ease future updates.

### 8.4 Updating from Hummingbird
If Hummingbird receives updates:

**Safe to update:**
- Template files (if you haven't modified them)
- `assets/css/theme.css` (base styles)
- `assets/js/theme.js` (base JavaScript)

**Do NOT overwrite:**
- `config/theme.yml` (your custom configuration)
- `assets/css/entretelas-custom.css` (your custom styles)
- `assets/fonts/` (your custom fonts)

**Update process:**
```bash
# Backup custom files first
cp themes/entretelas/config/theme.yml /tmp/
cp themes/entretelas/assets/css/entretelas-custom.css /tmp/

# Copy updated files from Hummingbird
cp tests/Resources/themes/hummingbird/assets/css/theme.css themes/entretelas/assets/css/
cp tests/Resources/themes/hummingbird/assets/js/theme.js themes/entretelas/assets/js/
cp -r tests/Resources/themes/hummingbird/templates/* themes/entretelas/templates/

# Restore custom files
cp /tmp/theme.yml themes/entretelas/config/
cp /tmp/entretelas-custom.css themes/entretelas/assets/css/

# Clear cache
php bin/console cache:clear
```

---

## 9. Rollback & Theme Switching

### 9.1 Switching Back to Hummingbird
**Admin Panel Method:**
1. Go to **Design > Theme & Logo**
2. Click **"Use this theme"** on Hummingbird
3. Done - instant switch

**No data loss:** PrestaShop preserves settings for inactive themes.

### 9.2 Removing Entretelas Theme
If you need to remove the theme:

```bash
# 1. Switch to different theme in admin first
# 2. Remove theme files
rm -rf themes/entretelas/

# 3. Remove git exception (optional)
# Edit .gitignore and remove line: !themes/entretelas
```

**Database cleanup:** PrestaShop may retain theme settings in database. To fully remove:
1. Switch to another theme
2. Use PrestaShop database cleanup (if available)
3. Or manually remove from `ps_theme` table (advanced)

---

## 10. File Permissions

### 10.1 Required Permissions
```bash
# Theme directory
chmod 755 themes/entretelas/

# All subdirectories
find themes/entretelas/ -type d -exec chmod 755 {} \;

# All files (readable by web server)
find themes/entretelas/ -type f -exec chmod 644 {} \;
```

### 10.2 Ownership
Files should be owned by web server user:
```bash
# Example (adjust user:group for your server)
chown -R www-data:www-data themes/entretelas/
```

---

## 11. Security Considerations

### 11.1 No Security Vulnerabilities Introduced
- No PHP code added
- No database queries added
- No user input handling added
- No file uploads handled
- No external resources loaded (fonts are local)

### 11.2 CSS Security
- No JavaScript in CSS
- No data URIs with executable content
- No external stylesheet imports
- All URLs are relative paths

### 11.3 Font File Security
- Fonts served as static files
- No executable code in font files
- Standard TrueType/OpenType formats
- Same-origin policy applies

---

## 12. Testing Checklist

### 12.1 Theme Detection
- [ ] Theme appears in admin panel (Design > Theme & Logo)
- [ ] Theme name shows as "Entretelas"
- [ ] Preview image displays correctly
- [ ] Version shows as "1.0.0"

### 12.2 Activation
- [ ] Theme activates without errors
- [ ] No PHP errors in PrestaShop logs
- [ ] Homepage loads correctly
- [ ] No console errors in browser DevTools

### 12.3 Asset Loading
- [ ] Custom CSS file loads (`entretelas-custom.css`)
- [ ] Base CSS file loads (`theme.css`)
- [ ] Pump Trid font loads (check DevTools Network tab)
- [ ] Quagmire font loads (check DevTools Network tab)
- [ ] No 404 errors for assets

### 12.4 Functionality
- [ ] All pages accessible (home, category, product, cart, checkout)
- [ ] Navigation works
- [ ] Search works
- [ ] Add to cart works
- [ ] Checkout process works
- [ ] User login/registration works
- [ ] Mobile responsive design works

---

## 13. Known Limitations

### 13.1 Template Compatibility
- Templates are exact copies from Hummingbird
- If Hummingbird has bugs, Entretelas inherits them
- PrestaShop module compatibility depends on module supporting Hummingbird

### 13.2 CSS Specificity
- Custom CSS might be overridden by module CSS with higher specificity
- Some PrestaShop modules inject CSS with `!important`
- May need to adjust priorities or add specificity

### 13.3 No Parent Theme Relationship
- This is a standalone theme, not a child theme
- Updates to Hummingbird don't automatically apply
- Must manually update templates when Hummingbird updates

### 13.4 Font Loading
- Custom fonts add ~114KB to initial page load
- Slower connections may see FOUT (Flash of Unstyled Text)
- Mitigated by `font-display: swap`

---

## 14. Future Enhancements

### 14.1 Potential Improvements
- Create child theme relationship with Hummingbird (reduces maintenance)
- Add theme-specific settings panel in admin
- Create page builder compatibility
- Add multiple color scheme options
- Optimize font loading with WOFF2 format
- Add theme documentation in admin panel

### 14.2 Module Development
Potential custom modules for Entretelas:
- Theme settings module
- Color scheme switcher
- Font customizer
- Layout options panel

---

## 15. Version History

### Version 1.0.0 (Initial Release)
**Date:** 2026-02-15

**Changes:**
- Created theme based on Hummingbird
- Added Entretelas brand colors and typography
- Integrated custom fonts (Pump Trid, Quagmire)
- Configured theme.yml with proper metadata
- Added custom CSS with comprehensive styling
- Updated .gitignore to track theme

**Files Added:**
- 36 files total (templates, assets, configuration)

**Lines of Code:**
- CSS: 485 lines
- Configuration: 143 lines (theme.yml)

**Compatibility:**
- PrestaShop 8.1.0+ / 9.1.0
- Bootstrap 5.2.0
- Modern browsers

---

## 16. Support & Resources

### 16.1 PrestaShop Resources
- **Official Documentation:** https://devdocs.prestashop-project.org/
- **Theme Documentation:** https://devdocs.prestashop-project.org/8/themes/
- **Community Forums:** https://www.prestashop.com/forums/

### 16.2 Theme-Specific Files
- **Implementation Guide:** `prestashop-aesthetic-package/documentation/IMPLEMENTATION_GUIDE.md`
- **Color Reference:** `prestashop-aesthetic-package/documentation/COLOR_PALETTE_REFERENCE.md`
- **Standalone Theme Guide:** `prestashop-aesthetic-package/documentation/STANDALONE_THEME_GUIDE.md`

### 16.3 Technical Support
- Check PrestaShop logs: `var/logs/`
- Enable Developer Mode in admin for detailed errors
- Use browser DevTools for CSS/JavaScript debugging
- Check file permissions if assets don't load

---

## 17. Conclusion

This theme implementation follows PrestaShop best practices:
- ✅ Standalone theme (doesn't modify core or other themes)
- ✅ Proper configuration and metadata
- ✅ Asset organization and loading
- ✅ Maintains all Hummingbird functionality
- ✅ Version controlled (Git)
- ✅ Documented changes
- ✅ No security vulnerabilities introduced
- ✅ Easy to maintain and update
- ✅ Preserves ability to switch themes
- ✅ Compatible with PrestaShop 9.1.0

The theme is ready for activation and testing in a PrestaShop 9.1.0 environment.
