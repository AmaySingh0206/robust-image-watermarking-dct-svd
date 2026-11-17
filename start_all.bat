@echo off
title SPECTRAMARK - Unified Master Launcher
color 0E

echo ======================================================================
echo           SPECTRAMARK DIGITAL IMAGE WATERMARKING PLATFORM
echo                     Master System Launcher
echo ======================================================================
echo.
echo Launching Backend FastAPI Server and Frontend React Dashboard...
echo.

cd /d "%~dp0"

:: Start backend in new console
start "SPECTRAMARK Backend (Port 8000)" cmd /k "%~dp0start_backend.bat"

:: Wait 2 seconds for backend initialization
timeout /t 2 /nobreak >nul

:: Start frontend in new console
start "SPECTRAMARK Frontend (Port 5173)" cmd /k "%~dp0start_frontend.bat"

:: Wait 3 seconds for Vite initialization
timeout /t 3 /nobreak >nul

echo [INFO] Opening SPECTRAMARK Dashboard in default web browser...
start http://localhost:5173

echo.
echo ======================================================================
echo  SPECTRAMARK is running:
echo  - Frontend Dashboard : http://localhost:5173
echo  - Backend API        : http://localhost:8000
echo  - Swagger API Docs   : http://localhost:8000/docs
echo.
echo  Default Login:
echo  - Username: admin
echo  - Password: spectramark2026
echo ======================================================================
echo.
pause

