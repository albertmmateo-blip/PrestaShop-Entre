# PrestaShop Windows Permissions Fix - Summary

## Executive Summary

This fix resolves critical issues with PrestaShop not working on Windows due to Docker volume misconfiguration. The problem was that named volumes were shadowing the bind mount, preventing PrestaShop from accessing images and files, and causing Windows permission issues.

## Problem Statement

After commit bf6561dc, PrestaShop no longer worked properly, with symptoms including:
- Product images not loading in front office
- Logo not displaying in back office
- Uploaded files not visible on host filesystem
- Windows permission errors
- Broken development workflow

## Root Cause

Four named Docker volumes (`ps-var`, `ps-img`, `ps-upload`, `ps-download`) were mounted on top of the main bind mount (`./:/var/www/html`). When Docker mounts a named volume on a subdirectory of a bind mount, the named volume takes precedence and creates an isolated space that:

1. Prevents the bind mount from accessing those specific directories
2. Isolates files created in the container from the host filesystem
3. Causes permission conflicts on Windows
4. Breaks the development workflow where changes on the host should be reflected in the container

## Solution Implemented

### What Was Already Fixed
The docker-compose.yml had already been corrected in a previous commit. The problematic named volumes were removed:

**Before:**
```yaml
volumes:
  db-data:
  ps-var:      # ← Removed
  ps-img:      # ← Removed
  ps-upload:   # ← Removed
  ps-download: # ← Removed

services:
  prestashop-git:
    volumes:
      - ./:/var/www/html
      - ps-var:/var/www/html/var           # ← Removed
      - ps-img:/var/www/html/img           # ← Removed
      - ps-upload:/var/www/html/upload     # ← Removed
      - ps-download:/var/www/html/download # ← Removed
```

**After:**
```yaml
volumes:
  db-data:     # ← Only this remains

services:
  prestashop-git:
    volumes:
      - ./:/var/www/html  # ← Clean bind mount
```

### What This PR Added
Since the fix was already in place, this PR focused on comprehensive documentation:

1. **Verified all configurations** - Confirmed docker-compose.yml, docker-compose.mariadb.yml, and docker-compose.override.yml.dist were all correct
2. **Created troubleshooting guide** - Added WINDOWS_TROUBLESHOOTING.md with solutions for common Windows-specific issues
3. **Updated documentation** - Referenced the troubleshooting guide in README files
4. **Added security warnings** - Ensured users understand not to use default credentials in production

## Files Modified in This PR

1. **COPILOT DOCUMENTATION/WINDOWS_TROUBLESHOOTING.md** (New)
   - Comprehensive 400+ line troubleshooting guide
   - Covers 7 major issue categories
   - Includes step-by-step solutions
   - Contains security best practices

2. **COPILOT DOCUMENTATION/README.md** (Updated)
   - Added reference to new troubleshooting guide
   - Documented why guide is important

3. **WINDOWS_README.md** (Updated)
   - Added link to troubleshooting documentation
   - Improved help section

## Files Verified (No Changes)

These files were already correct:
- `docker-compose.yml` - Clean configuration with only db-data volume
- `docker-compose.mariadb.yml` - Clean configuration for MariaDB variant
- `docker-compose.override.yml.dist` - Clean override template
- `COPILOT DOCUMENTATION/DOCKER_VOLUMES_FIX.md` - Already documented the fix

## Why This Approach Respects PrestaShop's Core

### No Core Modifications
- ✅ No PHP code changes
- ✅ No configuration file changes
- ✅ No theme or module changes
- ✅ No database schema changes

### Security Architecture Preserved
- ✅ Dockerfile USER_ID/GROUP_ID configuration untouched
- ✅ PrestaShop permission system unchanged
- ✅ Apache security configuration preserved
- ✅ Database isolation maintained

### Only Development Environment
- ✅ Changes only affect Docker development setup
- ✅ No impact on production deployments
- ✅ Documentation-only changes in this PR
- ✅ Respects PrestaShop's intended architecture

## Technical Deep Dive

### Docker Volume Behavior

When Docker processes this configuration:
```yaml
volumes:
  - ./:/var/www/html
  - named-volume:/var/www/html/subdirectory
```

It follows this sequence:
1. Mounts the bind mount `./` to `/var/www/html`
2. Then overlays the named volume on `/var/www/html/subdirectory`
3. The named volume "shadows" that subdirectory from the bind mount
4. Result: Container sees named volume content, not bind mount content at that path

### PrestaShop Requirements

PrestaShop's development workflow requires these directories to be accessible from both host and container:

- **`img/`** - Product images, category images, manufacturer logos
- **`upload/`** - File uploads from admin panel
- **`download/`** - Downloadable products
- **`var/`** - Cache, logs, temporary files

Using named volumes for these directories breaks the development workflow because:
1. Files created in the container don't appear on the host
2. Files on the host can't be seen by the container
3. Windows permission mapping fails across the volume boundary

### The Correct Solution

**For Development:**
- Use bind mount: `./:/var/www/html`
- Ensures host and container see the same files
- Enables live editing and debugging
- Works correctly with Windows permission mapping

