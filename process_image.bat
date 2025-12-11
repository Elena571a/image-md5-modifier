@echo off
chcp 65001 >nul
echo ========================================
echo 图片MD5修改工具
echo ========================================
echo.

if "%~1"=="" (
    echo 使用方法: 将图片拖到此文件上，或
    echo process_image.bat "图片路径"
    echo.
    pause
    exit /b
)

python image_md5_modifier.py "%~1"
echo.
pause

