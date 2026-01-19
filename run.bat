@echo off
echo 🌊 Starting Timetide...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the application
echo Starting server at http://localhost:8000
echo Press Ctrl+C to stop
echo.
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

pause
