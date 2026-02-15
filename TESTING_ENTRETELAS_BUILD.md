# Testing Entretelas Theme Build Integration

This document provides instructions for testing the Entretelas theme build integration after merging this PR.

## Quick Test

After merging, you can quickly verify the integration:

```bash
# Test the build target
./tools/assets/build.sh front-entretelas

# Expected output:
# > Front entretelas already exists (use --force to rebuild)
# All done!
```

## Testing with Docker

The main use case is when restarting Docker containers:

### Method 1: Full Restart

```bash
# Stop containers
docker-compose down

# Start containers (this will trigger the build)
docker-compose up -d

# Check the logs for Entretelas verification
docker-compose logs prestashop-git | grep -i entretelas
```

### Method 2: Restart Only

```bash
# Restart containers
docker-compose restart

# The build script will run automatically
```

### Expected Log Output

When the containers start, you should see in the logs:

```
>>> Verifying entretelas theme assets...
> Entretelas theme assets verified successfully
```

Or if assets already exist:

```
> Front entretelas already exists (use --force to rebuild)
```

## Testing with Makefile

You can also test using the Makefile targets:

```bash
# Inside the Docker container
make front-entretelas

# Or build all front themes
make front
```

## Manual Verification

After the build completes, verify the theme is ready:

### 1. Check Theme Files Exist

```bash
ls -la themes/entretelas/assets/css/theme.css
ls -la themes/entretelas/assets/js/theme.js
ls -la themes/entretelas/config/theme.yml
```

All files should exist.

### 2. Check Theme in PrestaShop Admin

1. Access PrestaShop admin panel: http://localhost:8001/admin-dev
2. Navigate to **Design > Theme & Logo**
3. Verify "Entretelas" theme appears in the list
4. The theme should be selectable

### 3. Activate the Theme

1. In the theme list, click "Use this theme" for Entretelas
2. Visit the front-end: http://localhost:8001
3. The Entretelas theme should be active with custom colors

## Testing for Playwright

If you're setting up Playwright tests:

### 1. Ensure Docker is Running

```bash
docker-compose ps
# Should show prestashop-git container as running
```

### 2. Verify Theme is Available

```bash
# Inside container or using make
docker-compose exec prestashop-git ls -la /var/www/html/themes/entretelas/
```

### 3. Run Your Playwright Tests

The Entretelas theme should now be available for your tests.

## Troubleshooting

### Issue: Theme not appearing after restart

**Solution:**
```bash
# Force rebuild
docker-compose exec prestashop-git bash -c "cd /var/www/html && ./tools/assets/build.sh front-entretelas --force"

# Clear cache
docker-compose exec prestashop-git php bin/console cache:clear
```

### Issue: Assets missing error

**Error:**
```
ERROR: Entretelas theme assets are missing!
```

**Solution:**
This means the theme files aren't present. Verify:

```bash
# Check if theme directory exists
ls -la themes/entretelas/

# If missing, the theme wasn't committed properly
# Re-clone the repository or check .gitignore
```

### Issue: Build seems to skip Entretelas

**Solution:**
```bash
# Check if using the updated build script
cat tools/assets/build.sh | grep -A 5 "front-entretelas"

# Should show the entretelas build target
```

## What Changed vs. Before

### Before This PR

```bash
# Running build would process:
✓ admin-default
✓ admin-new-theme  
✓ front-core
✓ front-classic
✓ front-hummingbird
✗ front-entretelas (NOT INCLUDED)
```

### After This PR

```bash
# Running build now processes:
✓ admin-default
✓ admin-new-theme
✓ front-core
✓ front-classic
✓ front-hummingbird
✓ front-entretelas (NOW INCLUDED!)
```

## Verification Checklist

Use this checklist after merging:

- [ ] Docker containers restart successfully
- [ ] Build logs show Entretelas verification
- [ ] No error messages about missing assets
- [ ] Theme appears in PrestaShop admin
- [ ] Theme can be activated
- [ ] Theme displays correctly on frontend
- [ ] Playwright tests can access the theme
- [ ] `make front-entretelas` command works
- [ ] `make front` includes Entretelas

## Need Help?

If something isn't working:

1. Check the logs: `docker-compose logs prestashop-git`
2. Review documentation: `ENTRETELAS_BUILD_INTEGRATION.md`
3. Verify files: `git status` and check .gitignore
4. Force rebuild: `./tools/assets/build.sh front-entretelas --force`

## Success Criteria

You'll know everything is working when:

✅ Docker restart completes without errors  
✅ Build log shows "Entretelas theme assets verified successfully"  
✅ Theme appears in admin panel  
✅ Theme can be activated and viewed  
✅ Playwright tests can run against the theme  

---

**Last Updated:** 2026-02-15  
**Related Documentation:** ENTRETELAS_BUILD_INTEGRATION.md
