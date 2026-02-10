# Git Menu Script - Sample Output

This document shows what users will see when running the git-menu.bat script.

## Main Menu Display (With Sync Status)

### Example 1: Branch is Synced
```
============================================================
           Git Interactive Menu System
============================================================

Current Branch: main [Synced]

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

### Example 2: Branch Has Uncommitted Changes and is Behind
```
============================================================
           Git Interactive Menu System
============================================================

Current Branch: feature-branch [2 behind] [Uncommitted changes]

------------------------------------------------------------
Select a Git operation:
...
```

### Example 3: Branch is Ahead (Ready to Push)
```
============================================================
           Git Interactive Menu System
============================================================

Current Branch: feature-work [3 ahead]

------------------------------------------------------------
Select a Git operation:
...
```

### Example 4: Branch is Diverged
```
============================================================
           Git Interactive Menu System
============================================================

Current Branch: develop [1 behind, 2 ahead]

------------------------------------------------------------
Select a Git operation:
...
```

## Sample Operation: Fetch from Origin (Option 1) - Enhanced

```
============================================================
   Fetch from Origin
============================================================

What this does:
  - Downloads all new commits, branches, and tags from the remote repository
  - Safe operation - Does NOT merge or modify your working directory
  - Updates your local copy of remote branches (origin/branch-name)
  - After fetching, you can see what changed with 'git log' or merge manually

Use this when:
  - You want to see what's new on the remote without changing your code
  - Before pulling to check what changes are incoming
  - To update all remote branch information

Command to execute: git fetch origin

Continue? (y/n): y

Executing: git fetch origin

From https://github.com/user/repo
   abc1234..def5678  main       -> origin/main
 * [new branch]      feature-x  -> origin/feature-x

Success: Fetched from origin successfully.

------------------------------------------------------------

Press 'M' for menu or 'E' to exit: _
```

## Sample Operation: Create New Branch (Option 5) - Enhanced

```
============================================================
   Create and Checkout New Branch
============================================================

Current branch: main

Enter new branch name: feature/new-awesome-feature

What this does:
  - Creates a new branch starting from your current commit (HEAD)
  - Automatically switches to the newly created branch
  - The new branch starts with all commits from the current branch
  - Your working directory remains unchanged

Use this when:
  - Starting work on a new feature or bug fix
  - Creating a branch for experimentation
  - Separating development work from the main branch

Branch name tips:
  - Use descriptive names: feature/user-login, bugfix/crash-on-save
  - Avoid spaces and special characters (~, ^, :, \, etc.)
  - Common conventions: feature/, bugfix/, hotfix/, release/

This will create and switch to: 'feature/new-awesome-feature' from current branch.
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

## Sample Operation: Reset to Origin (Option 12) - Enhanced DESTRUCTIVE

```
============================================================
   DANGER: Reset to Origin (DESTRUCTIVE OPERATION)
============================================================

WARNING: This operation is DESTRUCTIVE and CANNOT be undone easily!

What this does:
  1. Fetches the latest version of the branch from origin
  2. HARD RESETS your branch to match origin exactly (discards all local commits)
  3. DELETES all uncommitted changes (modified, staged, new files)
  4. Cleans untracked files and directories from your working tree

Use this when:
  - Your local branch is corrupted or in a bad state
  - You want to completely abandon local changes and start fresh
  - Recovering from a merge conflict by discarding local work
  - ONLY if you're absolutely sure you don't need the local changes

CANNOT BE UNDONE: Once executed, your local commits and changes are gone forever!
ALTERNATIVES: Consider using 'git stash' (option 10) or creating a backup branch.

Current branch: feature-branch

What will be DELETED:

Current uncommitted changes (will be LOST):
 M file1.txt
 M file2.js

Unpushed local commits (will be LOST FOREVER):
abc1234 Work in progress
def5678 Added new feature

Commands that will be executed:
  git fetch origin (download latest remote state)
  git reset --hard origin/feature-branch (DESTROY local commits)
  git clean -fd (DELETE untracked files)

╔═══════════════════════════════════════════════════════════════╗
║  FINAL WARNING: This will permanently delete your local work! ║
║  Make sure you have pushed or backed up anything important!   ║
╚═══════════════════════════════════════════════════════════════╝

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
