# Rembg API 使用说明

## 概述

这是一个基于FastAPI的背景去除API服务，可以通过HTTP接口调用rembg库的功能。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements_api.txt
```

或手动安装：
```bash
pip install fastapi uvicorn python-multipart rembg pillow
```

### 2. 启动服务器

方式一：使用启动脚本
```bash
python start_api.py
```

方式二：直接启动
```bash
python api_server.py
```

方式三：使用uvicorn启动
```bash
uvicorn api_server:app --host 127.0.0.1 --port 8000 --reload
```

### 3. 访问API文档

启动后访问：http://127.0.0.1:8000/docs

## API接口说明

### 1. 健康检查
- **URL**: `GET /health`
- **描述**: 检查服务器状态
- **响应**: 
```json
{
  "status": "healthy",
  "service": "rembg-api"
}
```

### 2. 文件上传去背景
- **URL**: `POST /remove-bg`
- **描述**: 上传图片文件进行背景去除
- **请求**: multipart/form-data
  - `file`: 图片文件
- **响应**: PNG格式的处理后图片

#### 示例 (curl)
```bash
curl -X POST "http://127.0.0.1:8000/remove-bg" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_image.jpg" \
     --output result.png
```

#### 示例 (Python)
```python
import requests

with open('your_image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://127.0.0.1:8000/remove-bg', files=files)

if response.status_code == 200:
    with open('result.png', 'wb') as f:
        f.write(response.content)
```

### 3. Base64去背景
- **URL**: `POST /remove-bg-base64`
- **描述**: 通过Base64编码的图片进行背景去除
- **请求**: application/json
```json
{
  "image": "base64编码的图片数据"
}
```
- **响应**: 
```json
{
  "result": "base64编码的处理后图片",
  "format": "png",
  "message": "背景去除成功"
}
```

#### 示例 (Python)
```python
import requests
import base64

# 读取图片并编码
with open('your_image.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# 发送请求
payload = {"image": image_data}
response = requests.post('http://127.0.0.1:8000/remove-bg-base64', json=payload)

if response.status_code == 200:
    result = response.json()
    # 解码并保存结果
    output_data = base64.b64decode(result['result'])
    with open('result.png', 'wb') as f:
        f.write(output_data)
```

### 4. 批量处理
- **URL**: `POST /remove-bg-batch`
- **描述**: 批量处理多张图片（最多10张）
- **请求**: multipart/form-data
  - `files`: 多个图片文件
- **响应**: 
```json
{
  "total": 3,
  "results": [
    {
      "filename": "image1.jpg",
      "status": "success",
      "result": "base64编码的处理后图片",
      "format": "png"
    },
    {
      "filename": "image2.jpg",
      "status": "error",
      "message": "处理失败原因"
    }
  ]
}
```

#### 示例 (Python)
```python
import requests

files = [
    ('files', ('image1.jpg', open('image1.jpg', 'rb'), 'image/jpeg')),
    ('files', ('image2.jpg', open('image2.jpg', 'rb'), 'image/jpeg')),
]

response = requests.post('http://127.0.0.1:8000/remove-bg-batch', files=files)

# 记得关闭文件
for _, (_, f, _) in files:
    f.close()
```

## 错误码

- `400 Bad Request`: 请求参数错误（如文件格式不支持）
- `500 Internal Server Error`: 服务器内部错误（如处理图片失败）

## 测试

运行测试脚本：
```bash
python test_api.py
```

这会自动测试所有API接口，并生成测试结果图片。

## 支持的图片格式

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- GIF (.gif)
- TIFF (.tiff)

## 性能说明

- 处理时间取决于图片大小和复杂度
- 建议图片大小不超过10MB
- 批量处理限制为10张图片
- 第一次使用时需要下载模型文件（约1-2GB）

## 注意事项

1. 确保有足够的磁盘空间存储模型文件
2. 首次运行时会自动下载AI模型，请保持网络连接
3. 处理大图片时可能需要较长时间
4. 服务器默认监听127.0.0.1:8000，只允许本地访问

## 故障排除

### 端口被占用
如果8000端口被占用，可以修改`api_server.py`中的端口号：
```python
uvicorn.run(app, host="127.0.0.1", port=8001)  # 改为8001或其他端口
```

### 模型下载失败
确保网络连接正常，或手动下载模型文件到rembg模型目录。

### 内存不足
处理大图片时可能出现内存不足，建议：
- 减小图片尺寸
- 增加系统内存
- 关闭其他占用内存的程序 