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
    
    # 从环境变量获取端口，默认为8000
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"  # 改为 0.0.0.0 以便外部访问
    
    print("🚀 正在启动Rembg API服务器...")
    print(f"📝 API文档地址: http://{host}:{port}/docs")
    print(f"🎯 健康检查: http://{host}:{port}/health")
    print("💡 按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    try:
        # 启动uvicorn服务器
        subprocess.run([
            sys.executable, "-c",
            f"import uvicorn; uvicorn.run('api_server:app', host='{host}', port={port}, reload=False)"
        ])
    except KeyboardInterrupt:
        print("\n👋 API服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    start_api() 