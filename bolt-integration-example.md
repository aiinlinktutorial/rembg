# Bolt.new 集成你的AI背景去除API

## 🚀 方案1：纯前端调用（简单方案）

### HTML 文件 (index.html)

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI背景去除工具</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .upload-area {
            border: 2px dashed #ccc;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            margin: 20px 0;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .upload-area:hover {
            border-color: #007bff;
            background-color: #f8f9fa;
        }
        .upload-area.dragover {
            border-color: #007bff;
            background-color: #e3f2fd;
        }
        .preview-container {
            display: flex;
            gap: 20px;
            margin-top: 20px;
        }
        .preview-box {
            flex: 1;
            text-align: center;
        }
        .preview-box img {
            max-width: 100%;
            max-height: 300px;
            border-radius: 5px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        .loading .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 2s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px 5px;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #0056b3;
        }
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .error {
            color: #dc3545;
            margin: 10px 0;
            padding: 10px;
            background: #f8d7da;
            border-radius: 5px;
        }
        .success {
            color: #155724;
            margin: 10px 0;
            padding: 10px;
            background: #d4edda;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 AI智能背景去除</h1>
        <p>上传图片，AI自动去除背景，支持人物、物体、动物等</p>
        
        <div class="upload-area" id="uploadArea">
            <p>📁 点击选择图片或拖拽到这里</p>
            <p style="color: #666; font-size: 14px;">支持 JPG, PNG, GIF 等格式</p>
            <input type="file" id="fileInput" accept="image/*" style="display: none;">
        </div>
        
        <div id="message"></div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>AI正在处理中，请稍候...</p>
        </div>
        
        <div class="preview-container" id="previewContainer" style="display: none;">
            <div class="preview-box">
                <h3>原图</h3>
                <img id="originalImage" alt="原图">
            </div>
            <div class="preview-box">
                <h3>去背景后</h3>
                <img id="processedImage" alt="处理后">
                <br>
                <button class="btn" id="downloadBtn" style="margin-top: 10px;">💾 下载图片</button>
            </div>
        </div>
    </div>

    <script>
        // 配置你的API
        const API_BASE_URL = 'https://rembg-12mt.onrender.com';
        const API_KEY = 'your-api-key-here'; // 替换为你的真实API Key
        
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const loading = document.getElementById('loading');
        const previewContainer = document.getElementById('previewContainer');
        const originalImage = document.getElementById('originalImage');
        const processedImage = document.getElementById('processedImage');
        const downloadBtn = document.getElementById('downloadBtn');
        const message = document.getElementById('message');
        
        // 点击上传区域
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        // 文件选择
        fileInput.addEventListener('change', handleFile);
        
        // 拖拽上传
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile({ target: { files } });
            }
        });
        
        function handleFile(event) {
            const file = event.target.files[0];
            if (!file) return;
            
            // 验证文件类型
            if (!file.type.startsWith('image/')) {
                showMessage('请选择图片文件！', 'error');
                return;
            }
            
            // 验证文件大小 (限制为10MB)
            if (file.size > 10 * 1024 * 1024) {
                showMessage('图片文件不能超过10MB！', 'error');
                return;
            }
            
            // 显示原图预览
            const reader = new FileReader();
            reader.onload = (e) => {
                originalImage.src = e.target.result;
                previewContainer.style.display = 'flex';
            };
            reader.readAsDataURL(file);
            
            // 调用API处理
            processImage(file);
        }
        
        async function processImage(file) {
            try {
                loading.style.display = 'block';
                showMessage('');
                
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await fetch(`${API_BASE_URL}/remove-bg`, {
                    method: 'POST',
                    headers: {
                        'X-API-Key': API_KEY
                    },
                    body: formData
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `HTTP ${response.status}`);
                }
                
                const blob = await response.blob();
                const imageUrl = URL.createObjectURL(blob);
                
                processedImage.src = imageUrl;
                
                // 设置下载按钮
                downloadBtn.onclick = () => {
                    const a = document.createElement('a');
                    a.href = imageUrl;
                    a.download = `removed_bg_${file.name.split('.')[0]}.png`;
                    a.click();
                };
                
                showMessage('✅ 背景去除成功！', 'success');
                
            } catch (error) {
                console.error('处理失败:', error);
                showMessage(`❌ 处理失败: ${error.message}`, 'error');
            } finally {
                loading.style.display = 'none';
            }
        }
        
        function showMessage(text, type = '') {
            message.innerHTML = text ? `<div class="${type}">${text}</div>` : '';
        }
    </script>
