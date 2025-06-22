#!/usr/bin/env python3
import uvicorn
import os

# 设置API Key
os.environ["API_KEY"] = "my-secret-key"

if __name__ == "__main__":
    print("🚀 启动 Rembg API 服务器...")
    print("📍 端口: 8080")
    print("🔑 API Key: my-secret-key")
    print("📚 API文档: http://localhost:8080/docs")
    print("🔗 健康检查: http://localhost:8080/health")
    print("=" * 50)
    
    # 启动服务器
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_level="info"
    ) 