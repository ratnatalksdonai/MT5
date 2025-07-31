@echo off
echo 🔧 Installing MT5 to MatchTrader MVP...

REM Create virtual environment
python -m venv venv_mvp
call venv_mvp\Scripts\activate.bat

REM Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

REM Create necessary directories
if not exist logs mkdir logs
if not exist data mkdir data

echo ✅ Installation complete!
echo ▶️  Next steps:
echo    1. Edit config_mvp.json with your credentials
echo    2. Run: python run_mvp.py
pause
