@echo off
cd /d "%~dp0"

echo Restarting PrestaShop (web) service...
docker compose restart prestashop-git

echo.
echo Done.
pause
