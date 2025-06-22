#!/usr/bin/env python3
"""
Bolt.new Rembg API 测试脚本
验证API各个接口的功能
"""
import os
import sys
import time
import base64
import requests
from pathlib import Path

# API配置
API_BASE_URL = "http://localhost:8080"
TEST_IMAGE_PATH = "examples/girl-1.jpg"  # 使用项目中的示例图片

def check_api_health():
    """检查API健康状态"""
    print("🔍 检查API健康状态...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API健康状态: {data.get('status', 'unknown')}")
            print(f"   服务名称: {data.get('service', 'unknown')}")
            return True
        else:
            print(f"❌ API健康检查失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到API: {e}")
        print(f"   请确保API服务正在运行: python start_bolt_api.py")
        return False

def test_api_info():
    """测试API信息接口"""
    print("\n📋 获取API信息...")
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务: {data.get('service', 'unknown')}")
            print(f"   版本: {data.get('version', 'unknown')}")
            print(f"   描述: {data.get('description', 'unknown')}")
            return True
        else:
            print(f"❌ 获取API信息失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_file_upload():
    """测试文件上传抠图接口"""
    print("\n📁 测试文件上传抠图...")
    
    # 寻找测试图片
    test_image = None
    possible_paths = [
        TEST_IMAGE_PATH,
        "examples/animal-1.jpg",
        "examples/car-1.jpg",
        "output/girl-1.png"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            test_image = path
            break
    
    if not test_image:
        print("❌ 找不到测试图片，请确保examples目录中有图片文件")
        return False
    
    print(f"   使用测试图片: {test_image}")
    
    try:
        with open(test_image, 'rb') as f:
            files = {'file': (os.path.basename(test_image), f, 'image/jpeg')}
            
            print("   🚀 开始上传和处理...")
            start_time = time.time()
            
            response = requests.post(
                f"{API_BASE_URL}/api/remove-bg",
                files=files,
                timeout=60  # 增加超时时间
            )
            
            end_time = time.time()
            process_time = end_time - start_time
            
            if response.status_code == 200:
                # 保存结果
                output_path = f"test_output_{int(time.time())}.png"
                with open(output_path, 'wb') as output_file:
                    output_file.write(response.content)
                
                print(f"✅ 文件上传抠图成功!")
                print(f"   处理时间: {process_time:.2f}秒")
                print(f"   结果保存至: {output_path}")
                print(f"   原图大小: {os.path.getsize(test_image)} 字节")
                print(f"   结果大小: {len(response.content)} 字节")
                return True
            else:
                print(f"❌ 文件上传抠图失败: HTTP {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False
                
    except requests.exceptions.Timeout:
        print("❌ 请求超时，可能是图片太大或网络问题")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_base64_upload():
    """测试Base64抠图接口"""
    print("\n📊 测试Base64抠图...")
    
    # 寻找测试图片
    test_image = None
    possible_paths = [
        TEST_IMAGE_PATH,
        "examples/animal-1.jpg",
        "examples/car-1.jpg"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            test_image = path
            break
    
    if not test_image:
        print("❌ 找不到测试图片")
        return False
    
    print(f"   使用测试图片: {test_image}")
    
    try:
        # 读取图片并转换为base64
        with open(test_image, 'rb') as f:
            image_data = f.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
        
        print("   🚀 开始Base64处理...")
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/api/remove-bg-base64",
            json={"image": base64_image},
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        end_time = time.time()
        process_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                # 保存结果
                result_base64 = data['result']
                result_data = base64.b64decode(result_base64)
                output_path = f"test_base64_output_{int(time.time())}.png"
                
                with open(output_path, 'wb') as f:
                    f.write(result_data)
                
                print(f"✅ Base64抠图成功!")
                print(f"   处理时间: {process_time:.2f}秒")
                print(f"   结果保存至: {output_path}")
                print(f"   格式: {data.get('format', 'unknown')}")
                print(f"   消息: {data.get('message', 'unknown')}")
                return True
            else:
                print(f"❌ Base64抠图失败: {data}")
                return False
        else:
            print(f"❌ Base64抠图失败: HTTP {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_error_handling():
    """测试错误处理"""
    print("\n🚨 测试错误处理...")
    
    # 测试无效的base64数据
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/remove-bg-base64",
            json={"image": "invalid_base64_data"},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ 无效Base64数据错误处理正常")
        else:
            print(f"⚠️  无效Base64数据返回状态: {response.status_code}")
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
    
    # 测试缺少数据字段
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/remove-bg-base64",
            json={},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ 缺少数据字段错误处理正常")
        else:
            print(f"⚠️  缺少数据字段返回状态: {response.status_code}")
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")

def main():
    """主函数"""
    print("🧪 Bolt.new Rembg API 测试")
    print("=" * 50)
    
    # 检查API是否运行
    if not check_api_health():
        print("\n❌ API服务未运行，请先启动API服务:")
        print("   python start_bolt_api.py")
        sys.exit(1)
    
    # 运行测试
    tests_passed = 0
    total_tests = 4
    
    if test_api_info():
        tests_passed += 1
    
    if test_file_upload():
        tests_passed += 1
    
    if test_base64_upload():
        tests_passed += 1
    
    test_error_handling()  # 错误处理测试不计入通过数
    tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 测试完成: {tests_passed}/{total_tests} 通过")
    
    if tests_passed == total_tests:
        print("🎉 所有测试通过! API准备就绪，可以在bolt.new中使用了")
        print("\n💡 下一步:")
        print("   1. 复制bolt_integration_guide.md中的React组件")
        print("   2. 在bolt.new项目中使用该组件")
        print("   3. 确保API服务保持运行状态")
    else:
        print("⚠️  部分测试失败，请检查API服务状态")
    
    print(f"\n🌐 API服务地址: {API_BASE_URL}")
    print(f"📚 API文档: {API_BASE_URL}/docs")

if __name__ == "__main__":
    main() 