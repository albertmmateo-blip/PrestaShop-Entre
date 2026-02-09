#!/bin/bash

# PrestaShop Installation Health Check Script
# This script performs a comprehensive diagnosis of your PrestaShop installation

echo "=================================================="
echo "PrestaShop Installation Health Check"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC} - $2"
    else
        echo -e "${RED}✗ FAIL${NC} - $2"
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠ WARNING${NC} - $1"
}

echo "1. Checking PHP Configuration..."
echo "   PHP Version: $(php -v | head -n 1)"

# Check if PrestaShop root exists
if [ -f "config/defines.inc.php" ]; then
    print_status 0 "PrestaShop installation found"
else
    print_status 1 "PrestaShop installation not found - run this script from PrestaShop root"
    exit 1
fi

echo ""
echo "2. Checking Development Mode Settings..."

# Check _PS_MODE_DEV_ setting
if grep -q "define('_PS_MODE_DEV_', false)" config/defines.inc.php; then
    print_status 0 "Developer mode is DISABLED (Production mode)"
elif grep -q "define('_PS_MODE_DEV_', true)" config/defines.inc.php; then
    print_status 1 "Developer mode is ENABLED (Will cause slow performance)"
    echo "   → Fix: Edit config/defines.inc.php and set _PS_MODE_DEV_ to false"
else
    print_warning "Could not determine developer mode setting"
fi

# Check debug profiling
if grep -q "define('_PS_DEBUG_PROFILING_', false)" config/defines.inc.php; then
    print_status 0 "Debug profiling is DISABLED"
elif grep -q "define('_PS_DEBUG_PROFILING_', true)" config/defines.inc.php; then
    print_status 1 "Debug profiling is ENABLED (Adds overhead)"
    echo "   → Fix: Edit config/defines.inc.php and set _PS_DEBUG_PROFILING_ to false"
fi

# Check compatibility warnings
if grep -q "define('_PS_DISPLAY_COMPATIBILITY_WARNING_', false)" config/defines.inc.php; then
    print_status 0 "Compatibility warnings are DISABLED"
elif grep -q "define('_PS_DISPLAY_COMPATIBILITY_WARNING_', true)" config/defines.inc.php; then
    print_status 1 "Compatibility warnings are ENABLED (Adds overhead)"
    echo "   → Fix: Edit config/defines.inc.php and set _PS_DISPLAY_COMPATIBILITY_WARNING_ to false"
fi

echo ""
echo "3. Checking Admin Folders..."

# Check admin folders
if [ -d "admin-dev" ]; then
    print_warning "Development admin folder 'admin-dev' exists"
    echo "   → For production, use 'admin-prod' instead"
fi

if [ -d "admin-prod" ]; then
    print_status 0 "Production admin folder 'admin-prod' exists"
    if [ -f "admin-prod/index.php" ]; then
        print_status 0 "admin-prod/index.php exists"
    else
        print_status 1 "admin-prod/index.php is missing"
    fi
else
    print_status 1 "Production admin folder 'admin-prod' does not exist"
    echo "   → Create it for optimized admin access"
fi

echo ""
echo "4. Checking Cache Directories..."

# Check cache directories
if [ -d "var/cache" ]; then
    print_status 0 "Cache directory exists"
    
    if [ -w "var/cache" ]; then
        print_status 0 "Cache directory is writable"
    else
        print_status 1 "Cache directory is not writable"
        echo "   → Fix: chmod -R 777 var/cache/"
    fi
else
    print_status 1 "Cache directory does not exist"
    echo "   → Fix: mkdir -p var/cache && chmod -R 777 var/cache"
fi

if [ -d "var/logs" ]; then
    if [ -w "var/logs" ]; then
        print_status 0 "Logs directory exists and is writable"
    else
        print_status 1 "Logs directory is not writable"
        echo "   → Fix: chmod -R 777 var/logs/"
    fi
else
    print_warning "Logs directory does not exist"
    echo "   → Fix: mkdir -p var/logs && chmod -R 777 var/logs"
fi

echo ""
echo "5. Checking Install Directory..."

if [ -d "install-dev" ]; then
    print_warning "Installation directory 'install-dev' still exists"
    echo "   → For security, delete it after installation is complete"
    echo "   → Command: rm -rf install-dev/"
else
    print_status 0 "Installation directory has been removed (secure)"
fi

echo ""
echo "6. Checking File Permissions..."

# Check if important files are readable
if [ -r "config/config.inc.php" ]; then
    print_status 0 "config/config.inc.php is readable"
else
    print_status 1 "config/config.inc.php is not readable"
fi

if [ -r "config/defines.inc.php" ]; then
    print_status 0 "config/defines.inc.php is readable"
else
    print_status 1 "config/defines.inc.php is not readable"
fi

echo ""
echo "7. Checking Environment Configuration..."

if [ -f ".env" ]; then
    print_status 0 ".env file exists"
    
    # Check for front container setting
    if grep -q "PS_FF_FRONT_CONTAINER_V2" .env; then
        CONTAINER_V2=$(grep "PS_FF_FRONT_CONTAINER_V2" .env | cut -d'=' -f2)
        echo "   → Front Container V2: $CONTAINER_V2"
    fi
else
    print_warning ".env file not found"
fi

echo ""
echo "=================================================="
echo "Summary & Recommendations"
echo "=================================================="
echo ""
echo "For optimal performance:"
echo "1. Ensure developer mode is DISABLED"
echo "2. Use the 'admin-prod' folder for admin access"
echo "3. Clear cache after making changes: rm -rf var/cache/prod/* var/cache/dev/*"
echo "4. Rename 'admin-prod' to something unique for security"
echo "5. Delete 'install-dev' folder if installation is complete"
echo "6. Set proper file permissions (see PRODUCTION_SETUP.md)"
echo ""
echo "For detailed instructions, see: PRODUCTION_SETUP.md"
echo "=================================================="
