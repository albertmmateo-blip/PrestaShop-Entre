@echo off
REM ============================================================
REM Git Interactive Menu Script
REM A user-friendly interactive menu system for common Git operations
REM ============================================================

SETLOCAL EnableDelayedExpansion

REM Set up colors using ANSI escape codes (Windows 10+)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "CYAN=[96m"
set "WHITE=[97m"
set "RESET=[0m"

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

echo %GREEN%Current Branch:%RESET% %YELLOW%!CURRENT_BRANCH!%RESET%
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
echo %WHITE%This will fetch all branches and tags from origin.%RESET%
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
echo %WHITE%This will pull changes from origin/!CURRENT_BRANCH!.%RESET%
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
echo %WHITE%This will fetch and checkout a Pull Request from GitHub.%RESET%
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
echo %WHITE%This will create a new branch '!NEW_BRANCH!' from the current branch.%RESET%
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
echo %WHITE%This will push your commits to origin/!CURRENT_BRANCH!.%RESET%
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
echo %WHITE%This will push your current branch to origin/!TARGET_BRANCH!.%RESET%
echo %WHITE%Command to execute:%RESET% %YELLOW%git push origin !CURRENT_BRANCH!:!TARGET_BRANCH!%RESET%
echo.
echo %YELLOW%Warning: This can overwrite remote branch if names differ!%RESET%
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
echo %WHITE%Current branch:%RESET% %YELLOW%!CURRENT_BRANCH!%RESET%
echo.
echo %WHITE%Last 10 commits:%RESET%
echo %CYAN%------------------------------------------------------------%RESET%
echo.
git log -10 --oneline --decorate --graph
echo.
echo %CYAN%------------------------------------------------------------%RESET%
echo.
echo %WHITE%For more details, use:%RESET% %YELLOW%git log%RESET%
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
echo %WHITE%Current branch:%RESET% %YELLOW%!CURRENT_BRANCH!%RESET%
echo.
echo %WHITE%This will:%RESET%
echo   %RED%- Discard ALL local commits not pushed to origin%RESET%
echo   %RED%- Discard ALL uncommitted changes%RESET%
echo   %RED%- Reset your branch to match origin/!CURRENT_BRANCH! exactly%RESET%
echo.
echo %WHITE%Current uncommitted changes:%RESET%
git status --short
echo.
echo %WHITE%Unpushed commits (will be LOST):%RESET%
git log origin/!CURRENT_BRANCH!..HEAD --oneline 2>nul
if %ERRORLEVEL%==1 (
    echo %YELLOW%Could not determine unpushed commits.%RESET%
)
echo.
echo %WHITE%Commands to execute:%RESET%
echo   %YELLOW%git fetch origin%RESET%
echo   %YELLOW%git reset --hard origin/!CURRENT_BRANCH!%RESET%
echo   %YELLOW%git clean -fd%RESET%
echo.
echo %RED%====== FINAL WARNING ======%RESET%
echo %RED%This will permanently delete your local changes!%RESET%
echo %RED%============================%RESET%
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
