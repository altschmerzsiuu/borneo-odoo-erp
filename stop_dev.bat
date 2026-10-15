@echo off
echo ===================================================
echo [1/2] Mematikan Container Odoo & PostgreSQL...
echo ===================================================
docker compose down

echo.
echo ===================================================
echo [2/2] Mematikan WSL2 untuk melepaskan kuncian Drive P:...
echo ===================================================
wsl --shutdown

echo.
echo ===================================================
echo SELESAI! Semua service sudah mati 100%%.
echo Langkah terakhir: Tutup jendela VS Code/IDE, lalu
echo klik kanan Drive P: di Windows Explorer -> Eject.
echo SSD sudah aman untuk dicabut!
echo ===================================================
pause
