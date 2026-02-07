# 🚨 PrestaShop Docker Installation - Important Notice

## Permission Errors Fix

If you're experiencing **permission errors** like:
```
Permission denied in /var/www/html/var/logs/...
```

This has been **fixed**! Follow these steps:

### Quick Fix

```bash
# Set your user ID and group ID
export USER_ID=$(id -u)
export GROUP_ID=$(id -g)

# Rebuild and restart
docker compose down
docker compose build
docker compose up -d
```

### For Complete Instructions

📖 **See our comprehensive guides:**

- **[Noob Guide](./Noob%20guide/)** - If you're new to PrestaShop or Docker
- **[Installation Guide](./Noob%20guide/INSTALLATION_GUIDE.md)** - Step-by-step setup instructions
- **[Troubleshooting Guide](./Noob%20guide/TROUBLESHOOTING.md)** - Detailed solutions for all common issues

### What Was Fixed

The Docker startup script (`.docker/docker_run_git.sh`) now automatically:
- Creates the `var/logs` and `var/cache` directories
- Sets correct ownership (`www-data:www-data`)
- Sets correct permissions (`775`)

This prevents the permission errors that were occurring during installation.

---

**Need more help?** Check the [Troubleshooting Guide](./Noob%20guide/TROUBLESHOOTING.md)!
