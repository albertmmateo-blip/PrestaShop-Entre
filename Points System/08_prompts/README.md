# Prompts Directory

This directory contains comprehensive prompts and workflows for building and maintaining the Fidelity Points loyalty system.

## 📋 Where to Start

### Building from Scratch?
👉 **Start with [BUILD_SEQUENCE.md](BUILD_SEQUENCE.md)**

This file contains a complete, ordered sequence of copy-and-paste ready prompts that walk you through building the entire project step-by-step, from environment setup to production deployment.

**Why use BUILD_SEQUENCE.md?**
- ✅ Comprehensive step-by-step guide
- ✅ Copy-and-paste ready prompts
- ✅ Organized in logical build order
- ✅ Includes all prerequisites and documentation references
- ✅ Clear deliverables and testing checklists for each step
- ✅ Complete coverage of all project phases

### Working on a Specific Component?
👉 **Use [SESSION_PROMPTS.md](SESSION_PROMPTS.md)**

This file contains component-specific prompts for working on individual features, integrations, or subsystems after the initial project structure is in place.

**When to use SESSION_PROMPTS.md?**
- Working on a specific backend endpoint
- Implementing a specific PrestaShop feature
- Working on Windows agent functionality
- Adding a specific integration
- Modifying data models
- Implementing security features

### Understanding the Overall Workflow?
👉 **Read [AGENT_WORKFLOW.md](AGENT_WORKFLOW.md)**

This file defines the mandatory process that all agents and developers must follow in every work session. It covers documentation-first development, testing requirements, and best practices.

**What's in AGENT_WORKFLOW.md?**
- Mandatory before-starting checklist
- Documentation-first development process
- Testing requirements
- PR requirements
- Anti-patterns to avoid
- Component-specific guidelines

## Quick Decision Tree

```
Are you starting the project from scratch?
├─ YES → Use BUILD_SEQUENCE.md
│         Follow phases 1-8 in order
└─ NO → Is the basic structure already in place?
          ├─ YES → Use SESSION_PROMPTS.md
          │         Find the component you're working on
          └─ NO → Use BUILD_SEQUENCE.md
                    Start from the phase that matches your current state
```

## Files in This Directory

| File | Purpose | When to Use |
|------|---------|-------------|
| **BUILD_SEQUENCE.md** | Complete ordered build guide | Building project from scratch or following a structured implementation plan |
| **SESSION_PROMPTS.md** | Component-specific prompts | Working on individual components or features |
| **AGENT_WORKFLOW.md** | Mandatory workflow process | Every work session (always follow this) |
| **README.md** | This file | Finding the right document to use |

## Important Notes

1. **Always read AGENT_WORKFLOW.md first** - It defines the mandatory process for all work
2. **Follow BUILD_SEQUENCE.md in order** - Each phase builds on the previous one
3. **Update documentation as you go** - Don't defer documentation updates
4. **Reference the comprehensive docs** - All prompts reference detailed documentation in other directories
5. **Follow the testing checklists** - Each step has specific testing requirements

## Need More Information?

- **Project Overview**: See `01_project/PROJECT_OVERVIEW.md`
- **Architecture**: See files in `02_architecture/`
- **Features**: See files in `03_features/`
- **Integrations**: See files in `04_integrations/`
- **Data Models**: See files in `05_data/`
- **Security**: See files in `06_security/`
- **Operations**: See files in `07_operations/`

## Contributing

When adding new prompts:
1. Add to BUILD_SEQUENCE.md if it's part of the initial build process
2. Add to SESSION_PROMPTS.md if it's component-specific maintenance work
3. Update this README with any new files
4. Ensure all prompts reference the relevant documentation files
5. Include clear deliverables and testing checklists

---

**Remember**: Quality documentation leads to quality code. Follow the prompts, reference the documentation, and build something excellent! 🚀
