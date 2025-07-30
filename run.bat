@echo off
echo ========================================
echo Starting MT5 to Match-Trader Trade Copier
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the main application
python main.py

pause
