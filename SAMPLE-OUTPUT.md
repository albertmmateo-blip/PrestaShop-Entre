# Git Menu Script - Sample Output

This document shows what users will see when running the git-menu.bat script.

## Main Menu Display

```
============================================================
           Git Interactive Menu System
============================================================

Current Branch: copilot/add-git-interactive-menu

------------------------------------------------------------
Select a Git operation:

 1.  Fetch from origin
 2.  Pull from current branch
 3.  Checkout to a different branch
 4.  Checkout a Pull Request by number
 5.  Create and checkout a new branch
 6.  Push to origin (current branch)
 7.  Push to a specific branch
 8.  View current branch and status
 9.  View recent commit history
 10. Stash changes
 11. Apply stash
 12. Reset to origin (WARNING: Destructive!)
 13. Exit

------------------------------------------------------------

Enter your choice (1-13): _
```

## Sample Operation: Create New Branch (Option 5)

```
============================================================
   Create and Checkout New Branch
============================================================

Current branch: main

Enter new branch name: feature/new-awesome-feature

This will create a new branch 'feature/new-awesome-feature' from the current branch.
Command to execute: git checkout -b feature/new-awesome-feature

Continue? (y/n): y

Executing: git checkout -b feature/new-awesome-feature

Switched to a new branch 'feature/new-awesome-feature'

Success: Created and checked out to branch feature/new-awesome-feature.

------------------------------------------------------------

Press 'M' for menu or 'E' to exit: _
```

## Sample Operation: Checkout PR (Option 4)

```
============================================================
   Checkout Pull Request
============================================================

This will fetch and checkout a Pull Request from GitHub.

Enter Pull Request number: 123

Commands to execute:
  git fetch origin pull/123/head:pr-123
  git checkout pr-123

Continue? (y/n): y

Executing: git fetch origin pull/123/head:pr-123

From https://github.com/user/repo
 * [new ref]         refs/pull/123/head -> pr-123

Executing: git checkout pr-123

Switched to branch 'pr-123'

Success: Checked out Pull Request #123 to branch pr-123.

------------------------------------------------------------

Press 'M' for menu or 'E' to exit: _
```

## Sample Operation: Reset to Origin (Option 12) - DESTRUCTIVE

```
============================================================
   DANGER: Reset to Origin (DESTRUCTIVE OPERATION)
============================================================

WARNING: This operation is DESTRUCTIVE and CANNOT be undone easily!

Current branch: feature-branch

This will:
  - Discard ALL local commits not pushed to origin
  - Discard ALL uncommitted changes
  - Reset your branch to match origin/feature-branch exactly

Current uncommitted changes:
 M file1.txt
 M file2.js

Unpushed commits (will be LOST):
abc1234 Work in progress
def5678 Added new feature

Commands to execute:
  git fetch origin
  git reset --hard origin/feature-branch
  git clean -fd

====== FINAL WARNING ======
This will permanently delete your local changes!
============================

Type 'RESET' to confirm (case-sensitive): RESET

Are you absolutely sure? (yes/no): yes

Executing: git fetch origin
...
Executing: git reset --hard origin/feature-branch
HEAD is now at xyz9876 Latest commit from origin

Executing: git clean -fd
Removing untracked-file.txt

Success: Reset to origin/feature-branch completed.
All local changes have been discarded.

------------------------------------------------------------

Press 'M' for menu or 'E' to exit: _
```

## Error Handling Example

```
============================================================
   Checkout to a Different Branch
============================================================

Current branch: main

Available branches:
* main
  develop
  feature-x

Warning: You have uncommitted changes.
 M important-file.txt
 ?? new-file.txt

These changes may prevent checkout or will be carried over.

Enter branch name to checkout: non-existent-branch

Command to execute: git checkout non-existent-branch

Continue? (y/n): y

Executing: git checkout non-existent-branch

error: pathspec 'non-existent-branch' did not match any file(s) known to git

Error: Failed to checkout to branch non-existent-branch.
Tip: Make sure the branch exists or stash your changes.

------------------------------------------------------------

Press 'M' for menu or 'E' to exit: _
```

## Input Validation Example

```
Enter your choice (1-13): 99

Invalid choice. Please enter a number between 1 and 13.
```

```
Enter Pull Request number: abc

Error: Pull Request number must be numeric.
```

```
Enter new branch name: feature~bad*name

Error: Branch name contains invalid characters.
Tip: Avoid spaces and special characters like ~, ^, :, \, etc.
```

## Exit Screen

```
============================================================
   Thank you for using Git Interactive Menu!
============================================================

Goodbye!
```

---

## Color Legend

In actual execution:
- **Cyan** (96m): Headers, menu items, section dividers
- **Green** (92m): Success messages, current branch label
- **Yellow** (93m): Warnings, branch names, commands
- **Red** (91m): Errors, critical warnings, destructive operation warnings
- **White** (97m): General information text

Note: Colors require Windows 10 Anniversary Update (1607) or later, or Windows Terminal.
