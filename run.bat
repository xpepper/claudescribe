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
cd frontend
call npm run build
if errorlevel 1 (
    echo ERROR: Frontend build failed.
    cd ..
    exit /b 1
)
cd ..

:: Start the app
echo Starting Claudescribe at http://localhost:8000 ...
python main.py
endlocal
