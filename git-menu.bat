@echo off
REM ============================================================
REM Git Interactive Menu Script
REM A user-friendly interactive menu system for common Git operations
REM ============================================================

SETLOCAL EnableDelayedExpansion

REM Enable ANSI color support in Windows 10+
REM Set ESC character for potential use with ANSI sequences
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do set "ESC=%%b"
REM Enable Virtual Terminal Processing to interpret ANSI codes in Console
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1

REM Set up colors using ANSI escape codes (Windows 10+)
set "RED=%ESC%[91m"
set "GREEN=%ESC%[92m"
set "YELLOW=%ESC%[93m"
set "BLUE=%ESC%[94m"
set "CYAN=%ESC%[96m"
set "WHITE=%ESC%[97m"
set "RESET=%ESC%[0m"

:MAIN_MENU
cls
echo.
echo %CYAN%============================================================%RESET%
echo %CYAN%           Git Interactive Menu System%RESET%
echo %CYAN%============================================================%RESET%
echo.

REM Get current branch name
for /f "tokens=*" %%i in ('git branch --show-current 2^>nul') do set CURRENT_BRANCH=%%i
if "!CURRENT_BRANCH!"=="" (
    echo %RED%Error: Not a git repository or unable to determine branch%RESET%
    echo.
    pause
    exit /b 1
)

REM Get sync status (commits behind/ahead)
set BEHIND=0
set AHEAD=0
set SYNC_STATUS=
git rev-list --left-right --count origin/!CURRENT_BRANCH!...HEAD 2>nul >nul
if %ERRORLEVEL%==0 (
    for /f "tokens=1,2" %%a in ('git rev-list --left-right --count origin/!CURRENT_BRANCH!...HEAD 2^>nul') do (
        set BEHIND=%%a
        set AHEAD=%%b
    )
    if !BEHIND!==0 if !AHEAD!==0 (
        set SYNC_STATUS=%GREEN%[Synced]%RESET%
    ) else if !BEHIND! GTR 0 if !AHEAD!==0 (
        set SYNC_STATUS=%YELLOW%[!BEHIND! behind]%RESET%
    ) else if !BEHIND!==0 if !AHEAD! GTR 0 (
        set SYNC_STATUS=%CYAN%[!AHEAD! ahead]%RESET%
    ) else (
        set SYNC_STATUS=%RED%[!BEHIND! behind, !AHEAD! ahead]%RESET%
    )
) else (
    set SYNC_STATUS=%YELLOW%[No remote branch]%RESET%
)

REM Check for uncommitted changes
git diff-index --quiet HEAD -- 2>nul
if %ERRORLEVEL%==1 (
    set UNCOMMITTED=%YELLOW%[Uncommitted changes]%RESET%
) else (
    set UNCOMMITTED=
)

echo %GREEN%Current Branch:%RESET% %YELLOW%!CURRENT_BRANCH!%RESET% !SYNC_STATUS! !UNCOMMITTED!
echo.
echo %CYAN%------------------------------------------------------------%RESET%
echo %WHITE%Select a Git operation:%RESET%
echo.
echo  %CYAN%1.%RESET%  Fetch from origin
echo  %CYAN%2.%RESET%  Pull from current branch
echo  %CYAN%3.%RESET%  Checkout to a different branch
echo  %CYAN%4.%RESET%  Checkout a Pull Request by number
echo  %CYAN%5.%RESET%  Create and checkout a new branch
echo  %CYAN%6.%RESET%  Push to origin (current branch)
echo  %CYAN%7.%RESET%  Push to a specific branch
echo  %CYAN%8.%RESET%  View current branch and status
echo  %CYAN%9.%RESET%  View recent commit history
echo  %CYAN%10.%RESET% Stash changes
echo  %CYAN%11.%RESET% Apply stash
echo  %CYAN%12.%RESET% Reset to origin %RED%(WARNING: Destructive!)%RESET%
echo  %CYAN%13.%RESET% Exit
echo.
echo %CYAN%------------------------------------------------------------%RESET%
echo.

set /p CHOICE="Enter your choice (1-13): "

REM Validate input
set VALID=0
for %%i in (1 2 3 4 5 6 7 8 9 10 11 12 13) do (
    if "%CHOICE%"=="%%i" set VALID=1
)

if %VALID%==0 (
    echo %RED%Invalid choice. Please enter a number between 1 and 13.%RESET%
    timeout /t 2 >nul
    goto MAIN_MENU
)

