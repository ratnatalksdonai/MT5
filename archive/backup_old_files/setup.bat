@echo off
echo ========================================
echo Trade Copier Security Setup
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the setup script
python setup.py

pause
