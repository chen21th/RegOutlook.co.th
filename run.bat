@echo off
chcp 65001 >nul
title RegOutlookTH - Portable
echo ========================================
echo   RegOutlookTH - Outlook Registration
echo   Domain: @outlook.co.th
echo ========================================
echo.

REM ตรวจสอบว่ามี Python portable หรือไม่
if exist "python\python.exe" (
    echo [OK] Found Portable Python
    set PYTHON_EXE=python\python.exe
) else if exist "python\Scripts\python.exe" (
    echo [OK] Found Portable Python in Scripts
    set PYTHON_EXE=python\Scripts\python.exe
) else (
    echo [!] Portable Python not found, using system Python
    set PYTHON_EXE=python
)

REM ตรวจสอบ chromedriver
if not exist "chromedriver.exe" (
    echo [WARNING] chromedriver.exe not found!
    echo Please download from: https://chromedriver.chromium.org/downloads
    echo.
)

echo.
echo [Starting with ABC Proxy - Rotating]
echo.

%PYTHON_EXE% main.py --mode abc --loop

pause
