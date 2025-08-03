@echo off
echo 🚀 Starting MT5 to CTI Trade Copier...
echo.
echo Prerequisites Check:
echo ✓ MT5 Terminal should be running
echo ✓ Logged into GNTCapital-Demo with account 200374
echo ✓ CTI API access configured (contact support if not working)
echo.

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else if exist "venv_mvp\Scripts\activate.bat" (
    echo Activating MVP virtual environment...
    call venv_mvp\Scripts\activate.bat
) else (
    echo No virtual environment found, using system Python...
)

echo.
echo Starting trade copier...
python run_mvp.py

pause
