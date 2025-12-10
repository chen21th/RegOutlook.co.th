@echo off
chcp 65001 >nul
title RegOutlookTH - Test Proxy
echo ========================================
echo   Testing ABC Proxy Connection
echo ========================================
echo.

if exist "python\python.exe" (
    set PYTHON_EXE=python\python.exe
) else (
    set PYTHON_EXE=python
)

%PYTHON_EXE% -c "from proxy_manager import ABCProxyManager; p = ABCProxyManager(); p.test_proxy(); p.check_current_ip()"

echo.
pause