REM Execute chosen operation
if "%CHOICE%"=="1" goto FETCH_ORIGIN
if "%CHOICE%"=="2" goto PULL_CURRENT
if "%CHOICE%"=="3" goto CHECKOUT_BRANCH
if "%CHOICE%"=="4" goto CHECKOUT_PR
if "%CHOICE%"=="5" goto CREATE_BRANCH
if "%CHOICE%"=="6" goto PUSH_CURRENT
if "%CHOICE%"=="7" goto PUSH_SPECIFIC
if "%CHOICE%"=="8" goto VIEW_STATUS
if "%CHOICE%"=="9" goto VIEW_HISTORY
if "%CHOICE%"=="10" goto STASH_CHANGES
if "%CHOICE%"=="11" goto APPLY_STASH
if "%CHOICE%"=="12" goto RESET_ORIGIN
if "%CHOICE%"=="13" goto EXIT_SCRIPT

REM ============================================================
REM OPERATION 1: Fetch from origin
REM ============================================================
:FETCH_ORIGIN
cls
echo.
echo %CYAN%============================================================%RESET%
echo %CYAN%   Fetch from Origin%RESET%
echo %CYAN%============================================================%RESET%
echo.
echo %WHITE%What this does:%RESET%
echo   - Downloads all new commits, branches, and tags from the remote repository
echo   - %GREEN%Safe operation%RESET% - Does NOT merge or modify your working directory
echo   - Updates your local copy of remote branches (origin/branch-name)
echo   - After fetching, you can see what changed with 'git log' or merge manually
echo.
echo %WHITE%Use this when:%RESET%
echo   - You want to see what's new on the remote without changing your code
echo   - Before pulling to check what changes are incoming
echo   - To update all remote branch information
echo.
echo %WHITE%Command to execute:%RESET% %YELLOW%git fetch origin%RESET%
echo.
set /p CONFIRM="Continue? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo %YELLOW%Operation cancelled.%RESET%
    goto OPERATION_END
)

echo.
echo %CYAN%Executing:%RESET% git fetch origin
echo.
git fetch origin
if %ERRORLEVEL%==0 (
    echo.
    echo %GREEN%Success: Fetched from origin successfully.%RESET%
) else (
    echo.
    echo %RED%Error: Failed to fetch from origin.%RESET%
)
goto OPERATION_END

REM ============================================================
REM OPERATION 2: Pull from current branch
REM ============================================================
:PULL_CURRENT
cls
echo.
echo %CYAN%============================================================%RESET%
echo %CYAN%   Pull from Current Branch%RESET%
echo %CYAN%============================================================%RESET%
echo.
echo %WHITE%Current branch:%RESET% %YELLOW%!CURRENT_BRANCH!%RESET%
echo.
echo %WHITE%What this does:%RESET%
echo   - Fetches commits from origin/!CURRENT_BRANCH!
echo   - Automatically merges them into your current branch
echo   - Combines 'git fetch' and 'git merge' in one command
echo   - May require resolving conflicts if changes overlap
echo.
echo %WHITE%Use this when:%RESET%
echo   - You want to get the latest changes from the remote branch
echo   - Your branch is behind the remote and you want to sync
echo   - Working in a team and need to integrate others' work
echo.
echo %YELLOW%Note:%RESET% If you have uncommitted changes, they may conflict with incoming changes.
echo Consider stashing your changes first (option 10) if you have conflicts.
echo.
echo %WHITE%Command to execute:%RESET% %YELLOW%git pull origin !CURRENT_BRANCH!%RESET%
echo.

REM Check for uncommitted changes
git diff-index --quiet HEAD --
if %ERRORLEVEL%==1 (
    echo %YELLOW%Warning: You have uncommitted changes.%RESET%
    git status --short
    echo.
)

set /p CONFIRM="Continue? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo %YELLOW%Operation cancelled.%RESET%
    goto OPERATION_END
)

echo.
echo %CYAN%Executing:%RESET% git pull origin !CURRENT_BRANCH!
echo.
git pull origin !CURRENT_BRANCH!
if %ERRORLEVEL%==0 (
    echo.
    echo %GREEN%Success: Pulled from origin/!CURRENT_BRANCH! successfully.%RESET%
) else (
    echo.
    echo %RED%Error: Failed to pull from origin/!CURRENT_BRANCH!.%RESET%
    echo %YELLOW%Tip: You may need to resolve merge conflicts or stash your changes.%RESET%
)
goto OPERATION_END

