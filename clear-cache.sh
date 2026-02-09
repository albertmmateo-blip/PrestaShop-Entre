#!/bin/bash
# PrestaShop Cache Cleaner
# This script clears PrestaShop cache directories

echo "============================================="
echo "PrestaShop Cache Cleaner"
echo "============================================="
echo ""

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "Clearing PrestaShop cache..."
echo ""

# Clear Symfony dev cache
if [ -d "var/cache/dev" ]; then
    echo -e "${BLUE}[*]${NC} Clearing development cache (var/cache/dev)..."
    rm -rf var/cache/dev/*
    echo -e "${GREEN}    Done!${NC}"
else
    echo -e "${YELLOW}[i]${NC} Development cache folder not found"
fi

# Clear Symfony prod cache
if [ -d "var/cache/prod" ]; then
    echo -e "${BLUE}[*]${NC} Clearing production cache (var/cache/prod)..."
    rm -rf var/cache/prod/*
    echo -e "${GREEN}    Done!${NC}"
else
    echo -e "${YELLOW}[i]${NC} Production cache folder not found"
fi

# Clear Smarty compiled templates
if [ -d "cache/smarty/compile" ]; then
    echo -e "${BLUE}[*]${NC} Clearing Smarty compiled templates..."
    find cache/smarty/compile -type f -name "*.php" -delete 2>/dev/null
    echo -e "${GREEN}    Done!${NC}"
else
    echo -e "${YELLOW}[i]${NC} Smarty compile folder not found"
fi

# Clear Smarty cache
if [ -d "cache/smarty/cache" ]; then
    echo -e "${BLUE}[*]${NC} Clearing Smarty cache..."
    find cache/smarty/cache -type f -delete 2>/dev/null
    echo -e "${GREEN}    Done!${NC}"
else
    echo -e "${YELLOW}[i]${NC} Smarty cache folder not found"
fi

echo ""
echo "============================================="
echo -e "${GREEN}Cache cleared successfully!${NC}"
echo "============================================="
echo ""
echo "Note: First page load may be slower as cache rebuilds"
echo ""
