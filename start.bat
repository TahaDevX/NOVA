@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\activate.bat" (
  echo First run install.bat to install NOVA.
  pause
  exit /b 1
)
call ".venv\Scripts\activate.bat"
python main.py
pause