REM ============================================================
REM OPERATION 3: Checkout to a different branch
REM ============================================================
:CHECKOUT_BRANCH
cls
echo.
echo %CYAN%============================================================%RESET%
echo %CYAN%   Checkout to a Different Branch%RESET%
echo %CYAN%============================================================%RESET%
echo.
echo %WHITE%Current branch:%RESET% %YELLOW%!CURRENT_BRANCH!%RESET%
echo.
echo %WHITE%What this does:%RESET%
echo   - Switches your working directory to a different branch
echo   - Updates all files to match the selected branch
echo   - Changes HEAD pointer to the target branch
echo   - Uncommitted changes will be carried over if they don't conflict
echo.
echo %WHITE%Use this when:%RESET%
echo   - You need to work on a different feature or bug fix
echo   - Reviewing someone else's work on another branch
echo   - Switching between development tasks
echo.
echo %YELLOW%Important:%RESET% Uncommitted changes may prevent checkout or be carried over.
echo Consider committing or stashing changes first (option 10).
echo.
echo %WHITE%Available branches:%RESET%
git branch -a
echo.

REM Check for uncommitted changes
git diff-index --quiet HEAD --
if %ERRORLEVEL%==1 (
    echo %YELLOW%Warning: You have uncommitted changes.%RESET%
    git status --short
    echo.
    echo %YELLOW%These changes may prevent checkout or will be carried over.%RESET%
    echo.
)

set /p BRANCH_NAME="Enter branch name to checkout: "
if "!BRANCH_NAME!"=="" (
    echo %RED%Error: Branch name cannot be empty.%RESET%
    goto OPERATION_END
)

echo.
echo %WHITE%Command to execute:%RESET% %YELLOW%git checkout !BRANCH_NAME!%RESET%
echo.
set /p CONFIRM="Continue? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo %YELLOW%Operation cancelled.%RESET%
    goto OPERATION_END
)

echo.
echo %CYAN%Executing:%RESET% git checkout !BRANCH_NAME!
echo.
git checkout !BRANCH_NAME!
if %ERRORLEVEL%==0 (
    echo.
    echo %GREEN%Success: Checked out to branch !BRANCH_NAME!.%RESET%
) else (
    echo.
    echo %RED%Error: Failed to checkout to branch !BRANCH_NAME!.%RESET%
    echo %YELLOW%Tip: Make sure the branch exists or stash your changes.%RESET%
)
goto OPERATION_END

REM ============================================================
REM OPERATION 4: Checkout a Pull Request by number
REM ============================================================
:CHECKOUT_PR
cls
echo.
echo %CYAN%============================================================%RESET%
echo %CYAN%   Checkout Pull Request%RESET%
echo %CYAN%============================================================%RESET%
echo.
echo %WHITE%What this does:%RESET%
echo   - Fetches a specific Pull Request from GitHub by its number
echo   - Creates a local branch named 'pr-{number}' with the PR's code
echo   - Switches to the new branch so you can test/review the PR
echo   - Uses GitHub's PR reference: pull/{number}/head
echo.
echo %WHITE%Use this when:%RESET%
echo   - You want to test someone's Pull Request locally
echo   - Reviewing code changes before merging
echo   - Running tests on a PR before approval
echo.
echo %YELLOW%Note:%RESET% The PR must exist in the remote repository.
echo The local branch 'pr-{number}' will be created if it doesn't exist.
echo.

set /p PR_NUMBER="Enter Pull Request number: "
if "!PR_NUMBER!"=="" (
    echo %RED%Error: Pull Request number cannot be empty.%RESET%
    goto OPERATION_END
)

REM Validate PR number is numeric
echo !PR_NUMBER!| findstr /r "^[0-9][0-9]*$" >nul
if %ERRORLEVEL%==1 (
    echo %RED%Error: Pull Request number must be numeric.%RESET%
    goto OPERATION_END
)

echo.
echo %WHITE%Commands to execute:%RESET%
echo   %YELLOW%git fetch origin pull/!PR_NUMBER!/head:pr-!PR_NUMBER!%RESET%
echo   %YELLOW%git checkout pr-!PR_NUMBER!%RESET%
echo.
set /p CONFIRM="Continue? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo %YELLOW%Operation cancelled.%RESET%
    goto OPERATION_END
)

