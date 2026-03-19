@echo off
REM Weather App Setup Script for Windows
REM This script will help you set up the Weather Dashboard application

cls
echo.
echo ================================================
echo Weather Dashboard - Setup Script
echo ================================================
echo.

REM Check if Python is available
echo Checking for Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python not found!
    echo.
    echo Please follow these steps:
    echo 1. Download Python from https://python.org/downloads
    echo 2. Install with "Add Python to PATH" checked
    echo 3. Restart this script
    echo.
    pause
    exit /b 1
)

echo Python found!
python --version
echo.

REM Install dependencies
echo Installing dependencies...
echo This may take a minute...
echo.
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies!
    echo Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================
echo Installation Complete!
echo ================================================
echo.

REM Ask user if they want to run the app now
echo Ready to start the Weather Dashboard?
set /p run="Run app now? (y/n): "
if /i "%run%"=="y" (
    echo.
    echo Starting Weather App...
    echo.
    echo Navigate to: http://127.0.0.1:5000 in your browser
    echo.
    echo Press Ctrl+C to stop the server
    echo.
    python app.py
) else (
    echo.
    echo To run the app later, use:
    echo   python app.py
    echo.
    echo Then open: http://127.0.0.1:5000
    echo.
)

pause
