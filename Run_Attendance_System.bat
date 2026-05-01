@echo off
setlocal
title Bluetooth Attendance System

:: Set the project directory
set "PROJECT_DIR=d:\auto\attendance_system"

echo ======================================================
echo    BLUETOOTH ATTENDANCE SYSTEM - STARTUP
echo ======================================================
echo.

:: Check if the directory exists
if not exist "%PROJECT_DIR%" (
    echo [ERROR] Project directory not found: %PROJECT_DIR%
    pause
    exit /b
)

:: Navigate to project directory
d:
cd "%PROJECT_DIR%"

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python from python.org
    pause
    exit /b
)

echo [1/3] Checking dependencies...
:: Optional: Uncomment the next line if you want it to auto-install missing libraries every time
:: pip install flask flask-cors openpyxl pybluez-win10 >nul 2>&1

echo [2/3] Starting Flask Server...
echo.
echo ------------------------------------------------------
echo  TEACHER DASHBOARD: http://localhost:5000
echo  STUDENT REGISTRATION: Open your IP at port 5000
echo ------------------------------------------------------
echo.

:: Automatically open the teacher dashboard in the default browser
start http://localhost:5000

:: Start the app
python app.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The application crashed or failed to start.
    echo Make sure no other app is using port 5000.
    pause
)

echo.
echo Application closed.
pause
