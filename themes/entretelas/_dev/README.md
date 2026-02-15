# Entretelas Theme Development

This directory contains the source files for the Entretelas PrestaShop theme.

## Structure

```
_dev/
├── css/                      # SCSS source files
│   ├── theme.scss           # Main SCSS entry point
│   └── entretelas-custom.scss  # Custom Entretelas styles
├── js/                       # JavaScript source files
│   ├── theme.js             # Main JS entry point
│   └── theme-base.js        # Base theme functionality
├── package.json              # NPM dependencies
├── webpack.config.js         # Webpack build configuration
├── postcss.config.js         # PostCSS configuration
└── .babelrc                  # Babel configuration

```

## Building the Theme

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn

### Build Commands

```bash
# Install dependencies
npm install

# Build for production
npm run build

# Build for development (with source maps)
npm run dev

# Watch for changes and rebuild automatically
npm run watch
```

### Build Output

Compiled assets are output to `../assets/`:
- `assets/css/theme.css` - Compiled CSS
- `assets/js/theme.js` - Compiled JavaScript

## Development Workflow

1. Make changes to source files in `_dev/`
2. Run `npm run watch` for automatic rebuilding
3. Test changes in PrestaShop
4. Build for production with `npm run build` before committing

## Integration with PrestaShop Build System

The theme integrates with PrestaShop's build system via:

- **Makefile target:** `make front-entretelas`
- **Build script:** `./tools/assets/build.sh front-entretelas`
- **Docker build:** Automatically built on container start

## Customization

### Adding Styles

1. Create new SCSS files in `css/`
2. Import them in `css/theme.scss`
3. Run build

### Adding JavaScript

1. Create new JS files in `js/`
2. Import them in `js/theme.js`
3. Run build

## Notes

- Base theme styles from Hummingbird are inherited
- Custom Entretelas branding is applied via `entretelas-custom.scss`
- The theme follows PrestaShop theme development best practices
