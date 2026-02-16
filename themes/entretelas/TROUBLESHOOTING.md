# Entretelas Theme - Troubleshooting Guide

This document provides solutions to common issues you may encounter with the Entretelas theme.

## Table of Contents

1. [Theme Causes 500 Error When Selected](#theme-causes-500-error-when-selected)
2. [Custom Styling Not Applied](#custom-styling-not-applied)
3. [Font Loading Issues](#font-loading-issues)

---

## Theme Causes 500 Error When Selected

### Problem

When you select the Entretelas theme in the PrestaShop back office (Appearance → Theme & Logo → Use this theme), the frontend shows:

```
This page isn't working
localhost is currently unable to handle this request.
HTTP ERROR 500
```

### Root Cause

The theme's `theme.yml` configuration file was referencing a custom CSS file (`assets/css/custom.css`) that in turn references Manrope font files that don't exist in the theme's assets directory. These missing font files cause PrestaShop to fail when trying to load the theme.

### Solution (Current - Version 0.1.1)

**Status:** ✅ **FIXED** in version 0.1.1

The theme now uses Google Fonts CDN to load the Manrope font family, eliminating the need for local font files. The custom CSS asset loading has been re-enabled in `config/theme.yml`. The local @font-face declarations in `theme.css` have been commented out to prevent attempts to load missing font files.

**Changes made:**
- Added Google Fonts CDN import to `custom.css` for Manrope font (weights 200-800)
- Commented out local @font-face declarations in `theme.css`
- Uncommented custom CSS asset loading in `config/theme.yml`

The theme now loads successfully with full custom styling applied.

### Solution (Future - Adding Custom Styling)

If you want to add custom styling back to the theme:

#### Option 1: Add Missing Font Files (Recommended)

1. **Obtain the Manrope font files:**
   - Download Manrope from [Google Fonts](https://fonts.google.com/specimen/Manrope)
   - Or use a font hosting service like Google Fonts CDN

2. **For local font files:**
   - Place the font files in `themes/entretelas/assets/css/fonts/`
   - Update `theme.css` to reference the correct paths:
     ```css
     @font-face {
       font-family: "Manrope";
       src: url(fonts/manrope-regular.woff2) format("woff2"),
            url(fonts/manrope-regular.woff) format("woff");
       font-style: normal;
       font-weight: 400;
     }
     ```

3. **Uncomment the CSS assets in `config/theme.yml`:**
   ```yaml
   assets:
     css:
       all:
         - id: entretelas-custom
           path: assets/css/custom.css
           media: all
           priority: 200
   ```

#### Option 2: Use Google Fonts CDN (Simpler)

1. **Update `custom.css` to use Google Fonts:**
   ```css
   @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@200;300;400;500;600;700;800&display=swap');

   :root {
     --font-body: "Manrope", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
   }
   ```

2. **Remove local @font-face declarations from `theme.css`**

3. **Uncomment the CSS assets in `config/theme.yml`** (as shown in Option 1, step 3)

#### Option 3: Use System Fonts (Fastest)

1. **Update `custom.css` to remove font-family declarations:**
   ```css
   :root {
     /* Use system fonts instead */
     --font-body: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
   }
   ```

2. **Uncomment the CSS assets in `config/theme.yml`** (as shown in Option 1, step 3)

---

## Custom Styling Not Applied

### Problem

The Entretelas theme looks identical to the default Hummingbird theme. Custom brand colors and styling are not appearing.

### Cause

As of version 0.1.0, custom styling has been intentionally disabled to fix the 500 error issue. The `custom.css` file exists but is not being loaded.

### Solution

Follow one of the options in the [Font Loading Issues](#font-loading-issues) section above to re-enable custom styling after resolving the font file dependencies.

---

## Font Loading Issues

### Problem

Console errors or missing fonts after enabling custom.css:

```
Failed to load resource: net::ERR_FILE_NOT_FOUND
.../assets/css/895e092292d88717adaa.woff2
```

### Cause

The `theme.css` file contains hardcoded references to webpack-generated font file names that don't exist in the repository.

### Solution

Choose one of these approaches:

1. **Rebuild the theme assets** (if you have the source files and build tools):
   ```bash
   npm install
   npm run build
   ```

2. **Manually add font files** following Option 1 in the [Theme Causes 500 Error](#theme-causes-500-error-when-selected) section

3. **Use CDN fonts** following Option 2 in the same section

4. **Use system fonts** following Option 3 in the same section

---

## Additional Resources

- **Theme Documentation:** See [README.md](README.md) for installation and usage instructions
- **Style Guide:** See [PRESTASHOP_THEME_STYLE_GUIDE.md](PRESTASHOP_THEME_STYLE_GUIDE.md) for design specifications
- **PrestaShop Theme Documentation:** https://devdocs.prestashop-project.org/9/themes/
- **PrestaShop Help Center:** https://help-center.prestashop.com/

---

## Version History

### Version 0.1.1 (Current)
- **Status:** Full theme with custom styling enabled
- **Known Issues:** None - theme loads successfully with custom branding
- **Custom Styling:** Enabled using Google Fonts CDN for Manrope font
- **Recommendation:** Ready for production use

### Version 0.1.0
- **Status:** Foundation theme (custom styling disabled)
- **Known Issues:** None - theme loads successfully
- **Custom Styling:** Disabled to prevent 500 errors
- **Recommendation:** Use as-is for testing, or follow solutions above to add custom styling

---

## Getting Help

If you encounter issues not covered in this guide:

1. Check the PrestaShop error logs in `var/logs/`
2. Enable PrestaShop debug mode to see detailed error messages
3. Review the theme's README.md for basic setup instructions
4. Consult PrestaShop documentation at https://devdocs.prestashop-project.org/

---

**Last Updated:** 2026-02-16
**Theme Version:** 0.1.1
