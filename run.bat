@echo off
setlocal

:: Activate virtual environment
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found. Run setup.bat first.
    exit /b 1
)
call .venv\Scripts\activate.bat

:: Build frontend
echo Building frontend...
echo [DEBUG] Current directory: %cd%
cd frontend
echo [DEBUG] Changed to frontend directory: %cd%
npm run build
echo [DEBUG] npm build exit code: %errorlevel%
if errorlevel 1 (
    echo ERROR: Frontend build failed.
    cd ..
    exit /b 1
)
echo [DEBUG] About to cd ..
cd ..
echo [DEBUG] Back in root directory: %cd%

:: Start the app
echo [DEBUG] About to start Python
echo Starting Claudescribe at http://localhost:8000 ...
python main.py
echo [DEBUG] Python exited with code: %errorlevel%
endlocal
