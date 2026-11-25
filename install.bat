@echo off
setlocal
cd /d "%~dp0"
echo [1/2] Checking Python...
py -3 --version
if errorlevel 1 (
  echo Python 3.10+ is required. Install Python and enable Add Python to PATH.
  pause
  exit /b 1
)
echo [2/2] Installing local controller dependency...
if not exist ".venv\Scripts\python.exe" py -3 -m venv .venv
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 goto failed
echo.
echo Setup complete. Run start.bat to open VacuumTube Remote.
pause
exit /b 0
:failed
echo Setup failed. Read the error above.
pause
exit /b 1
