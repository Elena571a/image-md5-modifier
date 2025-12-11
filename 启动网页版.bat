@echo off
chcp 65001 >nul
title 图片MD5修改工具 - Web版
echo ========================================
echo 图片MD5修改工具 - Web版
echo ========================================
echo.

REM 获取本机IP地址
setlocal enabledelayedexpansion
set LOCAL_IP=
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set "LOCAL_IP=%%a"
    set "LOCAL_IP=!LOCAL_IP:~1!"
    goto :found_ip
)
:found_ip

echo 访问地址:
echo   本机: http://localhost:5001
if defined LOCAL_IP (
    echo   局域网: http://%LOCAL_IP%:5001
)
echo.
echo 按 Ctrl+C 停止服务器
echo ========================================
echo.
python app.py
pause
