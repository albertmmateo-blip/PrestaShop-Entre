# 🚀 PrestaShop Installation Guide for Windows

**Welcome Windows Users!** This guide will help you install PrestaShop on your Windows computer using Docker. We'll walk through everything step by step!

## 📋 Table of Contents

- [What You'll Need](#-what-youll-need)
- [Step 1: Install Docker Desktop](#-step-1-install-docker-desktop)
- [Step 2: Install Git](#-step-2-install-git)
- [Step 3: Clone PrestaShop](#-step-3-clone-prestashop)
- [Step 4: Start PrestaShop](#-step-4-start-prestashop)
- [Step 5: Access Your Store](#-step-5-access-your-store)
- [Managing Your Store](#-managing-your-store)
- [Common Windows Issues & Solutions](#-common-windows-issues--solutions)
- [What's Next?](#-whats-next)

---

## 🎯 What You'll Need

Before we start, let's understand what we're working with:

- **PrestaShop**: A free, open-source e-commerce platform for creating online stores
- **Docker**: A tool that packages software so it runs the same way on any computer
- **Git**: A tool for downloading and managing code

**Time Required**: 30-45 minutes for complete setup

**Technical Skill Level**: Beginner-friendly (no coding experience required!)

**Windows Requirements**:
- Windows 10/11 (64-bit)
- At least 4GB of RAM
- At least 10GB of free disk space
- Administrator access

---

## 🐳 Step 1: Install Docker Desktop

Docker is like a virtual container that will run PrestaShop on your Windows computer without affecting anything else.

### Download Docker Desktop

1. **Visit Docker's Website**:
   - Go to: https://www.docker.com/products/docker-desktop/
   - Click "Download for Windows"
   
2. **Run the Installer**:
   - Find the downloaded file: `Docker Desktop Installer.exe`
   - Double-click to run it
   - If Windows asks for permission, click "Yes"

### Installation Settings

3. **Configure WSL 2** (Recommended):
   - During installation, you'll see a checkbox for "Use WSL 2 instead of Hyper-V"
   - ✅ **Check this box** - WSL 2 is faster and uses less resources
   - If you don't have WSL 2, Docker will help you install it

4. **Complete Installation**:
   - Click through the installation wizard
   - Wait for installation to complete (5-10 minutes)
   - Click "Finish"
   - Docker Desktop will start automatically

### Start Docker Desktop

5. **Launch Docker**:
   - Look for Docker Desktop in your Start menu
   - Click to open it
   - Wait for Docker to start completely
   - You'll see a whale icon in your system tray (bottom-right)
   - The whale icon will show "Docker Desktop is running" when ready

### Verify Installation

6. **Test Docker**:
   - Press `Windows key`, type `cmd`, press `Enter`
   - In Command Prompt, type:
   ```cmd
   docker --version
   ```
   - You should see something like: `Docker version 24.0.0, build ...`
   - If you see this, Docker is installed correctly! ✅

### 💡 Docker Desktop Tips

- **Memory**: Docker needs at least 4GB of RAM (6GB recommended)
- **Disk Space**: Make sure you have at least 10GB free
- **Settings**: Right-click Docker icon → Settings → Resources to adjust memory

### Troubleshooting Docker Installation

**Problem: "WSL 2 installation is incomplete"**
- Windows will show you how to install WSL 2
- Follow the prompts to install it
- Restart your computer
- Start Docker Desktop again

**Problem: "Hardware assisted virtualization is not enabled"**
- You need to enable virtualization in your BIOS
- Restart computer → Enter BIOS (usually F2, F12, or Delete key)
- Look for "Virtualization Technology" or "VT-x"
- Enable it → Save → Exit BIOS

---

## 📦 Step 2: Install Git

Git helps you download and manage the PrestaShop code.

### Download Git for Windows

1. **Visit Git's Website**:
   - Go to: https://git-scm.com/download/win
   - The download should start automatically
   - File name: `Git-<version>-64-bit.exe`

### Install Git

2. **Run the Installer**:
   - Double-click the downloaded file
   - Click "Yes" if Windows asks for permission

3. **Installation Settings** (Important!):
   - **Select Components**: Keep defaults, click "Next"
   - **Start Menu Folder**: Keep default, click "Next"
   - **Default Editor**: Choose your preference, click "Next"
   - **PATH Environment**: Choose **"Git from the command line and also from 3rd-party software"** ✅
   - **Line Endings**: Keep default (Checkout Windows-style, commit Unix-style)
   - **Terminal Emulator**: Choose **"Use Windows' default console window"**
   - Click "Install"

4. **Complete Installation**:
   - Wait for installation (2-3 minutes)
   - Click "Finish"

### Verify Git Installation

5. **Test Git**:
   - Open Command Prompt (press `Windows key`, type `cmd`, press `Enter`)
   - Type:
   ```cmd
   git --version
   ```
   - You should see: `git version 2.40.0` (or similar)
   - If you see this, Git is installed correctly! ✅

### 💡 Git for Windows Tips

- **Git Bash**: Git installs "Git Bash" - a Linux-like terminal for Windows
- **Find it**: Start Menu → Git → Git Bash
- **Use it**: Some commands work better in Git Bash than Command Prompt

---

## 📥 Step 3: Clone PrestaShop

Now let's download PrestaShop to your computer!

### Choose a Location

1. **Decide Where to Store PrestaShop**:
   - Recommended location: `C:\Users\YourName\Documents\PrestaShop`
   - Replace `YourName` with your actual Windows username
   - Choose a location you can easily find

### Download PrestaShop

2. **Open Command Prompt or Git Bash**:
   - **Option A - Command Prompt**: Press `Windows key`, type `cmd`, press `Enter`
   - **Option B - Git Bash**: Start Menu → Git → Git Bash (recommended)

3. **Navigate to Your Documents Folder**:
   ```bash
   cd C:\Users\YourName\Documents
   ```
   Replace `YourName` with your Windows username
   
   **Example**:
   ```bash
   cd C:\Users\John\Documents
   ```

4. **Clone PrestaShop Repository**:
   ```bash
   git clone https://github.com/PrestaShop/PrestaShop.git
   ```
   
   **What happens**:
   - Git downloads approximately 1-2GB of files
   - This takes 5-15 minutes depending on your internet speed
   - A progress bar shows the download status
   - When complete, you'll see "Cloning into 'PrestaShop'... done"

5. **Enter PrestaShop Directory**:
   ```bash
   cd PrestaShop
   ```

6. **Verify Download**:
   ```bash
   dir
   ```
   You should see many folders and files including `docker-compose.yml`

### 💡 What Just Happened?

- Git created a `PrestaShop` folder in your Documents
- All PrestaShop files are now in: `C:\Users\YourName\Documents\PrestaShop`
- You're ready to start PrestaShop!

---

## 🎬 Step 4: Start PrestaShop

Now for the exciting part – let's start PrestaShop!

### Important: Set User Permissions (Required!)

**Why?** This prevents permission errors that cause installation to fail.

1. **Open Git Bash** (recommended) or **PowerShell**:
   - **Git Bash**: Start Menu → Git → Git Bash
   - **PowerShell**: Press `Windows key`, type `powershell`, press `Enter`

2. **Navigate to PrestaShop Directory**:
   ```bash
   cd C:\Users\YourName\Documents\PrestaShop
   ```
   Replace `YourName` with your actual username

3. **Set User ID and Group ID**:
   
   **In Git Bash** (recommended):
   ```bash
   export USER_ID=$(id -u)
   export GROUP_ID=$(id -g)
   ```
   
   **In PowerShell** (alternative):
   ```powershell
   $env:USER_ID=1000
   $env:GROUP_ID=1000
   ```

💡 **Or Add to .env File** (permanent solution):
```bash
echo USER_ID=1000 >> .env
echo GROUP_ID=1000 >> .env
```

### Check Docker is Running

4. **Verify Docker Desktop**:
   - Look for the whale icon in your system tray (bottom-right)
   - It should show "Docker Desktop is running"
   - If not, open Docker Desktop and wait for it to start

### Start PrestaShop

5. **Build and Start Containers**:

   **Option A - Using Git Bash** (recommended):
   ```bash
   docker compose build
   docker compose up -d
   ```

   **Option B - Using Command Prompt**:
   ```cmd
   docker compose build
   docker compose up -d
   ```

   **What this does**:
   - `docker compose build`: Prepares containers (first time: 10-15 minutes)
   - `docker compose up -d`: Starts containers in background

### Monitor the Installation

6. **Watch the Progress**:
   ```bash
   docker compose logs -f
   ```
   
   **What to look for**:
   - "PrestaShop installed successfully" ✅
   - "Ready to accept connections" from MySQL ✅
   - No red error messages ✅
   
   **Stop viewing logs**: Press `Ctrl+C` (containers keep running)

### First-Time Setup Notes

⏰ **Be Patient!** The first time you run this:
- Docker downloads base images (1-2GB)
- Builds custom containers
- Installs dependencies
- Sets up the database
- Compiles assets
- **Total time: 15-30 minutes** depending on your computer and internet

☕ **Grab a coffee!** Subsequent startups are much faster (under 1 minute).

### Verify Installation

7. **Check Container Status**:
   ```bash
   docker compose ps
   ```
   
   You should see three services running:
   - `prestashop-git-1` - State: `Up`
   - `mysql-1` - State: `Up`
   - `maildev-1` - State: `Up`

---

## 🌐 Step 5: Access Your Store

Once installation is complete, you can access your PrestaShop store!

### Open Your Store in Browser

1. **Frontend (Customer View)**:
   - Open your web browser (Chrome, Edge, Firefox)
   - Go to: `http://localhost:8001`
   - This is what your customers would see

2. **Backend (Admin Panel)**:
   - In your browser, go to: `http://localhost:8001/admin-dev`
   - This is where you manage your store

### Login to Admin Panel

3. **Default Credentials**:
   - **Email**: `demo@prestashop.com`
   - **Password**: `Correct Horse Battery Staple`

⚠️ **Security**: Change these credentials after your first login!

### Additional Services

4. **MailDev (Email Testing)**:
   - URL: `http://localhost:1080`
   - All emails from PrestaShop appear here
   - Perfect for testing without sending real emails

5. **Database Access** (optional):
   - **Host**: `localhost`
   - **Port**: `3306`
   - **Database**: `prestashop`
   - **Username**: `root`
   - **Password**: `prestashop`
   
   Use tools like:
   - [MySQL Workbench](https://www.mysql.com/products/workbench/)
   - [HeidiSQL](https://www.heidisql.com/)
   - [DBeaver](https://dbeaver.io/)

### 🎉 Congratulations!

You now have a fully functional PrestaShop store running on your Windows computer!

---

## 🛠️ Managing Your Store

### Starting and Stopping

**Start Your Store**:
```bash
# Navigate to PrestaShop directory
cd C:\Users\YourName\Documents\PrestaShop

# Start containers
docker compose up -d
```

**Stop Your Store**:
```bash
docker compose down
```

**Restart Your Store**:
```bash
docker compose restart
```

### Viewing Logs

**See What's Happening**:
```bash
# View all logs
docker compose logs -f

# View specific service
docker compose logs -f prestashop-git
```

Press `Ctrl+C` to stop viewing logs.

### Checking Status

**See Container Status**:
```bash
docker compose ps
```

All services should show "Up" status.

### Accessing the Container

**Run Commands Inside Container**:
```bash
docker compose exec prestashop-git bash
```

Type `exit` to leave the container.

### Common Management Tasks

**Clear Cache**:
```bash
docker compose exec prestashop-git rm -rf var/cache/*
```

**Reinstall Database** (⚠️ Deletes all data!):
```bash
docker compose down -v
docker compose up -d
```

---

## 🔧 Common Windows Issues & Solutions

### Issue 1: "Port 8001 is already in use"

**Problem**: Another application is using port 8001.

**Solution - Find and Stop Conflicting Process**:

**PowerShell (as Administrator)**:
```powershell
# Find what's using port 8001
Get-NetTCPConnection -LocalPort 8001

# Stop the process (replace <PID> with actual process ID)
Stop-Process -Id <PID> -Force
```

**Alternative - Use Different Port**:
1. Open `docker-compose.yml` in Notepad
2. Find line: `"8001:80"`
3. Change to: `"8080:80"`
4. Save file
5. Restart: `docker compose down && docker compose up -d`
6. Access at: `http://localhost:8080`

### Issue 2: "Cannot connect to the Docker daemon"

**Problem**: Docker Desktop is not running.

**Solution**:
1. Press `Windows key`
2. Type "Docker Desktop"
3. Click to open it
4. Wait for it to fully start (whale icon in system tray)
5. Try your command again

### Issue 3: Docker Build Fails - Not Enough Memory

**Problem**: Docker needs more RAM.

**Solution**:
1. Right-click Docker icon in system tray
2. Click "Settings"
3. Go to "Resources" → "Advanced"
4. Increase Memory to at least 4GB (6GB recommended)
5. Click "Apply & Restart"

### Issue 4: Permission Denied Errors

**Problem**: Container can't write to directories.

**Solution - Set User ID**:

**Git Bash**:
```bash
export USER_ID=$(id -u)
export GROUP_ID=$(id -g)
docker compose down
docker compose build
docker compose up -d
```

**PowerShell**:
```powershell
$env:USER_ID=1000
$env:GROUP_ID=1000
docker compose down
docker compose build
docker compose up -d
```

### Issue 5: WSL 2 Issues

**Problem**: WSL 2 not working properly.

**Solution - Update WSL**:

**PowerShell (as Administrator)**:
```powershell
# Update WSL to latest version
wsl --update

# Check WSL version
wsl --list --verbose

# Set WSL 2 as default
wsl --set-default-version 2
```

### Issue 6: Firewall Blocking Docker

**Problem**: Windows Firewall blocks Docker.

**Solution**:
1. Press `Windows key`
2. Type "Windows Defender Firewall"
3. Click "Allow an app through firewall"
4. Find "Docker Desktop" in the list
5. Check both "Private" and "Public"
6. Click "OK"

### Issue 7: Slow Performance

**Problem**: PrestaShop is slow on Windows.

**Solutions**:

**1. Use WSL 2** (best performance):
- Docker Desktop → Settings → General
- Ensure "Use WSL 2 based engine" is checked

**2. Allocate More Resources**:
- Docker Desktop → Settings → Resources
- Increase CPU and Memory

**3. Store Files in WSL**:
- Clone PrestaShop inside WSL for better performance
- Access via: `\\wsl$\Ubuntu\home\username\PrestaShop`

### Issue 8: "localhost refused to connect"

**Problem**: Can't access PrestaShop in browser.

**Solutions**:

**Check container status**:
```bash
docker compose ps
```

**Wait longer** - First startup takes 15-20 minutes

**Check logs for errors**:
```bash
docker compose logs prestashop-git
```

**Restart containers**:
```bash
docker compose restart
```

### Getting More Help

**If still stuck**:
1. Check logs: `docker compose logs`
2. Search [GitHub Issues](https://github.com/PrestaShop/PrestaShop/issues)
3. Ask on [Slack](https://www.prestashop-project.org/slack/)
4. Post on [Forums](https://www.prestashop.com/forums/)

---

## 🎓 What's Next?

### Explore the Admin Panel

1. **Login**:
   - Go to: `http://localhost:8001/admin-dev`
   - Use default credentials

2. **Browse Sections**:
   - Dashboard - Overview of your store
   - Catalog → Products - Add products
   - Design → Theme - Customize appearance
   - Modules - Add functionality

### Customize Your Store

**Upload Your Logo**:
- Design → Theme & Logo
- Click "Add logo"
- Upload your image

**Change Colors**:
- Design → Theme & Logo
- Use the color picker
- Save changes

### Add Your First Product

1. Go to: Catalog → Products
2. Click "Add new product"
3. Fill in:
   - Product name
   - Description
   - Price
   - Upload images
4. Click "Save"

### Learn More

**Official Documentation**:
- [User Guide](https://docs.prestashop-project.org/)
- [Developer Docs](https://devdocs.prestashop-project.org/)
- [Module Development](https://devdocs.prestashop-project.org/9/modules/)

**Video Tutorials**:
- [PrestaShop YouTube](https://www.youtube.com/user/prestashop)

**Development Tools**:
- [VS Code](https://code.visualstudio.com/) - Best code editor for Windows
- [Windows Terminal](https://apps.microsoft.com/store/detail/windows-terminal/) - Better command line

### Environment Variables

Create `.env` file for custom settings:

```bash
# Database
DB_PASSWD=your_secure_password
DB_NAME=prestashop

# Admin Credentials
ADMIN_MAIL=your-email@example.com
ADMIN_PASSWD=YourSecurePassword

# PrestaShop Settings
PS_DOMAIN=localhost:8001
PS_DEV_MODE=1

# User IDs (Windows with WSL/Git Bash)
USER_ID=1000
GROUP_ID=1000
```

### Useful Commands for Windows

```bash
# Container Management
docker compose up -d           # Start
docker compose down            # Stop
docker compose restart         # Restart
docker compose ps              # Status
docker compose logs -f         # View logs

# Development
docker compose exec prestashop-git bash  # Access container
docker compose exec prestashop-git rm -rf var/cache/*  # Clear cache

# Cleanup
docker compose down -v         # Stop and remove volumes
docker system prune -a         # Clean up Docker
```

---

## 🎯 Windows-Specific Tips

### For Best Performance

1. **Use WSL 2**: Much faster than Hyper-V
2. **Store in WSL**: Clone PrestaShop in WSL filesystem
3. **Allocate Resources**: Give Docker 4GB+ RAM
4. **Close Other Apps**: Free up system resources
5. **Use SSD**: Docker runs better on SSD than HDD

### For Development

1. **Use Git Bash**: Better than Command Prompt for development
2. **Install Windows Terminal**: Modern terminal with tabs
3. **Enable Developer Mode**: Settings → Update & Security → Developer Mode
4. **Use VS Code**: Best editor for Windows development

### Security Best Practices

1. **Change Admin Password**: Do this immediately after first login
2. **Keep Docker Updated**: Check for updates regularly
3. **Use Strong Passwords**: For database and admin
4. **Enable Firewall**: Keep Windows Firewall on
5. **Backup Data**: Regularly backup your store

---

## 📞 Support

**Need help?**

**Community Support**:
- 💬 [Slack](https://www.prestashop-project.org/slack/)
- 💭 [GitHub Discussions](https://github.com/PrestaShop/PrestaShop/discussions)
- 📚 [Forums](https://www.prestashop.com/forums/)

**Documentation**:
- 📖 [User Docs](https://docs.prestashop-project.org/)
- 🔧 [Developer Docs](https://devdocs.prestashop-project.org/)
- 🐛 [Report Issues](https://github.com/PrestaShop/PrestaShop/issues)

**Windows-Specific Help**:
- [Docker Desktop for Windows](https://docs.docker.com/desktop/windows/)
- [WSL 2 Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
- [Git for Windows](https://git-scm.com/download/win)

---

## 🏁 Summary

You now have:

✅ Docker Desktop installed on Windows  
✅ Git for Windows installed  
✅ PrestaShop downloaded and running  
✅ Access to admin panel and frontend  
✅ Email testing with MailDev  
✅ Knowledge of common Windows issues and solutions  

**Remember**: Development is a learning process. Don't worry if you encounter issues – they're opportunities to learn!

**Happy coding on Windows! 🚀**

---

## 📄 License

PrestaShop is licensed under the [Academic Free License (AFL 3.0)](../LICENSE.md)

---

**Last Updated**: February 2026  
**PrestaShop Version**: 9.0+  
**Platform**: Windows 10/11  
**Maintainer**: PrestaShop Community