echo.
echo %CYAN%Executing:%RESET% git fetch origin pull/!PR_NUMBER!/head:pr-!PR_NUMBER!
echo.
git fetch origin pull/!PR_NUMBER!/head:pr-!PR_NUMBER!
if %ERRORLEVEL%==0 (
    echo.
    echo %CYAN%Executing:%RESET% git checkout pr-!PR_NUMBER!
    echo.
    git checkout pr-!PR_NUMBER!
    if %ERRORLEVEL%==0 (
        echo.
        echo %GREEN%Success: Checked out Pull Request #!PR_NUMBER! to branch pr-!PR_NUMBER!.%RESET%
    ) else (
        echo.
        echo %RED%Error: Failed to checkout PR branch.%RESET%
    )
) else (
    echo.
    echo %RED%Error: Failed to fetch Pull Request #!PR_NUMBER!.%RESET%
    echo %YELLOW%Tip: Make sure the PR number exists in the repository.%RESET%
)
goto OPERATION_END

REM ============================================================
REM OPERATION 5: Create and checkout a new branch
REM ============================================================
:CREATE_BRANCH
cls
echo.
echo %CYAN%============================================================%RESET%
echo %CYAN%   Create and Checkout New Branch%RESET%
echo %CYAN%============================================================%RESET%
echo.
echo %WHITE%Current branch:%RESET% %YELLOW%!CURRENT_BRANCH!%RESET%
echo.

set /p NEW_BRANCH="Enter new branch name: "
if "!NEW_BRANCH!"=="" (
    echo %RED%Error: Branch name cannot be empty.%RESET%
    goto OPERATION_END
)

REM Validate branch name (basic validation)
echo !NEW_BRANCH!| findstr /r "[~^: \\]" >nul
if %ERRORLEVEL%==0 (
    echo %RED%Error: Branch name contains invalid characters.%RESET%
    echo %YELLOW%Tip: Avoid spaces and special characters like ~, ^, :, \, etc.%RESET%
    goto OPERATION_END
)

echo.
echo %WHITE%What this does:%RESET%
echo   - Creates a new branch starting from your current commit (HEAD)
echo   - Automatically switches to the newly created branch
echo   - The new branch starts with all commits from the current branch
echo   - Your working directory remains unchanged
echo.
echo %WHITE%Use this when:%RESET%
echo   - Starting work on a new feature or bug fix
echo   - Creating a branch for experimentation
echo   - Separating development work from the main branch
echo.
echo %WHITE%Branch name tips:%RESET%
echo   - Use descriptive names: feature/user-login, bugfix/crash-on-save
echo   - Avoid spaces and special characters (~, ^, :, \, etc.)
echo   - Common conventions: feature/, bugfix/, hotfix/, release/
echo.
echo %WHITE%This will create and switch to: '%YELLOW%!NEW_BRANCH!%WHITE%' from current branch.%RESET%
echo %WHITE%Command to execute:%RESET% %YELLOW%git checkout -b !NEW_BRANCH!%RESET%
echo.
set /p CONFIRM="Continue? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo %YELLOW%Operation cancelled.%RESET%
    goto OPERATION_END
)

echo.
echo %CYAN%Executing:%RESET% git checkout -b !NEW_BRANCH!
echo.
git checkout -b !NEW_BRANCH!
if %ERRORLEVEL%==0 (
    echo.
    echo %GREEN%Success: Created and checked out to branch !NEW_BRANCH!.%RESET%
) else (
    echo.
    echo %RED%Error: Failed to create branch !NEW_BRANCH!.%RESET%
    echo %YELLOW%Tip: The branch may already exist.%RESET%
)
goto OPERATION_END

REM ============================================================
REM OPERATION 6: Push to origin (current branch)
REM ============================================================
:PUSH_CURRENT
cls
echo.
echo %CYAN%============================================================%RESET%
echo %CYAN%   Push to Origin (Current Branch)%RESET%
echo %CYAN%============================================================%RESET%
echo.
echo %WHITE%Current branch:%RESET% %YELLOW%!CURRENT_BRANCH!%RESET%
echo.
echo %WHITE%What this does:%RESET%
echo   - Uploads your local commits to the remote repository (origin)
echo   - Updates origin/!CURRENT_BRANCH! with your new commits
echo   - Makes your changes available to other team members
echo   - If the remote branch doesn't exist, it will be created
echo.
echo %WHITE%Use this when:%RESET%
echo   - You've made commits and want to share them with the team
echo   - Backing up your work to the remote repository
echo   - Your branch is ahead of origin and you want to sync
echo   - Before creating a Pull Request
echo.
echo %YELLOW%Note:%RESET% If the remote branch has changes you don't have, push may fail.
echo You'll need to pull first (option 2) to merge remote changes.
echo.
echo %WHITE%Command to execute:%RESET% %YELLOW%git push origin !CURRENT_BRANCH!%RESET%
echo.

