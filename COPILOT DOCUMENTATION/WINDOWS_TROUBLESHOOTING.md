# Windows Troubleshooting Guide

## Overview
This guide helps resolve common issues when running PrestaShop in Docker on Windows, particularly after fixing the volume mounting configuration.

## Common Issues and Solutions

### Issue 1: Old Named Volumes Still Exist

**Symptoms:**
- Images still don't load even after fix
- Changes to img/upload/download directories not reflected
- PrestaShop behaves as if using old configuration

**Cause:** 
Docker may have created named volumes (ps-var, ps-img, ps-upload, ps-download) before the fix was applied. These volumes persist even after changing docker-compose.yml.

**Solution:**
```bash
# Stop all containers
docker compose down

# Remove old volumes (will prompt for confirmation)
docker volume rm prestashop-entre_ps-var
docker volume rm prestashop-entre_ps-img  
docker volume rm prestashop-entre_ps-upload
docker volume rm prestashop-entre_ps-download

# Or use force removal
docker volume rm prestashop-entre_ps-var prestashop-entre_ps-img prestashop-entre_ps-upload prestashop-entre_ps-download

# Start fresh
docker compose up -d
```

**Windows Batch Script Users:**
```batch
# Use stop.bat then manually remove volumes
stop.bat
docker volume rm prestashop-entre_ps-var prestashop-entre_ps-img prestashop-entre_ps-upload prestashop-entre_ps-download
start.bat
```

### Issue 2: File Permission Errors

**Symptoms:**
- "Permission denied" errors in PrestaShop
- Cannot write to directories
- Upload fails

**Cause:**
Windows file permissions or Docker Desktop configuration issues.

**Solution:**

1. **Check Docker Desktop Settings:**
   - Open Docker Desktop
   - Go to Settings → Resources → File Sharing
   - Ensure your project directory is in the shared folders list
   - Click "Apply & Restart"

2. **Verify USER_ID and GROUP_ID:**
   
   Windows users should use the default values (1000:1000). The Dockerfile is configured to handle this:
   ```bash
   # Check current .env file or use defaults
   # USER_ID=1000
   # GROUP_ID=1000
   ```

3. **Reset permissions in container:**
   ```bash
   docker compose exec prestashop-git chown -R www-data:www-data /var/www/html/img
   docker compose exec prestashop-git chown -R www-data:www-data /var/www/html/upload
   docker compose exec prestashop-git chown -R www-data:www-data /var/www/html/download
   docker compose exec prestashop-git chown -R www-data:www-data /var/www/html/var
   ```

### Issue 3: Images Directory Empty or Not Syncing

**Symptoms:**
- `/img` directory appears empty in container
- New images uploaded in PrestaShop don't appear on host
- PrestaShop logo missing

**Cause:**
Bind mount not working correctly or using wrong directory.

**Solution:**

1. **Verify bind mount is active:**
   ```bash
   docker compose exec prestashop-git df -h | grep /var/www/html
   ```
   Should show something like:
   ```
   overlay   xxx   xxx   xxx   xx%   /var/www/html
   ```

2. **Check directory contents:**
   ```bash
   # In container
   docker compose exec prestashop-git ls -la /var/www/html/img | head -20
   
   # On host (from repository root)
   dir img
   ```
   
   Both should show the same files.

3. **If directories don't match, recreate container:**
   ```bash
   docker compose down
   docker compose up -d --force-recreate prestashop-git
   ```

### Issue 4: Port Conflicts (8001 already in use)

**Symptoms:**
- "port is already allocated" error
- Cannot start containers

**Cause:**
Another application or previous PrestaShop instance using port 8001.

**Solution:**

1. **Find what's using the port:**
   ```bash
   # Windows Command Prompt
   netstat -ano | findstr :8001
   
   # Windows PowerShell  
   Get-NetTCPConnection -LocalPort 8001
   ```

2. **Kill the process or change port:**
   
   **Option A - Kill process:**
   ```bash
   # Find PID from netstat output, then:
   taskkill /PID <PID> /F
   ```
   
   **Option B - Change PrestaShop port:**
   Edit `docker-compose.yml`:
   ```yaml
   ports:
     - "8080:80"  # Change 8001 to 8080 (or any free port)
     - "8443:443" # Change 8002 to 8443
   ```
   
   Then access PrestaShop at `http://localhost:8080`

### Issue 5: Slow Performance on Windows

**Symptoms:**
- Container startup very slow
- File access sluggish
- Asset compilation takes forever

**Cause:**
Windows bind mounts have performance overhead compared to native Linux.

**Solutions:**

1. **Use WSL2 backend in Docker Desktop:**
   - Open Docker Desktop
   - Settings → General → "Use WSL 2 based engine" (should be enabled)
   - Restart Docker Desktop

2. **Move project to WSL2 filesystem (BEST for performance):**
   ```bash
   # In WSL2 terminal:
   cd ~
   git clone https://github.com/albertmmateo-blip/PrestaShop-Entre.git
   cd PrestaShop-Entre
   docker compose up -d
   ```
   Access the repo from Windows at: `\\wsl$\Ubuntu\home\<username>\PrestaShop-Entre`

3. **Consider disabling DISABLE_MAKE for faster startup:**
   
   If you don't need asset building on every startup:
   ```bash
   # Create .env file or edit existing
   DISABLE_MAKE=1
   ```
   
   Then manually run asset build when needed:
   ```bash
   docker compose exec prestashop-git /var/www/html/tools/assets/build.sh
   ```

