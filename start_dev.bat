@echo off
echo ===================================================
echo [1/2] Menyalakan Container Odoo 17 & PostgreSQL...
echo ===================================================
docker compose up -d

echo.
echo ===================================================
echo [2/2] Memeriksa Status Container...
echo ===================================================
docker compose ps

echo.
echo ===================================================
echo SISTEM SIAP DIGUNAKAN!
echo - Web URL    : http://localhost:8069
echo - Database   : bbs_dev
echo - Master Pwd : admin_bbs_dev
echo ===================================================
echo.
pause