REM Show commits to be pushed
echo %WHITE%Commits to be pushed:%RESET%
git log origin/!CURRENT_BRANCH!..HEAD --oneline 2>nul
if %ERRORLEVEL%==1 (
    echo %YELLOW%Note: Branch may not exist on origin yet (will be created).%RESET%
)
echo.

set /p CONFIRM="Continue? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo %YELLOW%Operation cancelled.%RESET%
    goto OPERATION_END
)

echo.
echo %CYAN%Executing:%RESET% git push origin !CURRENT_BRANCH!
echo.
git push origin !CURRENT_BRANCH!
if %ERRORLEVEL%==0 (
    echo.
    echo %GREEN%Success: Pushed to origin/!CURRENT_BRANCH! successfully.%RESET%
) else (
    echo.
    echo %RED%Error: Failed to push to origin/!CURRENT_BRANCH!.%RESET%
    echo %YELLOW%Tip: You may need to pull first or use force push if histories diverged.%RESET%
)
goto OPERATION_END

REM ============================================================
REM OPERATION 7: Push to a specific branch
REM ============================================================
:PUSH_SPECIFIC
cls
echo.
echo %CYAN%============================================================%RESET%
echo %CYAN%   Push to a Specific Branch%RESET%
echo %CYAN%============================================================%RESET%
echo.
echo %WHITE%Current branch:%RESET% %YELLOW%!CURRENT_BRANCH!%RESET%
echo.

set /p TARGET_BRANCH="Enter target branch name: "
if "!TARGET_BRANCH!"=="" (
    echo %RED%Error: Branch name cannot be empty.%RESET%
    goto OPERATION_END
)

echo.
echo %WHITE%What this does:%RESET%
echo   - Pushes your current branch (!CURRENT_BRANCH!) to a different remote branch name
echo   - Format: git push origin local-branch:remote-branch
echo   - Creates the remote branch if it doesn't exist
echo   - Can be used to rename a branch on the remote
echo.
echo %WHITE%Use this when:%RESET%
echo   - You want to push to a different branch name on the remote
echo   - Creating a backup with a different name
echo   - Contributing to a branch with a specific naming convention
echo.
echo %RED%WARNING:%RESET% %YELLOW%This can overwrite the remote branch if it already exists!%RESET%
echo Make sure you know what you're doing to avoid data loss.
echo.
echo %WHITE%This will push:%RESET% %YELLOW%!CURRENT_BRANCH!%RESET% %WHITE%to remote:%RESET% %YELLOW%!TARGET_BRANCH!%RESET%
echo %WHITE%Command to execute:%RESET% %YELLOW%git push origin !CURRENT_BRANCH!:!TARGET_BRANCH!%RESET%
echo.

set /p CONFIRM="Continue? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo %YELLOW%Operation cancelled.%RESET%
    goto OPERATION_END
)

echo.
echo %CYAN%Executing:%RESET% git push origin !CURRENT_BRANCH!:!TARGET_BRANCH!
echo.
git push origin !CURRENT_BRANCH!:!TARGET_BRANCH!
if %ERRORLEVEL%==0 (
    echo.
    echo %GREEN%Success: Pushed to origin/!TARGET_BRANCH! successfully.%RESET%
) else (
    echo.
    echo %RED%Error: Failed to push to origin/!TARGET_BRANCH!.%RESET%
)
goto OPERATION_END

