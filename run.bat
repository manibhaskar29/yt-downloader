@echo off
echo ========================================
echo   YouTube Downloader - Starting...
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
echo.
echo Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
) else (
    echo Dependencies already installed.
    echo.
)

REM Run the application
echo ========================================
echo   Starting Flask server...
echo   Open http://localhost:8080 in your browser
echo ========================================
echo.
python app.py

pause

