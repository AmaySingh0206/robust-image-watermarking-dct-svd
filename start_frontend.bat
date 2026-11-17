@echo off
title SPECTRAMARK Frontend Dashboard (React + Vite)
color 0B

echo ======================================================================
echo           SPECTRAMARK FRONTEND DASHBOARD - REACT + VITE
echo ======================================================================
echo.

cd /d "%~dp0frontend"

if not exist "node_modules\" (
    echo [INFO] node_modules directory not detected. Running npm install...
    call npm.cmd install
    if errorlevel 1 (
        echo [ERROR] npm install failed. Please check your internet connection or Node.js installation.
        pause
        exit /b 1
    )
)

echo [INFO] Starting Vite development server on http://localhost:5173...
echo.

call npm.cmd run dev

if errorlevel 1 (
    echo.
    echo [ERROR] Frontend failed to start.
    echo [TIP] Try navigating into the 'frontend' directory and running 'npm install' then 'npm run dev'.
)

pause