REM ============================================================
REM OPERATION 8: View current branch and status
REM ============================================================
:VIEW_STATUS
cls
echo.
echo %CYAN%============================================================%RESET%
echo %CYAN%   Current Branch and Status%RESET%
echo %CYAN%============================================================%RESET%
echo.
echo %WHITE%What this shows:%RESET%
echo   - Current branch name and tracking status
echo   - Modified, added, deleted, and untracked files
echo   - Whether you're ahead/behind the remote branch
echo   - Number of stashed changes (if any)
echo.
echo %WHITE%Use this when:%RESET%
echo   - You want to see what changes you've made
echo   - Checking if you're in sync with the remote
echo   - Before committing to review what will be included
echo   - Verifying your working directory state
echo.
echo %WHITE%Current branch:%RESET% %YELLOW%!CURRENT_BRANCH!%RESET%
echo.
echo %CYAN%------------------------------------------------------------%RESET%
echo %WHITE%Git Status:%RESET%
echo %CYAN%------------------------------------------------------------%RESET%
echo.
git status
echo.
echo %CYAN%------------------------------------------------------------%RESET%
echo %WHITE%Local vs Remote:%RESET%
echo %CYAN%------------------------------------------------------------%RESET%
echo.
git rev-list --left-right --count origin/!CURRENT_BRANCH!...HEAD 2>nul
if %ERRORLEVEL%==0 (
    for /f "tokens=1,2" %%a in ('git rev-list --left-right --count origin/!CURRENT_BRANCH!...HEAD') do (
        echo Behind origin by %%a commit(s)
        echo Ahead of origin by %%b commit(s)
    )
) else (
    echo %YELLOW%Could not compare with origin (branch may not exist remotely).%RESET%
)
echo.
echo %CYAN%------------------------------------------------------------%RESET%
echo %WHITE%Stash List:%RESET%
echo %CYAN%------------------------------------------------------------%RESET%
echo.
git stash list
if %ERRORLEVEL%==1 (
    echo No stashes found.
)
goto OPERATION_END

REM ============================================================
REM OPERATION 9: View recent commit history
REM ============================================================
:VIEW_HISTORY
cls
echo.
echo %CYAN%============================================================%RESET%
echo %CYAN%   Recent Commit History%RESET%
echo %CYAN%============================================================%RESET%
echo.
echo %WHITE%What this shows:%RESET%
echo   - Last 10 commits in a graphical tree view
echo   - Commit hash (short form) for referencing commits
echo   - Commit messages showing what changed
echo   - Branch and tag decorations
echo   - Commit relationships and merge history
echo.
echo %WHITE%Use this when:%RESET%
echo   - You want to see recent changes to the codebase
echo   - Finding a specific commit by its message
echo   - Understanding the branch structure and merges
echo   - Before resetting or reverting changes
echo.
echo %WHITE%Current branch:%RESET% %YELLOW%!CURRENT_BRANCH!%RESET%
echo.
echo %WHITE%Last 10 commits:%RESET%
echo %CYAN%------------------------------------------------------------%RESET%
echo.
git log -10 --oneline --decorate --graph
echo.
echo %CYAN%------------------------------------------------------------%RESET%
echo.
echo %WHITE%For more details, use:%RESET% %YELLOW%git log%RESET% %WHITE% or %RESET% %YELLOW%git log --stat%RESET%
goto OPERATION_END

REM ============================================================
REM OPERATION 10: Stash changes
REM ============================================================
:STASH_CHANGES
cls
echo.
echo %CYAN%============================================================%RESET%
echo %CYAN%   Stash Changes%RESET%
echo %CYAN%============================================================%RESET%
echo.
echo %WHITE%What this does:%RESET%
echo   - Temporarily saves your uncommitted changes (modified and staged files)
echo   - Reverts your working directory to match the last commit (clean state)
echo   - Allows you to switch branches without committing incomplete work
echo   - Creates a stash entry you can apply later
echo.
echo %WHITE%Use this when:%RESET%
echo   - You need to switch branches but aren't ready to commit
echo   - Pulling changes and you have local modifications
echo   - Want to test something with a clean working directory
echo   - Saving work in progress before trying something risky
echo.
echo %YELLOW%Note:%RESET% Untracked files are NOT stashed by default.
echo Use 'git stash -u' manually to include untracked files.
echo.
echo %WHITE%This will save your uncommitted changes to the stash.%RESET%
echo.

REM Check if there are changes to stash
git diff-index --quiet HEAD --
if %ERRORLEVEL%==0 (
    echo %YELLOW%Note: No changes detected to stash.%RESET%
    git status --short
    echo.
    set /p CONFIRM="Continue anyway? (y/n): "
    if /i not "%CONFIRM%"=="y" (
        echo %YELLOW%Operation cancelled.%RESET%
        goto OPERATION_END
    )
) else (
    echo %WHITE%Changes to be stashed:%RESET%
    git status --short
    echo.
)

