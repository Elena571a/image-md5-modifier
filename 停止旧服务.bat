@echo off
chcp 65001 >nul
echo 正在停止占用5000端口的进程...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    echo 结束进程 PID: %%a
    taskkill /PID %%a /F >nul 2>&1
)
echo 完成！
timeout /t 2 >nul

