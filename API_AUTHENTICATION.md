# API 认证使用说明

## 🔐 API Key 认证

为了保护服务资源，所有图像处理接口都需要API Key认证。

### 📋 需要认证的接口

- `POST /remove-bg` - 文件上传背景去除
- `POST /remove-bg-base64` - Base64背景去除  
- `POST /remove-bg-batch` - 批量背景去除

### 🔓 公开接口（无需认证）

- `GET /` - 服务信息
- `GET /health` - 健康检查
- `GET /docs` - API文档

## 🔑 如何获取API Key

1. 登录 Render Dashboard
2. 进入你的服务设置
3. 查看 Environment Variables
4. 找到 `API_KEY` 的值

## 💡 如何使用API Key

### 方法1：通过 X-API-Key Header

```bash
curl -H "X-API-Key: your-api-key-here" \
     -X POST \
     -F "file=@image.jpg" \
     https://your-service.onrender.com/remove-bg
```

### 方法2：通过 Python requests

```python
import requests

headers = {
    'X-API-Key': 'your-api-key-here'
}

# 文件上传
with open('image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'https://your-service.onrender.com/remove-bg',
        headers=headers,
        files=files
    )

# Base64方式
import base64
with open('image.jpg', 'rb') as f:
    img_data = base64.b64encode(f.read()).decode()

data = {'image': img_data}
response = requests.post(
    'https://your-service.onrender.com/remove-bg-base64',
    headers=headers,
    json=data
)
```

### 方法3：通过 JavaScript/fetch

```javascript
// 文件上传
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('https://your-service.onrender.com/remove-bg', {
    method: 'POST',
    headers: {
        'X-API-Key': 'your-api-key-here'
    },
    body: formData
})
.then(response => response.blob())
.then(blob => {
    // 处理返回的图片
});
```

## ❌ 认证失败

如果API Key无效或缺失，会返回：

```json
{
    "detail": "Invalid or missing API Key. Please provide X-API-Key header."
}
```

状态码：`401 Unauthorized`

## 🔒 安全建议

1. **保密API Key** - 不要在客户端代码中硬编码
2. **使用环境变量** - 在服务器端通过环境变量传递
3. **定期更换** - 定期更新API Key
4. **监控使用** - 关注API调用日志
5. **限制访问** - 只给需要的人员提供API Key 