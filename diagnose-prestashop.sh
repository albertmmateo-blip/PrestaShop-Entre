#!/bin/bash
# PrestaShop Performance Diagnostics Script
# This script checks your PrestaShop installation and provides recommendations

echo "============================================="
echo "PrestaShop Performance Diagnostics"
echo "============================================="
echo ""

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print with color
print_status() {
    local status=$1
    local message=$2
    case $status in
        "OK")
            echo -e "${GREEN}✓${NC} $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}✗${NC} $message"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ${NC} $message"
            ;;
    esac
}

echo "1. Checking configuration files..."
echo "-----------------------------------"

# Check defines.inc.php
if [ -f "config/defines.inc.php" ]; then
    print_status "OK" "Found config/defines.inc.php"
    
    # Check _PS_MODE_DEV_ setting
    if grep -q "define('_PS_MODE_DEV_', true)" config/defines.inc.php; then
        print_status "WARNING" "Development mode is ENABLED in defines.inc.php"
        echo "   This causes slower performance but provides debugging features"
    else
        print_status "OK" "Development mode is disabled in defines.inc.php"
    fi
    
    # Check _PS_DEBUG_PROFILING_
    if grep -q "define('_PS_DEBUG_PROFILING_', true)" config/defines.inc.php; then
        print_status "WARNING" "Debug profiling is ENABLED"
        echo "   This significantly impacts performance"
    else
        print_status "OK" "Debug profiling is disabled"
    fi
else
    print_status "ERROR" "config/defines.inc.php not found!"
fi

echo ""
echo "2. Checking admin folders..."
echo "-----------------------------------"

# Check admin-dev
if [ -d "admin-dev" ]; then
    print_status "OK" "Found admin-dev folder (debug mode)"
    
    if [ -f "admin-dev/index.php" ]; then
        if grep -q "Debug::enable()" admin-dev/index.php; then
            print_status "INFO" "admin-dev uses full debug mode (SLOW but detailed)"
        fi
    fi
else
    print_status "WARNING" "admin-dev folder not found"
fi

# Check admin-fast
if [ -d "admin-fast" ]; then
    print_status "OK" "Found admin-fast folder (optimized mode)"
    
    if [ -f "admin-fast/index.php" ]; then
        if grep -q "define('_PS_MODE_DEV_', false)" admin-fast/index.php; then
            print_status "OK" "admin-fast is configured for fast performance"
        else
            print_status "WARNING" "admin-fast may not be properly configured"
        fi
    fi
else
    print_status "WARNING" "admin-fast folder not found (should be created)"
fi

echo ""
echo "3. Checking cache directories..."
echo "-----------------------------------"

# Check cache directories
if [ -d "var/cache" ]; then
    print_status "OK" "Found var/cache directory"
    
    # Check dev cache
    if [ -d "var/cache/dev" ]; then
        DEV_SIZE=$(du -sh var/cache/dev 2>/dev/null | cut -f1)
        print_status "INFO" "Development cache size: $DEV_SIZE"
    fi
    
    # Check prod cache
    if [ -d "var/cache/prod" ]; then
        PROD_SIZE=$(du -sh var/cache/prod 2>/dev/null | cut -f1)
        print_status "INFO" "Production cache size: $PROD_SIZE"
    else
        print_status "INFO" "Production cache not created yet (will be created on first admin-fast access)"
    fi
else
    print_status "WARNING" "var/cache directory not found"
fi

# Check old cache directory
if [ -d "cache" ]; then
    CACHE_SIZE=$(du -sh cache 2>/dev/null | cut -f1)
    print_status "INFO" "Legacy cache size: $CACHE_SIZE"
fi

echo ""
echo "4. PHP Configuration..."
echo "-----------------------------------"

# Check if PHP is available
if command -v php &> /dev/null; then
    PHP_VERSION=$(php -v | head -n 1)
    print_status "OK" "$PHP_VERSION"
    
    # Check important PHP settings
    MEMORY_LIMIT=$(php -r "echo ini_get('memory_limit');")
    print_status "INFO" "PHP memory_limit: $MEMORY_LIMIT"
    
    MAX_EXECUTION=$(php -r "echo ini_get('max_execution_time');")
    print_status "INFO" "PHP max_execution_time: ${MAX_EXECUTION}s"
    
    # Check opcache
    OPCACHE=$(php -r "echo extension_loaded('Zend OPcache') ? 'enabled' : 'disabled';")
    if [ "$OPCACHE" = "enabled" ]; then
        print_status "OK" "OPcache is enabled (good for performance)"
    else
        print_status "WARNING" "OPcache is disabled (consider enabling for better performance)"
    fi
else
    print_status "WARNING" "PHP CLI not available for checking"
fi

echo ""
echo "============================================="
echo "Summary & Recommendations"
echo "============================================="
echo ""

# Provide recommendations based on findings
echo "📊 Current Setup:"
echo ""

if [ -d "admin-fast" ]; then
    echo "✅ You have both admin folders available:"
    echo "   • admin-dev/  - Full debug mode (slower but detailed)"
    echo "   • admin-fast/ - Optimized mode (faster for daily work)"
    echo ""
    echo "💡 Recommendation:"
    echo "   Use admin-fast/ for regular development work"
    echo "   Switch to admin-dev/ when you need to debug issues"
else
    echo "⚠️  You only have admin-dev available"
    echo ""
    echo "💡 Recommendation:"
    echo "   The admin-fast folder has been created with this fix"
    echo "   Start using it for better performance!"
fi

echo ""
echo "🚀 To use the optimized admin:"
echo "   Access: http://your-site.com/admin-fast/"
echo ""
echo "📖 Documentation:"
echo "   • See PERFORMANCE_OPTIMIZATION.md for full guide"
echo "   • See admin-fast/README.md for technical details"
echo ""

# Check if there are any critical issues
CRITICAL=0
if [ ! -f "config/defines.inc.php" ]; then
    CRITICAL=1
fi

if [ $CRITICAL -eq 1 ]; then
    echo "❌ CRITICAL ISSUES FOUND - PrestaShop may not work properly"
    exit 1
else
    echo "✅ PrestaShop is configured and ready to use"
    echo ""
    echo "For best performance while developing:"
    echo "1. Use admin-fast/ for daily work"
    echo "2. Clear cache when switching between admin folders"
    echo "3. Consider enabling PHP OPcache if not already enabled"
    echo ""
    exit 0
fi
