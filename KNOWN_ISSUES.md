# Known Issues & Technical Debt

**Last Updated**: 2026-02-15  
**Branches**: Multiple (copilot/implement-core-data-model, copilot/implement-loyalty-api-structure)  
**Maintained By**: Development Team

## Purpose

This document tracks known issues, technical debt, and deferred CI/CD failures that require future attention. All items here are explicitly documented with:
- Clear description of the issue
- Impact assessment
- Reasoning for deferral
- Planned resolution timeline
- Workarounds (if available)
- GitHub issue tracking

## Active Issues (Deferred)

### CI/CD - PR Metadata Validation Failure

- **Status**: 🟡 Deferred until merge to main branch
- **Affected Checks/Components**: PR Metadata Validation workflow
- **Affected Branches**: All feature branches (copilot/implement-core-data-model, copilot/implement-loyalty-api-structure)
- **Description**: PrestaShop requires specific metadata (Category, Type, Milestone) for all PRs targeting core branches. Feature branches for the Loyalty System don't have this metadata as it's an additive feature rather than a core PrestaShop modification.
- **Impact**: 
  - User Impact: None - this is administrative
  - Developer Impact: CI check shows as failed but doesn't block development
  - Build Impact: Does not affect code functionality
- **Why Not Fixed Now**: 
  - These are feature branches with a separate loyalty system
  - PrestaShop metadata conventions are for core PrestaShop contributions
  - The loyalty system is additive and doesn't modify PrestaShop core files
  - Metadata will be added when preparing for merge to main/develop branches
- **Planned Resolution**: 
  - Timeline: Before merge to main or develop branch
  - Approach: Add PR metadata with appropriate values:
    - Category: PM (Project Management) or FO (Front Office) depending on final scope
    - Type: new feature
    - Milestone: Next release version
- **Workaround**: None needed - check is informational for feature branches
- **Tracking**: 
  - Documented in CI_CHECKS_STATUS.md
  - Documented in CI_CD_DIAGNOSIS_loyalty-api.md
- **Owner**: Development Team
- **Added**: 2026-02-15
- **Severity**: Low (administrative only)

---

### CI/CD - Symfony Console Tests Container Failure

- **Status**: 🟡 Deferred - Infrastructure Issue (Not Code-Related)
- **Affected Checks/Components**: 
  - Symfony Console - front
  - Symfony Console - admin  
  - Symfony Console - admin-api
- **Description**: All three Symfony Console test jobs fail during Docker container setup with error: "No such container: prestashop-prestashop-git-1". This is a Docker infrastructure issue in the CI environment, not related to code changes.
- **Impact**:
  - User Impact: None - infrastructure only
  - Developer Impact: CI shows failed checks but doesn't indicate code problems
  - Build Impact: PrestaShop console commands are not tested, but loyalty system uses separate database
