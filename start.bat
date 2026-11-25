@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run install.bat first.
  pause
  exit /b 1
)
if not exist "node_modules" (
  echo Run install.bat first.
  pause
  exit /b 1
)
start "VacuumTube Remote - Local Controller" cmd /k ""%CD%\.venv\Scripts\python.exe" -m uvicorn local_agent:app --host 127.0.0.1 --port 8765"
start "VacuumTube Remote - Web App" cmd /k "npm run dev"
timeout /t 3 >nul
start "" "http://127.0.0.1:5173"
