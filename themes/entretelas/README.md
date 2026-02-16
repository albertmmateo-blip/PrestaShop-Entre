# Entretelas Theme for PrestaShop 9.1.0

A custom PrestaShop theme based on Hummingbird, featuring the Entretelas brand identity with warm earthy colors and traditional Spanish haberdashery aesthetic.

## Quick Start

### Activation
1. Navigate to **Design > Theme & Logo** in PrestaShop admin
2. Find "Entretelas" theme in the list
3. Click **"Use this theme"**
4. Clear cache: `php bin/console cache:clear`

### Theme Information
- **Name:** Entretelas
- **Version:** 1.0.1
- **Base Theme:** Hummingbird (PrestaShop 9.1.0)
- **Framework:** Bootstrap 5.2.0
- **Compatibility:** PrestaShop 8.1.0+

## Features

### Design System
- **Primary Color:** Deep Brown (#542e26)
- **Secondary Color:** Vibrant Orange (#e87722)
- **Accent Color:** Bold Red (#cb2c30)
- **Background:** Warm Tan (#f1e5d6)

### Typography
- **Display Font:** Pump Trid (hero text)
- **Heading Font:** Quagmire Extended Bold (uppercase)
- **Body Font:** System sans-serif

### Styling Features
- Warm, earthy color palette
- Traditional haberdashery aesthetic
- Custom brand fonts
- Rounded corners and smooth transitions
- Product card hover effects
- Brand-colored buttons and links
- Responsive design (mobile-friendly)

## File Structure

```
entretelas/
├── assets/
│   ├── css/
│   │   ├── theme.css                    # Base Hummingbird styles
│   │   └── entretelas-custom.css        # Custom Entretelas styles
│   ├── fonts/
│   │   ├── PumpTriD Regular.ttf         # Display font
│   │   └── Quagmire Extended Bold.otf   # Heading font
│   └── js/
│       └── theme.js                     # Base theme JavaScript
├── config/
│   └── theme.yml                        # Theme configuration
├── templates/                           # Smarty templates (from Hummingbird)
│   ├── _partials/
│   ├── catalog/
│   ├── checkout/
│   ├── cms/
│   ├── customer/
│   ├── errors/
│   └── ...
├── preview.png                          # Theme preview image
├── README.md                            # This file
└── THEME_IMPLEMENTATION_NOTES.md        # Detailed technical documentation
```

## Customization

### Changing Colors
Edit `assets/css/entretelas-custom.css` and modify the CSS variables:

```css
:root {
  --entretelas-brown: #542e26;      /* Your primary color */
  --entretelas-orange: #e87722;     /* Your secondary color */
  --entretelas-red: #cb2c30;        /* Your accent color */
  --entretelas-soft-tan: #f1e5d6;   /* Your background color */
}
```

After changes, clear cache:
```bash
php bin/console cache:clear
```

### Adding Custom CSS
1. Edit `assets/css/entretelas-custom.css`
2. Add your custom styles at the end of the file
3. Clear PrestaShop cache
4. Refresh browser (Ctrl+Shift+R)

### Modifying Templates
Templates are located in `templates/` directory. Edit `.tpl` files using Smarty syntax.

⚠️ **Warning:** Template changes can break functionality. Test thoroughly!

## Maintenance

### Updating Styles
1. Edit `assets/css/entretelas-custom.css`
2. Run: `php bin/console cache:clear`
3. Refresh browser

### Switching Themes
You can switch between themes anytime:
1. Go to **Design > Theme & Logo**
2. Click **"Use this theme"** on desired theme
3. Your Entretelas customizations remain saved

### Troubleshooting

**Styles not applying:**
```bash
php bin/console cache:clear
php bin/console prestashop:generate:assets
```

**Fonts not loading:**
- Check browser DevTools Network tab for 404 errors
- Verify fonts exist in `assets/fonts/` directory
- Check file permissions (644 for files, 755 for directories)

**Theme not appearing in admin:**
- Verify `config/theme.yml` exists
- Check file permissions
- Clear PrestaShop cache

## Browser Compatibility

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- Custom CSS: ~485 lines
- Custom fonts: ~114KB total
- No external dependencies
- CSS-only customization (no JavaScript overhead)

## Documentation

- **Technical Details:** See `THEME_IMPLEMENTATION_NOTES.md`
- **Design System:** See `../prestashop-aesthetic-package/documentation/`
- **PrestaShop Docs:** https://devdocs.prestashop-project.org/

## Testing Checklist

Before deploying to production:

- [ ] Homepage loads correctly
- [ ] Category pages display products
- [ ] Product detail pages work
- [ ] Add to cart functions
- [ ] Checkout process completes
- [ ] User login/registration works
- [ ] Search functionality works
- [ ] Mobile responsive design works
- [ ] All fonts load correctly
- [ ] No console errors in browser
- [ ] Page load time acceptable (<3s)

## Support

- **PrestaShop Community:** https://www.prestashop.com/forums/
- **Theme Documentation:** See `THEME_IMPLEMENTATION_NOTES.md`
- **Issue Tracking:** Use repository issue tracker

## Credits

- **Base Theme:** Hummingbird by PrestaShop Team
- **Custom Design:** Entretelas brand aesthetic
- **Framework:** Bootstrap 5.2.0
- **Fonts:** 
  - Pump Trid
  - Quagmire Extended Bold

## License

This theme is proprietary to Entretelas business. Not authorized for redistribution.

## Changelog

### Version 1.0.1 (2026-02-16)
- **CRITICAL FIX:** Added missing templates directory structure from full Hummingbird theme
- Added all 160 template files (previously only had 28 minimal templates)
- Added critical `templates/layouts/` directory with 6 layout files:
  - layout-both-columns.tpl
  - layout-content-only.tpl
  - layout-error.tpl
  - layout-full-width.tpl
  - layout-left-column.tpl
  - layout-right-column.tpl
- Added missing partial templates and components
- **Fixes HTTP 500 error** that occurred when theme was activated
- Theme now fully functional with complete template structure

### Version 1.0.0 (2026-02-15)
- Initial release
- Based on Hummingbird theme structure
- Custom Entretelas brand colors and typography
- Integrated custom fonts (Pump Trid, Quagmire)
- Comprehensive component styling
- Responsive design
- Mobile-optimized
