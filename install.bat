@echo off
setlocal
cd /d "%~dp0"
echo [1/3] Checking Python...
py -3 --version
if errorlevel 1 (
  echo Python 3 is required. Install Python 3.10+ and enable Add Python to PATH.
  pause
  exit /b 1
)
echo [2/3] Creating Python environment...
if not exist ".venv\Scripts\python.exe" py -3 -m venv .venv
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 goto failed
echo [3/3] Installing web dependencies...
where npm >nul 2>nul
if errorlevel 1 (
  echo Node.js 22.12.0+ is required. Install it, then run install.bat again.
  pause
  exit /b 1
)
npm install
if errorlevel 1 goto failed
if not exist ".env" copy ".env.example" ".env"
echo.
echo Setup complete. Edit .env and add your Zoom Meeting SDK credentials.
pause
exit /b 0
:failed
echo Setup failed. Read the error above.
pause
exit /b 1
