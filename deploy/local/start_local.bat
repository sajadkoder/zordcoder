@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    Local Hosting with Tunnel
echo ========================================
echo.

set PORT=8000
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..\..

cd /d "%PROJECT_ROOT%"

set "PYTHON_EXE="

if exist "C:\Users\abdul\miniconda3\python.exe" (
    "C:\Users\abdul\miniconda3\python.exe" -c "import llama_cpp" 2>nul
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=C:\Users\abdul\miniconda3\python.exe"
        echo Found Python with llama-cpp-python in miniconda
    )
)

if not defined PYTHON_EXE (
    if exist "C:\Python312\python.exe" (
        "C:\Python312\python.exe" -c "import llama_cpp" 2>nul
        if !errorlevel! equ 0 set "PYTHON_EXE=C:\Python312\python.exe"
    )
)

if not defined PYTHON_EXE (
    if exist "C:\Python311\python.exe" (
        "C:\Python311\python.exe" -c "import llama_cpp" 2>nul
        if !errorlevel! equ 0 set "PYTHON_EXE=C:\Python311\python.exe"
    )
)

if not defined PYTHON_EXE (
    if exist "C:\Python310\python.exe" (
        "C:\Python310\python.exe" -c "import llama_cpp" 2>nul
        if !errorlevel! equ 0 set "PYTHON_EXE=C:\Python310\python.exe"
    )
)

if not defined PYTHON_EXE (
    python -c "import llama_cpp" 2>nul
    if !errorlevel! equ 0 set "PYTHON_EXE=python"
)

if not defined PYTHON_EXE (
    echo.
    echo ERROR: Could not find Python with llama-cpp-python installed.
    echo.
    echo Please install it with one of these methods:
    echo.
    echo   Method 1 - Using pip:
    echo     pip install llama-cpp-python
    echo.
    echo   Method 2 - Using conda:
    echo     conda install -c conda-forge llama-cpp-python
    echo.
    echo   Method 3 - Install Miniconda from:
    echo     https://docs.conda.io/en/latest/miniconda.html
    echo.
    pause
    exit /b 1
)

echo Using Python: %PYTHON_EXE%
echo.

echo [1/2] Starting server on port %PORT%...
echo.

start "" /b "%PYTHON_EXE%" web\server.py --port %PORT%

timeout /t 3 /nobreak >nul

echo.
echo [2/2] Choose tunnel option:
echo.
echo   1. ngrok
echo   2. Cloudflare Tunnel (cloudflared)
echo   3. Skip tunnel (local only)
echo   4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto ngrok
if "%choice%"=="2" goto cloudflare
if "%choice%"=="3" goto local_only
if "%choice%"=="4" goto end

:ngrok
echo.
echo Starting ngrok tunnel...
echo.
ngrok http %PORT%
goto end

:cloudflare
echo.
echo Starting Cloudflare Tunnel...
echo.
cloudflared tunnel --url http://localhost:%PORT%
goto end

:local_only
echo.
echo ========================================
echo Local server running at:
echo   http://localhost:%PORT%
echo ========================================
echo.
echo Press any key to stop the server...
pause >nul
goto end

:end
echo.
echo Stopping server...
taskkill /f /im python.exe 2>nul
echo Done.
endlocal
