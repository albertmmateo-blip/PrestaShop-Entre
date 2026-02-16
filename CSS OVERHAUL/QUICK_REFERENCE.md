# Entretelas Theme - Quick Reference Card

## 🚀 One-Time Setup (Run Once)

```bash
# 1. Navigate to themes directory
cd /path/to/PrestaShop-Entre/themes

# 2. Clone Hummingbird as entretelas
git clone https://github.com/PrestaShop/hummingbird.git entretelas

# 3. Go into the theme
cd entretelas

# 4. Edit config/theme.yml - change these two lines:
#    name: hummingbird  →  name: entretelas
#    display_name: Hummingbird  →  display_name: Entretelas

# 5. Install dependencies
npm install

# 6. Build theme
npm run build

# 7. Activate in PrestaShop Back Office:
#    Design → Theme & Logo → Entretelas → "Use this theme"
```

## 🔄 Daily Development

```bash
# Navigate to theme
cd /path/to/PrestaShop-Entre/themes/entretelas

# Option 1: Build once (after making changes)
npm run build

# Option 2: Watch mode (auto-rebuild on save)
npm run watch
```

## ✅ Verification

```bash
# Check theme is configured correctly
cat config/theme.yml | grep -E "^name:|^display_name:"

# Should output:
# name: entretelas
# display_name: Entretelas

# Check compiled assets exist
ls -lh assets/css/theme.css
ls -lh assets/js/theme.js

# Both should show file size > 0 KB
```

## 🆘 Troubleshooting

```bash
# Problem: Build fails
cd /path/to/PrestaShop-Entre/themes/entretelas
rm -rf node_modules package-lock.json
npm install
npm run build

# Problem: Theme not appearing in back office
# - Check config/theme.yml syntax (no tabs, correct spacing)
# - Ensure name is "entretelas" not "hummingbird"

# Problem: Theme looks broken
# - Clear PrestaShop cache: Admin → Advanced Parameters → Performance
# - Rebuild: npm run build
# - Check browser console (F12) for errors
```

## 📂 File Structure

```
themes/entretelas/
├── src/scss/          ← Edit SCSS source files here
│   ├── abstract/     ← Variables, mixins (brand colors here)
│   ├── bootstrap/    ← Bootstrap overrides
│   └── prestashop/   ← PrestaShop components, layout, pages
├── src/js/           ← Edit JavaScript/TypeScript here
├── assets/           ← Compiled files (DO NOT edit)
│   ├── css/          ← Generated CSS
│   └── js/           ← Generated JS
├── config/
│   └── theme.yml     ← Theme config (name: entretelas)
└── templates/        ← Smarty templates
```

## 🎨 Making Changes

1. Edit files in `src/scss/` or `src/js/`
2. Run `npm run build` (or use `npm run watch`)
3. Refresh browser (Ctrl+F5 or Cmd+Shift+R)
4. Clear PrestaShop cache if needed

## 📚 Full Documentation

- **Complete Setup Guide**: `CSS OVERHAUL/ENTRETELAS_THEME_SETUP.md`
- **Brand CSS Changes**: `CSS OVERHAUL/PHASE2_BRAND_CUSTOMIZATION.md`
- **Documentation Index**: `CSS OVERHAUL/README.md`
- **Brand Style Guide**: `PRESTASHOP_THEME_STYLE_GUIDE.md`

## ⚠️ Important Notes

- Theme files are in `.gitignore` - not committed to git
- Always edit `src/scss/` files, never `assets/` files
- Always run `npm run build` after changes
- Brand colors are defined in `src/scss/abstract/variables/_colors.scss`
- Bootstrap overrides are in `src/scss/bootstrap/overrides/variables/`
- See `CSS OVERHAUL/PHASE2_BRAND_CUSTOMIZATION.md` for brand CSS details

---

**Need Help?** Read the full documentation in `CSS OVERHAUL/ENTRETELAS_THEME_SETUP.md`
