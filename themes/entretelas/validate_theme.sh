#!/bin/bash
# Simple validation script for Entretelas theme
# Run this to verify theme structure before deployment

THEME_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ERRORS=0

echo "=== Entretelas Theme Validation ==="
echo ""

# Check required directories
echo "Checking required directories..."
REQUIRED_DIRS=("assets" "assets/css" "assets/css/fonts" "assets/js" "config" "templates")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$THEME_DIR/$dir" ]; then
        echo "✓ Directory exists: $dir"
    else
        echo "✗ Missing directory: $dir"
        ((ERRORS++))
    fi
done
echo ""

# Check required files
echo "Checking required files..."
REQUIRED_FILES=("config/theme.yml" "assets/css/custom.css" "assets/css/theme.css" "README.md" "TROUBLESHOOTING.md")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$THEME_DIR/$file" ]; then
        echo "✓ File exists: $file"
    else
        echo "✗ Missing file: $file"
        ((ERRORS++))
    fi
done
echo ""

# Check font files
echo "Checking font files..."
FONT_FILES=("assets/css/fonts/PumpTriD Regular.ttf" "assets/css/fonts/Quagmire Extended Bold.otf")
for font in "${FONT_FILES[@]}"; do
    if [ -f "$THEME_DIR/$font" ]; then
        SIZE=$(stat -f%z "$THEME_DIR/$font" 2>/dev/null || stat -c%s "$THEME_DIR/$font" 2>/dev/null)
        echo "✓ Font file exists: $font (${SIZE} bytes)"
    else
        echo "✗ Missing font file: $font"
        ((ERRORS++))
    fi
done
echo ""

# Check theme.yml configuration
echo "Checking theme.yml configuration..."
if [ -f "$THEME_DIR/config/theme.yml" ]; then
    if grep -q "entretelas-custom" "$THEME_DIR/config/theme.yml"; then
        echo "✓ Custom CSS enabled in theme.yml"
    else
        echo "✗ Custom CSS not enabled in theme.yml"
        ((ERRORS++))
    fi

    if grep -q "version: 0.2.0" "$THEME_DIR/config/theme.yml"; then
        echo "✓ Theme version is 0.2.0"
    else
        echo "⚠ Theme version may not be 0.2.0"
    fi
fi
echo ""

# Check custom.css for font-face declarations
echo "Checking custom.css for font references..."
if [ -f "$THEME_DIR/assets/css/custom.css" ]; then
    if grep -q "@font-face" "$THEME_DIR/assets/css/custom.css"; then
        echo "✓ custom.css contains @font-face declarations"
    else
        echo "✗ custom.css missing @font-face declarations"
        ((ERRORS++))
    fi

    if grep -q "PumpTriD" "$THEME_DIR/assets/css/custom.css"; then
        echo "✓ custom.css references PumpTriD font"
    else
        echo "✗ custom.css missing PumpTriD font reference"
        ((ERRORS++))
    fi

    if grep -q "Quagmire Extended" "$THEME_DIR/assets/css/custom.css"; then
        echo "✓ custom.css references Quagmire Extended font"
    else
        echo "✗ custom.css missing Quagmire Extended font reference"
        ((ERRORS++))
    fi
fi
echo ""

# Check for broken font references
echo "Checking for broken font references..."
if [ -f "$THEME_DIR/assets/css/theme.css" ]; then
    if grep -q "895e092292d88717adaa.woff2" "$THEME_DIR/assets/css/theme.css"; then
        echo "✗ theme.css contains broken Manrope font references"
        ((ERRORS++))
    else
        echo "✓ theme.css does not contain broken font references"
    fi
fi
echo ""

# Summary
echo "==================================="
if [ $ERRORS -eq 0 ]; then
    echo "✓ Theme validation PASSED"
    echo "The Entretelas theme is properly configured."
    exit 0
else
    echo "✗ Theme validation FAILED with $ERRORS error(s)"
    echo "Please fix the errors above before using the theme."
    exit 1
fi
