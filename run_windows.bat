@echo off
setlocal

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install/Update dependencies
echo Checking dependencies...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo Error installing dependencies.
    echo Retrying with output...
    pip install -r requirements.txt
    pause
    exit /b 1
)

REM Launch the game
echo Launching Essence Bound...
python src\game_app.py %*

if %errorlevel% neq 0 (
    echo Game crashed or exited with error.
    pause
)
