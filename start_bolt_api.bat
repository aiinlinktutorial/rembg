@echo off
title Bolt.new Rembg API Server
echo 🎨 启动 Bolt.new AI抠图 API 服务器
echo ==========================================

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python已安装

:: 检查并安装依赖
echo 📦 检查依赖包...
pip install -r requirements_bolt.txt

if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo ✅ 依赖已安装

:: 启动API服务器
echo 🚀 启动API服务器...
echo.
echo 服务地址: http://localhost:8080
echo API文档: http://localhost:8080/docs
echo 健康检查: http://localhost:8080/health
echo.
echo 按 Ctrl+C 停止服务器
echo ==========================================

python start_bolt_api.py

pause 