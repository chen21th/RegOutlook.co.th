@echo off
chcp 65001 >nul
title RegOutlookTH - Install Dependencies
echo ========================================
echo   Installing Dependencies
echo ========================================
echo.

REM ตรวจสอบว่ามี Python portable หรือไม่
if exist "python\python.exe" (
    echo [OK] Found Portable Python
    set PYTHON_EXE=python\python.exe
    set PIP_EXE=python\Scripts\pip.exe
) else if exist "python\Scripts\python.exe" (
    set PYTHON_EXE=python\Scripts\python.exe
    set PIP_EXE=python\Scripts\pip.exe
) else (
    echo [!] Using system Python
    set PYTHON_EXE=python
    set PIP_EXE=pip
)

echo Installing packages...
%PIP_EXE% install selenium requests --quiet

echo.
echo [DONE] Dependencies installed!
echo.
pause
