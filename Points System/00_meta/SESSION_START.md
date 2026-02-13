# Session Start Checklist

Every agent or developer MUST execute this checklist at the start of each work session.

## Pre-Work Checklist

### 1. Identify Components to Modify

Before writing any code, identify:

- [ ] Which features will be modified? (List from `03_features/`)
- [ ] Which integrations will be impacted? (List from `04_integrations/`)
- [ ] Which data models will change? (List from `05_data/`)
- [ ] Which architecture components are involved? (List from `02_architecture/`)
- [ ] Which operations or offline behavior is affected? (List from `07_operations/`)
- [ ] Which security mechanisms are involved? (List from `06_security/`)

### 2. Read All Relevant Documentation

For each component identified above, read the complete documentation file.

Required reading:
- [ ] `01_project/PROJECT_OVERVIEW.md` - Understand scope and constraints
- [ ] `01_project/IMPLEMENTATION_PLAN.md` - Check current status and known issues
- [ ] All feature documents for modified features
- [ ] All integration documents for impacted integrations
- [ ] All architecture documents for involved components
- [ ] All data model documents for modified entities

**Never skip this step. Never rely on memory or assumptions.**

### 3. Verify Documentation Currency

Check each document read for:
- [ ] No "TODO" or "INCOMPLETE" markers in critical sections
- [ ] No obvious contradictions with other documents
- [ ] Examples and diagrams appear current (match API versions, data models, etc.)
- [ ] Related documents links are valid and bidirectional

If documentation is outdated or incomplete:
- **STOP** - Do not proceed to coding
- Update documentation first
- Get review if uncertain

### 4. Check for Recent Deviations

Read the "Deviations" section in `01_project/IMPLEMENTATION_PLAN.md`:
- [ ] Note any recent architectural changes
- [ ] Identify any new technical debt
- [ ] Check for any postponed items that might affect current work

### 5. Identify Documentation Updates Needed

Before starting to code, plan documentation updates:
- [ ] Which files will need updates after this work?
- [ ] Will new files need to be created?
- [ ] Will new cross-references need to be added?
- [ ] Will diagrams need to be updated?

### 6. Understand Offline Implications

If working on POS or Windows agent:
- [ ] Read `07_operations/OFFLINE_QUEUE.md`
- [ ] Read `02_architecture/SYNC_STRATEGY.md`
- [ ] Understand how this change affects offline operation
- [ ] Understand how sync will handle this change

### 7. Understand Security Implications

For any change involving:
- User data
- Authentication
- Authorization
- External integrations
- Card handling
- Points transactions

Read:
- [ ] `06_security/SECURITY_MODEL.md`
- [ ] Relevant security documentation for the specific component

### 8. Prepare for Testing

Identify:
- [ ] What tests already exist for this component?
- [ ] What new tests will be needed?
- [ ] How will offline scenarios be tested?
- [ ] How will edge cases be tested?

## During Work

As you work, maintain discipline:

- [ ] Keep documentation open and reference it frequently
- [ ] Update documentation immediately when you discover it's incorrect
- [ ] Add TODOs to documentation for any open questions
- [ ] Don't make assumptions - if unsure, document the question

## Pre-Commit Checklist

Before committing code:

- [ ] All planned documentation updates are complete
- [ ] All new cross-references are added
- [ ] All modified files are consistent with each other
- [ ] All examples in documentation still work
- [ ] IMPLEMENTATION_PLAN.md is updated if needed
- [ ] No new implicit assumptions were introduced

## PR Preparation Checklist

Before opening a pull request:

- [ ] Run full enforcement checklist from `00_meta/DOCUMENTATION_RULES.md`
- [ ] Verify all documentation changes are included in the PR
- [ ] Write PR description explaining what documentation was updated and why
- [ ] Include links to updated documentation in PR description
- [ ] Flag any documentation TODOs or uncertainties for review

## Quick Reference: Key Documents

Always keep these open during work:

- `00_meta/DOCUMENTATION_RULES.md` - The rules
- `01_project/PROJECT_OVERVIEW.md` - The big picture
- `01_project/IMPLEMENTATION_PLAN.md` - Current status
- `08_prompts/AGENT_WORKFLOW.md` - How to work on this project

## Emergency Exception

If a production issue requires immediate action without time for full documentation review:

1. Fix the issue
2. Document the fix in IMPLEMENTATION_PLAN.md as a "Hotfix"
3. Create a follow-up task to properly document the change
4. Complete documentation within 24 hours

**This exception should be rare. Most work should follow the full process.**