set /p STASH_MESSAGE="Enter stash message (optional, press Enter to skip): "
if "!STASH_MESSAGE!"=="" (
    set STASH_CMD=git stash
    echo %WHITE%Command to execute:%RESET% %YELLOW%git stash%RESET%
) else (
    set STASH_CMD=git stash push -m "!STASH_MESSAGE!"
    echo %WHITE%Command to execute:%RESET% %YELLOW%git stash push -m "!STASH_MESSAGE!"%RESET%
)
echo.
set /p CONFIRM="Continue? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo %YELLOW%Operation cancelled.%RESET%
    goto OPERATION_END
)

echo.
echo %CYAN%Executing:%RESET% !STASH_CMD!
echo.
!STASH_CMD!
if %ERRORLEVEL%==0 (
    echo.
    echo %GREEN%Success: Changes stashed successfully.%RESET%
    echo %WHITE%To view stashes, use:%RESET% %YELLOW%git stash list%RESET%
) else (
    echo.
    echo %RED%Error: Failed to stash changes.%RESET%
)
goto OPERATION_END

REM ============================================================
REM OPERATION 11: Apply stash
REM ============================================================
:APPLY_STASH
cls
echo.
echo %CYAN%============================================================%RESET%
echo %CYAN%   Apply Stash%RESET%
echo %CYAN%============================================================%RESET%
echo.
echo %WHITE%What this does:%RESET%
echo   - Restores previously stashed changes to your working directory
echo   - Applies changes on top of your current code
echo   - Keeps the stash in the list (use 'git stash pop' to remove it)
echo   - May create conflicts if changes overlap with current work
echo.
echo %WHITE%Use this when:%RESET%
echo   - You want to restore work you previously stashed
echo   - Continuing work after switching back to a branch
echo   - Applying the same changes to multiple branches
echo   - Testing if stashed changes still work with current code
echo.
echo %YELLOW%Note:%RESET% If there are conflicts, you'll need to resolve them manually.
echo The stash will remain in the list until you use 'git stash drop' or 'pop'.
echo.
echo %WHITE%Available stashes:%RESET%
echo.
git stash list
if %ERRORLEVEL%==1 (
    echo %YELLOW%No stashes found.%RESET%
    goto OPERATION_END
)
echo.

set /p STASH_INDEX="Enter stash index (e.g., 0 for stash@{0}) or press Enter for latest: "
if "!STASH_INDEX!"=="" (
    set STASH_REF=stash@{0}
    echo %WHITE%Command to execute:%RESET% %YELLOW%git stash apply%RESET%
) else (
    echo !STASH_INDEX!| findstr /r "^[0-9][0-9]*$" >nul
    if %ERRORLEVEL%==1 (
        echo %RED%Error: Stash index must be numeric.%RESET%
        goto OPERATION_END
    )
    set STASH_REF=stash@{!STASH_INDEX!}
    echo %WHITE%Command to execute:%RESET% %YELLOW%git stash apply stash@{!STASH_INDEX!}%RESET%
)
echo.
echo %YELLOW%Note: This will apply the stash but keep it in the stash list.%RESET%
echo %WHITE%To remove after applying, use 'git stash pop' manually.%RESET%
echo.

set /p CONFIRM="Continue? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo %YELLOW%Operation cancelled.%RESET%
    goto OPERATION_END
)

echo.
if "!STASH_INDEX!"=="" (
    echo %CYAN%Executing:%RESET% git stash apply
    echo.
    git stash apply
) else (
    echo %CYAN%Executing:%RESET% git stash apply stash@{!STASH_INDEX!}
    echo.
    git stash apply stash@{!STASH_INDEX!}
)

if %ERRORLEVEL%==0 (
    echo.
    echo %GREEN%Success: Stash applied successfully.%RESET%
) else (
    echo.
    echo %RED%Error: Failed to apply stash.%RESET%
    echo %YELLOW%Tip: There may be conflicts to resolve.%RESET%
)
goto OPERATION_END

