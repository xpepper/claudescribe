@echo off
setlocal

echo === Claudescribe setup ===

:: Create virtual environment
echo.
echo [1/4] Creating Python virtual environment...
if exist .venv (
    echo Removing existing .venv...
    rmdir /s /q .venv
)
python -m venv .venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment. Is Python 3.10+ installed and on PATH?
    echo If you installed Python from the Microsoft Store, try uninstalling it and
    echo reinstalling from https://www.python.org/downloads/ instead.
    exit /b 1
)

:: Activate and install Python deps
echo.
echo [2/4] Installing Python dependencies...
call .venv\Scripts\activate.bat
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: pip install failed.
    exit /b 1
)

:: Install frontend deps
echo.
echo [3/4] Installing frontend dependencies...
cd frontend
npm install
if errorlevel 1 (
    echo ERROR: npm install failed. Is Node.js 18+ installed and on PATH?
    cd ..
    exit /b 1
)
cd ..

:: Build frontend
echo.
echo [4/4] Building frontend...
cd frontend
npm run build
if errorlevel 1 (
    echo ERROR: Frontend build failed.
    cd ..
    exit /b 1
)
cd ..

echo.
echo === Setup complete! ===
echo Run run.bat to start Claudescribe.
endlocal
