# Entretelas Theme Creation Guide

## ⚠️ IMPORTANT: This is an Inspiration Guide

**Document Purpose:** This guide contains brand style elements from the original Entretelas website as **inspiration only**. The original website's CSS framework is fundamentally different from how PrestaShop Hummingbird themes work.

**What This Guide IS:**
- ✅ A reference for Entretelas brand colors, fonts, and visual identity
- ✅ Inspiration for styling decisions
- ✅ A step-by-step workflow for safely cloning and customizing Hummingbird

**What This Guide IS NOT:**
- ❌ A detailed implementation specification
- ❌ A CSS framework to copy directly
- ❌ Instructions to recreate the original website exactly

**Critical Approach:** 
1. **Preserve Hummingbird's structure** - Don't break what works
2. **Apply brand identity conservatively** - Colors and fonts first
3. **Test everything** - Verify after each small change
4. **Use as inspiration** - Adapt ideas to PrestaShop's architecture

---

## 🚀 The Three-Phase Workflow

**Simple and Safe:**

1. **Phase 1: Clone Hummingbird** → Get a working copy with all build tools intact
2. **Phase 2: Apply Brand Basics** → Colors and fonts only (conservative)
3. **Phase 3: Optional Enhancements** → Add styling progressively as needed (use inspiration guide)

