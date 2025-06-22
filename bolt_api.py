from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from rembg import remove
from PIL import Image
import io
import base64
import os
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Bolt.new Rembg API",
    description="为bolt.new定制的AI抠图API服务 - 无需认证，即开即用",
    version="1.0.0"
)

# 添加CORS中间件 - 允许bolt.new访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # 允许所有域名
        "https://bolt.new",  # bolt.new域名
        "https://*.bolt.new",  # bolt.new子域名
        "http://localhost:*",  # 本地开发
        "https://localhost:*",  # 本地HTTPS
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS", "HEAD"],
    allow_headers=[
        "*",
        "Content-Type",
        "Authorization",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Headers",
    ],
    expose_headers=["*"],
)

@app.get("/")
async def root():
    """API根路径，返回服务信息"""
    return {
        "service": "Bolt.new Rembg API",
        "version": "1.0.0",
        "description": "AI智能抠图服务 - 为bolt.new定制",
        "endpoints": {
            "health": "GET /health - 健康检查",
            "remove_bg": "POST /api/remove-bg - 图片抠图",
            "remove_bg_base64": "POST /api/remove-bg-base64 - Base64抠图"
        },
        "usage": "直接上传图片即可，无需API Key",
        "status": "ready"
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "bolt-rembg-api", "timestamp": int(time.time())}

@app.options("/api/remove-bg")
@app.options("/api/remove-bg-base64")
async def handle_options():
    """处理预检请求"""
    return Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "86400",
        }
    )

@app.post("/api/remove-bg")
async def remove_background_for_bolt(file: UploadFile = File(...)):
    """
    专为bolt.new设计的抠图接口
    
    参数:
    - file: 上传的图片文件
    
    返回:
    - 去除背景后的PNG图片（直接返回图片数据）
    """
    try:
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Only image files are supported")
        
        # 验证文件大小 (限制20MB)
        contents = await file.read()
        if len(contents) > 20 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size too large (max 20MB)")
        
        logger.info(f"Processing image: {file.filename}, size: {len(contents)} bytes")
        
        # 使用rembg去除背景
        output_data = remove(contents)
        
        logger.info(f"Background removal completed for: {file.filename}")
        
        # 返回处理后的PNG图片
        return Response(
            content=output_data,
            media_type="image/png",
            headers={
                "Content-Disposition": f"inline; filename=removed_{file.filename.split('.')[0]}.png",
                "Cache-Control": "no-cache"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")

@app.post("/api/remove-bg-base64")
async def remove_background_base64_for_bolt(request_data: dict):
    """
    Base64格式的抠图接口 - 专为bolt.new的前端调用设计
    
    请求格式:
    {
        "image": "base64编码的图片数据"
    }
    
    返回:
    {
        "success": true,
        "result": "base64编码的处理后图片",
        "format": "png"
    }
    """
    try:
        # 检查请求数据
        if not isinstance(request_data, dict) or "image" not in request_data:
            raise HTTPException(status_code=400, detail="Request must contain 'image' field")
        
        base64_image = request_data["image"]
        if not base64_image:
            raise HTTPException(status_code=400, detail="Image data cannot be empty")
        
        # 处理data URL格式
        if base64_image.startswith('data:image'):
            try:
                base64_image = base64_image.split(',')[1]
            except IndexError:
                raise HTTPException(status_code=400, detail="Invalid data URL format")
        
        # 解码base64图片
        try:
            image_data = base64.b64decode(base64_image)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 image data")
        
        # 验证图片大小
        if len(image_data) > 20 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image size too large (max 20MB)")
        
        logger.info(f"Processing base64 image, size: {len(image_data)} bytes")
        
        # 使用rembg去除背景
        output_data = remove(image_data)
        
        # 将结果编码为base64
        result_base64 = base64.b64encode(output_data).decode('utf-8')
        
        logger.info("Base64 background removal completed")
        
        return {
            "success": True,
            "result": result_base64,
            "format": "png",
            "message": "Background removed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing base64 image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """自定义404处理"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "message": "Available endpoints: GET /, GET /health, POST /api/remove-bg, POST /api/remove-bg-base64"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """自定义500处理"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "Please check your image format and try again"
        }
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    host = "0.0.0.0"
    
    print("🚀 Bolt.new Rembg API Server Starting...")
    print(f"📝 API Docs: http://localhost:{port}/docs")
    print(f"🎯 Health Check: http://localhost:{port}/health")
    print("💡 Main Endpoints:")
    print(f"   - POST http://localhost:{port}/api/remove-bg")
    print(f"   - POST http://localhost:{port}/api/remove-bg-base64")
    print("🎨 Ready for bolt.new integration!")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False
    ) 