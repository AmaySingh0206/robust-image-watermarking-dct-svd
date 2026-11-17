@echo off
title SPECTRAMARK Backend Server (FastAPI)
color 0A

echo ======================================================================
echo           SPECTRAMARK BACKEND SERVER - FASTAPI / UVICORN
echo ======================================================================
echo.

cd /d "%~dp0"

:: Check if virtual environment exists
if not exist "%~dp0venv\Scripts\activate.bat" (
    echo [INFO] Virtual environment 'venv' not found.
    echo [INFO] Creating Python virtual environment...
    py -m venv venv || python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment. Ensure Python is installed.
        pause
        exit /b 1
    )
    echo [INFO] Installing backend dependencies from backend\requirements.txt...
    call "%~dp0venv\Scripts\activate.bat"
    python -m pip install --upgrade pip
    pip install -r "%~dp0backend\requirements.txt"
    if errorlevel 1 (
        echo [WARNING] Some dependencies had warnings during install. Proceeding...
    )
) else (
    echo [INFO] Activating virtual environment in venv...
    call "%~dp0venv\Scripts\activate.bat"
)

echo.
echo [INFO] Starting Uvicorn ASGI server on http://127.0.0.1:8000...
echo [INFO] Interactive Swagger docs available at http://127.0.0.1:8000/docs
echo.

python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

if errorlevel 1 (
    echo.
    echo [ERROR] Backend failed to start.
    echo [TIP] Try running: pip install -r backend\requirements.txt
)

pause
