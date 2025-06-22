#!/usr/bin/env python3
"""
HTTPS代理服务器 - 解决bolt.new的HTTPS混合内容问题
支持自签名证书的HTTPS服务
"""
import uvicorn
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import ssl
import os

app = FastAPI(
    title="HTTPS Proxy for Bolt.new",
    description="HTTPS代理服务器，解决混合内容问题",
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
        "service": "HTTPS Proxy for Bolt.new",
        "proxy_port": 8443,
        "target_api": LOCAL_API_URL,
        "status": "ready",
        "protocol": "https",
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
            data["protocol"] = "https"
            return data
    except Exception as e:
        return {
            "status": "error", 
            "proxy_status": "healthy",
            "api_status": "offline",
            "protocol": "https",
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

def create_self_signed_cert():
    """创建自签名证书"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import datetime
        
        # 生成私钥
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # 生成证书
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"CA"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"Local"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Rembg API"),
            x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(u"localhost"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # 保存证书和私钥
        with open("cert.pem", "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open("key.pem", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print("✅ 自签名证书创建成功")
        return True
        
    except ImportError:
        print("❌ 需要安装cryptography库: pip install cryptography")
        return False
    except Exception as e:
        print(f"❌ 创建证书失败: {e}")
        return False

if __name__ == "__main__":
    print("🔐 启动HTTPS代理服务器...")
    print("📍 代理端口: 8443 (HTTPS)")
    print("🎯 目标API: 8081")
    print("🌐 在bolt.new中使用: https://localhost:8443")
    print("💡 健康检查: https://localhost:8443/health")
    print("=" * 60)
    
    # 检查证书文件是否存在
    if not (os.path.exists("cert.pem") and os.path.exists("key.pem")):
        print("📋 证书文件不存在，正在创建自签名证书...")
        if not create_self_signed_cert():
            print("❌ 无法创建证书，使用HTTP模式")
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=8443,
                reload=False
            )
            exit()
    
    # 启动HTTPS服务器
    print("🚀 启动HTTPS服务器...")
    print("⚠️  浏览器会显示证书警告，请选择'继续访问'")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8443,
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem",
        reload=False
    ) 