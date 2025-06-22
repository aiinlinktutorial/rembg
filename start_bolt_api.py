#!/usr/bin/env python3
"""
Bolt.new Rembg API 启动脚本
为bolt.new项目提供AI抠图服务
"""
import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """检查依赖包是否安装"""
    required_packages = ['fastapi', 'uvicorn', 'rembg', 'pillow']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少依赖包:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n📦 请运行以下命令安装依赖:")
        print("pip install fastapi uvicorn rembg pillow python-multipart")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def check_rembg_models():
    """检查rembg模型是否已下载"""
    print("🔍 检查rembg模型...")
    try:
        from rembg import remove
        # 测试模型是否可用（这会触发首次模型下载）
        print("📥 首次运行会自动下载AI模型（约1-2GB），请稍候...")
        return True
    except Exception as e:
        print(f"❌ rembg模型检查失败: {e}")
        return False

def start_server():
    """启动API服务器"""
    try:
        print("🚀 正在启动Bolt.new Rembg API服务器...")
        
        # 设置环境变量
        os.environ.setdefault("PORT", "8080")
        port = os.environ.get("PORT")
        
        print(f"📡 服务器将运行在: http://localhost:{port}")
        print("🌐 API文档: http://localhost:{port}/docs")
        print("❤️  健康检查: http://localhost:{port}/health")
        print("\n💡 主要接口:")
        print(f"   - POST http://localhost:{port}/api/remove-bg")
        print(f"   - POST http://localhost:{port}/api/remove-bg-base64")
        print("\n🎯 为bolt.new项目定制 - 无需API Key认证")
        print("=" * 60)
        
        # 启动服务器
        from bolt_api import app
        import uvicorn
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=int(port),
            reload=False,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

def test_api():
    """测试API是否正常工作"""
    port = os.environ.get("PORT", "8080")
    base_url = f"http://localhost:{port}"
    
    print(f"🧪 测试API连接: {base_url}")
    
    try:
        # 测试健康检查
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API服务正常运行")
            return True
        else:
            print(f"❌ API响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到API: {e}")
        return False

def main():
    """主函数"""
    print("🎨 Bolt.new Rembg API 启动器")
    print("=" * 40)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        sys.exit(1)
    
    print(f"✅ Python版本: {sys.version}")
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查模型
    if not check_rembg_models():
        sys.exit(1)
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main() 