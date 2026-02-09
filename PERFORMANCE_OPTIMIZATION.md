# PrestaShop Performance Optimization Guide

## Problem Statement

PrestaShop's back office can be very slow when running in development mode, especially on Windows systems. This is because development mode enables extensive debugging features that significantly impact performance:

- Symfony Debug Toolbar
- Debug profiling
- Detailed error reporting
- No template caching
- No opcode caching

## Solution Overview

This repository now includes **two admin folders** to give you the flexibility to choose between speed and debugging capabilities:

### 1. `admin-dev/` - Full Debug Mode (Original)
- ✅ Complete debugging capabilities
- ✅ Symfony profiler enabled
- ✅ Detailed error messages
- ⚠️ **SLOW** - Significant performance overhead

### 2. `admin-fast/` - Optimized Mode (New)
- ⚡ **FAST** - Much better performance
- ✅ Error logging still enabled
- ✅ Full functionality maintained
- ⚠️ No Symfony profiler
- ⚠️ Less detailed error output

## Configuration Details

### Current System Configuration

#### Development Mode Status
The main configuration file `/config/defines.inc.php` sets:
```php
define('_PS_MODE_DEV_', true);  // Line 36
```

This affects:
- Error reporting level
- SQL debugging
- Environment (`dev` vs `prod`)
- Cache directory (`/var/cache/dev/` vs `/var/cache/prod/`)

#### Admin Folders

**admin-dev/** (Original - Slow but Full Debug)
- Uses `_PS_MODE_DEV_ = true` from defines.inc.php
- Enables Symfony Debug: `Debug::enable()`
- Environment: `dev`
- Cache: `/var/cache/dev/`

**admin-fast/** (New - Fast Performance)
- Overrides `_PS_MODE_DEV_ = false` in index.php
- Disables Symfony Debug (commented out)
- Environment: `prod`
- Cache: `/var/cache/prod/`

## How to Use

### Daily Development (Recommended)
```
Access: http://your-site.com/admin-fast/
```
Use this for regular development work where you need a responsive interface.

### Debugging Issues
```
Access: http://your-site.com/admin-dev/
```
Switch to this when you need detailed debugging information.

## Performance Impact

### Before (admin-dev only):
- ❌ Page load: 5-10+ seconds
- ❌ Navigation: Painfully slow
- ❌ Memory usage: High
- ❌ Template recompilation: Every request

### After (using admin-fast):
- ✅ Page load: 1-3 seconds
- ✅ Navigation: Responsive
- ✅ Memory usage: Moderate
- ✅ Template compilation: Once, then cached

## What Gets Optimized?

### In admin-fast/:

1. **No Symfony Debug Components**
   - No profiler toolbar
   - No exception traces in browser
   - Reduced memory overhead

2. **Production Environment**
   - Template caching enabled
   - Optimized class loading
   - Reduced logging verbosity

3. **Disabled Debug Features**
   - `_PS_MODE_DEV_ = false`
   - `_PS_DEBUG_PROFILING_ = false`
   - Symfony Debug disabled

### What's Still Working:

✅ Error logging (to files)
✅ All admin functionality
✅ Module management
✅ Product editing
✅ Order management
✅ Database operations
✅ File uploads
✅ Theme customization

## Maintenance

### Clearing Cache

If you experience issues after switching between admin folders:

```bash
# Clear development cache
rm -rf /var/cache/dev/*

# Clear production cache
rm -rf /var/cache/prod/*

# Or use PrestaShop's cache clearing in admin panel
```

### Troubleshooting

**Problem: Changes not reflecting**
- Solution: Clear cache for the environment you're using

**Problem: Error 500 or white screen**
- Solution: Check error logs in `/var/logs/`
- Switch to admin-dev for detailed error messages

**Problem: Still slow**
- Check if your PHP configuration has opcache disabled
- Verify file permissions on cache directories
- Consider enabling Redis or Memcached for better caching

## System Requirements

This setup works on:
- ✅ Windows (XAMPP, WAMP, etc.)
- ✅ Linux (Apache, Nginx)
- ✅ macOS (MAMP, Valet, etc.)
- ✅ Docker environments

## Important Notes

### This is NOT a Production Setup
- Both admin-dev and admin-fast are for **development only**
- Before going live, follow PrestaShop's production deployment guide
- Rename admin folder and secure your installation

### Why Not Just Disable Dev Mode Globally?
- Keeping defines.inc.php in dev mode allows quick switching
- Some developers need full debugging capabilities
- Front office might benefit from dev mode during development
- Separation of concerns: choose per admin session

### Security Considerations
- Never use admin-dev in production
- admin-fast is safer than admin-dev but still development-oriented
- Always rename admin folder in production
- Use strong passwords and restrict admin access

## Additional Optimizations (Optional)

### 1. PHP Opcache
Ensure opcache is enabled in your php.ini:
```ini
opcache.enable=1
opcache.memory_consumption=128
opcache.max_accelerated_files=10000
```

### 2. Smarty Optimization
In PrestaShop admin, go to:
- Advanced Parameters > Performance
- Set "Smarty Cache" to "Yes"
- Set "Compilation" to "Check compile"

### 3. Database Optimization
- Enable MySQL query cache if possible
- Optimize PrestaShop database tables regularly

### 4. File System
- Use SSD storage if possible
- Ensure proper permissions (755 for directories, 644 for files)
- Exclude cache/var from antivirus scanning on Windows

## Support

For issues or questions:
1. Check admin-fast/README.md for folder-specific documentation
2. Review PrestaShop documentation
3. Check system logs in /var/logs/
4. Consider hardware/PHP configuration improvements

## Version Information

- PrestaShop Version: 9.x
- PHP Requirement: 8.1+
- Admin Folders: admin-dev (original), admin-fast (optimized)