REM ============================================================
REM OPERATION 12: Reset to origin (DESTRUCTIVE)
REM ============================================================
:RESET_ORIGIN
cls
echo.
echo %RED%============================================================%RESET%
echo %RED%   DANGER: Reset to Origin (DESTRUCTIVE OPERATION)%RESET%
echo %RED%============================================================%RESET%
echo.
echo %RED%WARNING: This operation is DESTRUCTIVE and CANNOT be undone easily!%RESET%
echo.
echo %WHITE%What this does:%RESET%
echo   %RED%1. Fetches the latest version of the branch from origin%RESET%
echo   %RED%2. HARD RESETS your branch to match origin exactly (discards all local commits)%RESET%
echo   %RED%3. DELETES all uncommitted changes (modified, staged, new files)%RESET%
echo   %RED%4. Cleans untracked files and directories from your working tree%RESET%
echo.
echo %WHITE%Use this when:%RESET%
echo   - Your local branch is corrupted or in a bad state
echo   - You want to completely abandon local changes and start fresh
echo   - Recovering from a merge conflict by discarding local work
echo   - %YELLOW%ONLY if you're absolutely sure you don't need the local changes%RESET%
echo.
echo %RED%CANNOT BE UNDONE:%RESET% %WHITE%Once executed, your local commits and changes are gone forever!%RESET%
echo %YELLOW%ALTERNATIVES:%RESET% Consider using 'git stash' (option 10) or creating a backup branch.
echo.
echo %WHITE%Current branch:%RESET% %YELLOW%!CURRENT_BRANCH!%RESET%
echo.
echo %WHITE%What will be DELETED:%RESET%
echo.
echo %WHITE%Current uncommitted changes (will be LOST):%RESET%
git status --short
echo.
echo %WHITE%Unpushed local commits (will be LOST FOREVER):%RESET%
git log origin/!CURRENT_BRANCH!..HEAD --oneline 2>nul
if %ERRORLEVEL%==1 (
    echo %YELLOW%Could not determine unpushed commits (branch may not exist on origin).%RESET%
)
echo.
echo %WHITE%Commands that will be executed:%RESET%
echo   %YELLOW%git fetch origin%RESET% %WHITE%(download latest remote state)%RESET%
echo   %YELLOW%git reset --hard origin/!CURRENT_BRANCH!%RESET% %RED%(DESTROY local commits)%RESET%
echo   %YELLOW%git clean -fd%RESET% %RED%(DELETE untracked files)%RESET%
echo.
echo %RED%╔═══════════════════════════════════════════════════════════════╗%RESET%
echo %RED%║  FINAL WARNING: This will permanently delete your local work! ║%RESET%
echo %RED%║  Make sure you have pushed or backed up anything important!   ║%RESET%
echo %RED%╚═══════════════════════════════════════════════════════════════╝%RESET%
echo.

set /p CONFIRM1="Type 'RESET' to confirm (case-sensitive): "
if not "!CONFIRM1!"=="RESET" (
    echo %YELLOW%Operation cancelled (confirmation not matched).%RESET%
    goto OPERATION_END
)

echo.
set /p CONFIRM2="Are you absolutely sure? (yes/no): "
if /i not "!CONFIRM2!"=="yes" (
    echo %YELLOW%Operation cancelled.%RESET%
    goto OPERATION_END
)

echo.
echo %CYAN%Executing:%RESET% git fetch origin
echo.
git fetch origin
if %ERRORLEVEL%==1 (
    echo %RED%Error: Failed to fetch from origin.%RESET%
    goto OPERATION_END
)

echo.
echo %CYAN%Executing:%RESET% git reset --hard origin/!CURRENT_BRANCH!
echo.
git reset --hard origin/!CURRENT_BRANCH!
if %ERRORLEVEL%==1 (
    echo %RED%Error: Failed to reset to origin/!CURRENT_BRANCH!.%RESET%
    goto OPERATION_END
)

echo.
echo %CYAN%Executing:%RESET% git clean -fd
echo.
git clean -fd

echo.
echo %GREEN%Success: Reset to origin/!CURRENT_BRANCH! completed.%RESET%
echo %YELLOW%All local changes have been discarded.%RESET%
goto OPERATION_END

REM ============================================================
REM Operation end - Return to menu or exit
REM ============================================================
:OPERATION_END
echo.
echo %CYAN%------------------------------------------------------------%RESET%
echo.
set /p CONTINUE="Press 'M' for menu or 'E' to exit: "
if /i "!CONTINUE!"=="M" goto MAIN_MENU
if /i "!CONTINUE!"=="E" goto EXIT_SCRIPT
goto MAIN_MENU

REM ============================================================
REM Exit script
REM ============================================================
:EXIT_SCRIPT
cls
echo.
echo %CYAN%============================================================%RESET%
echo %GREEN%   Thank you for using Git Interactive Menu!%RESET%
echo %CYAN%============================================================%RESET%
echo.
echo %WHITE%Goodbye!%RESET%
echo.
timeout /t 2 >nul
exit /b 0
