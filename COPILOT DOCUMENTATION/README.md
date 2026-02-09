# COPILOT DOCUMENTATION

This folder contains **custom documentation** created by GitHub Copilot for modifications and enhancements made to this PrestaShop repository.

## Purpose

PrestaShop's official documentation (located in `docs/`) should remain unchanged. All additional documentation, explanations, and references for custom modifications are stored in this folder.

## Documentation Files

### docker-volume-fix.md
**Purpose:** Documents the fix for Docker volume configuration issue  
**Related Files:** `docker-compose.yml`  
**Issue:** Named volumes were overlaying bind mount, preventing image loading  
**Solution:** Removed named volumes (ps-var, ps-img, ps-upload, ps-download), kept only db-data for MySQL

## Documentation Structure

Each documentation file in this folder follows this structure:
1. **Issue Summary** - Brief description of the problem
2. **Root Cause** - Detailed explanation with file paths and line numbers
3. **Solution Implemented** - Exact changes made with before/after comparisons
4. **Technical Details** - In-depth technical explanation
5. **Impact** - Before and after effects
6. **Troubleshooting** - Steps to diagnose and resolve related issues
7. **Files Modified** - Table of all files changed with line references
8. **References** - Related commits, files, and resources
9. **Validation** - How the fix was tested and verified
10. **Best Practices** - Guidelines for similar situations

## Official PrestaShop Documentation

**Location:** `docs/` directory  
**Status:** Unchanged - official documentation is preserved  
**Reference:** See `docs/DEVELOPMENT.md` for official development guide

## Contributing

When adding custom modifications to this repository:
1. ✅ DO create documentation in `COPILOT DOCUMENTATION/`
2. ✅ DO include specific file paths and line numbers
3. ✅ DO reference official documentation when relevant
4. ❌ DO NOT modify official PrestaShop documentation in `docs/`
5. ❌ DO NOT duplicate official documentation

## Version Information

- **PrestaShop Version:** 9.0+ (develop branch)
- **Documentation Created:** 2026-02-09
- **Repository:** albertmmateo-blip/PrestaShop-Entre
