@echo off
start /b "" "dist\radar-ao-vivo.exe"
timeout /t 3 /nobreak
start http://localhost:5000