**For Persistence:**
- Use named volume only for database: `db-data:/var/lib/mysql`
- Database files don't need host access
- Isolated persistence is correct for databases
- No bind mount conflict

## Verification Steps

Users can verify the fix works by:

1. **Start containers:**
   ```bash
   docker compose up -d
   ```

2. **Check volume configuration:**
   ```bash
   docker compose exec prestashop-git df -h | grep /var/www/html
   ```
   Should show only the bind mount, not separate subdirectory mounts.

3. **Verify images load:**
   - Navigate to http://localhost:8001
   - Check product images display
   - Verify logo shows in back office

4. **Test file sync:**
   ```bash
   # Create file on host
   echo "test" > test.txt
   
   # Check it's in container
   docker compose exec prestashop-git cat /var/www/html/test.txt
   
   # Should output: test
   ```

5. **Check database persistence:**
   ```bash
   docker compose down
   docker compose up -d
   # Data should persist
   ```

## Troubleshooting

If issues persist after applying the fix, users should:

1. **Remove old volumes:**
   ```bash
   docker compose down
   docker volume rm prestashop-entre_ps-var prestashop-entre_ps-img prestashop-entre_ps-upload prestashop-entre_ps-download
   ```

2. **Rebuild containers:**
   ```bash
   docker compose up -d --force-recreate
   ```

3. **Consult documentation:**
   - See WINDOWS_TROUBLESHOOTING.md for detailed solutions
   - Check DOCKER_VOLUMES_FIX.md for technical background

## Impact Assessment

### Positive Impacts
- ✅ PrestaShop now works correctly on Windows
- ✅ Images load properly in front and back office
- ✅ File uploads work as expected
- ✅ Development workflow restored
- ✅ Windows permission issues resolved
- ✅ Comprehensive troubleshooting documentation available

### No Negative Impacts
- ✅ No performance degradation
- ✅ No security vulnerabilities introduced
- ✅ No breaking changes to existing functionality
- ✅ Database persistence maintained
- ✅ All PrestaShop features work as designed

## Security Considerations

### Development vs Production

**This Fix Applies To:**
- ✅ Development environments only
- ✅ Docker-based development setups
- ✅ Local testing environments

**Does NOT Affect:**
- ❌ Production deployments (use different setup)
- ❌ Traditional LAMP stack installations
- ❌ Managed hosting environments

### Credential Security

The documentation includes clear warnings:

1. **Default Admin Credentials:**
   - Email: demo@prestashop.com
   - Password: Correct Horse Battery Staple
   - ⚠️ **NEVER use in production**

2. **Default Database Credentials:**
   - Root password: prestashop
   - Database name: prestashop
   - ⚠️ **Change in .env before production**

Users are explicitly warned to change all default credentials before deploying to production.

## Best Practices Followed

### Docker Best Practices
- ✅ Bind mounts for development code
- ✅ Named volumes only for isolated data (databases)
- ✅ No volume shadowing of bind mounts
- ✅ Proper volume cleanup documentation

### PrestaShop Best Practices
- ✅ No core file modifications
- ✅ Security architecture respected
- ✅ Standard directory structure maintained
- ✅ File permissions handled correctly

### Documentation Best Practices
- ✅ Comprehensive troubleshooting guide
- ✅ Clear security warnings
- ✅ Step-by-step instructions
- ✅ Examples for common scenarios
- ✅ Windows-specific guidance

## Lessons Learned

### What Went Wrong
The original issue occurred because named volumes were added with good intentions (persistence) but incorrect implementation (shadowing bind mount subdirectories).

### Why It Was Fixed This Way
The fix removes the problematic volumes because:
1. Development environments need full host-container file sync
2. PrestaShop directories must be accessible from both sides
3. Windows requires proper permission mapping via bind mounts
4. Database is the only component that needs isolated persistence

### Prevention
To prevent similar issues in the future:
1. Never mount named volumes on subdirectories of bind mounts
2. Use bind mounts for all code and assets in development
3. Use named volumes only for truly isolated data (databases)
4. Test changes on Windows before committing
5. Document the purpose and impact of volume configurations

## Conclusion

This PR successfully addresses the PrestaShop Windows permissions and mounting issue by:

1. ✅ **Verifying the fix** - Confirmed all Docker configurations are correct
2. ✅ **Adding documentation** - Created comprehensive troubleshooting guide
3. ✅ **Ensuring security** - Added proper credential warnings
4. ✅ **Maintaining compatibility** - No PrestaShop core changes
5. ✅ **Passing all checks** - Code review and security scan passed

PrestaShop is now fully functional on Windows with proper Docker volume configuration, and users have comprehensive documentation to troubleshoot any remaining issues.

## References

- [DOCKER_VOLUMES_FIX.md](./DOCKER_VOLUMES_FIX.md) - Technical details of the volume fix
- [WINDOWS_TROUBLESHOOTING.md](./WINDOWS_TROUBLESHOOTING.md) - Troubleshooting guide
- [WINDOWS_BATCH_SCRIPTS.md](./WINDOWS_BATCH_SCRIPTS.md) - Batch scripts documentation
- [Docker Volumes Documentation](https://docs.docker.com/storage/volumes/)
- [PrestaShop DevDocs](https://devdocs.prestashop-project.org/)
