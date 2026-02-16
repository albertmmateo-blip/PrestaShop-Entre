#!/bin/bash

##############################################################################
# Entretelas Theme Packaging Script
# 
# This script creates an importable ZIP file for PrestaShop 9.1.x
# The ZIP structure follows PrestaShop's theme import requirements:
# - One top-level folder named "entretelas/"
# - Contains all theme runtime files (assets/, config/, templates/, etc.)
# - Excludes development artifacts and build files
##############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
THEME_NAME="entretelas"
THEME_SOURCE="$PROJECT_ROOT/themes/$THEME_NAME"
DIST_DIR="$PROJECT_ROOT/dist"
OUTPUT_ZIP="$DIST_DIR/${THEME_NAME}.zip"
TEMP_DIR="$(mktemp -d)"

# Cleanup function
cleanup() {
    if [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
        echo -e "${GREEN}Cleaned up temporary files${NC}"
    fi
}

# Set trap to cleanup on exit
trap cleanup EXIT

echo "============================================="
echo "Entretelas Theme Packaging Script"
echo "============================================="
echo ""

# Check if theme source exists
if [ ! -d "$THEME_SOURCE" ]; then
    echo -e "${RED}ERROR: Theme source directory not found: $THEME_SOURCE${NC}"
    exit 1
fi

# Check if theme.yml exists
if [ ! -f "$THEME_SOURCE/config/theme.yml" ]; then
    echo -e "${RED}ERROR: theme.yml not found in $THEME_SOURCE/config/${NC}"
    exit 1
fi

# Verify theme name in theme.yml
if ! grep -q "name: $THEME_NAME" "$THEME_SOURCE/config/theme.yml"; then
    echo -e "${YELLOW}WARNING: theme.yml does not contain 'name: $THEME_NAME'${NC}"
    echo -e "${YELLOW}Please verify the theme configuration.${NC}"
fi

echo -e "${GREEN}✓${NC} Theme source found: $THEME_SOURCE"
echo -e "${GREEN}✓${NC} Theme configuration validated"
echo ""

# Create dist directory if it doesn't exist
mkdir -p "$DIST_DIR"

# Create temporary packaging directory
PACKAGE_DIR="$TEMP_DIR/$THEME_NAME"
mkdir -p "$PACKAGE_DIR"

echo "Copying theme files..."

# Copy theme files to temporary directory
# Using rsync for better control over exclusions
if command -v rsync &> /dev/null; then
    rsync -a \
        --exclude='.git' \
        --exclude='.github' \
        --exclude='.gitignore' \
        --exclude='.idea' \
        --exclude='.vscode' \
        --exclude='.DS_Store' \
        --exclude='Thumbs.db' \
        --exclude='node_modules' \
        --exclude='*.log' \
        --exclude='*.swp' \
        --exclude='*.swo' \
        --exclude='*~' \
        --exclude='.sass-cache' \
        --exclude='cache' \
        "$THEME_SOURCE/" "$PACKAGE_DIR/"
else
    # Fallback to cp if rsync is not available
    cp -r "$THEME_SOURCE"/* "$PACKAGE_DIR/"
    
    # Clean up excluded items
    find "$PACKAGE_DIR" -type d \( -name '.git' -o -name '.github' -o -name '.idea' -o -name '.vscode' -o -name 'node_modules' -o -name '.sass-cache' -o -name 'cache' \) -exec rm -rf {} + 2>/dev/null || true
    find "$PACKAGE_DIR" -type f \( -name '.DS_Store' -o -name 'Thumbs.db' -o -name '*.log' -o -name '*.swp' -o -name '*.swo' -o -name '*~' -o -name '.gitignore' \) -delete 2>/dev/null || true
fi

echo -e "${GREEN}✓${NC} Theme files copied to temporary directory"
echo ""

# Verify critical files exist
echo "Verifying theme structure..."
CRITICAL_FILES=(
    "$PACKAGE_DIR/config/theme.yml"
    "$PACKAGE_DIR/preview.png"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}ERROR: Critical file missing: ${file#$PACKAGE_DIR/}${NC}"
        exit 1
    fi
done

CRITICAL_DIRS=(
    "$PACKAGE_DIR/assets"
    "$PACKAGE_DIR/config"
    "$PACKAGE_DIR/templates"
)

for dir in "${CRITICAL_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        echo -e "${RED}ERROR: Critical directory missing: ${dir#$PACKAGE_DIR/}${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✓${NC} Theme structure validated"
echo ""

# Create ZIP file
echo "Creating ZIP archive..."

# Remove existing ZIP if it exists
if [ -f "$OUTPUT_ZIP" ]; then
    rm "$OUTPUT_ZIP"
fi

# Create ZIP with the theme folder as the top-level entry
cd "$TEMP_DIR"
if command -v zip &> /dev/null; then
    zip -r "$OUTPUT_ZIP" "$THEME_NAME" -q
else
    echo -e "${RED}ERROR: 'zip' command not found. Please install zip.${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} ZIP archive created"
echo ""

# Get ZIP file size
ZIP_SIZE=$(du -h "$OUTPUT_ZIP" | cut -f1)

# Verify ZIP structure
echo "Verifying ZIP structure..."
ZIP_CONTENTS=$(unzip -l "$OUTPUT_ZIP" | head -10)
if echo "$ZIP_CONTENTS" | grep -q "$THEME_NAME/"; then
    echo -e "${GREEN}✓${NC} ZIP structure is correct (contains $THEME_NAME/ as top-level folder)"
else
    echo -e "${RED}ERROR: ZIP structure is incorrect${NC}"
    exit 1
fi

echo ""
echo "============================================="
echo -e "${GREEN}SUCCESS!${NC} Theme packaged successfully"
echo "============================================="
echo ""
echo "Output: $OUTPUT_ZIP"
echo "Size:   $ZIP_SIZE"
echo ""
echo "Import Instructions:"
echo "1. Go to PrestaShop Back Office"
echo "2. Navigate to: Appearance → Theme & Logo"
echo "3. Click: Add a theme"
echo "4. Select: Import from computer"
echo "5. Upload: $OUTPUT_ZIP"
echo ""
