@echo off
REM X-Recon v3.0 - Windows Startup Script
REM Created by Muhammad Izaz Haider

title X-Recon v3.0 - Professional Reconnaissance Toolkit

echo.
echo ========================================
echo   X-RECON v3.0
echo   Advanced Security Toolkit
echo   Created by Muhammad Izaz Haider
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo [*] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo [*] Checking dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [WARNING] Some dependencies may not have installed correctly
)

REM Check for .env file
if not exist ".env" (
    echo.
    echo [WARNING] .env file not found
    echo [*] Creating .env template...
    echo CEREBRAS_API_KEY=your_api_key_here > .env
    echo [!] Please edit .env and add your Cerebras API key
    echo.
)

REM Create results directory if it doesn't exist
if not exist "results\" mkdir results

REM Run main application
echo.
echo [*] Starting X-Recon...
echo.
python main.py

REM Cleanup on exit
deactivate
pause
