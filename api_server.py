from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Header, status
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
from rembg import remove
from PIL import Image
import io
import base64
import json
import os
from typing import Optional

app = FastAPI(
    title="Rembg API - AI背景去除服务",
    description="提供AI智能背景去除功能的REST API，需要API Key认证",
    version="1.0.0"
)

# API Key配置
API_KEY = os.environ.get("API_KEY", "your-secret-api-key-here")  # 从环境变量获取API Key
security = HTTPBearer()

# API Key验证函数
async def verify_api_key(
    authorization: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """验证API Key"""
    if authorization.credentials != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return authorization.credentials

# 或者通过Header验证API Key的替代方法
async def verify_api_key_header(x_api_key: Optional[str] = Header(None)) -> str:
    """通过X-API-Key Header验证"""
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key. Please provide X-API-Key header.",
        )
    return x_api_key

# 添加CORS中间件支持跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """API根路径，返回服务信息"""
    return {
        "message": "Rembg API - AI背景去除服务",
        "version": "1.0.0",
        "authentication": "Required - Use X-API-Key header",
        "endpoints": {
            "remove_background": "/remove-bg (需要API Key)",
            "remove_background_base64": "/remove-bg-base64 (需要API Key)",
            "remove_background_batch": "/remove-bg-batch (需要API Key)",
            "health": "/health (公开访问)",
            "docs": "/docs (API文档)"
        },
        "usage": {
            "header": "X-API-Key: your-api-key",
            "example": "curl -H 'X-API-Key: your-api-key' -X POST ..."
        }
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "rembg-api"}

@app.post("/remove-bg")
async def remove_background_file(
    file: UploadFile = File(...),
    api_key: str = Depends(verify_api_key_header)
):
    """
    上传图片文件进行背景去除
    
    参数:
    - file: 上传的图片文件 (支持 jpg, jpeg, png, bmp, gif 等格式)
    
    返回:
    - 去除背景后的PNG图片
    """
    # 检查文件类型
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="请上传有效的图片文件")
    
    try:
        # 读取上传的文件
        image_data = await file.read()
        
        # 使用rembg去除背景
        output_data = remove(image_data)
        
        # 返回处理后的图片
        return Response(
            content=output_data,
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename=removed_bg_{file.filename.split('.')[0]}.png"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理图片时发生错误: {str(e)}")

@app.post("/remove-bg-base64")
async def remove_background_base64(
    request_data: dict,
    api_key: str = Depends(verify_api_key_header)
):
    """
    通过Base64编码的图片进行背景去除
    
    请求格式:
    {
        "image": "base64编码的图片数据"
    }
    
    返回:
    {
        "result": "base64编码的处理后图片",
        "format": "png"
    }
    """
    try:
        # 从请求中获取base64图片数据
        if "image" not in request_data:
            raise HTTPException(status_code=400, detail="请求中缺少 'image' 字段")
        
        base64_image = request_data["image"]
        
        # 解码base64图片
        try:
            # 如果包含data:image前缀，需要去除
            if base64_image.startswith('data:image'):
                base64_image = base64_image.split(',')[1]
            
            image_data = base64.b64decode(base64_image)
        except Exception:
            raise HTTPException(status_code=400, detail="无效的base64图片数据")
        
        # 使用rembg去除背景
        output_data = remove(image_data)
        
        # 将结果编码为base64
        result_base64 = base64.b64encode(output_data).decode('utf-8')
        
        return {
            "result": result_base64,
            "format": "png",
            "message": "背景去除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理图片时发生错误: {str(e)}")

@app.post("/remove-bg-batch")
async def remove_background_batch(
    files: list[UploadFile] = File(...),
    api_key: str = Depends(verify_api_key_header)
):
    """
    批量处理多张图片的背景去除
    
    参数:
    - files: 多个上传的图片文件
    
    返回:
    - 包含所有处理结果的base64编码数组
    """
    if len(files) > 10:  # 限制批量处理数量
        raise HTTPException(status_code=400, detail="批量处理最多支持10张图片")
    
    results = []
    
    for i, file in enumerate(files):
        try:
            # 检查文件类型
            if not file.content_type or not file.content_type.startswith('image/'):
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "message": "不是有效的图片文件"
                })
                continue
            
            # 读取和处理图片
            image_data = await file.read()
            output_data = remove(image_data)
            result_base64 = base64.b64encode(output_data).decode('utf-8')
            
            results.append({
                "filename": file.filename,
                "status": "success",
                "result": result_base64,
                "format": "png"
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": f"处理失败: {str(e)}"
            })
    
    return {
        "total": len(files),
        "results": results
    }

if __name__ == "__main__":
    # 从环境变量获取端口，默认为8000
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"  # 改为 0.0.0.0 以便 Render 能够访问
    
    print("🚀 正在启动Rembg API服务器...")
    print(f"📝 API文档地址: http://{host}:{port}/docs")
    print(f"🎯 健康检查: http://{host}:{port}/health")
    print("💡 主要接口:")
    print("   - POST /remove-bg (文件上传)")
    print("   - POST /remove-bg-base64 (Base64)")
    print("   - POST /remove-bg-batch (批量处理)")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False  # 生产环境建议关闭 reload
    ) 