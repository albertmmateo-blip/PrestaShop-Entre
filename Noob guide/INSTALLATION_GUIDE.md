# 🚀 PrestaShop Installation Guide for Beginners

**Welcome!** This guide will help you install PrestaShop on your local computer using Docker. Don't worry if you're new to this – we'll walk through everything step by step!

## 📋 Table of Contents

- [What You'll Need](#-what-youll-need)
- [Step 1: Install Docker Desktop](#-step-1-install-docker-desktop)
- [Step 2: Install Git](#-step-2-install-git)
- [Step 3: Clone PrestaShop](#-step-3-clone-prestashop)
- [Step 4: Start PrestaShop](#-step-4-start-prestashop)
- [Step 5: Access Your Store](#-step-5-access-your-store)
- [Managing Your Store](#-managing-your-store)
- [Common Issues & Solutions](#-common-issues--solutions)
- [What's Next?](#-whats-next)

---

## 🎯 What You'll Need

Before we start, let's understand what we're working with:

- **PrestaShop**: A free, open-source e-commerce platform for creating online stores
- **Docker**: A tool that packages software so it runs the same way on any computer
- **Git**: A tool for downloading and managing code

**Time Required**: 30-45 minutes for complete setup

**Technical Skill Level**: Beginner-friendly (no coding experience required!)

---

## 🐳 Step 1: Install Docker Desktop

Docker is like a virtual container that will run PrestaShop on your computer without affecting anything else.

### Windows

1. **Download Docker Desktop**:
   - Visit: https://www.docker.com/products/docker-desktop/
   - Click "Download for Windows"
   
2. **Install Docker Desktop**:
   - Run the downloaded installer (Docker Desktop Installer.exe)
   - Follow the installation wizard
   - When prompted, enable WSL 2 (Windows Subsystem for Linux) - this is recommended
   
3. **Start Docker**:
   - Docker Desktop should start automatically
   - You'll see a whale icon in your system tray when it's running
   - Wait for it to say "Docker Desktop is running"

4. **Verify Installation**:
   - Open Command Prompt (press Windows key, type "cmd", press Enter)
   - Type: `docker --version`
   - You should see something like: `Docker version 24.0.0`

### macOS

1. **Download Docker Desktop**:
   - Visit: https://www.docker.com/products/docker-desktop/
   - Click "Download for Mac"
   - Choose the correct version:
     - **Mac with Intel chip**: Download Intel version
     - **Mac with Apple chip (M1/M2/M3)**: Download Apple Silicon version
   
2. **Install Docker Desktop**:
   - Open the downloaded .dmg file
   - Drag Docker to your Applications folder
   - Open Docker from Applications
   - Grant necessary permissions when prompted
   
3. **Start Docker**:
   - Docker Desktop should start automatically
   - You'll see a whale icon in your menu bar when it's running
   - Wait for the indicator to turn green
   
4. **Verify Installation**:
   - Open Terminal (press Cmd+Space, type "terminal", press Enter)
   - Type: `docker --version`
   - You should see something like: `Docker version 24.0.0`

### Linux

1. **Install Docker**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install docker.io docker-compose
   
   # Fedora
   sudo dnf install docker docker-compose
   
   # Arch Linux
   sudo pacman -S docker docker-compose
   ```

2. **Start Docker Service**:
   ```bash
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

3. **Add Your User to Docker Group** (to run Docker without sudo):
   ```bash
   sudo usermod -aG docker $USER
   ```
   **Note**: Log out and log back in for this to take effect

4. **Verify Installation**:
   ```bash
   docker --version
   docker-compose --version
   ```

### 💡 Docker Desktop Tips

- **Memory**: Docker needs at least 4GB of RAM to run PrestaShop smoothly
- **Disk Space**: Make sure you have at least 10GB of free disk space
- **Settings**: Open Docker Desktop settings to adjust memory and CPU allocation if needed

---

## 📦 Step 2: Install Git

Git helps you download and manage the PrestaShop code.

### Windows

1. **Download Git**:
   - Visit: https://git-scm.com/download/win
   - The download should start automatically
   
2. **Install Git**:
   - Run the downloaded installer
   - Use the default settings (just keep clicking "Next")
   - On the "Adjusting your PATH environment" screen, select "Git from the command line and also from 3rd-party software"
   
3. **Verify Installation**:
   - Open Command Prompt
   - Type: `git --version`
   - You should see something like: `git version 2.40.0`

### macOS

1. **Install Git** (easiest method):
   - Open Terminal
   - Type: `git --version`
   - If Git is not installed, macOS will prompt you to install it
   - Click "Install" and follow the prompts
   
   **Alternative**: Install via Homebrew
   ```bash
   # Install Homebrew if you don't have it
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Install Git
   brew install git
   ```

2. **Verify Installation**:
   ```bash
   git --version
   ```

### Linux

Git is usually pre-installed on Linux. If not:

```bash
# Ubuntu/Debian
sudo apt-get install git

# Fedora
sudo dnf install git

# Arch Linux
sudo pacman -S git
```

Verify:
```bash
git --version
```

---

## 📥 Step 3: Clone PrestaShop

Now let's download PrestaShop to your computer!

### Choose a Location

First, decide where you want to store PrestaShop on your computer. We recommend:
- **Windows**: `C:\Users\YourName\Documents\PrestaShop`
- **macOS**: `/Users/YourName/Documents/PrestaShop`
- **Linux**: `/home/YourName/Documents/PrestaShop`

### Download PrestaShop

1. **Open Your Terminal/Command Prompt**:
   - **Windows**: Press Windows key, type "cmd", press Enter
   - **macOS**: Press Cmd+Space, type "terminal", press Enter
   - **Linux**: Press Ctrl+Alt+T

2. **Navigate to Your Desired Location**:
   ```bash
   # Windows
   cd C:\Users\YourName\Documents
   
   # macOS/Linux
   cd ~/Documents
   ```

3. **Clone the Repository**:
   ```bash
   git clone https://github.com/PrestaShop/PrestaShop.git
   cd PrestaShop
   ```
   
   This will:
   - Download all PrestaShop files (this may take a few minutes)
   - Create a "PrestaShop" folder
   - Navigate into that folder

4. **What Just Happened?**
   - Git downloaded approximately 1-2GB of files
   - You now have a complete copy of PrestaShop on your computer
   - All the code and files are in the "PrestaShop" folder

---

## 🎬 Step 4: Start PrestaShop

Now for the exciting part – let's start PrestaShop!

### Important: Set User Permissions (Required!)

To avoid permission errors, set your user ID and group ID:

**Windows (Git Bash or WSL)**:
```bash
export USER_ID=$(id -u)
export GROUP_ID=$(id -g)
```

**macOS/Linux**:
```bash
export USER_ID=$(id -u)
export GROUP_ID=$(id -g)
```

**Or add to `.env` file** (recommended for permanent setup):
```bash
# Create or edit .env file
echo "USER_ID=$(id -u)" >> .env
echo "GROUP_ID=$(id -g)" >> .env
```

💡 **Why?** This ensures the Docker container can write to your files without permission errors.

### Check Docker is Running

Before starting, make sure Docker Desktop is running:
- **Windows/macOS**: Look for the whale icon in your system tray/menu bar
- **Linux**: Run `sudo systemctl status docker`

### Start PrestaShop with Make (Recommended)

If you have `make` installed (pre-installed on macOS/Linux, needs installation on Windows):

```bash
make docker-start
```

**What this does**:
1. Builds Docker containers (first time takes 10-15 minutes)
2. Downloads MySQL database server
3. Downloads MailDev (for testing emails)
4. Installs PrestaShop automatically
5. Compiles all necessary assets

**Progress Indicators**:
- You'll see lots of text scrolling by – this is normal!
- Wait for messages indicating services are ready
- First-time setup can take 15-20 minutes

### Start PrestaShop with Docker Compose (Alternative Method)

If you don't have `make` or prefer using Docker directly:

```bash
docker compose build
docker compose up -d
```

**Explanation**:
- `docker compose build`: Prepares all the containers
- `docker compose up -d`: Starts containers in the background (`-d` means "detached mode")

### Monitor the Installation

To see what's happening:

```bash
docker compose logs -f
```

Press `Ctrl+C` to stop viewing logs (containers keep running).

**What to Look For**:
- Messages like "PrestaShop installed successfully"
- "Ready to accept connections" from MySQL
- No error messages in red

### First-Time Setup Notes

⏰ **Be Patient**: The first time you run this:
- Docker downloads base images (1-2GB)
- Builds custom containers
- Installs dependencies
- Sets up the database
- **Total time: 15-30 minutes** depending on your internet speed

☕ **Grab a coffee!** Subsequent startups are much faster (under 1 minute).

---

## 🌐 Step 5: Access Your Store

Once installation is complete, you can access your PrestaShop store!

### Open Your Store

Open your web browser and go to:

**Frontend (Customer View)**:
```
http://localhost:8001
```

This is what your customers would see.

**Backend (Admin Panel)**:
```
http://localhost:8001/admin-dev
```

This is where you manage your store.

### Login to Admin Panel

Use these default credentials:

- **Email**: `demo@prestashop.com`
- **Password**: `Correct Horse Battery Staple`

⚠️ **Important**: Change these credentials after your first login for security!

### Additional Services

**MailDev (Email Testing)**:
```
http://localhost:1080
```

All emails sent by PrestaShop appear here instead of actually being sent. Perfect for testing!

**Database Access**:
- **Host**: `localhost`
- **Port**: `3306`
- **Database**: `prestashop`
- **Username**: `root`
- **Password**: `prestashop`

Use a tool like [MySQL Workbench](https://www.mysql.com/products/workbench/) or [phpMyAdmin](https://www.phpmyadmin.net/) to connect.

### 🎉 Congratulations!

You now have a fully functional PrestaShop store running on your computer!

---

## 🛠️ Managing Your Store

### Starting and Stopping

**Start Your Store**:
```bash
# Using make (recommended)
make docker-up

# Or using docker compose
docker compose up -d
```

**Stop Your Store**:
```bash
# Using make (recommended)
make docker-down

# Or using docker compose
docker compose down
```

**Restart Your Store**:
```bash
# Using make (recommended)
make docker-restart

# Or using docker compose
docker compose restart
```

**View Live Logs**:
```bash
# Using make
make docker-logs

# Or using docker compose
docker compose logs -f
```

### Checking Status

To see if containers are running:

```bash
docker compose ps
```

You should see three services:
- `prestashop-git` (the main PrestaShop application)
- `mysql` (the database)
- `maildev` (email testing)

All should show "Up" status.

### Accessing the Container

Sometimes you need to run commands inside the PrestaShop container:

```bash
# Using make (recommended)
make docker-sh

# Or using docker compose
docker compose exec prestashop-git bash
```

This gives you a command prompt inside the container. Type `exit` to leave.

### Common Management Tasks

**Clear Cache**:
```bash
make cc
```

**Reinstall Database**:
```bash
make install-prestashop
```
⚠️ **Warning**: This deletes all your data and starts fresh!

**Update Dependencies**:
```bash
make composer
```

**Build Assets**:
```bash
make assets
```

---

## 🔧 Common Issues & Solutions

⚠️ **Experiencing problems?** See our comprehensive [Troubleshooting Guide](TROUBLESHOOTING.md) for detailed solutions!

### Issue 0: Permission Denied Errors (Most Common!)

**Problem**: Errors like "Permission denied" when writing to `/var/www/html/var/logs/` or `/var/www/html/var/cache/`.

**Symptoms**:
```
Warning: file_put_contents(/var/www/html/var/logs/...): Failed to open stream: Permission denied
```

**Solution**:

**Method 1 - Set User ID (Recommended)**:
```bash
# Set environment variables
export USER_ID=$(id -u)
export GROUP_ID=$(id -g)

# Rebuild and restart
docker compose down
docker compose build
docker compose up -d
```

**Method 2 - Fix Permissions Manually**:
```bash
# Stop containers
docker compose down

# Fix ownership
sudo chown -R $(id -u):$(id -g) var/

# Fix permissions  
chmod -R 775 var/logs var/cache

# Restart
docker compose up -d
```

**Method 3 - Complete Reset**:
```bash
# If above doesn't work, start fresh
docker compose down -v
rm -rf var/logs/* var/cache/*
docker compose up -d --build
```

📖 **For more details**: See the [Permission Errors section in the Troubleshooting Guide](TROUBLESHOOTING.md#-permission-errors)

### Issue 1: "Port 8001 is already in use"

**Problem**: Another application is using port 8001.

**Solution 1** - Stop the conflicting application:
```bash
# Windows (PowerShell)
Get-Process -Id (Get-NetTCPConnection -LocalPort 8001).OwningProcess | Stop-Process

# macOS/Linux
lsof -ti:8001 | xargs kill
```

**Solution 2** - Use a different port:
1. Open `docker-compose.yml`
2. Find the line with `"8001:80"`
3. Change it to `"8080:80"` (or any unused port)
4. Access your store at `http://localhost:8080`

### Issue 2: "Cannot connect to the Docker daemon"

**Problem**: Docker is not running.

**Solution**:
1. Open Docker Desktop application
2. Wait for it to fully start (whale icon in system tray)
3. Try your command again

### Issue 3: Docker Build Fails

**Problem**: Not enough memory or disk space.

**Solutions**:

1. **Increase Docker Memory**:
   - Open Docker Desktop
   - Go to Settings → Resources
   - Increase memory to at least 4GB
   - Click "Apply & Restart"

2. **Free Up Disk Space**:
   ```bash
   # Remove unused Docker images and containers
   docker system prune -a
   ```

3. **Check Available Space**:
   - Make sure you have at least 10GB free

### Issue 4: "Database connection failed"

**Problem**: MySQL container is not ready or has issues.

**Solution**:
```bash
# Stop everything
docker compose down

# Remove the database volume (deletes data!)
docker volume rm prestashop_db-data

# Start fresh
docker compose up -d
```

### Issue 5: Permission Errors (Linux/macOS)

**Problem**: File permission issues.

**Solution**:
```bash
# Fix ownership of files
sudo chown -R $USER:$USER .

# Fix directory permissions
find . -type d -exec chmod 755 {} \;

# Fix file permissions
find . -type f -exec chmod 644 {} \;
```

### Issue 6: "localhost refused to connect"

**Problem**: Containers are not running or not ready yet.

**Solutions**:

1. **Check container status**:
   ```bash
   docker compose ps
   ```

2. **Wait a bit longer**: First startup can take 10-20 minutes

3. **Check logs for errors**:
   ```bash
   docker compose logs prestashop-git
   ```

4. **Restart containers**:
   ```bash
   docker compose restart
   ```

### Issue 7: Changes Don't Appear

**Problem**: Cache needs to be cleared.

**Solution**:
```bash
# Clear PrestaShop cache
make cc

# Or manually
docker compose exec prestashop-git rm -rf var/cache/*
```

### Issue 8: Slow Performance

**Problem**: Docker needs more resources.

**Solutions**:

1. **Increase Docker Resources**:
   - Open Docker Desktop → Settings → Resources
   - Increase CPU cores and memory
   - Recommended: 4 CPU cores, 4GB RAM

2. **Restart Docker Desktop**

3. **Close Other Applications**: Free up system resources

### Getting More Help

If you're still stuck:

1. **Check Docker logs**:
   ```bash
   docker compose logs
   ```

2. **Search for your error**:
   - [PrestaShop Forums](https://www.prestashop.com/forums/)
   - [GitHub Issues](https://github.com/PrestaShop/PrestaShop/issues)
   - [Stack Overflow](https://stackoverflow.com/questions/tagged/prestashop)

3. **Ask the community**:
   - [PrestaShop Slack](https://www.prestashop-project.org/slack/)
   - [GitHub Discussions](https://github.com/PrestaShop/PrestaShop/discussions)

---

## 🎓 What's Next?

### Learn the Basics

1. **Explore the Admin Panel**:
   - Go to `http://localhost:8001/admin-dev`
   - Browse through different sections
   - Try creating a test product

2. **Customize Your Store**:
   - Go to Design → Theme & Logo
   - Upload your logo
   - Change colors and styles

3. **Add Products**:
   - Go to Catalog → Products
   - Click "Add new product"
   - Fill in product details

### Development Resources

**Official Documentation**:
- [User Documentation](https://docs.prestashop-project.org/)
- [Developer Documentation](https://devdocs.prestashop-project.org/)
- [Module Development](https://devdocs.prestashop-project.org/9/modules/)
- [Theme Development](https://devdocs.prestashop-project.org/9/themes/)

**Learning Resources**:
- [PrestaShop YouTube Channel](https://www.youtube.com/user/prestashop)
- [PrestaShop Blog](https://build.prestashop-project.org/)
- [Community Forums](https://www.prestashop.com/forums/)

**Development Tools**:
- [VS Code](https://code.visualstudio.com/) - Recommended code editor
- [Chrome DevTools](https://developer.chrome.com/docs/devtools/) - For debugging
- [Postman](https://www.postman.com/) - For testing APIs

### Advanced Topics

Once you're comfortable with the basics:

1. **Module Development**:
   - Learn to create custom modules
   - Extend PrestaShop functionality
   - [Module Development Guide](https://devdocs.prestashop-project.org/9/modules/)

2. **Theme Customization**:
   - Customize templates
   - Modify CSS and JavaScript
   - [Theme Development Guide](https://devdocs.prestashop-project.org/9/themes/)

3. **Contributing**:
   - Fix bugs
   - Add features
   - [Contributing Guide](../CONTRIBUTING.md)

### Best Practices

**Security**:
- Change default admin credentials immediately
- Keep PrestaShop updated
- Use strong passwords
- Enable HTTPS in production

**Performance**:
- Enable caching in production
- Optimize images
- Use a CDN for static assets
- Monitor database performance

**Backup**:
- Regularly backup your database
- Keep copies of custom code
- Document changes you make

### Environment Variables

You can customize your installation by setting environment variables. Create a `.env` file in the PrestaShop directory:

```bash
# Database Configuration
DB_PASSWD=your_secure_password
DB_NAME=prestashop
DB_PREFIX=ps_

# Admin Configuration
ADMIN_MAIL=your-email@example.com
ADMIN_PASSWD=YourSecurePassword

# PrestaShop Configuration
PS_DOMAIN=localhost:8001
PS_COUNTRY=us
PS_LANGUAGE=en
PS_DEV_MODE=1

# Development Tools
INSTALL_XDEBUG=true
```

Then restart your containers:
```bash
docker compose down
docker compose up -d
```

### Useful Commands Reference

```bash
# Container Management
make docker-start      # Build and start everything
make docker-up         # Start containers
make docker-down       # Stop containers
make docker-restart    # Restart containers
make docker-logs       # View logs
make docker-sh         # Access container shell

# Development
make cc               # Clear cache
make composer         # Install PHP dependencies
make assets           # Build frontend assets

# Database
make install-prestashop  # Fresh install (deletes data!)

# Testing
make test             # Run all tests
make test-unit        # Run unit tests

# Code Quality
make cs-fixer         # Fix code style
make phpstan          # Run static analysis
```

---

## 🎯 Quick Tips

### For Beginners

1. **Don't be afraid to break things** - You can always reinstall with `make install-prestashop`
2. **Use MailDev** (http://localhost:1080) to test emails without sending real emails
3. **Check logs** when something goes wrong: `docker compose logs`
4. **Clear cache** after making changes: `make cc`
5. **Google is your friend** - Many people have had the same issues you're facing

### For Development

1. **Enable Xdebug** for debugging:
   ```bash
   export INSTALL_XDEBUG=true
   make docker-start
   ```

2. **Use dev mode** to see detailed errors:
   - Already enabled by default (`PS_DEV_MODE=1`)

3. **Watch for changes**:
   ```bash
   make assets-dev
   ```

4. **Keep containers running** instead of stopping/starting repeatedly

5. **Use version control**: Commit your changes regularly with Git

---

## 📞 Support

Need help? Here's where to get it:

**Community Support**:
- 💬 [Slack Channel](https://www.prestashop-project.org/slack/) - Chat with other developers
- 💭 [GitHub Discussions](https://github.com/PrestaShop/PrestaShop/discussions) - Ask questions
- 📚 [Forums](https://www.prestashop.com/forums/) - Browse and search topics

**Documentation**:
- 📖 [User Docs](https://docs.prestashop-project.org/)
- 🔧 [Developer Docs](https://devdocs.prestashop-project.org/)
- 📝 [Development Guide](../docs/DEVELOPMENT.md)

**Issues**:
- 🐛 [Report Bugs](https://github.com/PrestaShop/PrestaShop/issues/new/choose)
- 🔒 [Security Issues](https://www.prestashop-project.org/security/bug-bounty/)

---

## 🏁 Conclusion

Congratulations on setting up your PrestaShop development environment! You now have:

✅ Docker and Git installed  
✅ PrestaShop running locally  
✅ Access to admin panel and frontend  
✅ Email testing with MailDev  
✅ Knowledge of common issues and solutions  

**Remember**: Development is a learning process. Don't worry if you encounter issues – they're opportunities to learn!

**Happy coding! 🚀**

---

## 📄 License

PrestaShop is licensed under the [Academic Free License (AFL 3.0)](../LICENSE.md)

---

**Last Updated**: February 2026  
**PrestaShop Version**: 9.0+  
**Maintainer**: PrestaShop Community
