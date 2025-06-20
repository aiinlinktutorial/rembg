import requests
import base64
import json
import os
from PIL import Image
import io

# API服务器地址
API_BASE = "http://127.0.0.1:8000"

def test_health():
    """测试健康检查接口"""
    print("🔍 测试健康检查接口...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ 健康检查通过:", response.json())
        else:
            print("❌ 健康检查失败:", response.status_code)
    except Exception as e:
        print("❌ 健康检查失败:", str(e))

def test_file_upload(image_path):
    """测试文件上传接口"""
    print(f"📤 测试文件上传接口: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"❌ 文件不存在: {image_path}")
        return
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
            response = requests.post(f"{API_BASE}/remove-bg", files=files)
        
        if response.status_code == 200:
            # 保存处理后的图片
            output_path = f"output_api_{os.path.basename(image_path).split('.')[0]}.png"
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ 文件上传成功，结果保存为: {output_path}")
        else:
            print(f"❌ 文件上传失败: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"❌ 文件上传失败: {str(e)}")

def test_base64_upload(image_path):
    """测试Base64接口"""
    print(f"📤 测试Base64接口: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"❌ 文件不存在: {image_path}")
        return
    
    try:
        # 读取图片并转换为base64
        with open(image_path, 'rb') as f:
            image_data = f.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
        
        # 发送请求
        payload = {"image": base64_data}
        response = requests.post(
            f"{API_BASE}/remove-bg-base64",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('result'):
                # 解码并保存结果
                output_data = base64.b64decode(result['result'])
                output_path = f"output_api_base64_{os.path.basename(image_path).split('.')[0]}.png"
                with open(output_path, 'wb') as f:
                    f.write(output_data)
                print(f"✅ Base64处理成功，结果保存为: {output_path}")
            else:
                print("❌ 响应中没有结果数据")
        else:
            print(f"❌ Base64处理失败: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"❌ Base64处理失败: {str(e)}")

def test_batch_upload(image_paths):
    """测试批量处理接口"""
    print(f"📤 测试批量处理接口: {image_paths}")
    
    # 过滤存在的文件
    existing_files = [path for path in image_paths if os.path.exists(path)]
    if not existing_files:
        print("❌ 没有找到有效的图片文件")
        return
    
    try:
        files = []
        for image_path in existing_files:
            with open(image_path, 'rb') as f:
                files.append(('files', (os.path.basename(image_path), f.read(), 'image/jpeg')))
        
        response = requests.post(f"{API_BASE}/remove-bg-batch", files=files)
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ 批量处理完成，处理了 {results['total']} 个文件")
            
            for i, result in enumerate(results['results']):
                if result['status'] == 'success':
                    # 保存成功处理的图片
                    output_data = base64.b64decode(result['result'])
                    filename = result['filename'].split('.')[0]
                    output_path = f"output_api_batch_{filename}.png"
                    with open(output_path, 'wb') as f:
                        f.write(output_data)
                    print(f"  ✅ {result['filename']} -> {output_path}")
                else:
                    print(f"  ❌ {result['filename']}: {result['message']}")
        else:
            print(f"❌ 批量处理失败: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"❌ 批量处理失败: {str(e)}")

def main():
    print("🚀 开始测试Rembg API...")
    print("=" * 50)
    
    # 测试健康检查
    test_health()
    print()
    
    # 寻找测试图片
    test_images = []
    for img_dir in ['examples', 'tests/fixtures']:
        if os.path.exists(img_dir):
            for file in os.listdir(img_dir):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    test_images.append(os.path.join(img_dir, file))
    
    if not test_images:
        print("❌ 没有找到测试图片，请确保examples或tests/fixtures目录中有图片文件")
        return
    
    # 测试第一张图片的文件上传
    if test_images:
        test_file_upload(test_images[0])
        print()
    
    # 测试第一张图片的Base64接口
    if test_images:
        test_base64_upload(test_images[0])
        print()
    
    # 测试批量处理（最多3张图片）
    if len(test_images) > 1:
        test_batch_upload(test_images[:3])
        print()
    
    print("🎉 API测试完成！")

if __name__ == "__main__":
    main() 