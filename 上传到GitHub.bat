@echo off
chcp 65001 >nul
title 上传代码到GitHub
echo ========================================
echo 上传代码到GitHub
echo ========================================
echo.

REM 检查是否已初始化Git
if not exist .git (
    echo 正在初始化Git仓库...
    git init
    echo.
)

REM 添加所有文件
echo 正在添加文件...
git add .
echo.

REM 提交
echo 正在提交代码...
git commit -m "Add all project files"
echo.

REM 检查是否已设置远程仓库
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在设置远程仓库地址...
    git remote add origin https://github.com/Elena571a/image-md5-modifier.git
    echo.
)

REM 设置主分支
git branch -M main
echo.

REM 推送代码
echo 正在上传到GitHub...
echo 如果提示输入用户名和密码，请使用GitHub的Personal Access Token作为密码
echo.
git push -u origin main

if %errorlevel% == 0 (
    echo.
    echo ========================================
    echo 上传成功！
    echo ========================================
    echo.
    echo 现在可以到Railway部署了：
    echo 1. 访问 https://railway.app
    echo 2. 点击 "New Project"
    echo 3. 选择 "GitHub Repository"
    echo 4. 选择 "image-md5-modifier"
    echo.
) else (
    echo.
    echo ========================================
    echo 上传失败
    echo ========================================
    echo.
    echo 可能的原因：
    echo 1. 需要安装Git: https://git-scm.com/download/win
    echo 2. 需要配置Git用户信息
    echo 3. 需要GitHub的Personal Access Token
    echo.
    echo 如果还没安装Git，请先安装后再运行此脚本
    echo.
)

pause

