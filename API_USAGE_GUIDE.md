# Rembg AI背景去除API 使用指南

## 🌟 服务概述

本API提供基于AI的智能背景去除服务，支持多种图片格式，返回透明背景的PNG图片。

## 🔗 API基础信息

- **服务地址**: `https://rembg-l2mt.onrender.com`
- **认证方式**: API Key（通过Header传递）
- **支持格式**: JPG, PNG, BMP, GIF等主流图片格式
- **返回格式**: PNG（透明背景）

## 🔑 认证说明

所有处理接口都需要API Key认证，请在请求头中包含：

```
X-API-Key: 您的API密钥
```

## 📚 接口文档

### 1. 健康检查 (无需认证)

**请求**
```
GET https://rembg-l2mt.onrender.com/health
```

**响应**
```json
{
  "status": "healthy",
  "service": "rembg-api"
}
```

### 2. 文件上传方式去背景

**请求**
```
POST https://rembg-l2mt.onrender.com/remove-bg
Content-Type: multipart/form-data
X-API-Key: 您的API密钥

file: [图片文件]
```

**响应**: PNG图片文件（二进制数据）

### 3. Base64方式去背景

**请求**
```
POST https://rembg-l2mt.onrender.com/remove-bg-base64
Content-Type: application/json
X-API-Key: 您的API密钥

{
  "image": "base64编码的图片数据"
}
```

**响应**
```json
{
  "result": "base64编码的PNG图片",
  "format": "png",
  "message": "背景去除成功"
}
```

### 4. 批量处理（最多10张）

**请求**
```
POST https://rembg-l2mt.onrender.com/remove-bg-batch
Content-Type: multipart/form-data
X-API-Key: 您的API密钥

files: [图片文件1, 图片文件2, ...]
```

**响应**
```json
[
  {
    "filename": "image1.jpg",
    "status": "success",
    "result": "base64编码的处理结果"
  },
  {
    "filename": "image2.jpg", 
    "status": "error",
    "message": "错误信息"
  }
]
```

## 💻 代码示例

### JavaScript/前端

#### 文件上传方式
```javascript
async function removeBackground(file, apiKey) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('https://rembg-l2mt.onrender.com/remove-bg', {
        method: 'POST',
        headers: {
            'X-API-Key': apiKey
        },
        body: formData
    });

    if (response.ok) {
        return await response.blob(); // PNG图片blob
    } else {
        throw new Error(`处理失败: ${response.status}`);
    }
}

// 使用示例
const fileInput = document.getElementById('fileInput');
const file = fileInput.files[0];
const apiKey = 'your-api-key';

removeBackground(file, apiKey)
    .then(blob => {
        const imageUrl = URL.createObjectURL(blob);
        document.getElementById('result').src = imageUrl;
    })
    .catch(console.error);
```

#### Base64方式
```javascript
async function removeBackgroundBase64(base64Image, apiKey) {
    const response = await fetch('https://rembg-l2mt.onrender.com/remove-bg-base64', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': apiKey
        },
        body: JSON.stringify({ image: base64Image })
    });

    if (response.ok) {
        const result = await response.json();
        return result.result; // base64编码的PNG
    } else {
        throw new Error(`处理失败: ${response.status}`);
    }
}
```

### Python

```python
import requests
import base64

API_URL = 'https://rembg-l2mt.onrender.com'
API_KEY = 'your-api-key'

# 文件上传方式
def remove_background_file(image_path):
    with open(image_path, 'rb') as f:
        response = requests.post(
            f'{API_URL}/remove-bg',
            headers={'X-API-Key': API_KEY},
            files={'file': f}
        )
    
    if response.status_code == 200:
        return response.content  # PNG图片数据
    else:
        raise Exception(f'处理失败: {response.status_code} - {response.text}')

# Base64方式
def remove_background_base64(image_path):
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    response = requests.post(
        f'{API_URL}/remove-bg-base64',
        headers={
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        },
        json={'image': image_data}
    )
    
    if response.status_code == 200:
        result = response.json()
        return base64.b64decode(result['result'])
    else:
        raise Exception(f'处理失败: {response.status_code} - {response.text}')

# 使用示例
try:
    # 处理图片
    result = remove_background_file('input.jpg')
    
    # 保存结果
    with open('output.png', 'wb') as f:
        f.write(result)
    
    print("背景去除成功！")
except Exception as e:
    print(f"错误: {e}")
```

### PHP

```php
<?php
function removeBackground($imagePath, $apiKey) {
    $url = 'https://rembg-l2mt.onrender.com/remove-bg';
    
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_HTTPHEADER => [
            'X-API-Key: ' . $apiKey
        ],
        CURLOPT_POSTFIELDS => [
            'file' => new CURLFile($imagePath)
        ]
    ]);
    
    $response = curl_exec($curl);
    $httpCode = curl_getinfo($curl, CURLINFO_HTTP_CODE);
    curl_close($curl);
    
    if ($httpCode === 200) {
        return $response; // PNG图片数据
    } else {
        throw new Exception("处理失败: HTTP $httpCode");
    }
}

// 使用示例
try {
    $apiKey = 'your-api-key';
    $result = removeBackground('input.jpg', $apiKey);
    file_put_contents('output.png', $result);
    echo "背景去除成功！";
} catch (Exception $e) {
    echo "错误: " . $e->getMessage();
}
?>
```

### cURL命令行

```bash
# 文件上传方式
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -F "file=@image.jpg" \
  https://rembg-l2mt.onrender.com/remove-bg \
  --output result.png

# Base64方式
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"image":"'$(base64 -i image.jpg)'"}' \
  https://rembg-l2mt.onrender.com/remove-bg-base64
```

## 🔧 React组件示例

```jsx
import React, { useState } from 'react';

const BackgroundRemover = ({ apiKey }) => {
    const [file, setFile] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) return;

        setLoading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('https://rembg-l2mt.onrender.com/remove-bg', {
                method: 'POST',
                headers: { 'X-API-Key': apiKey },
                body: formData
            });

            if (response.ok) {
                const blob = await response.blob();
                setResult(URL.createObjectURL(blob));
            }
        } catch (error) {
            console.error('处理失败:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <input 
                    type="file" 
                    accept="image/*"
                    onChange={(e) => setFile(e.target.files[0])}
                />
                <button type="submit" disabled={loading}>
                    {loading ? '处理中...' : '去除背景'}
                </button>
            </form>
            {result && <img src={result} alt="处理结果" />}
        </div>
    );
};

export default BackgroundRemover;
```

## ⚠️ 重要注意事项

### 安全性
- **不要在前端代码中暴露API Key**
- 建议通过后端服务代理API调用
- 在生产环境中使用环境变量存储API Key

### 性能
- 支持的最大文件大小：约10MB
- 处理时间：通常2-10秒（取决于图片大小和复杂度）
- 首次调用可能较慢（冷启动）

### 错误处理
- `400`: 请求参数错误
- `401`: API Key无效或缺失
- `413`: 文件过大
- `429`: 请求过于频繁
- `500`: 服务器内部错误

## 📞 技术支持

如有问题，请检查：
1. API Key是否正确
2. 请求格式是否符合要求
3. 图片文件是否有效
4. 网络连接是否正常

## 🔗 相关链接

- API在线文档: https://rembg-l2mt.onrender.com/docs
- 健康检查: https://rembg-l2mt.onrender.com/health

---

*最后更新: 2024年* 