#!/usr/bin/env python3
"""
Rembg API 启动脚本
"""

import subprocess
import sys
import os

def check_dependencies():
    """检查依赖是否安装"""
    required_packages = ['fastapi', 'uvicorn', 'rembg']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少以下依赖包: {', '.join(missing_packages)}")
        print("💡 请运行以下命令安装：")
        print(f"   pip install {' '.join(missing_packages)}")
        print("   或者：")
        print("   pip install -r requirements_api.txt")
        return False
    
    return True

def start_api():
    """启动API服务器"""
    if not check_dependencies():
        return
    
    print("🚀 正在启动Rembg API服务器...")
    print("📝 API文档地址: http://127.0.0.1:8000/docs")
    print("🎯 健康检查: http://127.0.0.1:8000/health")
    print("💡 按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    try:
        # 启动uvicorn服务器
        subprocess.run([
            sys.executable, "-c",
            "import uvicorn; uvicorn.run('api_server:app', host='127.0.0.1', port=8000, reload=True)"
        ])
    except KeyboardInterrupt:
        print("\n👋 API服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    start_api() 