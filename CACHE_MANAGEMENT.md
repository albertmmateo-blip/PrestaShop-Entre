# Quick Reference: PrestaShop Cache Management

## Clearing Cache

### Method 1: Delete cache folders (Recommended)

**For admin-fast (production cache):**
```bash
rm -rf var/cache/prod/*
```

**For admin-dev (development cache):**
```bash
rm -rf var/cache/dev/*
```

**For legacy cache:**
```bash
rm -rf cache/smarty/compile/*
rm -rf cache/smarty/cache/*
```

**Clear all caches at once:**
```bash
rm -rf var/cache/*/
rm -rf cache/smarty/compile/*
rm -rf cache/smarty/cache/*
```

### Method 2: From PrestaShop Admin Panel

1. Go to: **Advanced Parameters > Performance**
2. Click: **Clear cache** button
3. This clears Smarty cache and compiled templates

### Method 3: Using Console (if available)

```bash
php bin/console cache:clear --env=prod
php bin/console cache:clear --env=dev
```

## When to Clear Cache

### ✅ Always clear cache when:
- Switching between admin-dev and admin-fast
- After updating configuration files
- After installing/updating modules
- Template changes not appearing
- Experiencing strange behavior

### ⚠️ You might need to clear cache when:
- Performance suddenly degrades
- Changes to theme/templates not visible
- After editing .tpl files
- After changing PHP code in modules

### ℹ️ No need to clear cache for:
- Regular content updates (products, pages, etc.)
- Order processing
- Customer management
- Most day-to-day operations

## Windows-Specific Cache Clearing

### Using File Explorer:
1. Navigate to your PrestaShop installation folder
2. Go to `var\cache\` folder
3. Delete the `dev` and `prod` folders
4. Go to `cache\smarty\` folder
5. Delete contents of `compile` and `cache` folders

### Using Command Prompt:
```cmd
cd C:\path\to\prestashop
rmdir /s /q var\cache\dev
rmdir /s /q var\cache\prod
rmdir /s /q cache\smarty\compile
rmdir /s /q cache\smarty\cache
```

### Using PowerShell:
```powershell
cd C:\path\to\prestashop
Remove-Item -Recurse -Force var\cache\dev\*
Remove-Item -Recurse -Force var\cache\prod\*
Remove-Item -Recurse -Force cache\smarty\compile\*
Remove-Item -Recurse -Force cache\smarty\cache\*
```

## Troubleshooting Cache Issues

### Issue: Permission denied when clearing cache
**Solution:**
```bash
# Linux/Mac:
sudo chmod -R 777 var/cache
sudo chmod -R 777 cache

# Or use proper ownership:
sudo chown -R www-data:www-data var/cache
sudo chown -R www-data:www-data cache
```

**Windows:**
- Right-click folder > Properties > Security
- Give "Full control" to your user account

### Issue: Cache keeps rebuilding incorrectly
**Solution:**
1. Stop your web server
2. Clear all caches completely
3. Start your web server
4. Access admin panel once to rebuild cache

### Issue: Can't delete cache files (in use)
**Solution:**
1. Stop your web server (Apache, Nginx, IIS)
2. Delete cache files
3. Start web server again

## Best Practices

### For Development:
- Use **admin-fast** for regular work (no cache clearing needed often)
- Use **admin-dev** for debugging (cache clears automatically more often)
- Clear cache when switching between the two

### For Performance:
- Don't clear cache unnecessarily in production
- Let PrestaShop manage its own cache
- Only clear when you make changes that require it

### Automated Cache Clearing Script:

Create `clear-cache.sh`:
```bash
#!/bin/bash
echo "Clearing PrestaShop cache..."
rm -rf var/cache/*/
rm -rf cache/smarty/compile/*
rm -rf cache/smarty/cache/*
echo "Cache cleared successfully!"
```

Make it executable:
```bash
chmod +x clear-cache.sh
```

Run it:
```bash
./clear-cache.sh
```

## Cache Locations Reference

| Cache Type | Location | Purpose |
|------------|----------|---------|
| Dev Symfony | `var/cache/dev/` | Development environment cache |
| Prod Symfony | `var/cache/prod/` | Production environment cache |
| Smarty Compiled | `cache/smarty/compile/` | Compiled template files |
| Smarty Cache | `cache/smarty/cache/` | Cached template output |
| Class Index | `cache/class_index.php` | Autoloader cache |

## Monitoring Cache Size

```bash
# Check total cache size
du -sh var/cache cache

# Check individual cache sizes
du -sh var/cache/dev
du -sh var/cache/prod
du -sh cache/smarty
```

## Notes

- Cache clearing is **instant** and **safe**
- PrestaShop rebuilds cache **automatically** when needed
- **No data loss** - only temporary compiled files are deleted
- First page load after cache clear may be slower (rebuilding)
- Subsequent loads will be fast again
