# 🎯 Standalone Theme Approach - Visual Guide

## PrestaShop Theme Architecture

### Before (What You Have Now)
```
/prestashop/themes/
├── classic/          # Legacy theme
└── hummingbird/      # PS 9.1.0 default theme
```

### After (What You'll Create)
```
/prestashop/themes/
├── classic/          # Legacy theme (UNTOUCHED)
├── hummingbird/      # PS 9.1.0 default (UNTOUCHED)
└── entretelas/       # YOUR NEW THEME ✨
    ├── assets/
    │   ├── css/
    │   │   ├── theme.css              # Base styles (from Hummingbird)
    │   │   └── entretelas-custom.css  # YOUR CUSTOMIZATIONS
    │   ├── fonts/
    │   │   ├── PumpTriD Regular.ttf
    │   │   └── Quagmire Extended Bold.otf
    │   ├── js/
    │   └── img/
    ├── templates/
    │   ├── catalog/
    │   ├── checkout/
    │   ├── cms/
    │   └── _partials/
    └── config/
        └── theme.yml  # name: entretelas
```

---

## How Theme Switching Works

### In PrestaShop Admin: Design > Theme & Logo

```
┌─────────────────────────────────────────────────────┐
│  Available Themes                                   │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  │   Classic    │  │ Hummingbird  │  │  Entretelas  │
│  │              │  │              │  │   (Active)   │
│  │  [Preview]   │  │  [Preview]   │  │  [Preview]   │
│  │              │  │              │  │              │
│  │ [Use Theme]  │  │ [Use Theme]  │  │  ✓ Active    │
│  └──────────────┘  └──────────────┘  └──────────────┘
│                                                      │
│  You can switch between themes with one click!      │
└─────────────────────────────────────────────────────┘
```

---

## Development Workflow

### Safe Development Process

```
1. Start with Hummingbird (current state)
   ↓
2. Create Entretelas theme (copy Hummingbird)
   ↓
3. Activate Entretelas theme
   ↓
4. Make customizations in Entretelas
   ↓
5. Test thoroughly
   ↓
6. [IF ISSUE] → Switch back to Hummingbird instantly
   ↓
7. [IF SUCCESS] → Continue with Entretelas
```

### Rollback Safety

```
Problem with Entretelas?
   ↓
Go to: Design > Theme & Logo
   ↓
Click "Use this theme" on Hummingbird
   ↓
✓ Instant rollback!
   ↓
Fix issues in Entretelas
   ↓
Switch back when ready
```

---

## File Modifications Scope

### ❌ NEVER Touch These:
```
/themes/classic/          # Don't modify
/themes/hummingbird/      # Don't modify
/modules/                 # Don't modify (unless module-specific)
/classes/                 # Don't modify (core files)
/controllers/             # Don't modify (core files)
```

### ✅ ONLY Modify These:
```
/themes/entretelas/       # YOUR theme - modify freely!
  ├── assets/css/         # Add custom CSS here
  ├── assets/fonts/       # Add custom fonts here
  ├── templates/          # Customize templates (carefully)
  └── config/theme.yml    # Theme configuration
```

---

## Creation Commands

### Quick Setup Script

```bash
#!/bin/bash
# Create Entretelas theme from Hummingbird

# Navigate to themes directory
cd /path/to/prestashop/themes/

# Create new theme by copying Hummingbird
echo "Creating Entretelas theme..."
cp -r hummingbird entretelas

# Update theme name in config
cd entretelas
echo "Updating theme configuration..."
sed -i 's/name: hummingbird/name: entretelas/g' config/theme.yml
sed -i 's/display_name: Hummingbird/display_name: Entretelas/g' config/theme.yml

# Create custom CSS file
echo "Creating custom CSS file..."
touch assets/css/entretelas-custom.css

# Create fonts directory
echo "Creating fonts directory..."
mkdir -p assets/fonts

echo "✓ Entretelas theme created!"
echo "Next steps:"
echo "1. Copy fonts to themes/entretelas/assets/fonts/"
echo "2. Edit assets/css/entretelas-custom.css"
echo "3. Activate theme in PrestaShop admin"
```

---

## Benefits of Standalone Theme

### 1. Safety
- ✅ Original themes remain untouched
- ✅ Can switch back anytime
- ✅ No risk to working installation
- ✅ Test without affecting live site

