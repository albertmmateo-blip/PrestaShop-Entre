@echo off
cd /d "%~dp0"

echo Clearing PrestaShop cache safely...
docker exec -it prestashop-prestashop-git-1 bash -lc "cd /var/www/html && rm -rf var/cache/* && mkdir -p var/cache"

echo.
echo Done.
pause
