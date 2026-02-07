# 🚨 PrestaShop Docker Installation for Windows - Quick Setup

## Permission Errors Fix for Windows

If you're experiencing **permission errors** like:
```
Permission denied in /var/www/html/var/logs/...
```

This has been **fixed**! Follow these steps:

### Quick Fix (Windows)

**Using Git Bash** (recommended):
```bash
# Navigate to PrestaShop directory
cd C:/Users/YourName/Documents/PrestaShop

# Set your user ID and group ID
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

# Set user ID and group ID
$env:USER_ID=1000
$env:GROUP_ID=1000

# Rebuild and restart
docker compose down
docker compose build
docker compose up -d
```

### Or Add to .env File (Permanent)

Create or edit `.env` file in your PrestaShop directory:

**Using Git Bash**:
```bash
echo "USER_ID=1000" >> .env
echo "GROUP_ID=1000" >> .env
```

**Using Notepad**:
1. Open Notepad
2. Open: `C:\Users\YourName\Documents\PrestaShop\.env`
3. Add these lines:
   ```
   USER_ID=1000
   GROUP_ID=1000
   ```
4. Save file
5. Restart: `docker compose down && docker compose up -d`

### For Complete Instructions

📖 **Windows-Specific Guides:**

- **[Windows Installation Guide](./Noob%20guide/INSTALLATION_GUIDE_WINDOWS.md)** ⭐ - Complete Windows setup
- **[Windows Troubleshooting Guide](./Noob%20guide/TROUBLESHOOTING_WINDOWS.md)** ⭐ - Windows-specific solutions

**Multi-Platform Guides:**
- [General Installation Guide](./Noob%20guide/INSTALLATION_GUIDE.md) - All platforms
- [General Troubleshooting Guide](./Noob%20guide/TROUBLESHOOTING.md) - All platforms

### What Was Fixed

The Docker startup script (`.docker/docker_run_git.sh`) now automatically:
- Creates the `var/logs` and `var/cache` directories
- Sets correct ownership (`www-data:www-data`)
- Sets correct permissions (`775`)

This prevents the permission errors that were occurring during installation.

### Common Windows Issues

**Docker Desktop not starting?**
- Restart Docker Desktop
- Enable WSL 2 in Docker settings
- Enable virtualization in BIOS

**Port 8001 already in use?**
```powershell
# PowerShell (as Administrator)
Get-NetTCPConnection -LocalPort 8001 | Select-Object OwningProcess
Stop-Process -Id <PID> -Force
```

**Slow performance?**
- Use WSL 2 (Docker Settings → General)
- Allocate more RAM (Docker Settings → Resources)
- Clone PrestaShop inside WSL for best performance

**WSL 2 issues?**
```powershell
# PowerShell (as Administrator)
wsl --update
wsl --set-default-version 2
```

### Windows-Specific Tips

1. **Use Git Bash** for best compatibility with Docker commands
2. **Enable WSL 2** in Docker Desktop for better performance
3. **Allocate 4GB+ RAM** to Docker Desktop
4. **Add to antivirus exclusions**: `C:\Users\YourName\Documents\PrestaShop`
5. **Use Windows Terminal** for a better command-line experience

---

**Need more help?** Check the [Windows Troubleshooting Guide](./Noob%20guide/TROUBLESHOOTING_WINDOWS.md)!

**Platform**: Windows 10/11  
**Last Updated**: February 2026
