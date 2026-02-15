# Entretelas Theme Build Integration

## Overview
This document describes the changes made to integrate the Entretelas theme into PrestaShop's build system, ensuring it is properly recognized and verified when restarting the Docker compose environment.

## Problem Statement
The Entretelas theme was added to the repository but was not being processed during the asset build phase when restarting Docker containers. This meant the theme wouldn't be verified as part of the standard build process, potentially causing issues with Playwright testing or deployment.

## Solution
Added the Entretelas theme as a recognized build target in the asset build system, with appropriate verification steps since the theme uses pre-built assets rather than requiring compilation.

## Changes Made

### 1. Modified `tools/assets/build.sh`

#### Change 1.1: Updated Usage Documentation
**Lines:** 1-8  
**Change:** Added `front-entretelas` to the list of available asset names in the script header.

```bash
# Usage: ./tools/assets/build.sh [asset-name] [--force]
#   asset-name: admin-default, admin-new-theme, front-core, front-classic, front-hummingbird, front-entretelas, or all
```

#### Change 1.2: Added Asset Detection
**Lines:** 84-86  
**Change:** Added detection logic to check if Entretelas theme assets exist.

```bash
front-entretelas)
  [[ ! -f "$PROJECT_PATH/themes/entretelas/assets/css/theme.css" ]]
  ;;
```

**Purpose:** Allows the build system to determine if the Entretelas theme assets are already present, avoiding unnecessary rebuilds.

#### Change 1.3: Added Build Target
**Lines:** 135-149  
**Change:** Added the `front-entretelas` build target with verification logic.

```bash
front-entretelas)
  if should_build_asset "front-entretelas"; then
    echo ">>> Verifying entretelas theme assets..."
    # Entretelas is a pre-built theme based on Hummingbird
    # No build process needed, just verify assets exist
    if [[ -f "$PROJECT_PATH/themes/entretelas/assets/css/theme.css" ]] && \
       [[ -f "$PROJECT_PATH/themes/entretelas/assets/js/theme.js" ]]; then
      echo "> Entretelas theme assets verified successfully"
    else
      echo "ERROR: Entretelas theme assets are missing!"
      exit 1
    fi
  else
    echo "> Front entretelas already exists (use --force to rebuild)"
  fi
;;
```

**Rationale:** Unlike Classic and Hummingbird themes which have source files that need compilation (webpack, npm build), Entretelas uses pre-built assets copied from Hummingbird. Therefore, instead of running a build process, we verify that the required assets exist.

#### Change 1.4: Updated "all" Target
**Line:** 152  
**Change:** Added `build_asset front-entretelas` to the "all" target.

```bash
all)
  build_asset admin-default & build_asset admin-new-theme & build_asset front-core & build_asset front-classic & build_asset front-hummingbird & build_asset front-entretelas
;;
```

**Purpose:** Ensures Entretelas is processed when building all assets (e.g., during Docker container startup).

#### Change 1.5: Updated Available Assets List
**Line:** 156  
**Change:** Added `front-entretelas` to the error message listing available assets.

### 2. Modified `Makefile`

#### Change 2.1: Updated .PHONY Declaration
**Line:** 20  
**Change:** Added `front-entretelas` to the list of phony targets.

```makefile
.PHONY: ... front-entretelas ...
```

#### Change 2.2: Updated "front" Target
**Lines:** 63-66  
**Change:** Added entretelas build to the front target.

```makefile
front: ## Build front assets
	$(PHP_CONT_WITH_LOGIN) ./tools/assets/build.sh front-core --force
	$(PHP_CONT_WITH_LOGIN) ./tools/assets/build.sh front-classic --force
	$(PHP_CONT_WITH_LOGIN) ./tools/assets/build.sh front-hummingbird --force
	$(PHP_CONT_WITH_LOGIN) ./tools/assets/build.sh front-entretelas --force
```

**Purpose:** When running `make front`, all front-end themes including Entretelas are now built/verified.

#### Change 2.3: Added Individual Target
**Lines:** 80-82  
**Change:** Added a dedicated Makefile target for building Entretelas theme.

```makefile
front-entretelas: ## Build assets for entretelas theme
	$(PHP_CONT_WITH_LOGIN) ./tools/assets/build.sh front-entretelas --force
```

**Purpose:** Allows developers to specifically verify/build just the Entretelas theme with `make front-entretelas`.

## How It Works

### Build Process Flow
1. **Docker Startup:** When Docker containers start (via `docker-compose up` or restart), the startup script (`docker_run_git.sh`) calls the build script.
2. **Asset Building:** The build script runs with the "all" target, processing all themes including Entretelas.
3. **Entretelas Verification:** When processing Entretelas, the script verifies that `theme.css` and `theme.js` exist in the theme's assets directory.
4. **Success/Failure:** If assets exist, the build succeeds. If they're missing, the build fails with an error.

### Build vs Verification
- **Classic & Hummingbird:** Have source files (SCSS, JS) that need compilation via npm/webpack
- **Entretelas:** Uses pre-built CSS/JS files, only needs verification

### Usage Examples

```bash
# Build all themes
make front

# Build only Entretelas theme
make front-entretelas

# Direct script usage
./tools/assets/build.sh front-entretelas

# Force rebuild/verify
./tools/assets/build.sh front-entretelas --force

# Build all assets (includes Entretelas)
./tools/assets/build.sh all
```

## Testing

### Verification Steps
1. **Theme Assets Exist:**
   ```bash
   ls themes/entretelas/assets/css/theme.css
   ls themes/entretelas/assets/js/theme.js
   ```

2. **Build Script Recognizes Target:**
   ```bash
   ./tools/assets/build.sh front-entretelas
   # Should output: "> Front entretelas already exists" or ">>> Verifying entretelas theme assets..."
   ```

3. **Makefile Target Works:**
   ```bash
   make front-entretelas
   # Should execute without errors
   ```

4. **Included in "all" Target:**
   ```bash
   ./tools/assets/build.sh all
   # Should include Entretelas in the build sequence
   ```

## Impact

### Positive Impacts
- **Build Consistency:** Entretelas is now part of the standard build process
- **Error Detection:** Missing theme assets are detected early during build
- **Docker Integration:** Theme is verified on container start/restart
- **Makefile Support:** Standard `make` commands now include Entretelas
- **Documentation:** Clear help text shows Entretelas as an available target

### No Breaking Changes
- Existing themes (Classic, Hummingbird) continue to work as before
- Build process backwards compatible
- No changes to theme files themselves
- No impact on existing Makefile targets

## Future Considerations

### If Entretelas Needs Compilation Later
If the Entretelas theme ever needs its own build process (e.g., SCSS compilation):

1. Create a `themes/entretelas/_dev` directory with source files
2. Add `package.json` with build scripts
3. Update the build script to call `build "$PROJECT_PATH/themes/entretelas/_dev"`
4. Remove the verification-only logic

### Maintenance
- If theme assets are moved or renamed, update the file paths in the build script
- Keep this documentation updated if build process changes

## Related Files
- `tools/assets/build.sh` - Main build script
- `Makefile` - Build automation
- `.docker/docker_run_git.sh` - Docker startup script that triggers builds
- `themes/entretelas/` - The theme directory

## References
- Original theme documentation: `themes/entretelas/THEME_IMPLEMENTATION_NOTES.md`
- Theme summary: `ENTRETELAS_THEME_SUMMARY.md`
- Build system: `tools/assets/`

---

**Last Updated:** 2026-02-15  
**Author:** GitHub Copilot  
**Version:** 1.0.0
