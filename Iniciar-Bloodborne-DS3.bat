@echo off
setlocal
cd /d "%~dp0"
if not exist "Bloodborne.exe" (
  echo Copia este BAT y la carpeta ds3_controls junto a Bloodborne.exe.
  pause
  exit /b 1
)
if not exist "ds3_controls\bridge.py" (
  echo Falta ds3_controls\bridge.py. Extrae todos los archivos del paquete.
  pause
  exit /b 1
)
"Bloodborne.exe" --script "%~dp0ds3_controls\bridge.py"
