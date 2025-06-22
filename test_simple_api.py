#!/usr/bin/env python3
import requests
import base64
import os

# API配置 - 无需API Key
API_URL = "http://localhost:8081"

def test_health():
    """测试健康检查"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        print(f"✅ 健康检查: {response.status_code}")
        print(f"   响应: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_file_upload():
    """测试文件上传抠图"""
    try:
        # 检查测试图片是否存在
        test_image = "examples/girl-1.jpg"
        if not os.path.exists(test_image):
            print(f"❌ 测试图片不存在: {test_image}")
            return False
        
        print(f"📸 使用测试图片: {test_image}")
        
        # 上传文件进行抠图 - 无需API Key
        with open(test_image, "rb") as f:
            files = {"file": ("girl-1.jpg", f, "image/jpeg")}
            response = requests.post(
                f"{API_URL}/remove-bg",
                files=files,
                timeout=60
            )
        
        if response.status_code == 200:
            # 保存结果
            output_path = "output/simple_api_test_result.png"
            os.makedirs("output", exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"✅ 文件上传抠图成功!")
            print(f"   保存到: {output_path}")
            return True
        else:
            print(f"❌ 文件上传抠图失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 文件上传抠图异常: {e}")
        return False

def test_base64():
    """测试Base64抠图"""
    try:
        # 检查测试图片是否存在
        test_image = "examples/girl-1.jpg"
        if not os.path.exists(test_image):
            print(f"❌ 测试图片不存在: {test_image}")
            return False
        
        # 将图片转换为base64
        with open(test_image, "rb") as f:
            image_data = f.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # 发送base64请求 - 无需API Key
        payload = {"image": base64_image}
        response = requests.post(
            f"{API_URL}/remove-bg-base64",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            # 保存结果
            output_data = base64.b64decode(result["result"])
            output_path = "output/simple_api_test_base64_result.png"
            os.makedirs("output", exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(output_data)
            print(f"✅ Base64抠图成功!")
            print(f"   保存到: {output_path}")
            return True
        else:
            print(f"❌ Base64抠图失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Base64抠图异常: {e}")
        return False

def main():
    print("🧪 开始测试简单抠图API (无需认证)...")
    print("=" * 50)
    
    # 测试健康检查
    if not test_health():
        print("\n❌ API服务器未运行，请先启动服务器!")
        print("   运行: python simple_api.py")
        return
    
    print("\n" + "=" * 50)
    
    # 测试文件上传
    print("📤 测试文件上传抠图...")
    test_file_upload()
    
    print("\n" + "=" * 50)
    
    # 测试Base64
    print("🔐 测试Base64抠图...")
    test_base64()
    
    print("\n" + "=" * 50)
    print("🎉 测试完成!")
    print("💡 提示: 你可以在浏览器中访问 http://localhost:8080/docs 查看完整的API文档")

if __name__ == "__main__":
    main() 