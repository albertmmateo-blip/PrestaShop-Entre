# Entretelas Theme

Entretelas is a PrestaShop 9.1.x compatible theme based on the Hummingbird theme. This theme is designed to be imported into PrestaShop via the Back Office theme import feature.

## Theme Information

- **Name:** entretelas
- **Display Name:** Entretelas
- **Version:** 0.1.0
- **Compatibility:** PrestaShop 9.1.0 and above
- **Framework:** Bootstrap v5.2.0
- **Base Theme:** Hummingbird

## Features

This theme includes:
- Full PrestaShop 9.1.x compatibility
- Bootstrap 5.2.0 framework
- Multiple layout options (Full Width, Three Columns, Two Columns with left/right sidebars)
- Responsive design
- All standard PrestaShop theme features

## Installation

### Method 1: Import via PrestaShop Back Office (Recommended)

1. **Generate the ZIP file** (see "Generating the ZIP Package" section below)

2. **Access PrestaShop Back Office:**
   - Go to your PrestaShop administration panel
   - Navigate to: **Appearance → Theme & Logo**

3. **Import the theme:**
   - Click: **Add a theme**
   - Select: **Import from computer**
   - Upload: `dist/entretelas.zip`
   - Click: **Save**

4. **Activate the theme:**
   - After import, the theme will appear in your themes list
   - Click: **Use this theme** to activate it

## Generating the ZIP Package

The theme must be packaged as a ZIP file before it can be imported into PrestaShop. Use one of the provided packaging scripts:

### Linux / macOS / WSL

```bash
./scripts/package-entretelas.sh
```

### Windows PowerShell

```powershell
.\scripts\package-entretelas.ps1
```

### Output

Both scripts will:
- Validate the theme structure
- Create a properly formatted ZIP file at `dist/entretelas.zip`
- Verify the ZIP structure meets PrestaShop requirements
- Display the output location and file size

The generated ZIP will contain:
```
entretelas.zip
  └── entretelas/
      ├── assets/
      │   ├── css/
      │   └── js/
      ├── config/
      │   └── theme.yml
      ├── templates/
      ├── preview.png
      └── ... (other theme files)
```

## Theme Structure

```
themes/entretelas/
├── assets/              # CSS and JavaScript assets
│   ├── css/
│   │   └── theme.css
│   └── js/
│       └── theme.js
├── config/              # Theme configuration
│   └── theme.yml        # Main theme configuration file
├── templates/           # Twig templates
│   ├── _partials/
│   ├── catalog/
│   ├── checkout/
│   ├── cms/
│   ├── customer/
│   ├── errors/
│   ├── contact.tpl
│   └── index.tpl
├── preview.png          # Theme preview image
└── README.md           # This file
```

## Configuration

The theme configuration is located at `config/theme.yml`. This file defines:
- Theme metadata (name, version, author)
- Compatibility information
- Available layouts
- Asset loading
- Global settings
- Image types
- Theme-specific settings

## Development Notes

### Current Status

This is version **0.1.0** - an initial foundation theme based on Hummingbird with PrestaShop 9.1.x compatibility.

**What's included:**
- Complete theme structure based on Hummingbird
- Updated theme.yml with Entretelas identity
- PrestaShop 9.1.x compatibility
- Packaging scripts for easy distribution
- ✅ **Fixed:** Theme now loads without 500 errors

**What's NOT included yet:**
- Custom design changes (custom styling temporarily disabled to prevent errors)
- Custom branding colors and fonts (see TROUBLESHOOTING.md to re-enable)
- Additional features beyond base Hummingbird

**Note:** Custom CSS styling has been temporarily disabled in this version to resolve a 500 error caused by missing font files. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for details on how to re-enable custom styling.

### Future Development

Future versions will include:
- Custom design and styling
- Branding updates
- Enhanced features
- Additional customization options

## Troubleshooting

⚠️ **For detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)**

### Common Issues

#### Theme Causes 500 Error When Selected

**Status:** ✅ **FIXED** in version 0.1.0

If you're using an older version and experiencing 500 errors when selecting this theme, see the [TROUBLESHOOTING.md](TROUBLESHOOTING.md#theme-causes-500-error-when-selected) guide for detailed solutions.

### Import Fails

If the theme import fails:

1. **Verify ZIP structure:**
   - Open the ZIP file and ensure it contains a single top-level folder named `entretelas/`
   - The theme.yml file should be at `entretelas/config/theme.yml` within the ZIP

2. **Check theme.yml:**
   - Ensure `name: entretelas` is set in the theme.yml file
   - Verify the compatibility settings include your PrestaShop version

3. **Review PrestaShop logs:**
   - Check `var/logs/` in your PrestaShop installation for error messages

### Theme Doesn't Appear After Import

1. Clear PrestaShop cache:
   - Go to: **Advanced Parameters → Performance**
   - Click: **Clear cache**

2. Verify file permissions:
   - Ensure the web server has read access to all theme files

## Support

For issues or questions:
- Check the PrestaShop documentation: https://devdocs.prestashop-project.org/9/themes/
- Review PrestaShop Help Center: https://help-center.prestashop.com/

## License

This theme is based on PrestaShop's Hummingbird theme and follows the same licensing terms as PrestaShop.

## Credits

- **Base Theme:** Hummingbird by PrestaShop Team
- **Framework:** Bootstrap 5.2.0
- **Compatible with:** PrestaShop 9.1.x

---

**Note:** This README describes version 0.1.0, which is a minimal clone of Hummingbird with updated metadata. Custom design and styling changes will be implemented in future versions.