### 2. Maintainability
- ✅ Updates to PrestaShop don't affect your theme
- ✅ Can update Hummingbird independently
- ✅ Clear separation of custom code
- ✅ Easy to version control

### 3. Flexibility
- ✅ Switch themes for comparison
- ✅ Multiple themes for different stores
- ✅ A/B testing different designs
- ✅ Seasonal theme changes

### 4. Professional
- ✅ Industry best practice
- ✅ Clean project structure
- ✅ Easy for other developers to understand
- ✅ PrestaShop-recommended approach

---

## Comparison: Child Theme vs Standalone Theme

### Child Theme (Inherits from Parent)
```yaml
# theme.yml
name: entretelas-child
parent: hummingbird   # Inherits from Hummingbird
```
- ✅ Smaller file size (only overrides)
- ❌ Depends on parent theme
- ❌ Parent updates may break child
- ⚠️ More complex to manage

### Standalone Theme (Independent) ⭐ RECOMMENDED
```yaml
# theme.yml
name: entretelas
# No parent - fully independent
```
- ✅ Fully independent
- ✅ Complete control
- ✅ Parent updates don't affect it
- ✅ Easier to understand and modify
- ⚠️ Larger file size (full copy)

**For this project, we use STANDALONE theme approach.**

---

## Version Control with Git

### .gitignore for Theme Development

```gitignore
# In /themes/entretelas/.gitignore

# Compiled/minified assets
/assets/css/*.min.css
/assets/js/*.min.js

# Cache files
/cache/
/config/cache/

# Temporary files
*.tmp
*.bak
*~

# OS files
.DS_Store
Thumbs.db
```

### Recommended Git Structure

```
prestashop/
├── themes/
│   └── entretelas/        # Track this in Git
│       ├── .git/
│       ├── .gitignore
│       ├── assets/
│       ├── templates/
│       └── config/
```

### Sample Commits

```bash
# Initial theme creation
git init
git add .
git commit -m "Initial Entretelas theme from Hummingbird base"

# Color customizations
git add assets/css/entretelas-custom.css
git commit -m "Add Entretelas color palette"

# Font integration
git add assets/fonts/
git add assets/css/entretelas-custom.css
git commit -m "Add custom fonts (Pump Trid, Quagmire)"

# Navigation styling
git add assets/css/entretelas-custom.css
git commit -m "Style navigation with brand colors"
```

---

## Testing Workflow

### Development Cycle

```
┌─────────────────────────────────────────┐
│ 1. Make changes in Entretelas theme     │
├─────────────────────────────────────────┤
│ 2. Clear cache (bin/console cache:clear)│
├─────────────────────────────────────────┤
│ 3. Refresh browser (Ctrl+Shift+R)       │
├─────────────────────────────────────────┤
│ 4. Test functionality                    │
├─────────────────────────────────────────┤
│ 5. Issues? → Fix and repeat             │
│    Working? → Continue customizing       │
└─────────────────────────────────────────┘
```

### Comparison Testing

```
Test Feature in Hummingbird:
  ↓
Switch to Entretelas:
  ↓
Test same feature:
  ↓
Compare results:
  ↓
Does Entretelas work as well as Hummingbird?
  ├─ YES → Continue
  └─ NO → Debug and fix
```

---

## Summary

### What You'll Have

```
Three Independent Themes:
1. Classic (PrestaShop legacy)
2. Hummingbird (PrestaShop 9.1.0 default)
3. Entretelas (Your custom theme with brand identity)

All themes available at any time!
Switch between them with ONE CLICK in admin panel!
```

### Key Principles

1. **Never modify Hummingbird or Classic**
2. **All customizations go in Entretelas theme**
3. **Test thoroughly before committing**
4. **Keep ability to switch back**
5. **Version control your theme**

---

## Next Steps

1. ✅ Read full implementation guide
2. ✅ Create Entretelas theme (copy Hummingbird)
3. ✅ Configure theme.yml
4. ✅ Activate in PrestaShop admin
5. ✅ Start with color customizations
6. ✅ Add fonts
7. ✅ Customize components
8. ✅ Test thoroughly
9. ✅ Deploy when ready

**You're creating a professional, maintainable theme structure! 🎨✨**

---

*See IMPLEMENTATION_GUIDE.md for detailed step-by-step instructions.*
