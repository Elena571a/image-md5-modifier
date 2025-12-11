@echo off
chcp 65001 >nul
title 图片MD5修改工具
python image_md5_modifier_gui.py
if errorlevel 1 (
    echo.
    echo 错误: 无法启动程序
    echo 请确保已安装Python和所需依赖: pip install -r requirements.txt
    pause
)

