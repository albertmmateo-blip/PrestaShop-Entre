# Agent Workflow: Mandatory Process for All Sessions

## Purpose

This document defines the exact workflow every agent must follow in every work session on the Fidelity Points loyalty system.

**This is not a suggestion. This is the required process.**

Deviation from this workflow leads to:
- Inconsistent documentation
- Integration failures
- Lost work
- Security vulnerabilities
- Untrackable technical debt

## Before Starting Any Task

### Step 1: Read Documentation First

**MANDATORY**: Before writing any code, read ALL impacted documentation files.

**Never skip this step. Never assume. Never rely on memory from previous sessions.**

Specifically:

1. Read `00_meta/SESSION_START.md` and complete the checklist
2. Read `01_project/PROJECT_OVERVIEW.md` to understand scope and constraints
3. Read `01_project/IMPLEMENTATION_PLAN.md` to understand current status
4. Identify which components your task involves (features, integrations, architecture, data)
5. Read EVERY documentation file for components you will modify
6. Read documentation for components that depend on what you'll modify
7. Read documentation for components your changes depend on

**If documentation is missing or unclear, STOP and create/update it before coding.**

### Step 2: Verify Documentation is Current

Before proceeding, verify:

- [ ] No critical TODOs or INCOMPLETE markers in relevant docs
- [ ] No obvious contradictions between documents
- [ ] Examples and diagrams appear current
- [ ] Related document links are valid

If documentation is outdated:
- **Do NOT proceed to coding**
- Update documentation first
- Get review if uncertain about the correct update

### Step 3: Plan Your Changes

Create a mental model (or written notes) of:

1. What you will change
2. Which documentation files must be updated
3. Which tests must be added or modified
4. What edge cases must be handled
5. How offline behavior is affected (if applicable)
6. What security implications exist (if any)

**Do not start coding until you have this clarity.**

## During Development

### Documentation-First Development

Follow this sequence:

1. **Update Documentation First**
   - Modify the relevant `.md` files to describe the new behavior
   - Add or update diagrams if needed
   - Update cross-references
   - Review for consistency

2. **Review Documentation Changes**
   - Read the updated documentation as if you were a new developer
   - Verify it's clear and complete
   - Check that it doesn't contradict other documents
   - Verify all cross-references are bidirectional

3. **Write Code Following Documentation**
   - Implement exactly what the documentation describes
   - Do not improvise or add undocumented features
   - If you discover the design is wrong, update documentation and review again

4. **Validate Code Matches Documentation**
   - Verify every documented behavior is implemented
   - Verify no undocumented behaviors were introduced
   - Update documentation if you discover necessary changes

### Continuous Documentation Maintenance

As you work:

- When you discover documentation is wrong → update it immediately
- When you make a decision → document the decision and rationale
- When you encounter an edge case → document how it's handled
- When you learn about a dependency → document it and add cross-references
- When you create technical debt → log it in IMPLEMENTATION_PLAN.md

**Do not accumulate documentation changes to do "later". Update as you go.**

### Never Infer Behavior from Code

**CRITICAL RULE**: If behavior is not documented, it does not exist.

- Do not copy patterns from existing code unless they are documented
- Do not assume APIs work a certain way unless documented
- Do not assume integrations behave a certain way unless documented
- Do not trust memory from previous sessions

**If in doubt, read the documentation. If documentation doesn't answer your question, update it.**

## After Code Changes

### Pre-Commit Checklist

Before committing, verify:

- [ ] All planned documentation updates are complete
- [ ] All new cross-references are added and bidirectional
- [ ] All modified files are consistent with each other
- [ ] All examples in documentation still work
- [ ] IMPLEMENTATION_PLAN.md is updated if scope or approach changed
- [ ] No new implicit assumptions were introduced
- [ ] All TODO comments in code reference documentation TODOs
- [ ] All edge cases are documented

### Testing Against Documentation

Your tests should verify that:

- Code implements what documentation describes
- Code does not implement undocumented behaviors
- Edge cases from documentation are tested
- Error scenarios from documentation are tested
- Offline behavior from documentation is tested (if applicable)

## Before Finalizing Any PR

### Final Validation

Execute the complete enforcement checklist from `00_meta/DOCUMENTATION_RULES.md`:

- [ ] All modified components have corresponding documentation updates
- [ ] Documentation is free of internal contradictions
- [ ] All cross-references are valid and bidirectional
- [ ] All examples and diagrams are current
- [ ] All edge cases and error scenarios are documented
- [ ] All offline behavior is explicitly described
- [ ] All security implications are documented
- [ ] All related documents have been identified and checked
- [ ] IMPLEMENTATION_PLAN.md is updated if scope or approach changed
- [ ] No assumptions are left implicit or undocumented

### Documentation Completeness Check

Verify that someone completely new to the codebase could:

- Understand what your change does by reading documentation alone
- Understand why the change was necessary
- Understand how your change fits into the larger system
- Understand what edge cases exist and how they're handled
- Understand the offline behavior (if applicable)
- Understand the security implications (if any)
- Find all related components by following cross-references

If any of these are not true, update documentation before submitting PR.

## PR Description Requirements

Your PR description must include:

1. **Summary**: What was changed and why
2. **Documentation Updated**: List all .md files that were modified or created
3. **Scope**: Which components are affected (features, integrations, architecture)
4. **Testing**: What was tested and how
5. **Breaking Changes**: Any breaking changes (should be rare)
6. **Deviations**: Any deviations from documented plan (reference IMPLEMENTATION_PLAN.md entry)
7. **Open Questions**: Any uncertainties or TODOs introduced

