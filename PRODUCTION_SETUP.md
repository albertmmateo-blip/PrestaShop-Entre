# PrestaShop Production Setup and Optimization Guide

## Overview
This document explains the optimizations made to ensure PrestaShop runs in a healthy, clean, and performant way.

## Issues Identified and Fixed

### 1. Developer Mode Disabled ✓
**Issue:** PrestaShop was running with `_PS_MODE_DEV_` set to `true`, causing significant performance degradation.

**Fix:** Changed `_PS_MODE_DEV_` to `false` in `/config/defines.inc.php` (line 36)

**Impact:** 
- Disables debug output
- Disables error display in production
- Disables SQL debugging
- Significantly improves performance

### 2. Compatibility Warnings Disabled ✓
**Issue:** `_PS_DISPLAY_COMPATIBILITY_WARNING_` was enabled, adding overhead to every request.

**Fix:** Changed to `false` in `/config/defines.inc.php` (line 39)

**Impact:**
- Removes E_DEPRECATED and E_USER_DEPRECATED warnings
- Reduces processing overhead

### 3. Production Admin Folder Created ✓
**Issue:** Using `admin-dev` folder (development-specific naming and configuration).

**Fix:** Created new `admin-prod` folder with production-optimized configuration.

**Features:**
- Optimized `index.php` without debug mode enablement
- All necessary files and directories for admin functionality
- Better security through non-standard naming

## Folder Structure

### admin-prod/ (Production Admin - RECOMMENDED)
```
admin-prod/
├── index.php          # Production-optimized entry point
├── bootstrap.php      # Bootstrap file
├── init.php           # Initialization file
├── cron_currency_rates.php
├── .htaccess          # Apache configuration
├── favicon.ico
├── robots.txt
├── themes/            # Admin themes
├── autoupgrade/       # Auto-upgrade directory
├── backups/           # Backups directory
├── export/            # Export directory
├── import/            # Import directory
└── filemanager/       # File manager directory
```

### admin-dev/ (Development Admin - For Development Only)
- Contains all files but includes debug enablement
- Should only be used in development environments
- NOT recommended for production use

## Current Configuration Status

### Production Mode Settings
Located in: `/config/defines.inc.php`

```php
define('_PS_MODE_DEV_', false);                    // ✓ Disabled for performance
define('_PS_DISPLAY_COMPATIBILITY_WARNING_', false); // ✓ Disabled for performance
define('_PS_DISPLAY_ONLY_ERRORS_', false);          // Shows all error types (when dev mode is on)
define('_PS_DEBUG_PROFILING_', false);              // ✓ Performance profiler disabled
define('_PS_MODE_DEMO_', false);                    // Demo mode disabled
```

### Environment Configuration
Located in: `/.env`

```
PS_FF_FRONT_CONTAINER_V2=false     # Using legacy front container
PS_TRUSTED_PROXIES=                # No proxies configured
PS_FF_DEFAULT_THEME=hummingbird    # Default theme
```

## Performance Improvements

### Before Optimization
- Developer mode: **ENABLED** ❌
- Debug profiling: Disabled
- Error display: **ENABLED** ❌
- SQL debugging: **ENABLED** ❌
- Compatibility warnings: **ENABLED** ❌
- Admin folder: admin-dev (development)

### After Optimization
- Developer mode: **DISABLED** ✓
- Debug profiling: Disabled ✓
- Error display: **DISABLED** ✓
- SQL debugging: **DISABLED** ✓
- Compatibility warnings: **DISABLED** ✓
- Admin folder: admin-prod (production) ✓

## How to Use

### For Production (Recommended)
1. Access your admin panel at: `http://yourdomain.com/admin-prod/`
2. Ensure you're using the production-optimized configuration
3. Developer mode is disabled for maximum performance

### For Development
1. If you need to develop or debug, you can still access: `http://yourdomain.com/admin-dev/`
2. Be aware this has debug mode enabled via the index.php

## Security Recommendations

### 1. Rename Admin Folder
For enhanced security, rename the `admin-prod` folder to something unique:

```bash
# Example: Rename to admin-mysecretname
mv admin-prod admin-mysecretname
```

Then access at: `http://yourdomain.com/admin-mysecretname/`

### 2. Delete install-dev Folder
After installation is complete, remove the installation folder:

```bash
rm -rf install-dev/
```

### 3. Set Proper File Permissions
```bash
# For directories
find . -type d -exec chmod 755 {} \;

# For files
find . -type f -exec chmod 644 {} \;

# For var/cache and var/logs (writable)
chmod -R 777 var/cache/
chmod -R 777 var/logs/
```

## Cache Management

### Clear Cache for Production
After making configuration changes, clear the cache:

```bash
# Clear Symfony cache
php bin/console cache:clear --env=prod

# Or manually delete cache
rm -rf var/cache/prod/*
rm -rf var/cache/dev/*
```

### Verify Cache Directories
Ensure cache directories exist and are writable:

```bash
mkdir -p var/cache/prod
mkdir -p var/cache/dev
chmod -R 777 var/cache/
```

## Performance Monitoring

### Check Current Environment
The environment is determined by `_PS_MODE_DEV_`:
- If `true`: Environment = `dev` (slower, more debugging)
- If `false`: Environment = `prod` (faster, optimized)

Current setting: **prod** (optimized) ✓

### Monitor Performance
1. **Front Office**: Should load significantly faster
2. **Back Office**: Admin panel operations should be more responsive
3. **Database Queries**: SQL debugging is now disabled, reducing overhead

## Troubleshooting

### If Admin Panel Doesn't Load
1. Check web server error logs
2. Verify `admin-prod` folder has all necessary files
3. Ensure PHP has write permissions to `var/cache/` and `var/logs/`

### If You Need Debug Mode Temporarily
Edit `/config/defines.inc.php` and temporarily change:
```php
define('_PS_MODE_DEV_', true);  // Enable temporarily
```

**Remember to disable it again after debugging!**

### Clear Cache Issues
If experiencing cache-related issues:
```bash
rm -rf var/cache/prod/*
rm -rf var/cache/dev/*
```

## Additional Optimizations

### Database Optimization
Consider enabling query caching and optimizing tables regularly.

### PHP Configuration
Ensure your php.ini has optimal settings:
```ini
memory_limit = 256M
max_execution_time = 300
upload_max_filesize = 20M
post_max_size = 22M
```

### Web Server
- Enable gzip compression
- Enable browser caching
- Use a CDN for static assets
- Consider using PHP-FPM with nginx or Apache

## Summary

✓ Developer mode disabled for production performance
✓ Debug profiling disabled
✓ Compatibility warnings disabled
✓ Production admin folder created (admin-prod)
✓ All necessary admin files in place
✓ Configuration optimized for speed

**Recommended Next Steps:**
1. Access admin panel via `/admin-prod/` 
2. Test functionality to ensure everything works
3. Rename `admin-prod` to a unique name for security
4. Delete or restrict access to `admin-dev` folder
5. Remove `install-dev` folder if installation is complete
6. Set up regular backups
7. Monitor performance improvements

## Support

For more information:
- PrestaShop Documentation: https://devdocs.prestashop-project.org/
- PrestaShop Forum: https://www.prestashop-project.org/support/
- GitHub Issues: https://github.com/PrestaShop/PrestaShop/issues
