# 🔧 PrestaShop Docker Troubleshooting Guide for Windows

This Windows-specific guide helps you resolve common issues when running PrestaShop with Docker on Windows 10/11.

## 📋 Table of Contents

- [Quick Diagnostics](#-quick-diagnostics)
- [Permission Errors](#-permission-errors)
- [Database Connection Issues](#-database-connection-issues)
- [Port Conflicts](#-port-conflicts)
- [Docker Desktop Issues](#-docker-desktop-issues)
- [WSL 2 Problems](#-wsl-2-problems)
- [Performance Problems](#-performance-problems)
- [Windows Firewall Issues](#-windows-firewall-issues)
- [Installation Failures](#-installation-failures)
- [Getting Help](#-getting-help)

---

## 🩺 Quick Diagnostics

Before diving into specific issues, gather information with these commands:

**Command Prompt or Git Bash**:
```bash
# Check Docker version
docker --version

# Check container status
docker compose ps

# View recent logs
docker compose logs --tail=50 prestashop-git

# Check Docker disk space
docker system df
```

**PowerShell** (as Administrator):
```powershell
# Check WSL status
wsl --list --verbose

# Check network connections
Get-NetTCPConnection | Where-Object {$_.LocalPort -eq 8001}
```

---

## 🔐 Permission Errors

### Problem: "Permission denied" errors in logs

This is the most common issue on Windows when using Docker.

**Symptoms**:
- Error: `Failed to open stream: Permission denied`
- Cannot write to `/var/www/html/var/logs/`
- Cannot write to `/var/www/html/var/cache/`
- PrestaShop installation fails

**Example Error**:
```
Warning: file_put_contents(/var/www/html/var/logs/20260207_exception.log): 
Failed to open stream: Permission denied
```

### Solution 1: Set User ID and Group ID

**Using Git Bash** (recommended):
```bash
# Navigate to PrestaShop directory
cd C:/Users/YourName/Documents/PrestaShop

# Set environment variables
export USER_ID=$(id -u)
export GROUP_ID=$(id -g)

# Rebuild and restart
docker compose down
docker compose build
docker compose up -d
```

**Using PowerShell**:
```powershell
# Navigate to PrestaShop directory
cd C:\Users\YourName\Documents\PrestaShop

# Set environment variables
$env:USER_ID=1000
$env:GROUP_ID=1000

# Rebuild and restart
docker compose down
docker compose build
docker compose up -d
```

### Solution 2: Add to .env File (Permanent)

**Using Git Bash**:
```bash
echo "USER_ID=1000" >> .env
echo "GROUP_ID=1000" >> .env
```

**Using Notepad**:
1. Open Notepad
2. Create/edit file: `C:\Users\YourName\Documents\PrestaShop\.env`
3. Add these lines:
   ```
   USER_ID=1000
   GROUP_ID=1000
   ```
4. Save file (Ctrl+S)
5. Restart containers

### Solution 3: Complete Reset

If permissions are still broken:

```bash
# Stop everything
docker compose down -v

# Remove var directories
rmdir /S var\logs
rmdir /S var\cache

# Rebuild
docker compose build --no-cache
docker compose up -d
```

### Solution 4: Fix WSL 2 Permissions

If using WSL 2 and still having issues:

```bash
# Inside WSL
sudo chown -R $(whoami):$(whoami) .
```

---

## 🗄️ Database Connection Issues

### Problem: "Can't connect to MySQL server"

**Symptoms**:
- Error: `ERROR 2002 (HY000): Can't connect to server on 'mysql'`
- Installation fails at database step
- PrestaShop can't start

### Solution 1: Wait for MySQL to Initialize

MySQL takes time to start on first run:

```bash
# Check MySQL logs
docker compose logs -f mysql

# Wait for this message:
# "mysqld: ready for connections"
```

⏰ **First startup can take 30-60 seconds for MySQL**

### Solution 2: Verify Database Settings

Check `.env` file in PrestaShop directory:

```
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

# Start fresh
docker compose up -d
```

### Solution 4: Check Docker Network

Verify containers can communicate:

```bash
# Check network exists
docker network ls | findstr prestashop

# Test connectivity
docker compose exec prestashop-git ping -c 3 mysql
```

### Problem: "Table doesn't exist" Error

**Symptoms**:
- Error: `Table 'prestashop.ps_hook' doesn't exist`
- Container exits with code 3
- Occurs during email configuration
- Database is empty but config file exists

**Example Error**:
```
* Configuring emails to use maildev ...
PrestaShopDatabaseException: Table 'prestashop.ps_hook' doesn't exist
prestashop-git-1 exited with code 3
```

### Solution: This Has Been Fixed! ✅

The latest version automatically checks if database tables exist before running commands.

**If you still see this error**:

1. **Pull latest changes**:
   ```bash
   # In Git Bash or PowerShell
   git pull origin develop
   ```

2. **Clean restart**:
   ```bash
   # Stop everything
   docker compose down -v
   
   # Remove old config
   rm app/config/parameters.php
   
   # Rebuild
   docker compose build
   docker compose up -d
   ```

3. **Force fresh installation** (PowerShell):
   ```powershell
   # Set environment variable
   $env:PS_ERASE_DB=1
   
   # Restart
   docker compose down
   docker compose up -d
   ```

   Or in Git Bash:
   ```bash
   export PS_ERASE_DB=1
   docker compose down
   docker compose up -d
   ```

4. **Manual maildev configuration** (after install):
   ```bash
   docker compose exec prestashop-git php bin/console prestashop:config set PS_MAIL_METHOD --value 2
   docker compose exec prestashop-git php bin/console prestashop:config set PS_MAIL_SERVER --value maildev
   docker compose exec prestashop-git php bin/console prestashop:config set PS_MAIL_SMTP_PORT --value 1025
   ```

---

## 🔌 Port Conflicts

### Problem: "Port 8001 is already in use"

**Symptoms**:
- Error: `Bind for 0.0.0.0:8001 failed: port is already allocated`
- Can't start containers
- Another application using the port

### Solution 1: Find and Stop Process

**PowerShell (as Administrator)**:
```powershell
# Find what's using port 8001
Get-NetTCPConnection -LocalPort 8001 | Select-Object OwningProcess

# Get process details
Get-Process -Id <PID>

# Stop the process
Stop-Process -Id <PID> -Force
```

**Command Prompt (as Administrator)**:
```cmd
# Find what's using port 8001
netstat -ano | findstr :8001

# Stop the process (replace <PID> with actual number)
taskkill /PID <PID> /F
```

### Solution 2: Change PrestaShop Port

Edit `docker-compose.yml`:

**Using Notepad**:
1. Open: `C:\Users\YourName\Documents\PrestaShop\docker-compose.yml`
2. Find line: `"8001:80"`
3. Change to: `"8080:80"`
4. Save file
5. Restart:
   ```bash
   docker compose down
   docker compose up -d
   ```
6. Access at: `http://localhost:8080`

### Solution 3: Check All Ports

PrestaShop uses multiple ports:

**PowerShell**:
```powershell
# Check port 8001 (PrestaShop HTTP)
Get-NetTCPConnection -LocalPort 8001

# Check port 3306 (MySQL)
Get-NetTCPConnection -LocalPort 3306

# Check port 1080 (MailDev)
Get-NetTCPConnection -LocalPort 1080
```

---

## 🐳 Docker Desktop Issues

### Problem: Docker Desktop Won't Start

**Symptoms**:
- Docker icon shows error
- "Docker is starting..." never completes
- Error messages on startup

### Solution 1: Restart Docker Desktop

1. Right-click Docker icon in system tray
2. Click "Quit Docker Desktop"
3. Wait 10 seconds
4. Press `Windows key`, type "Docker Desktop"
5. Click to start it

### Solution 2: Restart Docker Service

**PowerShell (as Administrator)**:
```powershell
# Stop Docker service
Stop-Service com.docker.service

# Start Docker service
Start-Service com.docker.service
```

### Solution 3: Reset Docker Desktop

1. Right-click Docker icon → Troubleshoot
2. Click "Reset to factory defaults"
3. Click "Reset"
4. Wait for reset to complete
5. Restart Docker Desktop

### Problem: "Hardware assisted virtualization is not enabled"

**Solution - Enable Virtualization in BIOS**:

1. Restart your computer
2. Enter BIOS (press F2, F12, Delete, or Esc during boot)
3. Look for these settings:
   - "Intel Virtualization Technology" or "Intel VT-x"
   - "AMD-V" (for AMD processors)
4. Enable the setting
5. Save changes and exit BIOS (usually F10)
6. Start Windows and try Docker again

### Problem: Container Keeps Restarting

**Check logs**:
```bash
docker compose logs prestashop-git
```

**Increase resources**:
1. Right-click Docker icon → Settings
2. Go to Resources → Advanced
3. Increase:
   - **Memory**: At least 4GB (6GB recommended)
   - **CPU**: At least 2 cores (4 recommended)
4. Click "Apply & Restart"

---

## 🔧 WSL 2 Problems

### Problem: "WSL 2 installation is incomplete"

**Solution - Install/Update WSL 2**:

**PowerShell (as Administrator)**:
```powershell
# Install WSL 2
wsl --install

# Or update existing installation
wsl --update

# Set WSL 2 as default
wsl --set-default-version 2

# Restart computer
shutdown /r /t 0
```

### Problem: WSL 2 Not Detected by Docker

**Solution**:

1. Open Docker Desktop
2. Go to Settings → General
3. Ensure "Use WSL 2 based engine" is checked
4. Click "Apply & Restart"

### Problem: WSL 2 Taking Too Much Memory

**Solution - Limit WSL Memory**:

1. Create file: `C:\Users\YourName\.wslconfig`
2. Add content:
   ```
   [wsl2]
   memory=4GB
   processors=2
   swap=1GB
   ```
3. Save file
4. Restart WSL:
   ```powershell
   wsl --shutdown
   ```

### Problem: Can't Access PrestaShop Files in WSL

**Solution - Access via Windows Explorer**:

1. Open Windows Explorer
2. In address bar, type: `\\wsl$`
3. Navigate to your WSL distribution
4. Find your PrestaShop folder

**Or use this path**:
```
\\wsl$\Ubuntu\home\username\PrestaShop
```

---

## 🐌 Performance Problems

### Problem: PrestaShop is Very Slow on Windows

### Solution 1: Use WSL 2 (Best Performance)

1. Docker Desktop → Settings → General
2. Ensure "Use WSL 2 based engine" is checked
3. Click "Apply & Restart"

### Solution 2: Store Files in WSL

**Best performance**: Clone PrestaShop inside WSL:

```bash
# Open WSL terminal
wsl

# Clone in WSL
cd ~
git clone https://github.com/PrestaShop/PrestaShop.git
cd PrestaShop

# Set permissions
export USER_ID=$(id -u)
export GROUP_ID=$(id -g)

# Start
docker compose up -d
```

### Solution 3: Allocate More Resources

1. Right-click Docker icon → Settings
2. Go to Resources → Advanced
3. Increase:
   - **Memory**: 6-8GB
   - **CPU**: 4+ cores
   - **Disk**: 60GB+
4. Click "Apply & Restart"

### Solution 4: Disable Antivirus Scanning

Add PrestaShop folder to antivirus exclusions:

**Windows Defender**:
1. Settings → Update & Security → Windows Security
2. Click "Virus & threat protection"
3. Scroll to "Virus & threat protection settings"
4. Click "Manage settings"
5. Scroll to "Exclusions"
6. Click "Add or remove exclusions"
7. Add: `C:\Users\YourName\Documents\PrestaShop`

### Solution 5: Disable Xdebug

If not debugging:

```bash
# Check if Xdebug is enabled
docker compose exec prestashop-git php -v

# Rebuild without Xdebug
$env:INSTALL_XDEBUG="false"  # PowerShell
docker compose down
docker compose build
docker compose up -d
```

---

## 🛡️ Windows Firewall Issues

### Problem: Firewall Blocking Docker

**Symptoms**:
- Can't access localhost:8001
- Containers can't communicate
- Network errors in logs

### Solution 1: Allow Docker Through Firewall

1. Press `Windows key`, type "firewall"
2. Click "Windows Defender Firewall"
3. Click "Allow an app or feature through Windows Defender Firewall"
4. Click "Change settings"
5. Find "Docker Desktop" in list
6. Check both "Private" and "Public"
7. Click "OK"

### Solution 2: Create Firewall Rules

**PowerShell (as Administrator)**:
```powershell
# Allow Docker Desktop
New-NetFirewallRule -DisplayName "Docker Desktop" -Direction Inbound -Program "C:\Program Files\Docker\Docker\Docker Desktop.exe" -Action Allow

# Allow port 8001
New-NetFirewallRule -DisplayName "PrestaShop HTTP" -Direction Inbound -LocalPort 8001 -Protocol TCP -Action Allow
```

### Solution 3: Temporarily Disable Firewall (Testing Only)

⚠️ **Not recommended for production!**

1. Control Panel → System and Security → Windows Defender Firewall
2. Click "Turn Windows Defender Firewall on or off"
3. Select "Turn off" for testing
4. Test PrestaShop
5. **Remember to turn it back on!**

---

## 💥 Installation Failures

### Problem: PrestaShop Installation Fails

### Solution 1: Check System Requirements

Verify your system:
- Windows 10/11 64-bit ✅
- 4GB+ RAM available ✅
- 10GB+ disk space ✅
- Virtualization enabled ✅

**Check available disk space**:
```cmd
wmic logicaldisk get size,freespace,caption
```

### Solution 2: Fresh Installation

Complete reset:

```bash
# Stop everything
docker compose down -v

# Remove volumes
docker volume prune -f

# Remove configuration
del app\config\parameters.php
del app\config\parameters.yml

# Remove var directories
rmdir /S var\cache
rmdir /S var\logs

# Fresh start
docker compose build --no-cache
docker compose up -d
```

### Solution 3: Manual Installation

If auto-install fails:

**PowerShell**:
```powershell
# Disable auto-install
$env:PS_INSTALL_AUTO=0

# Start containers
docker compose up -d

# Open browser to:
# http://localhost:8001/install-dev
```

Follow web installer steps.

### Solution 4: Clean Up Docker

Free up space:

```bash
# Remove stopped containers
docker container prune -f

# Remove unused images
docker image prune -a -f

# Remove unused volumes
docker volume prune -f

# Remove everything unused
docker system prune -a -f
```

---

## 🔍 Advanced Windows Diagnostics

### Check Docker Installation

**PowerShell**:
```powershell
# Docker version
docker --version

# Docker info
docker info

# WSL version
wsl --list --verbose

# Docker service status
Get-Service com.docker.service
```

### Check Container Health

```bash
# Container status
docker compose ps

# Container stats
docker stats --no-stream

# Inspect container
docker inspect prestashop-git-1
```

### Check Logs

```bash
# All logs
docker compose logs

# Specific service
docker compose logs prestashop-git
docker compose logs mysql
docker compose logs maildev

# Last 100 lines
docker compose logs --tail=100

# Follow logs
docker compose logs -f
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

# Exit
exit
```

---

## 🛠️ Common Fixes Checklist

Before asking for help, try these:

- [ ] Docker Desktop is running (check system tray)
- [ ] Run `docker compose ps` to see status
- [ ] Check logs: `docker compose logs prestashop-git`
- [ ] Verify ports aren't in use (8001, 3306, 1080)
- [ ] Ensure enough disk space (10GB+)
- [ ] Allocate enough memory (4GB+ to Docker)
- [ ] Set USER_ID and GROUP_ID environment variables
- [ ] Try rebuilding: `docker compose build --no-cache`
- [ ] Try fresh start: `docker compose down -v && docker compose up -d`
- [ ] Check firewall settings
- [ ] Verify WSL 2 is working

---

## 💡 Windows-Specific Best Practices

### Performance Tips

1. **Use WSL 2**: Much faster than Hyper-V
2. **Store in WSL**: Clone inside WSL filesystem for best performance
3. **Allocate Resources**: Give Docker 4GB+ RAM, 4+ CPU cores
4. **Use SSD**: Docker runs better on SSD
5. **Exclude from Antivirus**: Add PrestaShop folder to exclusions

### Development Tips

1. **Use Git Bash**: Better than Command Prompt
2. **Install Windows Terminal**: Modern terminal app
3. **Enable Developer Mode**: Windows Settings → Developer Mode
4. **Use VS Code**: Best code editor for Windows
5. **Regular Cleanup**: Run `docker system prune` weekly

### Security Tips

1. **Change Admin Password**: Immediately after first login
2. **Keep Software Updated**: Docker, WSL, Windows
3. **Use Strong Passwords**: For database and admin
4. **Enable Firewall**: Keep Windows Firewall on
5. **Backup Regularly**: Back up your data

---

## 📞 Getting Help

### Gather Information

Before asking for help, collect:

```bash
# System info
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
docker --version
docker compose --version
wsl --list --verbose

# Container status
docker compose ps

# Recent logs
docker compose logs --tail=200 > prestashop-logs.txt

# Environment
type .env
```

### Search Existing Issues

- [GitHub Issues](https://github.com/PrestaShop/PrestaShop/issues)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/prestashop)
- [PrestaShop Forums](https://www.prestashop.com/forums/)

### Ask the Community

- 💬 [Slack](https://www.prestashop-project.org/slack/)
- 💭 [GitHub Discussions](https://github.com/PrestaShop/PrestaShop/discussions)
- 📚 [Forums](https://www.prestashop.com/forums/)

### Windows-Specific Help

- [Docker Desktop for Windows](https://docs.docker.com/desktop/windows/)
- [WSL Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
- [Git for Windows](https://git-scm.com/download/win)

---

## 🎯 Quick Reference Commands

### Windows PowerShell

```powershell
# Set user ID
$env:USER_ID=1000
$env:GROUP_ID=1000

# Navigate to project
cd C:\Users\YourName\Documents\PrestaShop

# Container management
docker compose up -d
docker compose down
docker compose restart
docker compose ps
docker compose logs -f

# WSL commands
wsl --list --verbose
wsl --update
wsl --shutdown
```

### Git Bash / Command Prompt

```bash
# Set user ID
export USER_ID=$(id -u)
export GROUP_ID=$(id -g)

# Container management
docker compose up -d
docker compose down
docker compose restart
docker compose ps
docker compose logs -f

# Cleanup
docker system prune -a
docker volume prune
```

---

## 📚 Related Documentation

- [Windows Installation Guide](INSTALLATION_GUIDE_WINDOWS.md)
- [Main README](README.md)
- [General Troubleshooting](TROUBLESHOOTING.md)
- [PrestaShop DevDocs](https://devdocs.prestashop-project.org/)

---

**Last Updated**: February 2026  
**PrestaShop Version**: 9.0+  
**Platform**: Windows 10/11  
**Maintainer**: PrestaShop Community

---

**Still need help?** The PrestaShop community is here for you! 🤝