</body>
</html>
```

## 🚀 方案2：Node.js后端调用（推荐方案）

### 后端API (server.js)

```javascript
const express = require('express');
const multer = require('multer');
const FormData = require('form-data');
const fetch = require('node-fetch');
const cors = require('cors');

const app = express();
const port = process.env.PORT || 3000;

// 中间件
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// 文件上传配置
const upload = multer({
    limits: {
        fileSize: 10 * 1024 * 1024 // 10MB
    },
    fileFilter: (req, file, cb) => {
        if (file.mimetype.startsWith('image/')) {
            cb(null, true);
        } else {
            cb(new Error('只支持图片文件'), false);
        }
    }
});

// 配置你的API
const REMBG_API_URL = 'https://rembg-12mt.onrender.com';
const REMBG_API_KEY = process.env.REMBG_API_KEY || 'your-api-key-here';

// 背景去除接口
app.post('/api/remove-background', upload.single('image'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: '请上传图片文件' });
        }

        // 创建表单数据
        const formData = new FormData();
        formData.append('file', req.file.buffer, {
            filename: req.file.originalname,
            contentType: req.file.mimetype
        });

        // 调用你的rembg API
        const response = await fetch(`${REMBG_API_URL}/remove-bg`, {
            method: 'POST',
            headers: {
                'X-API-Key': REMBG_API_KEY,
                ...formData.getHeaders()
            },
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `API调用失败: ${response.status}`);
        }

        // 转发处理后的图片
        const imageBuffer = await response.buffer();
        
        res.set({
            'Content-Type': 'image/png',
            'Content-Disposition': `attachment; filename="removed_bg_${Date.now()}.png"`
        });
        
        res.send(imageBuffer);

    } catch (error) {
        console.error('背景去除失败:', error);
        res.status(500).json({ 
            error: '背景去除失败', 
            details: error.message 
        });
    }
});

// 健康检查
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.listen(port, () => {
    console.log(`服务器运行在 http://localhost:${port}`);
});
```

### package.json

```json
{
  "name": "rembg-frontend",
  "version": "1.0.0",
  "description": "AI背景去除前端应用",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "multer": "^1.4.5-lts.1",
    "form-data": "^4.0.0",
    "node-fetch": "^2.6.7",
    "cors": "^2.8.5"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
```

## 🎯 在 bolt.new 中使用步骤：

### 1. **创建新项目**
- 在 bolt.new 中创建一个新项目
- 选择 "React + Node.js" 或 "HTML/CSS/JS"

### 2. **添加代码**
- 复制上面的代码到对应文件
- 替换 `your-api-key-here` 为你的真实API Key

### 3. **环境变量设置**
```bash
REMBG_API_KEY=your-actual-api-key-here
```

### 4. **告诉bolt.new的提示词**

```
请帮我创建一个AI背景去除的Web应用：

1. 用户可以上传图片
2. 调用我的API：https://rembg-12mt.onrender.com/remove-bg
3. API需要X-API-Key header认证
4. 我的API Key是：[你的API Key]
5. 要有拖拽上传功能
6. 显示原图和处理后的对比
7. 支持下载处理后的图片
8. 要有加载动画和错误处理

技术栈：React + Node.js 或者纯HTML/JS都可以
```

## 🔒 安全提示：

1. **不要在前端暴露API Key** - 使用后端代理
2. **设置CORS** - 只允许你的域名访问
3. **添加速率限制** - 防止滥用
4. **文件大小限制** - 避免大文件上传

这样你就能在 bolt.new 中完美集成你的AI背景去除API了！🎉 