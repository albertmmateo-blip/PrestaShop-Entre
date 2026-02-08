@echo off
cd /d "%~dp0"

echo Stopping PrestaShop containers...
docker compose down

echo.
echo Done.
pause
