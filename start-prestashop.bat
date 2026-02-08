@echo off
cd /d "%~dp0"

echo Starting PrestaShop containers...
docker compose up -d

echo.
echo Opening Back Office (fast)...
start http://localhost:8001/admin-fast/

echo.
echo Done.
pause
