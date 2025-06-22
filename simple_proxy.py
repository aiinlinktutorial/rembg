#!/usr/bin/env python3
"""
简单HTTP代理服务器 - 解决bolt.new的CORS问题
运行在端口8082，代理到8081的API服务
"""
import uvicorn
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI(
    title="Simple Proxy for Bolt.new",
    description="简单HTTP代理，解决bolt.new跨域问题",
    version="1.0.0"
)

# 超强CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

LOCAL_API_URL = "http://localhost:8081"

@app.get("/")
async def root():
    return {
        "service": "Simple Proxy for Bolt.new",
        "proxy_port": 8082,
        "target_api": LOCAL_API_URL,
        "status": "ready",
        "cors": "enabled"
    }

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """处理所有OPTIONS预检请求"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "86400",
        }
    )

@app.get("/health")
async def health():
    """健康检查"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{LOCAL_API_URL}/health", timeout=5.0)
            data = response.json()
            data["proxy_status"] = "healthy"
            return data
    except Exception as e:
        return {
            "status": "error", 
            "proxy_status": "healthy",
            "api_status": "offline",
            "message": str(e)
        }

@app.post("/remove-bg")
async def proxy_remove_bg(file: UploadFile = File(...)):
    """代理抠图请求"""
    try:
        contents = await file.read()
        files = {"file": (file.filename, contents, file.content_type)}
        
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(f"{LOCAL_API_URL}/remove-bg", files=files)
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type="image/png",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Content-Disposition": f"inline; filename=processed_{file.filename}"
                }
            )
    except Exception as e:
        return JSONResponse(
            {"error": str(e)}, 
            status_code=500,
            headers={"Access-Control-Allow-Origin": "*"}
        )

@app.post("/remove-bg-base64")
async def proxy_remove_bg_base64(request: Request):
    """代理Base64抠图请求"""
    try:
        data = await request.json()
        
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{LOCAL_API_URL}/remove-bg-base64",
                json=data
            )
            
            result = response.json()
            return JSONResponse(
                result,
                headers={"Access-Control-Allow-Origin": "*"}
            )
    except Exception as e:
        return JSONResponse(
            {"error": str(e)}, 
            status_code=500,
            headers={"Access-Control-Allow-Origin": "*"}
        )

if __name__ == "__main__":
    print("🔄 启动简单代理服务器...")
    print("📍 代理端口: 8082")
    print("🎯 目标API: 8081")
    print("🌐 在bolt.new中使用: http://localhost:8082")
    print("💡 健康检查: http://localhost:8082/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8082,
        reload=False
    ) 