**Include direct links to updated documentation files in the PR description.**

## Working with Architectural Components

### Backend Work

When working on cloud backend:

1. Read `02_architecture/CLOUD_BACKEND.md`
2. Read `05_data/DATA_MODEL.md` and relevant entity documents
3. Read `06_security/IDEMPOTENCY.md` for transaction endpoints
4. Read relevant feature docs from `03_features/`
5. Update API contracts in architecture documentation before coding
6. Ensure changes are compatible with Windows agent and PrestaShop module

### Windows Agent Work

When working on Windows agent:

1. Read `02_architecture/WINDOWS_AGENT.md`
2. Read `07_operations/OFFLINE_QUEUE.md`
3. Read `02_architecture/SYNC_STRATEGY.md`
4. Read `04_integrations/ANIWIN_POS_INTEGRATION.md`
5. Read `04_integrations/NFC_HARDWARE.md`
6. Consider offline scenarios for every change
7. Ensure sync logic handles all new transaction types

### PrestaShop Module Work

When working on PrestaShop module:

1. Read `04_integrations/PRESTASHOP_MODULE.md`
2. Read `02_architecture/CLOUD_BACKEND.md` (API contracts)
3. Read relevant feature docs from `03_features/`
4. Ensure no PrestaShop core modifications
5. Test on PrestaShop 9.1.0 specifically
6. Document any PrestaShop hooks used

### Data Model Work

When working on data model:

1. Read `05_data/DATA_MODEL.md`
2. Read all entity-specific docs in `05_data/`
3. Consider migration impact on existing data
4. Update both documentation and migration scripts
5. Verify ledger immutability is preserved
6. Check all components that use the modified entities

### Integration Work

When working on integrations:

1. Read the specific integration doc from `04_integrations/`
2. Read `06_security/SECURITY_MODEL.md` for authentication
3. Read `07_operations/ERROR_HANDLING.md` for failure scenarios
4. Document all assumptions about external system behavior
5. Handle offline scenarios (for POS integrations)
6. Implement retry logic and circuit breakers

## Handling Uncertainty

### When Documentation is Unclear

If documentation doesn't clearly answer your question:

1. **Do NOT guess or infer**
2. Review related documents to gather context
3. If still unclear, add a TODO to the documentation stating the question
4. Discuss with team or stakeholders
5. Update documentation with the answer
6. Then proceed with implementation

### When You Discover a Better Approach

If you discover a better way to implement something:

1. **Do NOT silently change the approach**
2. Document the proposed change
3. Document why it's better
4. Document any risks or tradeoffs
5. Add entry to IMPLEMENTATION_PLAN.md under "Deviations" or "Architectural Changes"
6. Update relevant documentation to reflect new approach
7. Ensure all cross-references are updated
8. Then implement the new approach

### When You Find Contradictions

If you discover contradictory information in documentation:

1. **Do NOT pick one arbitrarily**
2. List all contradictory statements and their locations
3. Determine the correct behavior (research, discussion, testing)
4. Update ALL contradictory documents to be consistent
5. Add cross-references between the corrected documents
6. If the contradiction indicates a real problem, add to IMPLEMENTATION_PLAN.md

## Emergency Procedures

### Production Hotfix

If a production issue requires immediate action:

1. Fix the issue with minimal change
2. Immediately document the fix in IMPLEMENTATION_PLAN.md as "Hotfix"
3. Create a follow-up task to properly document the change
4. Complete full documentation within 24 hours
5. Review the hotfix documentation when less urgent work resumes

**This exception should be extremely rare.**

### Discovered Security Issue

If you discover a security vulnerability:

1. Do NOT document it in public places
2. Fix the issue immediately
3. Document the fix (but not the vulnerability details) in IMPLEMENTATION_PLAN.md
4. Notify security team/owner
5. Add to `06_security/SECURITY_MODEL.md` how this class of vulnerability is prevented

## Session Hygiene

### End of Session

Before ending a work session:

- [ ] All code changes committed
- [ ] All documentation changes committed
- [ ] All TODOs tracked in appropriate documentation files
- [ ] IMPLEMENTATION_PLAN.md updated with current status
- [ ] No uncommitted experiments or temporary changes
- [ ] No implicit knowledge exists only in your memory

### Handoff to Next Session

Assume the next session will be executed by someone with:
- No memory of this session
- Only the documentation to guide them
- No ability to ask you questions

Ensure documentation is complete enough for this scenario.

## Anti-Patterns to Avoid

### Forbidden Practices

Never do these:

1. **Code First, Document Later** - Always document first
2. **Defer Documentation Updates** - Update as you go
3. **Copy Code Patterns Without Understanding** - Read documentation, understand design
4. **Assume Behavior From Code** - Only trust documentation
5. **Trust Session Memory** - Always read documentation fresh
6. **Leave Contradictions for Later** - Fix immediately
7. **Skip Cross-References** - Always link related documents
8. **Write Generic Documentation** - Be specific and concrete
9. **Create Documentation Silos** - Always cross-reference
10. **Ignore Documentation Rules** - Rules exist for a reason

## Related Documents

### Process Documents
- `00_meta/SESSION_START.md` - Session start checklist
- `00_meta/DOCUMENTATION_RULES.md` - Documentation rules and enforcement

### Project Context
- `01_project/PROJECT_OVERVIEW.md` - Project scope and goals
- `01_project/IMPLEMENTATION_PLAN.md` - Current status and timeline

### Specific Workflows
- `08_prompts/SESSION_PROMPTS.md` - Component-specific prompts
