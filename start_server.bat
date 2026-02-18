@echo off
setlocal enabledelayedexpansion

echo ================================================
echo   Zord Coder v1 - Launcher
echo ================================================
echo.

REM Find Python with llama-cpp-python
set "PYTHON_EXE="

REM Check miniconda first
if exist "C:\Users\abdul\miniconda3\python.exe" (
    "C:\Users\abdul\miniconda3\python.exe" -c "import llama_cpp" 2>nul
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=C:\Users\abdul\miniconda3\python.exe"
        echo Found Python with llama-cpp-python in miniconda
    )
)

REM Check other common locations
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

REM Try default python
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

REM Change to script directory
cd /d "%~dp0"

REM Run the server
"%PYTHON_EXE%" web\server.py %*
