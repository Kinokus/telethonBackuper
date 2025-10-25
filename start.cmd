@echo off
REM Startup script for Telethon Userbot (Windows)

echo ====================================
echo   Telethon Userbot Launcher
echo ====================================
echo.

REM Check if .env file exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo Please create a .env file with your credentials.
    echo You can copy env.template to .env and fill in your values.
    echo.
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python from https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo [INFO] Checking dependencies...
pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo [WARNING] Failed to install some dependencies.
    echo Trying to continue anyway...
    echo.
)

echo.
echo [INFO] Starting userbot...
echo [INFO] Press Ctrl+C to stop
echo.

python userbot.py

if errorlevel 1 (
    echo.
    echo [ERROR] Userbot stopped with an error.
    pause
    exit /b 1
)

