# Git Interactive Menu - User Guide

A user-friendly Windows batch script that provides an interactive menu system for common Git operations.

## Features

### Core Functionality
- ✅ Interactive numbered menu system
- ✅ Keyboard navigation (number keys + Enter)
- ✅ Display current branch in menu header
- ✅ Color-coded output for better readability
- ✅ Clear screen between operations
- ✅ Shows actual Git commands before execution

### Supported Git Operations

1. **Fetch from origin** - Download all branches and tags from remote
2. **Pull from current branch** - Pull changes from origin for current branch
3. **Checkout to a different branch** - Switch to an existing branch
4. **Checkout a Pull Request by number** - Fetch and checkout a GitHub PR
5. **Create and checkout a new branch** - Create a new branch from current
6. **Push to origin (current branch)** - Push commits to remote
7. **Push to a specific branch** - Push to a different branch name
8. **View current branch and status** - Display detailed status information
9. **View recent commit history** - Show last 10 commits with graph
10. **Stash changes** - Save uncommitted changes for later
11. **Apply stash** - Restore previously stashed changes
12. **Reset to origin** - ⚠️ DESTRUCTIVE: Reset branch to match origin exactly
13. **Exit** - Close the menu system

### Safety Features

- ✅ Confirmation prompts for all operations
- ✅ Warning messages for destructive operations (reset, force push)
- ✅ Display uncommitted changes before checkout/reset
- ✅ Input validation for branch names and PR numbers
- ✅ Error handling with helpful messages
- ✅ Option to cancel at any confirmation step
- ✅ Success/failure feedback after execution

## Installation

1. Download `git-menu.bat` to your repository root or any directory
2. Ensure Git is installed and accessible from command line
3. Double-click the script or run from command prompt

## Usage

### Starting the Menu

**Option 1: Double-click**
```
Double-click git-menu.bat in Windows Explorer
```

**Option 2: Command Prompt**
```cmd
cd path\to\repository
git-menu.bat
```

### Navigating the Menu

1. The menu displays the current branch at the top
2. Type a number (1-13) corresponding to your desired operation
3. Press Enter to execute
4. Follow the prompts for confirmations and inputs
5. After each operation, choose:
   - **M** to return to main menu
   - **E** to exit

### Operation Examples

#### Example 1: Checking out a branch
```
Current Branch: main

Select operation: 3
Enter branch name: feature-branch
Continue? (y/n): y
```

#### Example 2: Creating a new branch
```
Current Branch: develop

Select operation: 5
Enter new branch name: feature/new-feature
Continue? (y/n): y
```

#### Example 3: Checking out a Pull Request
```
Current Branch: main

Select operation: 4
Enter Pull Request number: 123
Continue? (y/n): y
```

#### Example 4: Stashing changes
```
Current Branch: feature-branch

Select operation: 10
Changes to be stashed:
  M file1.txt
  M file2.js
Enter stash message: Work in progress
Continue? (y/n): y
```

### Safety Confirmations

For destructive operations like **Reset to origin** (option 12):
1. Type "RESET" (case-sensitive) to confirm
2. Type "yes" for final confirmation
3. The operation will show what will be deleted before executing

## Requirements

- Windows 10 or later (for ANSI color support)
- Git installed and configured
- Command prompt or Windows Terminal

## Color Support

The script uses ANSI escape codes for colored output:
- 🔵 **Cyan** - Headers and menu items
- 🟢 **Green** - Success messages and current branch
- 🟡 **Yellow** - Warnings and branch names
- 🔴 **Red** - Errors and critical warnings
- ⚪ **White** - General information

If colors don't display properly:
- Use Windows Terminal instead of legacy Command Prompt
- Ensure Windows 10 Anniversary Update (1607) or later

## Troubleshooting

### "Not a git repository" error
- Ensure you're running the script from within a Git repository
- Run `git status` to verify Git is working

### Colors not displaying
- Update to Windows 10 version 1607 or later
- Use Windows Terminal for best experience

### Branch not found
- Run option 8 to view available branches
- Ensure branch name is spelled correctly
- Use `git fetch` to download remote branches

### Push/Pull failures
- Check your network connection
- Verify remote origin is configured: `git remote -v`
- Ensure you have proper credentials/access

## Best Practices

1. **Before destructive operations**: Always review what will be changed
2. **Stash before switching branches**: Use option 10 to save work in progress
3. **Pull before push**: Keep your branch updated
4. **Use meaningful branch names**: Follow your team's naming conventions
5. **Review status regularly**: Use option 8 to stay informed

## Advanced Tips

### Viewing stash list
After stashing (option 10), manually run:
```cmd
git stash list
```

### Custom Git commands
For operations not in the menu, you can still use Git commands directly in your terminal.

### Integration with CI/CD
This menu is for local development. For automated operations, use Git commands directly in your scripts.

## License

This script is provided as-is for use with the PrestaShop-Entre repository.

## Support

For issues or suggestions:
1. Check this README for troubleshooting
2. Verify Git is installed and working
3. Ensure you're in a Git repository
4. Check Windows version supports ANSI colors

---

**Version**: 1.0  
**Last Updated**: February 2026  
**Compatible with**: Windows 10+, Git 2.x+
