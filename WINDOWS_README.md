# Windows Quick Start Guide

This repository includes batch scripts for Windows users to easily manage the PrestaShop Docker development environment.

## Quick Commands

### First Time Setup
```batch
start.bat
```
Builds Docker images and starts all containers. Takes several minutes.

### Daily Development
```batch
quick-start.bat
```
Quickly starts existing containers. Takes only seconds.

### Stop Development
```batch
stop.bat
```
Stops all containers gracefully.

### Rebuild and Restart
```batch
restart.bat
```
Completely rebuilds and restarts everything.

## Access URLs

Once started, access your PrestaShop installation at:
- **Frontend**: http://localhost:8001
- **Backend**: http://localhost:8001/admin-dev
- **Email Testing**: http://localhost:1080

## Default Admin Credentials

- Email: `demo@prestashop.com`
- Password: `Correct Horse Battery Staple`

## Troubleshooting

### Error: `/usr/bin/env: 'bash\r': No such file or directory`

If you see this error when running Docker containers, it means shell scripts have Windows line endings (CRLF) instead of Unix line endings (LF).

**Fix for existing clones:**

1. Pull the latest changes (includes `.gitattributes` fix):
   ```batch
   git pull
   ```

2. Reset line endings for all files:
   ```batch
   git rm --cached -r .
   git reset --hard
   ```

3. Rebuild Docker containers:
   ```batch
   restart.bat
   ```

**For new clones:** This issue is now prevented by the `.gitattributes` file and won't occur.

## Need Help?

See the full documentation: [COPILOT DOCUMENTATION/WINDOWS_BATCH_SCRIPTS.md](COPILOT%20DOCUMENTATION/WINDOWS_BATCH_SCRIPTS.md)

## For Linux/Mac Users

Use the Makefile commands instead:
```bash
make docker-start    # First time or full rebuild
make docker-up       # Quick start
make docker-down     # Stop
make docker-restart  # Restart
```
