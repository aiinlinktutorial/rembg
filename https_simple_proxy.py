#!/usr/bin/env python3
"""
简单HTTPS代理服务器 - 解决bolt.new的HTTPS访问问题
"""
import uvicorn
import ipaddress
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI(
    title="HTTPS Proxy for Bolt.new",
    description="HTTPS代理，解决bolt.new访问本地API的问题",
    version="1.0.0"
)

# 强化CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

LOCAL_API_URL = "http://localhost:8080"

@app.get("/")
async def root():
    return {
        "service": "HTTPS Proxy for Bolt.new",
        "version": "1.0.0",
        "https_port": 8443,
        "target_api": LOCAL_API_URL,
        "status": "ready",
        "message": "HTTPS代理服务器已就绪"
    }

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
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
            data["https_proxy"] = "healthy"
            return data
    except Exception as e:
        return {
            "status": "error", 
            "https_proxy": "healthy",
            "api_status": "offline",
            "message": str(e)
        }

@app.post("/api/remove-bg")
async def proxy_remove_bg(file: UploadFile = File(...)):
    """HTTPS代理抠图请求"""
    try:
        contents = await file.read()
        files = {"file": (file.filename, contents, file.content_type)}
        
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(f"{LOCAL_API_URL}/api/remove-bg", files=files)
            
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
            {"error": f"代理请求失败: {str(e)}"}, 
            status_code=500,
            headers={"Access-Control-Allow-Origin": "*"}
        )

@app.post("/api/remove-bg-base64")
async def proxy_remove_bg_base64(request: Request):
    """HTTPS代理Base64抠图"""
    try:
        data = await request.json()
        
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{LOCAL_API_URL}/api/remove-bg-base64",
                json=data
            )
            
            result = response.json()
            return JSONResponse(
                result,
                headers={"Access-Control-Allow-Origin": "*"}
            )
    except Exception as e:
        return JSONResponse(
            {"error": f"代理请求失败: {str(e)}"}, 
            status_code=500,
            headers={"Access-Control-Allow-Origin": "*"}
        )

def create_simple_cert():
    """创建简单的自签名证书"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime
        
        # 生成私钥
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # 创建证书
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
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
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # 保存证书
        with open("cert.pem", "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open("key.pem", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        return True
    except Exception as e:
        print(f"证书创建失败: {e}")
        return False

if __name__ == "__main__":
    print("🔐 启动HTTPS代理服务器...")
    
    # 检查或创建证书
    if not (os.path.exists("cert.pem") and os.path.exists("key.pem")):
        print("📄 创建自签名证书...")
        if not create_simple_cert():
            print("❌ 证书创建失败，使用HTTP模式")
            print("🌐 HTTP模式: http://localhost:8081")
            uvicorn.run(app, host="0.0.0.0", port=8081)
            exit()
    
    try:
        print("✅ HTTPS代理服务器启动成功!")
        print("🔐 HTTPS地址: https://localhost:8443")
        print("🔗 代理目标: http://localhost:8080")
        print("⚠️  浏览器会显示安全警告，点击'高级'→'继续访问'")
        print("💡 在bolt.new中使用: https://localhost:8443")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8443,
            ssl_keyfile="key.pem",
            ssl_certfile="cert.pem"
        )
    except Exception as e:
        print(f"❌ HTTPS启动失败: {e}")
        print("🔄 回退到HTTP模式...")
        uvicorn.run(app, host="0.0.0.0", port=8082) 