- **Why Not Fixed Now**:
  - Error occurs at Docker container setup, before any application code runs
  - Loyalty system changes don't affect PrestaShop Docker configuration
  - Loyalty system uses separate PostgreSQL database (not PrestaShop's MySQL)
  - No PrestaShop core files or Symfony console commands were modified
  - All loyalty-specific CI checks pass (5/5 jobs in loyalty-ci.yml)
  - Likely pre-existing in base branch
- **Planned Resolution**:
  - Timeline: Verify if failures exist in base branch `Fidelity-points`
  - Approach:
    1. Check base branch for same container errors
    2. If pre-existing: Track as known CI infrastructure issue
    3. If new: Investigate Docker Compose configuration changes
    4. Consider updating Docker setup or CI environment
  - Before production: Ensure PrestaShop installation works correctly
- **Workaround**: 
  - Loyalty system has dedicated CI workflow (loyalty-ci.yml) that passes all checks
  - PostgreSQL database operations are validated separately
  - PrestaShop integration can be validated manually in staging environment
- **Tracking**: Documented in CI_CHECKS_STATUS.md
- **Owner**: DevOps / Infrastructure Team
- **Added**: 2026-02-15
- **Severity**: Medium (blocks console command tests but doesn't affect loyalty system)

---

### CI/CD - Admin Security Attribute Linter Cancelled

- **Status**: 🟡 Deferred - Cascading Failure
- **Affected Checks/Components**: Admin Security Attribute Linter
- **Description**: This check was cancelled as it depends on successful completion of other jobs that failed (Symfony Console tests).
- **Impact**:
  - User Impact: None
  - Developer Impact: Security linting not performed
  - Build Impact: Admin security attributes not validated
- **Why Not Fixed Now**:
  - This is a downstream effect of Symfony Console test failures
  - No admin security-related code was modified in loyalty system
  - Will resolve automatically when upstream dependencies pass
  - Not a code issue
- **Planned Resolution**:
  - Timeline: Resolves when Symfony Console tests are fixed
  - Approach: Fix upstream Symfony Console Docker issues
- **Workaround**: None needed - no admin code modified
- **Tracking**: Documented in CI_CHECKS_STATUS.md, linked to Symfony Console issue
- **Owner**: Development Team (dependent on Symfony Console fix)
- **Added**: 2026-02-15
- **Severity**: Low (dependent check, no code changes in affected area)

---

### CI/CD - Docker Container Name Mismatch (loyalty-api branch)

- **Status**: 🟡 Deferred - Infrastructure Issue (Not Code-Related)
- **Affected Checks/Components**: Admin Security Attribute Linter, Symfony Console tests (expected)
- **Affected Branch**: copilot/implement-loyalty-api-structure
- **Description**: CI workflows fail when trying to execute commands in Docker container "prestashop-prestashop-git-1", but the actual container created is named "prestashop-entre-prestashop-git-1". This is a Docker Compose project name mismatch between CI configuration and the docker-compose.yml file.
- **Impact**:
  - User Impact: None - infrastructure only
  - Developer Impact: CI shows failed checks but doesn't indicate code problems
  - Build Impact: PrestaShop console commands and security linting not executed
- **Why Not Fixed Now**:
  - Error occurs at Docker container lookup, not in application code
  - Loyalty system uses separate Python FastAPI backend with PostgreSQL (not PrestaShop's PHP/MySQL)
  - No PrestaShop core files or Docker configuration modified by loyalty system
  - Likely configuration issue in base branch or CI environment setup
  - All loyalty-specific CI checks pass (loyalty-ci.yml workflow)
- **Planned Resolution**:
  - Timeline: Investigate within 1 week, fix before merge to main
  - Approach:
    1. Check if issue exists in base branch `Fidelity-points`
    2. Identify source of container name: CI workflow vs. Docker Compose project name
    3. Options:
       - Update CI workflows to use "prestashop-entre-*" container names
       - Normalize Docker Compose project name to "prestashop"
       - Make workflow container detection more flexible
  - Before production: Ensure PrestaShop and loyalty system integration works correctly
- **Workaround**: 
  - Loyalty system has dedicated CI workflow (loyalty-ci.yml) that passes all checks
  - Python FastAPI backend tested independently
  - PrestaShop integration can be validated manually in staging environment
- **Tracking**: 
  - [CI_CD_DIAGNOSIS_loyalty-api.md](CI_CD_DIAGNOSIS_loyalty-api.md)
  - This document
- **Owner**: DevOps / Infrastructure Team
- **Added**: 2026-02-15
- **Severity**: Medium (blocks some tests but doesn't affect loyalty system functionality)

**Error Log Example**:
```
docker exec prestashop-prestashop-git-1 php bin/console prestashop:linter:security-attribute find-missing
Error response from daemon: No such container: prestashop-prestashop-git-1
```

**Container Actually Created**:
```
Container prestashop-entre-prestashop-git-1  Creating
Container prestashop-entre-prestashop-git-1  Created
Container prestashop-entre-prestashop-git-1  Started
```

---

## Recently Resolved Issues

### ✅ YAML Lint Formatting Errors (Fixed 2026-02-15)

- **Issue**: 52 trailing spaces and 2 bracket spacing issues in `.github/workflows/loyalty-ci.yml`
- **Resolution**: Applied automatic YAML formatting fixes
- **Status**: ✅ Resolved
- **Verification**: YAML Lint check now passes

---

## Technical Debt Tracking

As per AGENT_WORKFLOW.md, technical debt is tracked in:
- This file (KNOWN_ISSUES.md) - User-facing known issues
- `Points System/01_project/IMPLEMENTATION_PLAN.md` - Project-level technical debt

### Links to Technical Debt Documentation
- [Implementation Plan - Technical Debt Section](Points%20System/01_project/IMPLEMENTATION_PLAN.md#technical-debt)
- [Implementation Plan - Postponed Items](Points%20System/01_project/IMPLEMENTATION_PLAN.md#postponed-items)

---

## Issue Status Legend

- 🔴 **Critical** - Blocks production deployment
- 🟠 **High** - Should be fixed before next release
- 🟡 **Medium** - Deferred with acceptable workaround
- 🟢 **Low** - Minor issue, low priority
- ✅ **Resolved** - Fixed and verified

---

## Process Notes

### When to Add Items to This Document

Items should be added here when:
1. A CI/CD check fails and is explicitly deferred (not immediately fixed)
2. Technical debt is created during implementation
3. Known limitations are discovered that affect functionality
4. Workarounds are implemented for complex issues
5. Infrastructure issues prevent proper testing

### When to Remove Items

Items can be removed when:
1. Issue is completely resolved and verified
2. Workaround is no longer needed
3. Code/infrastructure is replaced/refactored making issue obsolete

Move resolved items to "Recently Resolved Issues" section with resolution date.

### Cross-References

This document should be referenced in:
- Pull request descriptions when CI checks fail
- Commit messages when implementing workarounds
- Code comments when technical debt is created
- GitHub issues for tracking

---

## Related Documentation

- [CI Checks Status](CI_CHECKS_STATUS.md) - Detailed check-by-check analysis
- [CI Final Summary](CI_FINAL_SUMMARY.md) - Executive summary of CI state
- [Implementation Plan](Points%20System/01_project/IMPLEMENTATION_PLAN.md) - Overall project status
- [Agent Workflow](Points%20System/08_prompts/AGENT_WORKFLOW.md) - Documentation requirements

---

**Document Version**: 1.0  
**Next Review**: Before merge to main branch  
**Questions**: Contact Development Team
