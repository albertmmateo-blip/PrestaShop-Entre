@echo off
REM PrestaShop Cache Cleaner for Windows
REM This script clears PrestaShop cache directories

echo =============================================
echo PrestaShop Cache Cleaner
echo =============================================
echo.

cd /d "%~dp0"

echo Clearing PrestaShop cache...
echo.

REM Clear Symfony dev cache
if exist "var\cache\dev" (
    echo [*] Clearing development cache (var\cache\dev)...
    rmdir /s /q "var\cache\dev" 2>nul
    mkdir "var\cache\dev"
    echo     Done!
) else (
    echo [i] Development cache folder not found
)

REM Clear Symfony prod cache
if exist "var\cache\prod" (
    echo [*] Clearing production cache (var\cache\prod)...
    rmdir /s /q "var\cache\prod" 2>nul
    mkdir "var\cache\prod"
    echo     Done!
) else (
    echo [i] Production cache folder not found
)

REM Clear Smarty compiled templates
if exist "cache\smarty\compile" (
    echo [*] Clearing Smarty compiled templates...
    del /q /s "cache\smarty\compile\*.*" 2>nul
    echo     Done!
) else (
    echo [i] Smarty compile folder not found
)

REM Clear Smarty cache
if exist "cache\smarty\cache" (
    echo [*] Clearing Smarty cache...
    del /q /s "cache\smarty\cache\*.*" 2>nul
    echo     Done!
) else (
    echo [i] Smarty cache folder not found
)

echo.
echo =============================================
echo Cache cleared successfully!
echo =============================================
echo.
echo Note: First page load may be slower as cache rebuilds
echo.
pause
