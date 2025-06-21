#!/usr/bin/env python3
"""
快速测试API服务状态
"""

import requests
import json
from datetime import datetime

# 测试的URL列表
test_urls = [
    "https://rembg-12mt.onrender.com",
    "https://rembg-12mt.onrender.com/",
    "https://rembg-12mt.onrender.com/health",
    "https://rembg-12mt.onrender.com/docs"
]

def test_url(url):
    """测试单个URL"""
    try:
        print(f"🔍 测试: {url}")
        response = requests.get(url, timeout=30)
        print(f"✅ 状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📝 响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except:
                print(f"📝 响应: {response.text[:200]}...")
        else:
            print(f"❌ 错误: {response.text[:200]}...")
            
    except requests.exceptions.Timeout:
        print(f"⏱️  请求超时 - 服务可能正在启动中...")
    except requests.exceptions.ConnectionError:
        print(f"🔌 连接错误 - 服务可能离线")
    except Exception as e:
        print(f"❌ 其他错误: {str(e)}")
    
    print("-" * 50)

def main():
    print(f"🚀 API服务状态测试 - {datetime.now()}")
    print("=" * 50)
    
    for url in test_urls:
        test_url(url)
    
    print("\n💡 如果所有测试都失败：")
    print("1. 检查Render Dashboard中的服务状态")
    print("2. 查看服务日志")
    print("3. 确认服务URL是否正确")
    print("4. 尝试手动重新部署")

if __name__ == "__main__":
    main() 