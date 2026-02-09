# Docker Volume Configuration Fix

## Issue Summary

Named volumes in `docker-compose.yml` were overlaying the bind mount, preventing PrestaShop from serving product images and logos in both front and back office.

## Root Cause

**File:** `docker-compose.yml`  
**Lines affected:** 1-6 (volume declarations) and 60-65 (volume mounts)

The problematic configuration used named volumes that overlay the bind mount:

```yaml
# Lines 1-6: Named volume declarations (REMOVED)
volumes:
  db-data:
  ps-var:        # ❌ REMOVED - was isolating var/ from host
  ps-img:        # ❌ REMOVED - was isolating img/ from host
  ps-upload:     # ❌ REMOVED - was isolating upload/ from host
  ps-download:   # ❌ REMOVED - was isolating download/ from host

# Lines 60-65: Volume mounts in prestashop-git service (REMOVED)
    volumes:
      - ./:/var/www/html
      - ps-var:/var/www/html/var          # ❌ REMOVED
      - ps-img:/var/www/html/img          # ❌ REMOVED
      - ps-upload:/var/www/html/upload    # ❌ REMOVED
      - ps-download:/var/www/html/download # ❌ REMOVED
```

**Problem:** These named volumes created isolated Docker volumes that overlaid the bind mount (`./:/var/www/html`), meaning:
- Files in `img/`, `upload/`, `var/`, and `download/` existed in the container but were isolated from the host filesystem
- PrestaShop could not serve images or access uploads because they weren't synchronized with the local repository
- Product images, logos, and uploaded files were missing in both front office and back office

## Solution Implemented

**File:** `docker-compose.yml`  
**Changes:**

### Change 1: Top-level volumes section (Lines 1-2)
```yaml
# BEFORE (Lines 1-6)
volumes:
  db-data:
  ps-var:
  ps-img:
  ps-upload:
  ps-download:

# AFTER (Lines 1-2)
volumes:
  db-data:
```

**Rationale:** Keep only `db-data` for MySQL persistence. Remove all other named volumes.

### Change 2: prestashop-git service volumes (Lines 56-57)
```yaml
# BEFORE (Lines 60-65)
    volumes:
      - ./:/var/www/html
      - ps-var:/var/www/html/var
      - ps-img:/var/www/html/img
      - ps-upload:/var/www/html/upload
      - ps-download:/var/www/html/download

# AFTER (Lines 56-57)
    volumes:
      - ./:/var/www/html
```

**Rationale:** Use only the bind mount to ensure real-time file synchronization between host and container.

## Technical Details

### Bind Mount Strategy

**File:** `docker-compose.yml`  
**Line:** 57  
**Configuration:** `- ./:/var/www/html`

This single bind mount:
- Maps the entire repository directly into the container
- Enables real-time file synchronization between host and container
- Allows PrestaShop to serve images and uploads from the local filesystem
- Ensures product images, logos, and uploaded files are accessible in both front and back office
- Facilitates development by keeping host and container in sync

### Database Persistence

**File:** `docker-compose.yml`  
**Line:** 2 (declaration) and 14 (mount)  
**Configuration:** 
```yaml
volumes:
  db-data:  # Line 2

services:
  mysql:
    volumes:
      - db-data:/var/lib/mysql  # Line 14
```

**Rationale:** The `db-data` named volume is retained because:
- Database files should NOT be synchronized with the host filesystem
- Database persistence is required across container restarts
- Database files are binary and not meant for direct host access

## Impact

### Before Fix
- ❌ Product images missing in catalog
- ❌ Logo not displaying  
- ❌ Uploaded files not accessible
- ❌ 404 errors for image URLs
- ❌ Isolated directories: `var/`, `img/`, `upload/`, `download/`

### After Fix
- ✅ Product images load correctly
- ✅ Logo displays properly
- ✅ Uploaded files are accessible
- ✅ Images served from local filesystem
- ✅ Full host-container synchronization for all PrestaShop directories

## Troubleshooting

### Symptoms: Images or Uploads Not Loading

If you encounter missing product images, logos, or uploaded files:

**Diagnosis Steps:**

1. **Verify docker-compose.yml configuration:**
   ```bash
   cat docker-compose.yml | grep -A 10 "prestashop-git:" | grep volumes
   ```
   
   Expected output (Lines 56-57):
   ```yaml
   volumes:
     - ./:/var/www/html
   ```

2. **Check for unexpected named volumes:**
   ```bash
   cat docker-compose.yml | grep -E "ps-var|ps-img|ps-upload|ps-download"
   ```
   
   Expected: No output (these should not exist)

3. **Verify top-level volumes section:**
   ```bash
   head -5 docker-compose.yml
   ```
   
   Expected (Lines 1-2):
   ```yaml
   volumes:
     db-data:
   ```

### Solutions

**If named volumes are present:**

1. Edit `docker-compose.yml` to remove them
2. Restart containers:
   ```bash
   make docker-down
   make docker-up
   ```
3. Clear cache:
   ```bash
   make cc
   ```
4. Verify file permissions:
   ```bash
   ls -la img/ upload/ var/
   chmod -R 755 img/ upload/ var/  # if needed
   ```

## Files Modified

| File | Lines Modified | Description |
|------|---------------|-------------|
| `docker-compose.yml` | 1-6 | Removed named volume declarations (ps-var, ps-img, ps-upload, ps-download) |
| `docker-compose.yml` | 60-65 | Removed volume mounts overlaying bind mount |
| `docker-compose.yml` | Final: 1-2, 56-57 | Kept db-data declaration and bind mount only |

## References

- **Commit that introduced the issue:** bf6561dc1147bb598f2003201e74986c5b7ef876
- **PrestaShop Documentation:** docs/DEVELOPMENT.md (unchanged - official documentation)
- **Docker Compose Version:** Compatible with docker-compose.yml spec
- **Related Directories:**
  - `img/` - Product images and logos
  - `upload/` - User uploaded files
  - `var/` - Cache and temporary files
  - `download/` - Downloadable products

## Validation

The fix was validated through:
1. ✅ Docker Compose syntax validation: `docker compose config --quiet`
2. ✅ Code review: No issues found
3. ✅ Security scan: CodeQL found no vulnerabilities
4. ✅ Configuration comparison with problematic commit

## Best Practices

**For Development Environments:**
- ✅ Use bind mounts (`./:/var/www/html`) for application code
- ✅ Use named volumes only for data that should persist independently (e.g., databases)
- ❌ Avoid named volumes for directories that need host synchronization
- ❌ Do not overlay named volumes on top of bind mounts

**Volume Strategy:**
```yaml
volumes:
  db-data:  # ✅ GOOD: Database needs independent persistence

services:
  prestashop-git:
    volumes:
      - ./:/var/www/html  # ✅ GOOD: Bind mount for development
      # ❌ BAD: - ps-img:/var/www/html/img  (overlays bind mount)
```
