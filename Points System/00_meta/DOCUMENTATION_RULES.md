# Documentation Rules and Enforcement

## Authority Principle

**Documentation is authoritative over code.**

If code behavior and documentation diverge, the correct resolution is:
1. First, update the documentation to match current reality if the change was intentional
2. If the code change was unintentional, revert the code to match documentation
3. Never allow code and documentation to remain inconsistent

## Mandatory PR Requirements

Every pull request MUST include documentation updates when ANY of the following are impacted:
- Behavior changes (any functional change)
- Data structure or model changes
- API contract changes
- Flow or sequence modifications
- Configuration or deployment changes
- Integration points or external dependencies
- Security assumptions or mechanisms
- Error handling or failure modes
- Offline behavior or synchronization logic

**No PR may be merged if documentation is incomplete or outdated.**

## Consistency Enforcement

Before finalizing any PR, agents and developers MUST explicitly check for:

### Duplicated Definitions
- No component, entity, or process may be defined in multiple places
- If similar concepts exist, they must be explicitly distinguished and cross-referenced
- Shared definitions must live in one canonical location and be linked from other documents

### Contradictory Flows
- Sequence diagrams and flow descriptions must be consistent across all documents
- If a flow appears in multiple documents, the details must match exactly
- Different perspectives of the same flow (e.g., POS view vs backend view) must be explicitly labeled as such

### Incompatible Assumptions
- Integration assumptions must be validated against partner system documentation
- Offline and online behaviors must be compatible and clearly reconcile
- Data models across components must align (field names, types, constraints)
- Security assumptions must be consistent across all layers

### Outdated Diagrams and Examples
- All diagrams must reflect current architecture
- All code examples must be syntactically correct and match current API contracts
- All endpoint examples must include current request/response formats
- All configuration examples must reference actual configuration files

## Session Memory Policy

**Agents must never rely on memory from previous sessions.**

At the start of each session:
1. Identify which components will be modified
2. Read ALL relevant documentation files completely
3. Verify documentation is current before proceeding
4. If documentation is unclear or outdated, update it FIRST before coding

No code may be written based on assumptions, memory, or inference from existing code patterns.

## Documentation-First Workflow

The standard workflow is:

1. **Read** - Read all impacted documentation files before starting
2. **Plan** - Plan changes and identify documentation that must be updated
3. **Document** - Update documentation to reflect planned changes
4. **Review** - Review documentation for consistency and completeness
5. **Code** - Implement changes following updated documentation
6. **Validate** - Verify code matches documentation exactly
7. **Cross-check** - Verify no other documentation files are now inconsistent

## Atomic Documentation Principle

Every meaningful project item must have its own dedicated `.md` file.

Examples of items requiring their own file:
- Each API endpoint or endpoint group
- Each data model entity
- Each integration point
- Each business rule or calculation
- Each flow (earn, redeem, refund, sync, etc.)
- Each offline operation
- Each message type or communication channel
- Each security mechanism
- Each error scenario
- Each deployment component

Files must be:
- **Concise** - Cover one topic thoroughly but without scope creep
- **Narrowly scoped** - A reader should understand this item without reading everything
- **Independently readable** - Include necessary context, then link to details
- **Explicitly linked** - Always reference related documents

## Cross-Reference Requirements

Every documentation file MUST include a "Related Documents" section listing:

1. **Dependencies** - Documents describing components this item depends on
2. **Dependents** - Documents describing components that depend on this item
3. **Related Flows** - Documents describing flows that involve this item
4. **Data Models** - Documents describing data structures used by this item
5. **Integration Points** - Documents describing external systems this item interacts with

No file may exist in isolation without references.

## Change Impact Analysis

When updating any documentation file, the author must:

1. Identify all documents in the "Related Documents" section
2. Read those documents to verify consistency
3. Update those documents if they are now inconsistent
4. Add links if new relationships were created

This ensures documentation remains a consistent, interconnected web of truth.

## Living Document Requirement

The following files are **living documents** and must be continuously updated:

- `01_project/IMPLEMENTATION_PLAN.md` - Must reflect current project state
- `01_project/PROJECT_OVERVIEW.md` - Must reflect current scope
- Any file containing a "Status" or "Current State" section

These files must never describe a past or planned state - only current reality.

## Deviation Tracking

When implementation deviates from original documentation:

1. Do NOT silently update documentation to match implementation
2. First, add an entry to `01_project/IMPLEMENTATION_PLAN.md` under "Deviations"
3. Explain why the deviation occurred
4. Document any risks or technical debt created
5. Then update the affected documentation files
6. Cross-reference the deviation log from updated files

This maintains an audit trail of architectural decisions.

## Enforcement Checklist

Before merging any PR, verify:

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

## Documentation Debt

If documentation must be temporarily incomplete (e.g., during MVP), add explicit TODOs:

```markdown
## TODO - Incomplete Documentation

**Status**: Not yet implemented  
**Blocks**: [List any blocked features]  
**Required by**: [Target date or milestone]  
**Owner**: [Responsible team or individual]

### Missing Information
- [Specific missing item 1]
- [Specific missing item 2]
```

TODOs must be tracked and resolved before final release.

## Consequences of Violations

Violations of these rules lead to:
- Drift between implementation and documentation
- Conflicting assumptions between components
- Integration failures
- Security vulnerabilities
- Inability to onboard new developers
- Maintenance nightmare

**These rules are not optional.**
