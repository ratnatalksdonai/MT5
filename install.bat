@echo off
echo ========================================
echo MT5 to Match-Trader Trade Copier Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo Python is installed.
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment.
    pause
    exit /b 1
)

echo Virtual environment created.
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo Creating necessary directories...

REM Create logs directory
if not exist "logs" mkdir logs

REM Create data directory for secure storage
if not exist "data" mkdir data

REM Create config directory
if not exist "config" mkdir config

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Copy config.sample.json to config\config.json
echo 2. Update the configuration with your credentials
echo 3. Run 'setup.bat' to configure the application
echo 4. Use 'run.bat' to start the trade copier
echo.
pause
