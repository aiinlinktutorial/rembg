# 🎨 Bolt.new AI抠图功能集成指南

本指南将帮助您在bolt.new项目中集成AI抠图功能。

## 🚀 快速开始

### 1. 启动本地API服务

```bash
# 方式1：使用专用启动脚本
python start_bolt_api.py

# 方式2：直接启动
python bolt_api.py
```

服务启动后将运行在: `http://localhost:8080`

### 2. 在bolt.new中创建前端组件

以下是一个完整的React组件示例：

```jsx
import React, { useState, useRef } from 'react';

const ImageBackgroundRemover = () => {
  const [originalImage, setOriginalImage] = useState(null);
  const [processedImage, setProcessedImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  // API配置
  const API_BASE_URL = 'http://localhost:8080';

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      processImage(file);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      processImage(file);
    }
  };

  const processImage = async (file) => {
    setIsProcessing(true);
    setError(null);
    setProcessedImage(null);
    
    // 显示原图预览
    const reader = new FileReader();
    reader.onload = (e) => setOriginalImage(e.target.result);
    reader.readAsDataURL(file);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/api/remove-bg`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`处理失败: ${response.statusText}`);
      }

      const blob = await response.blob();
      const imageUrl = URL.createObjectURL(blob);
      setProcessedImage(imageUrl);
      
    } catch (err) {
      setError(err.message);
      console.error('抠图处理失败:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const downloadImage = () => {
    if (processedImage) {
      const link = document.createElement('a');
      link.href = processedImage;
      link.download = 'removed-background.png';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const resetImages = () => {
    setOriginalImage(null);
    setProcessedImage(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-center mb-6 text-gray-800">
        🎨 AI智能抠图工具
      </h2>
      
      {/* 上传区域 */}
      <div
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 transition-colors"
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="hidden"
        />
        <div className="text-gray-600">
          <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" stroke="currentColor" fill="none" viewBox="0 0 48 48">
            <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <p className="text-lg">点击选择图片或拖拽到此处</p>
          <p className="text-sm text-gray-500 mt-2">支持 JPG, PNG, GIF 等格式，最大20MB</p>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
          <p className="font-semibold">处理失败</p>
          <p>{error}</p>
        </div>
      )}

      {/* 处理中状态 */}
      {isProcessing && (
        <div className="mt-6 text-center">
          <div className="inline-flex items-center px-4 py-2 bg-blue-100 rounded-lg">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span className="text-blue-800">AI正在处理中，请稍候...</span>
          </div>
        </div>
      )}

      {/* 图片预览区域 */}
      {(originalImage || processedImage) && (
        <div className="mt-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 原图 */}
            {originalImage && (
              <div className="text-center">
                <h3 className="text-lg font-semibold mb-3 text-gray-700">原图</h3>
                <div className="bg-gray-100 rounded-lg p-4">
                  <img
                    src={originalImage}
                    alt="原图"
                    className="max-w-full max-h-64 mx-auto rounded-lg shadow-md"
                  />
                </div>
              </div>
            )}

            {/* 处理后的图片 */}
            {processedImage && (
              <div className="text-center">
                <h3 className="text-lg font-semibold mb-3 text-gray-700">抠图结果</h3>
                <div className="bg-gray-100 rounded-lg p-4" style={{
                  backgroundImage: 'linear-gradient(45deg, #f0f0f0 25%, transparent 25%), linear-gradient(-45deg, #f0f0f0 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #f0f0f0 75%), linear-gradient(-45deg, transparent 75%, #f0f0f0 75%)',
                  backgroundSize: '20px 20px',
                  backgroundPosition: '0 0, 0 10px, 10px -10px, -10px 0px'
                }}>
                  <img
                    src={processedImage}
                    alt="抠图结果"
                    className="max-w-full max-h-64 mx-auto rounded-lg shadow-md"
                  />
                </div>
                <button
                  onClick={downloadImage}
                  className="mt-3 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  💾 下载图片
                </button>
              </div>
            )}
          </div>

          {/* 重新开始按钮 */}
          <div className="text-center mt-6">
            <button
              onClick={resetImages}
              className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              🔄 重新开始
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageBackgroundRemover;
```

### 3. 使用Base64接口的示例

如果您需要使用Base64格式的接口，可以使用以下函数：

```javascript
const removeBackgroundBase64 = async (base64Image) => {
  try {
    const response = await fetch('http://localhost:8080/api/remove-bg-base64', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image: base64Image
      })
    });

    if (!response.ok) {
      throw new Error(`API错误: ${response.statusText}`);
    }

    const result = await response.json();
    
    if (result.success) {
      return `data:image/png;base64,${result.result}`;
    } else {
      throw new Error('抠图处理失败');
    }
  } catch (error) {
    console.error('抠图处理失败:', error);
    throw error;
  }
};

// 使用示例
const handleFileToBase64 = (file) => {
  const reader = new FileReader();
  reader.onload = async (e) => {
    try {
      const base64 = e.target.result.split(',')[1]; // 移除data:image前缀
      const resultImage = await removeBackgroundBase64(base64);
      // 使用resultImage显示结果
    } catch (error) {
      console.error('处理失败:', error);
    }
  };
  reader.readAsDataURL(file);
};
```

## 🛠️ API接口详情

### 健康检查
```
GET http://localhost:8080/health
```
返回服务器状态信息

### 文件上传抠图
```
POST http://localhost:8080/api/remove-bg
Content-Type: multipart/form-data

参数:
- file: 图片文件

返回: PNG格式的图片数据
```

### Base64抠图
```
POST http://localhost:8080/api/remove-bg-base64
Content-Type: application/json

请求体:
{
  "image": "base64编码的图片数据"
}

返回:
{
  "success": true,
  "result": "base64编码的PNG图片",
  "format": "png",
  "message": "Background removed successfully"
}
```

## 🎯 特性

- ✅ **无需认证**: 专为bolt.new设计，无需API Key
- ✅ **跨域支持**: 已配置CORS，支持前端直接调用
- ✅ **多格式支持**: 支持JPG、PNG、GIF等常见图片格式
- ✅ **大文件支持**: 最大支持20MB图片
- ✅ **错误处理**: 完善的错误提示和处理机制
- ✅ **实时日志**: 详细的处理日志便于调试

## 🚨 注意事项

1. **首次运行**: 第一次启动时会自动下载AI模型（约1-2GB），请确保网络连接正常
2. **内存占用**: 处理大图片时可能占用较多内存
3. **处理时间**: 图片越大，处理时间越长（通常5-30秒）
4. **本地服务**: API运行在本地，确保服务器正常运行

## 🔧 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 修改端口
   export PORT=8081
   python start_bolt_api.py
   ```

2. **依赖包缺失**
   ```bash
   pip install fastapi uvicorn rembg pillow python-multipart
   ```

3. **模型下载失败**
   - 检查网络连接
   - 尝试使用VPN
   - 手动下载模型文件

4. **内存不足**
   - 减小图片尺寸
   - 关闭其他应用程序
   - 增加虚拟内存

### 调试方法

1. 检查API状态:
   ```bash
   curl http://localhost:8080/health
   ```

2. 查看详细日志:
   ```bash
   python bolt_api.py
   ```

3. 测试API接口:
   ```bash
   curl -X POST -F "file=@test.jpg" http://localhost:8080/api/remove-bg --output result.png
   ```

## 🎉 完成

现在您可以在bolt.new项目中愉快地使用AI抠图功能了！如有问题，请查看控制台日志或参考故障排除部分。 