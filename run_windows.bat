@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title CMC AI Mentor Network - Windows launcher

echo.
echo ============================================
echo   CMC AI Mentor Network - LOCAL STARTUP
echo ============================================
echo.

if exist ".venv\Scripts\python.exe" goto venv_ready

echo [1/3] Creating Python virtual environment...
where py >nul 2>&1
if not errorlevel 1 (
    py -3.11 -m venv .venv >nul 2>&1
    if exist ".venv\Scripts\python.exe" goto venv_ready
    py -3 -m venv .venv >nul 2>&1
    if exist ".venv\Scripts\python.exe" goto venv_ready
)

where python >nul 2>&1
if not errorlevel 1 (
    python -m venv .venv
    if exist ".venv\Scripts\python.exe" goto venv_ready
)

echo ERROR: Python virtual environment could not be created.
echo Install Python 3.11 or newer from https://www.python.org/downloads/
echo Check "Add Python to PATH" during installation.
goto failed

:venv_ready
".venv\Scripts\python.exe" -c "import sys; assert sys.version_info >= (3,11), 'Python 3.11+ required'"
if errorlevel 1 (
    echo ERROR: Your existing .venv uses Python older than 3.11.
    echo Delete the .venv folder, install Python 3.11+, then run this file again.
    goto failed
)

echo [2/3] Installing or updating requirements...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Dependency installation failed. Check internet access and pip output.
    goto failed
)

echo [3/3] Starting Streamlit at http://localhost:8501
echo Open that address in your browser if it does not open automatically.
echo You do NOT need a Groq API key for offline demo mode.
echo Use Ctrl+C to stop the server.
echo.
".venv\Scripts\python.exe" -m streamlit run app.py
if errorlevel 1 (
    echo ERROR: Application stopped with a nonzero exit code.
    goto failed
)
echo Application stopped normally.
pause
exit /b 0

:failed
echo.
echo Please copy the ERROR output above when reporting an issue.
pause
exit /b 1
