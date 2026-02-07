# 🔧 PrestaShop Docker Troubleshooting Guide

This guide helps you resolve common issues when running PrestaShop with Docker. If you're experiencing problems, start here!

## 📋 Table of Contents

- [Quick Diagnostics](#-quick-diagnostics)
- [Permission Errors](#-permission-errors)
- [Database Connection Issues](#-database-connection-issues)
- [Port Conflicts](#-port-conflicts)
- [Container Issues](#-container-issues)
- [Performance Problems](#-performance-problems)
- [Installation Failures](#-installation-failures)
- [Getting Help](#-getting-help)

---

## 🩺 Quick Diagnostics

Before diving into specific issues, run these commands to gather information:

```bash
# Check if Docker is running
docker --version

# Check container status
docker compose ps

# View recent logs
docker compose logs --tail=50 prestashop-git

# Check Docker disk space
docker system df
```

---

## 🔐 Permission Errors

### Problem: "Permission denied" errors in logs

This is one of the most common issues with PrestaShop Docker setup.

**Symptoms**:
- Error messages like `Failed to open stream: Permission denied`
- Cannot write to `/var/www/html/var/logs/`
- Cannot write to `/var/www/html/var/cache/`
- PrestaShop installation fails with file permission errors

**Example Error from logs**:
```
Warning: file_put_contents(/var/www/html/var/logs/20260207_exception.log): 
Failed to open stream: Permission denied in /var/www/html/classes/log/FileLogger.php
```

### Solution 1: Set Correct User ID and Group ID

The Docker container needs to run with the same user ID as your host system.

**Windows (Git Bash or WSL)**:
```bash
# Get your user ID (usually 1000)
id -u

# Set environment variables and restart
export USER_ID=$(id -u)
export GROUP_ID=$(id -g)
docker compose down
docker compose up -d --build
```

**macOS**:
```bash
# Get your user ID
id -u

# Set environment variables and restart
export USER_ID=$(id -u)
export GROUP_ID=$(id -g)
docker compose down
docker compose up -d --build
```

**Linux**:
```bash
# Get your user ID
id -u

# Set environment variables and restart
export USER_ID=$(id -u)
export GROUP_ID=$(id -g)
docker compose down
docker compose up -d --build
```

### Solution 2: Fix Permissions Manually

If the above doesn't work, fix permissions directly:

```bash
# Stop containers
docker compose down

# Fix ownership of var directories
sudo chown -R $(id -u):$(id -g) var/

# Fix permissions
chmod -R 775 var/logs
chmod -R 775 var/cache

# Restart containers
docker compose up -d
```

### Solution 3: Reset and Rebuild

For persistent permission issues:

```bash
# Stop and remove containers
docker compose down -v

# Remove var directories
rm -rf var/logs/* var/cache/*

# Rebuild and start fresh
docker compose build --no-cache
docker compose up -d
```

### Solution 4: SELinux Issues (Linux Only)

If you're on Linux with SELinux enabled:

```bash
# Check SELinux status
sestatus

# If SELinux is enforcing, relabel the directory
chcon -Rt svirt_sandbox_file_t .

# Or add this to docker-compose.yml volumes section
# volumes:
#   - ./:/var/www/html:z
```

### Preventing Permission Issues

Add this to your `.env` file to set permissions automatically:

```bash
# Get your current user ID and group ID
id -u  # Example output: 1000
id -g  # Example output: 1000

# Add to .env file
USER_ID=1000
GROUP_ID=1000
```

---

## 🗄️ Database Connection Issues

### Problem: "Can't connect to MySQL server"

**Symptoms**:
- PrestaShop can't connect to database
- Error: `ERROR 2002 (HY000): Can't connect to server on 'mysql'`
- Installation fails at database step

**Example Error from logs**:
```
ERROR 2002 (HY000): Can't connect to server on 'mysql' (115)
wait-for-it.sh: Fetching status from docker mysql
```

### Solution 1: Wait for MySQL to Start

MySQL takes time to initialize on first run:

```bash
# Check MySQL container status
docker compose ps

# Wait for MySQL to be ready (can take 30-60 seconds)
docker compose logs -f mysql

# Look for: "mysqld: ready for connections"
```

### Solution 2: Verify Database Configuration

Check your database settings in `.env`:

```bash
DB_SERVER=mysql
DB_NAME=prestashop
DB_USER=root
DB_PASSWD=prestashop
```

### Solution 3: Reset Database

If database is corrupted:

```bash
# Stop containers
docker compose down

# Remove database volume
docker volume rm prestashop_db-data

# Restart (will create fresh database)
docker compose up -d
```

### Solution 4: Check Network Connectivity

Ensure containers are on the same network:

```bash
# Check network
docker network ls

# Inspect network
docker network inspect prestashop-network

# Verify containers are connected
docker compose exec prestashop-git ping -c 3 mysql
```

### Problem: "Table doesn't exist" Error

**Symptoms**:
- Error: `Table 'prestashop.ps_hook' doesn't exist`
- Container exits with code 3
- Occurs when configuring emails or running console commands
- Database is empty but PrestaShop thinks it's installed

**Example Error from logs**:
```
* Configuring emails to use maildev ...
PrestaShopDatabaseException in /var/www/html/classes/db/Db.php line 777
[ERROR] Failed setting value: Table 'prestashop.ps_hook' doesn't exist
```

### Solution: This Has Been Fixed! ✅

This issue has been resolved in the latest version. The startup script now automatically checks if the database is initialized before running configuration commands.

**What was fixed**:
- The Docker startup script now checks if database tables exist before running console commands
- If tables don't exist, it skips maildev configuration and provides helpful instructions
- You'll see a message: "Skipping maildev configuration (database not initialized yet)"

**If you still see this error**:

1. **Pull the latest changes**:
   ```bash
   git pull origin develop
   ```

2. **Clean restart**:
   ```bash
   # Stop containers and remove volumes
   docker compose down -v
   
   # Remove parameters file if it exists from old install
   rm -f app/config/parameters.php
   
   # Rebuild and restart
   docker compose build
   docker compose up -d
   ```

3. **If database exists but is empty**:
   ```bash
   # Set PS_ERASE_DB to force fresh installation
   export PS_ERASE_DB=1
   
   # Or add to .env file:
   echo "PS_ERASE_DB=1" >> .env
   
   # Then restart
   docker compose down
   docker compose up -d
   ```

4. **Configure maildev manually after installation** (if needed):
   ```bash
   docker compose exec prestashop-git php bin/console prestashop:config set PS_MAIL_METHOD --value 2
   docker compose exec prestashop-git php bin/console prestashop:config set PS_MAIL_SERVER --value maildev
   docker compose exec prestashop-git php bin/console prestashop:config set PS_MAIL_SMTP_PORT --value 1025
   ```

---

## 🔌 Port Conflicts

### Problem: "Port already in use"

**Symptoms**:
- Error: `Bind for 0.0.0.0:8001 failed: port is already allocated`
- Can't start containers
- Another application using the port

### Solution 1: Find and Stop Conflicting Service

**Windows (PowerShell as Admin)**:
```powershell
# Find what's using port 8001
Get-NetTCPConnection -LocalPort 8001

# Stop the process (replace PID with actual process ID)
Stop-Process -Id <PID> -Force
```

**macOS/Linux**:
```bash
# Find what's using port 8001
lsof -i :8001

# Kill the process (replace PID with actual process ID)
kill -9 <PID>
```

### Solution 2: Change PrestaShop Port

Edit `docker-compose.yml`:

```yaml
services:
  prestashop-git:
    ports:
      - "8080:80"  # Changed from 8001 to 8080
      - "8443:443"
```

Then restart:
```bash
docker compose down
docker compose up -d
```

Access at: `http://localhost:8080`

### Solution 3: Check All Ports

PrestaShop uses multiple ports. Check all of them:

```bash
# Check port 8001 (PrestaShop HTTP)
lsof -i :8001

# Check port 3306 (MySQL)
lsof -i :3306

# Check port 1080 (MailDev)
lsof -i :1080
```

---

## 🐳 Container Issues

### Problem: Container Keeps Restarting

**Symptoms**:
- Container status shows "Restarting"
- Services not accessible
- Continuous restart loop

### Solution 1: Check Logs

```bash
# View container logs
docker compose logs prestashop-git

# Follow logs in real-time
docker compose logs -f prestashop-git

# Check for error messages
```

### Solution 2: Increase Docker Resources

1. Open Docker Desktop
2. Go to Settings → Resources
3. Increase:
   - **Memory**: At least 4GB (6GB recommended)
   - **CPU**: At least 2 cores (4 recommended)
   - **Disk**: At least 10GB free
4. Click "Apply & Restart"

### Solution 3: Remove and Recreate

```bash
# Stop and remove everything
docker compose down -v

# Remove images
docker compose rm -f

# Rebuild from scratch
docker compose build --no-cache
docker compose up -d
```

### Problem: Container Exits Immediately

Check startup script errors:

```bash
# View full logs
docker compose logs prestashop-git

# Check for:
# - Missing dependencies
# - Configuration errors
# - Permission issues
```

---

## 🐌 Performance Problems

### Problem: PrestaShop is Slow

### Solution 1: Allocate More Resources to Docker

Open Docker Desktop → Settings → Resources:
- **Memory**: Increase to 6-8GB
- **CPU**: Increase to 4+ cores
- **Swap**: Set to 1GB

### Solution 2: Use Named Volumes (Advanced)

Replace file mounts with Docker volumes for better performance:

```yaml
# Instead of:
volumes:
  - ./:/var/www/html

# Use (advanced users only):
volumes:
  - prestashop-data:/var/www/html
```

**Note**: This makes file editing harder. Only for production-like setups.

### Solution 3: Disable Xdebug

If you're not debugging:

```bash
# Check if Xdebug is enabled
docker compose exec prestashop-git php -v

# Rebuild without Xdebug
export INSTALL_XDEBUG=false
docker compose down
docker compose build
docker compose up -d
```

### Solution 4: Clear Caches

```bash
# Clear PrestaShop cache
docker compose exec prestashop-git rm -rf var/cache/*

# Or use make command
make cc
```

---

## 💥 Installation Failures

### Problem: PrestaShop Installation Fails

### Solution 1: Check Requirements

Verify system meets requirements:
- PHP 8.1+ ✓ (in container)
- MySQL 5.6+ ✓ (in container)
- At least 4GB RAM available
- At least 10GB disk space

### Solution 2: Fresh Installation

```bash
# Complete reset
docker compose down -v
docker volume prune -f

# Remove configuration
rm -f app/config/parameters.php
rm -f app/config/parameters.yml

# Remove var directories
rm -rf var/cache/* var/logs/*

# Fresh start
docker compose up -d --build
```

### Solution 3: Manual Installation

If auto-install fails, try manual installation:

```bash
# Disable auto-install
export PS_INSTALL_AUTO=0

# Start containers
docker compose up -d

# Open browser and go to:
# http://localhost:8001/install-dev
```

Follow the web installer steps manually.

### Solution 4: Check Available Disk Space

```bash
# Check Docker disk usage
docker system df

# Clean up if needed
docker system prune -a --volumes

# Check host disk space
df -h
```

---

## 🔍 Advanced Diagnostics

### Inspect Container

Get detailed container information:

```bash
# Inspect PrestaShop container
docker inspect prestashop-git-1

# Check environment variables
docker compose exec prestashop-git env

# Check running processes
docker compose exec prestashop-git ps aux
```

### Check File Permissions Inside Container

```bash
# Access container
docker compose exec prestashop-git bash

# Check ownership
ls -la /var/www/html/var/

# Check specific directories
ls -la /var/www/html/var/logs/
ls -la /var/www/html/var/cache/

# Exit container
exit
```

### View All Logs

```bash
# All services
docker compose logs

# Specific service
docker compose logs mysql
docker compose logs maildev

# Last 100 lines
docker compose logs --tail=100

# Follow logs
docker compose logs -f
```

---

## 🛡️ Common Fixes Checklist

Before asking for help, try these steps:

- [ ] Check Docker Desktop is running
- [ ] Run `docker compose ps` to see container status
- [ ] Check logs: `docker compose logs prestashop-git`
- [ ] Verify ports aren't in use
- [ ] Ensure enough disk space (10GB+)
- [ ] Allocate enough memory (4GB+ to Docker)
- [ ] Set correct USER_ID and GROUP_ID
- [ ] Try rebuilding: `docker compose build --no-cache`
- [ ] Try fresh start: `docker compose down -v && docker compose up -d`
- [ ] Check `.env` file configuration

---

## 💡 Best Practices

### 1. Always Use Environment Variables

Create a `.env` file with your settings:

```bash
# User Configuration
USER_ID=1000
GROUP_ID=1000

# Database Configuration
DB_PASSWD=your_secure_password
DB_NAME=prestashop

# Admin Configuration
ADMIN_MAIL=your-email@example.com
ADMIN_PASSWD=YourSecurePassword

# PrestaShop Configuration
PS_DOMAIN=localhost:8001
PS_DEV_MODE=1
```

### 2. Regular Cleanup

Periodically clean Docker:

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes (careful!)
docker volume prune

# Remove everything unused
docker system prune -a
```

### 3. Monitor Resource Usage

```bash
# Check container resource usage
docker stats

# Check system-wide usage
docker system df
```

### 4. Keep Docker Updated

Regularly update Docker Desktop to the latest version for bug fixes and improvements.

---

## 📞 Getting Help

If you've tried everything and still have issues:

### 1. Gather Information

Collect this information before asking for help:

```bash
# System information
docker --version
docker compose --version

# Container status
docker compose ps

# Recent logs (save to file)
docker compose logs --tail=200 > my-prestashop-logs.txt

# Environment
cat .env
```

### 2. Check Existing Issues

Search for similar problems:
- [GitHub Issues](https://github.com/PrestaShop/PrestaShop/issues)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/prestashop)
- [PrestaShop Forums](https://www.prestashop.com/forums/)

### 3. Ask the Community

- 💬 [Slack Channel](https://www.prestashop-project.org/slack/)
- 💭 [GitHub Discussions](https://github.com/PrestaShop/PrestaShop/discussions)
- 📚 [Forums](https://www.prestashop.com/forums/)

### 4. Create a Bug Report

If you found a bug:
1. Go to [GitHub Issues](https://github.com/PrestaShop/PrestaShop/issues/new/choose)
2. Choose "Bug report"
3. Include:
   - Your system information
   - Steps to reproduce
   - Log files
   - Expected vs actual behavior

---

## 🎯 Quick Reference Commands

```bash
# Start/Stop
docker compose up -d          # Start containers
docker compose down           # Stop containers
docker compose restart        # Restart containers

# Logs
docker compose logs -f        # Follow all logs
docker compose logs prestashop-git  # Specific service

# Status
docker compose ps             # Container status
docker stats                  # Resource usage

# Cleanup
docker compose down -v        # Stop and remove volumes
docker system prune -a        # Clean everything

# Access
docker compose exec prestashop-git bash  # Container shell
make docker-sh                # Same using make

# Rebuild
docker compose build --no-cache  # Rebuild images
docker compose up -d --build     # Rebuild and start
```

---

## 📚 Related Documentation

- [Installation Guide](INSTALLATION_GUIDE.md) - Step-by-step installation
- [Main README](README.md) - Overview and quick start
- [Development Guide](../docs/DEVELOPMENT.md) - Advanced development topics
- [PrestaShop DevDocs](https://devdocs.prestashop-project.org/) - Official documentation

---

**Last Updated**: February 2026  
**PrestaShop Version**: 9.0+  
**Maintainer**: PrestaShop Community

---

**Still need help?** Don't hesitate to reach out to the community! We're here to help. 🤝
