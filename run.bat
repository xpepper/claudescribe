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
npm run build
if %errorlevel% neq 0 (
    echo ERROR: Frontend build failed with code %errorlevel%.
    cd ..
    exit /b 1
)
cd ..

:: Start the app
echo Starting Claudescribe at http://localhost:8000 ...
python main.py
endlocal
