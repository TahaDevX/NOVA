@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo             NOVA - Installer
echo ========================================
where py >nul 2>nul
if errorlevel 1 (
  echo Python Launcher not found. Install Python 3.10+ from python.org first.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  py -m venv .venv
  if errorlevel 1 goto :error
)
call ".venv\Scripts\activate.bat"
echo Installing required packages...
python -m pip install --upgrade pip
if errorlevel 1 goto :error
pip install -r requirements.txt
if errorlevel 1 goto :error
if not exist ".env" copy ".env.example" ".env" >nul
echo.
echo Installation completed.
echo Open .env and enter your OpenRouter API key, then run start.bat.
pause
exit /b 0
:error
echo Installation failed. Check the error above and your internet connection.
pause
exit /b 1
