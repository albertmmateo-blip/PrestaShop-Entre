# Admin-Fast: Optimized Back Office

This is an optimized version of the PrestaShop back office designed for **faster performance during development**.

## What's Different?

The `admin-fast` folder provides a performance-optimized admin interface while still maintaining development capabilities:

### Performance Optimizations:
- **Development mode disabled** (`_PS_MODE_DEV_ = false`)
- **Debug profiling disabled** (`_PS_DEBUG_PROFILING_ = false`)
- **Symfony Debug toolbar disabled** (no Debug::enable())
- **Production-like environment** (`_PS_ENV_ = prod`)

### Key Benefits:
- ⚡ **Significantly faster** page loads and navigation
- 💨 **Reduced memory usage**
- 🔧 **Still suitable for development** - errors are still logged
- 🛠️ **Easy to switch** between fast and debug modes

## When to Use

### Use `admin-fast/` when:
- Working on day-to-day development tasks
- Need responsive admin interface
- Don't need detailed debugging information
- Focusing on functionality rather than troubleshooting

### Use `admin-dev/` when:
- Debugging complex issues
- Need detailed error messages and stack traces
- Using Symfony profiler for performance analysis
- Developing new features that require extensive testing

## How to Access

Simply navigate to:
```
http://your-site.com/admin-fast/
```

Instead of:
```
http://your-site.com/admin-dev/
```

## Technical Details

### Changes from admin-dev:
The only file modified is `index.php`, which:
1. Forces `_PS_MODE_DEV_` to `false` before loading config
2. Forces `_PS_DEBUG_PROFILING_` to `false`
3. Comments out `Debug::enable()` to prevent Symfony debug components from loading

This ensures the back office runs in production-like mode for speed while:
- ✅ Keeping error logging enabled
- ✅ Maintaining all functionality
- ✅ Allowing full development capabilities
- ✅ Not affecting the front office or admin-dev

## Troubleshooting

If you encounter issues:

1. **Clear cache**: Delete `/var/cache/prod/` folder
2. **Check permissions**: Ensure proper file permissions on cache folders
3. **Switch to admin-dev**: For detailed debugging, use the admin-dev folder instead

## Configuration Files

The system still reads from:
- `/config/defines.inc.php` - Core configuration (overridden by index.php)
- `/app/config/parameters.yml` - Database and Symfony settings
- `/config/smarty.config.inc.php` - Template engine settings

## Notes

- This setup is **perfect for development** on slower systems or Windows environments
- Error logging still works, so you can debug issues from log files
- Cache is created in `/var/cache/prod/` instead of `/var/cache/dev/`
- This does NOT create a production environment - it's optimized development mode
