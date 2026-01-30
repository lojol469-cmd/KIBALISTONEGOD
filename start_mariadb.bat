@echo off
echo Starting MariaDB Server...
cd /d "%~dp0mariadb_portable\mariadb-11.4.2-winx64\bin"
start "" mariadbd.exe --datadir="%~dp0mariadb_portable\mariadb-11.4.2-winx64\data" --port=3306
echo MariaDB Server started. Press any key to stop...
pause >nul
taskkill /f /im mariadbd.exe
echo MariaDB Server stopped.