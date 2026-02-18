@echo off
echo ================================================
echo   Zord Coder v1 - Quick Start
echo ================================================
echo.

REM Check if miniconda exists
if exist "C:\Users\abdul\miniconda3\python.exe" (
    echo Found miniconda Python with llama-cpp-python
    echo.
    echo Starting server...
    call C:\Users\abdul\miniconda3\Scripts\activate.bat
    cd /d C:\Users\abdul\zordcoder
    python web\server.py
) else (
    echo miniconda not found. Please install dependencies:
    echo.
    echo   pip install llama-cpp-python rich huggingface-hub
    echo.
    echo Or install miniconda from: https://docs.conda.io/en/latest/miniconda.html
    pause
)