### Issue 6: MySQL Connection Refused

**Symptoms:**
- PrestaShop installation fails with "Cannot connect to MySQL"
- "Connection refused" errors in logs

**Cause:**
MySQL container not ready when PrestaShop container tries to connect.

**Solution:**

1. **Check if MySQL is running:**
   ```bash
   docker compose ps
   ```
   
   MySQL service should show as "Up".

2. **Check MySQL logs:**
   ```bash
   docker compose logs mysql
   ```
   
   Look for "ready for connections" message.

3. **Wait longer for MySQL startup:**
   
   The configuration already includes a wait script. If issues persist:
   ```bash
   # Stop everything
   docker compose down
   
   # Start MySQL first
   docker compose up -d mysql
   
   # Wait 30 seconds
   timeout 30
   
   # Start PrestaShop
   docker compose up -d prestashop-git
   ```

### Issue 7: PrestaShop Installation Keeps Re-running

**Symptoms:**
- Every time container starts, PrestaShop reinstalls
- Lose admin data on restart
- Fresh installation each time

**Cause:**
`app/config/parameters.php` is being deleted or not persisting.

**Solution:**

1. **Verify file exists and persists:**
   ```bash
   # Check if file exists
   dir app\config\parameters.php
   ```
   
   If missing after restart, the bind mount isn't working.

2. **Force parameters file to persist:**
   ```bash
   # After first successful install:
   docker compose exec prestashop-git ls -la /var/www/html/app/config/parameters.php
   
   # Should exist. If so, ensure database persists:
   docker compose down
   docker volume ls | findstr db-data
   
   # Should see prestashop-entre_db-data
   ```

3. **Manual reinstallation (if needed):**
   ```bash
   # Remove parameters file to trigger reinstall
   del app\config\parameters.php
   
   # Restart container
   docker compose restart prestashop-git
   ```

## Windows-Specific Best Practices

### 1. Use WSL2 for Best Performance
Running Docker Desktop with WSL2 backend and storing your project in the WSL2 filesystem gives near-native Linux performance.

### 2. Keep Repository on NTFS (Not Network Drive)
Don't clone the repository to:
- Network drives
- OneDrive/Dropbox synced folders
- USB drives

These can cause permission and synchronization issues.

### 3. Antivirus Exclusions
Add Docker directories to antivirus exclusions:
- `%PROGRAMDATA%\Docker`
- `%USERPROFILE%\.docker`
- Your project directory

### 4. Use Batch Scripts
For Windows users, use the provided batch scripts:
- `start.bat` - First time setup
- `quick-start.bat` - Daily use
- `stop.bat` - Stop containers
- `restart.bat` - Full rebuild

These handle Windows-specific quirks automatically.

## Verifying the Fix

After applying any solution, verify PrestaShop works correctly:

### 1. Check Frontend
```
http://localhost:8001
```
- Logo should be visible
- Product images should load
- No broken image icons

### 2. Check Backend  
```
http://localhost:8001/admin-dev
```
Login with:
- Email: demo@prestashop.com
- Password: Correct Horse Battery Staple

Then:
- Upload a product image
- Verify it appears in the product listing
- Check the image file appears on host: `img\p\`

### 3. Check File Sync
```bash
# Create a test file on host
echo test > test.txt

# Check it appears in container
docker compose exec prestashop-git cat /var/www/html/test.txt

# Should output: test

# Clean up
del test.txt
```

## Getting Help

If issues persist after trying these solutions:

1. **Collect diagnostic information:**
   ```bash
   docker compose version
   docker version
   docker compose ps
   docker compose logs prestashop-git > prestashop-logs.txt
   docker volume ls
   ```

2. **Check documentation:**
   - [DOCKER_VOLUMES_FIX.md](./DOCKER_VOLUMES_FIX.md) - Details on the volume fix
   - [WINDOWS_BATCH_SCRIPTS.md](./WINDOWS_BATCH_SCRIPTS.md) - Batch script usage
   - [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Quick command reference

3. **Review Docker Desktop:**
   - Ensure version is up to date
   - Check Resources allocated (CPU, Memory, Disk)
   - Verify WSL2 integration is enabled

## Advanced Troubleshooting

### Reset Everything (Nuclear Option)

If all else fails, completely reset the Docker environment:

```bash
# WARNING: This removes ALL containers, images, and volumes!

# Stop all containers
docker compose down -v

# Remove all PrestaShop images
docker images | findstr prestashop-entre
docker rmi prestashop-entre-prestashop-git

# Remove all volumes
docker volume ls | findstr prestashop
docker volume rm prestashop-entre_db-data

# Rebuild from scratch
start.bat
```

### Enable Debug Logging

For detailed container logs:

```bash
# Edit .env or set environment variable
PS_DEV_MODE=1

# View logs in real-time
docker compose logs -f prestashop-git
```

## Related Documentation

- [DOCKER_VOLUMES_FIX.md](./DOCKER_VOLUMES_FIX.md) - Technical details of the volume fix
- [WINDOWS_README.md](../WINDOWS_README.md) - Windows quick start guide
- [WINDOWS_BATCH_SCRIPTS.md](./WINDOWS_BATCH_SCRIPTS.md) - Batch scripts documentation
- [README.md](../README.md) - Main PrestaShop documentation