**Read This First:** Jump to [Step-by-Step Theme Creation](#step-by-step-theme-creation) to get started.

---

## 📋 Table of Contents

### Getting Started (Read This First)
1. [Prerequisites](#prerequisites)
2. [Step-by-Step Theme Creation](#step-by-step-theme-creation)

### Brand Reference (Inspiration Only)
3. [Brand Colors](#brand-colors-reference)
4. [Typography](#typography-reference)
5. [UI Inspiration Ideas](#ui-inspiration-ideas)

### Optional Advanced Styling
6. [Implementation Ideas](#implementation-ideas)
7. [Troubleshooting](#troubleshooting)

---

## ⚙️ Prerequisites

Before starting, ensure you have:

- [ ] **PrestaShop Installation:** Working PrestaShop 9.0+ installation
- [ ] **Development Tools:** Node.js (16+), npm, Composer
- [ ] **Git Access:** Ability to clone from GitHub
- [ ] **File Access:** SSH/FTP access to PrestaShop themes directory
- [ ] **Backup:** Complete backup of your PrestaShop installation
- [ ] **Staging Environment:** A safe testing environment (never work on production first)

**Required Assets:**
- Font files: `PumpTriD Regular.ttf`, `Quagmire Extended Bold.otf`
- Logo files (from Entretelas branding)

---

## 🛠️ Step-by-Step Theme Creation

### Step 1: Clone the Hummingbird Theme

The Hummingbird theme is available as a Composer package. Here's how to properly clone it:

#### Option A: Install via Composer (Recommended)

```bash
# Navigate to your PrestaShop root
cd /path/to/prestashop

# Install hummingbird theme via Composer
composer require prestashop/hummingbird:^2.0

# The theme will be installed in themes/ directory
```

#### Option B: Manual Clone from GitHub

```bash
# Navigate to themes directory
cd /path/to/prestashop/themes

# Clone the hummingbird repository
git clone https://github.com/PrestaShop/hummingbird.git entretelas

# Navigate into the new theme
cd entretelas

# Install dependencies
npm install

# Build the theme
npm run build
```

#### Step 1.1: Verify the Clone

After cloning, your theme structure should include:

```
themes/entretelas/
├── assets/
│   ├── css/          # Compiled CSS files
│   ├── js/           # Compiled JavaScript
│   └── img/          # Theme images
├── config/
│   └── theme.yml     # Theme configuration
├── templates/        # Smarty template files
├── _dev/             # Source files for building
│   ├── css/          # Source CSS/SCSS
│   ├── js/           # Source JavaScript
│   └── ...
├── package.json      # Node.js dependencies
├── webpack.config.js # Build configuration
└── README.md
```

**Test:** Can you see all these directories? If yes, proceed. If not, troubleshoot installation.

#### Step 1.2: Configure the Theme

Edit `config/theme.yml` to rename the theme:

```yaml
name: entretelas
display_name: Entretelas
version: 1.0.0
author:
  name: "Your Name"
  email: "your-email@example.com"
  url: "https://entretelas.com"

meta:
  compatibility:
    from: 9.0.0
  available: true

global_settings:
  configuration:
    PS_QUICK_VIEW: true
    PS_IMAGE_QUALITY: jpg

theme_settings:
  default_layout: layout-full-width
  layouts:
    layout-full-width:
      name: Full Width Layout
      description: No side columns, ideal for e-commerce
```

#### Step 1.3: Build the Theme

```bash
# Navigate to theme directory
cd /path/to/prestashop/themes/entretelas

# Install npm dependencies (if not done)
npm install

# Build for development (with watch mode)
npm run watch

# OR build for production
npm run build
```

**Test:** Check that `assets/css/theme.css` and `assets/js/theme.js` are created.

#### Step 1.4: Activate the Theme in PrestaShop

1. Log into PrestaShop Back Office
2. Navigate to **Design > Theme & Logo**
3. Find "Entretelas" theme
4. Click "Use this theme"
5. Visit your storefront to verify it works

**Critical Test:** Browse your site. Does everything work exactly like Hummingbird? If yes, you have successfully cloned the theme. If no, troubleshoot before proceeding.

---

### Step 2: Establish Brand Foundation (Colors & Fonts)

Now that you have a working copy, start with the smallest possible changes.

#### Step 2.1: Add CSS Variables

Create a new file: `_dev/css/custom-variables.scss`

```scss
// Entretelas Brand Variables
:root {
  // Core Brand Colors
  --logo-brown: #542e26;
  --logo-orange: #e87722;
  --logo-red: #cb2c30;
  --dark-brown: #3e221c;
  
  // Background Colors
  --soft-tan: #f1e5d6;
  --white: #ffffff;
  
  // Typography
  --font-body: sans-serif;
  --font-heading: 'Quagmire', sans-serif;
  --font-display: 'Pump Trid', sans-serif;
}
```

#### Step 2.2: Import Custom Variables

Edit `_dev/css/theme.scss` to import your custom variables at the top:

```scss
// Import custom variables first
@import "custom-variables";

// Then import the rest of hummingbird's styles
@import "partials/_variables";
// ... rest of imports
```

#### Step 2.3: Add Custom Fonts

1. Create directory: `assets/fonts/`
2. Copy font files:
   - `PumpTriD Regular.ttf`
   - `Quagmire Extended Bold.otf`

3. Create `_dev/css/custom-fonts.scss`:

```scss
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

4. Import in `_dev/css/theme.scss`:

```scss
@import "custom-variables";
@import "custom-fonts";
```

#### Step 2.4: Apply Basic Brand Colors

Create `_dev/css/custom-overrides.scss`:

```scss
// Body background
body {
  background-color: var(--soft-tan);
}

// Primary text color
body,
.page-content {
  color: var(--logo-brown);
}

// Links
a {
  color: var(--logo-orange);
  
  &:hover {
    color: var(--logo-red);
  }
}

// Primary buttons
.btn-primary {
  background-color: var(--logo-orange);
  border-color: var(--logo-orange);
  
  &:hover {
    background-color: var(--logo-red);
    border-color: var(--logo-red);
  }
}
```

Import in `_dev/css/theme.scss` at the end:

```scss
// ... all other imports

// Custom overrides should be last
@import "custom-overrides";
```

#### Step 2.5: Build and Test

```bash
# Build the theme
npm run build

# Clear PrestaShop cache
rm -rf var/cache/*

# In PrestaShop Back Office:
# Go to Advanced Parameters > Performance
# Click "Clear cache"
```

**Test Checklist:**
- [ ] Body background is soft tan (#f1e5d6)
- [ ] Links are orange (#e87722)
- [ ] Links turn red on hover (#cb2c30)
- [ ] Primary buttons are orange
- [ ] Buttons turn red on hover
- [ ] **Everything else still works normally** ← Most important!

**If anything is broken, revert and troubleshoot before proceeding.**

---

### Step 3: Stop Here (Recommended)

**Congratulations!** You now have a working Entretelas theme with:
- ✅ Hummingbird functionality fully intact
- ✅ Entretelas brand colors applied
- ✅ Custom fonts loaded
- ✅ Nothing broken

**This is enough for a conservative launch.** The theme works, looks branded, and maintains all PrestaShop/Hummingbird functionality.

### Step 4: Optional Progressive Enhancements

Only proceed if Step 3 is working perfectly. See [Implementation Ideas](#implementation-ideas) below for optional styling inspiration. Remember: **Every additional change increases risk.**

---

---

## 🎨 Brand Colors Reference

**Use these colors for inspiration when styling the Hummingbird theme.**

### Core Brand Colors

```css
--logo-brown: #542e26;     /* Primary brand color */
--logo-orange: #e87722;    /* Accent, CTAs, highlights */
--logo-red: #cb2c30;       /* Secondary accent, hover states */
--dark-brown: #3e221c;     /* Borders, depth */
--soft-tan: #f1e5d6;       /* Background (warm feeling) */
```

**Quick Copy:**
```
Brown:  #542e26
Orange: #e87722
Red:    #cb2c30
Tan:    #f1e5d6
```

### How to Use These Colors

**In Hummingbird Theme:**
- Find Hummingbird's existing color variables (likely in `_dev/css/partials/_variables.scss`)
- Replace primary/accent colors with Entretelas colors
- Don't remove Hummingbird's color system, just override the values

**Example:**
```scss
// If Hummingbird has:
$primary-color: #00aff0;

// Change it to:
$primary-color: #e87722;  // Entretelas orange
```

---

## 📝 Typography Reference

### Custom Fonts

**Font Files Needed:**
- `PumpTriD Regular.ttf` - For large, decorative headings
- `Quagmire Extended Bold.otf` - For section headings

### Font Loading (Optional)

Only add custom fonts if you want them. Hummingbird's default fonts work fine.

```scss
@font-face {
  font-family: 'Pump Trid';
  src: url('../fonts/PumpTriD Regular.ttf') format('truetype');
  font-display: swap;
}

@font-face {
  font-family: 'Quagmire';
  src: url('../fonts/Quagmire Extended Bold.otf') format('opentype');
  font-display: swap;
}
```

**Usage Suggestion:**
```scss
// Use sparingly for brand consistency
.page-heading {
  font-family: 'Pump Trid', sans-serif;
}

h1, h2, h3 {
  font-family: 'Quagmire', sans-serif;
}
```

---

## 💡 UI Inspiration Ideas

**These are styling ideas from the original Entretelas website. Use as inspiration only - adapt to Hummingbird's structure.**

### Navigation Ideas

**Original Entretelas had a three-stripe gradient:**
```css
background: linear-gradient(
  to bottom,
  #542e26 0%, #542e26 33.33%,    /* Brown */
  #e87722 33.33%, #e87722 66.66%, /* Orange */
  #cb2c30 66.66%, #cb2c30 100%    /* Red */
);
```

**For Hummingbird:** This might not work well with Hummingbird's navigation structure. Consider simpler alternatives:
- Solid brown background with orange accents
- Brown header with orange links on hover

### Button Styles

**Inspiration:**
- Primary buttons: Orange background, white text
- Hover: Change to red
- Border radius: 30px (pill shape)

**Adapt to Hummingbird:** Use Hummingbird's existing button classes, just change colors.

### Card Styles

**Inspiration:**
- White cards on tan background
- Subtle shadows: `0 2px 8px rgba(84, 46, 38, 0.1)`
- Border radius: 8px
- Hover: Lift effect with `transform: translateY(-3px)`

**Adapt to Hummingbird:** Hummingbird likely has product cards already - just adjust their styling.

### Product Price Display

**Inspiration:**
- Regular prices: Brown (#542e26)
- Discounted prices: Red (#cb2c30)

---

## 🎯 Implementation Ideas

**Only attempt these if Step 3 is working perfectly.**

### Idea 1: Enhanced Typography

Apply custom fonts to more elements (carefully):

```scss
// Headings
h1, h2, h3 {
  font-family: 'Quagmire', sans-serif;
  color: var(--logo-brown);
}

// Product titles
.product-title {
  font-family: 'Quagmire', sans-serif;
  color: var(--logo-orange);
}
```

**Test thoroughly after each addition.**

### Idea 2: Card Enhancements

Add subtle styling to cards:

```scss
.card,
.product-miniature {
  box-shadow: 0 2px 8px rgba(84, 46, 38, 0.1);
  border-radius: 8px;
  transition: transform 0.3s ease;
  
  &:hover {
    transform: translateY(-3px);
  }
}
```

### Idea 3: Navigation Styling

Simple navigation update (avoid complex gradients):

```scss
#header {
  background-color: var(--logo-brown);
}

.top-menu a {
  color: white;
  
  &:hover {
    color: var(--logo-orange);
  }
}
```

### Idea 4: Form Styling

Update form focus states:

```scss
.form-control:focus {
  border-color: var(--logo-orange);
  box-shadow: 0 0 0 3px rgba(232, 119, 34, 0.1);
}
```

---

## 🔧 Important Technical Notes

### Build Process

**Always build after CSS changes:**
```bash
npm run build
```

**For active development:**
```bash
npm run watch  # Auto-rebuilds on file changes
```

**Clear cache after building:**
```bash
rm -rf var/cache/*
```

### File Structure

**Where to add your custom styles:**

```
themes/entretelas/
├── _dev/
│   └── css/
│       ├── custom-variables.scss    ← Your brand colors
│       ├── custom-fonts.scss        ← Font declarations
│       ├── custom-overrides.scss    ← Your style changes
│       └── theme.scss               ← Import your files here
└── assets/
    └── css/
        └── theme.css                ← Generated (don't edit)
```

**Edit theme.scss to import your files:**
```scss
// At the top of theme.scss
@import "custom-variables";
@import "custom-fonts";

// ... existing Hummingbird imports ...

// At the end
@import "custom-overrides";
```

### Key Principles

1. **Don't remove Hummingbird's code** - Only add overrides
2. **Use Hummingbird's existing classes** - Don't create new markup
3. **Test after every change** - Even small ones
4. **Keep changes minimal** - Less is more
5. **Preserve functionality** - Never break working features

---

## 🆘 Troubleshooting

### Problem: Styles not applying

**Solutions:**
1. Did you run `npm run build`?
2. Did you clear PrestaShop cache? (`rm -rf var/cache/*`)
3. Hard refresh browser (Ctrl+Shift+R)
4. Check that your custom SCSS files are imported in `theme.scss`
5. Check browser console for errors

### Problem: Build fails

**Solutions:**
1. Run `npm install` to ensure dependencies are present
2. Check for SCSS syntax errors (missing semicolons, brackets)
3. Review build error messages carefully
4. Ensure you're in the theme directory when running `npm run build`

### Problem: Fonts not loading

**Solutions:**
1. Verify font files are in `assets/fonts/` directory
2. Check file names match exactly in `@font-face` declarations
3. Check browser console for 404 errors
4. Verify font file paths are correct relative to CSS file

### Problem: PrestaShop won't activate theme

**Solutions:**
1. Check `config/theme.yml` is properly formatted
2. Ensure required assets are compiled (`npm run build`)
3. Check PrestaShop error logs
4. Verify theme compatibility version in `theme.yml`

### Problem: Something broke

**Solutions:**
1. **Revert your last change immediately**
2. Use Git to see what changed: `git diff`
3. Restore from backup if needed
4. Start over with smaller changes
5. Test more frequently

---

## ✅ Success Checklist

**Before considering the theme "done":**

- [ ] Theme cloned successfully from Hummingbird
- [ ] Theme builds without errors (`npm run build`)
- [ ] Theme activates in PrestaShop without errors
- [ ] Brand colors applied (at minimum)
- [ ] All core functionality works:
  - [ ] Homepage loads
  - [ ] Product browsing works
  - [ ] Search functions
  - [ ] Add to cart works
  - [ ] Checkout process works
  - [ ] User account functions work
- [ ] Mobile responsive (test on phone)
- [ ] No console errors in browser
- [ ] Site loads at reasonable speed

**Remember:** A working site with basic brand colors is better than a broken site with perfect styling.

---

## 📚 Additional Resources

**Hummingbird Documentation:**
- GitHub: https://github.com/PrestaShop/hummingbird
- PrestaShop Docs: https://devdocs.prestashop-project.org/

**PrestaShop Theme Development:**
- https://devdocs.prestashop-project.org/9/themes/

**Git for Version Control:**
```bash
# Initialize git in your theme
git init
git add .
git commit -m "Initial Hummingbird clone"

# After each working change
git add .
git commit -m "Added brand colors"
```

---

**Document Version:** 2.0 (Simplified for Conservative Implementation)  
**Last Updated:** 2026-02-16  
**Purpose:** Inspiration guide for Entretelas PrestaShop theme based on Hummingbird  
**Approach:** Conservative, test-as-you-go, preserve Hummingbird structure
