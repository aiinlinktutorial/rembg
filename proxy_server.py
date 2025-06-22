#!/usr/bin/env python3
"""
HTTPS代理服务器 - 解决bolt.new的CORS和HTTPS问题
"""
import ssl
import uvicorn
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
import os

app = FastAPI(
    title="HTTPS Proxy for Bolt.new",
    description="HTTPS代理服务器，解决bolt.new的跨域和安全问题",
    version="1.0.0"
)

# 更强的CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 本地API地址
LOCAL_API_URL = "http://localhost:8080"

@app.get("/")
async def root():
    """代理服务器信息"""
    return {
        "service": "HTTPS Proxy for Bolt.new",
        "version": "1.0.0",
        "description": "解决bolt.new HTTPS/CORS问题的代理服务器",
        "local_api": LOCAL_API_URL,
        "endpoints": {
            "health": "GET /health",
            "remove_bg": "POST /api/remove-bg",
            "remove_bg_base64": "POST /api/remove-bg-base64"
        }
    }

@app.options("/{path:path}")
async def handle_options(path: str):
    """处理所有预检请求"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "86400",
        }
    )

@app.get("/health")
async def health_check():
    """健康检查 - 代理到本地API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{LOCAL_API_URL}/health", timeout=5.0)
            return response.json()
    except Exception as e:
        return {"status": "error", "message": f"本地API不可用: {str(e)}"}

@app.post("/api/remove-bg")
async def proxy_remove_bg(file: UploadFile = File(...)):
    """代理文件上传抠图请求"""
    try:
        # 读取文件内容
        file_content = await file.read()
        
        # 创建multipart数据
        files = {"file": (file.filename, file_content, file.content_type)}
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{LOCAL_API_URL}/api/remove-bg",
                files=files
            )
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers={
                    "Content-Type": "image/png",
                    "Access-Control-Allow-Origin": "*",
                    "Content-Disposition": f"inline; filename=removed_{file.filename.split('.')[0]}.png"
                }
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "代理请求失败", "message": str(e)},
            headers={"Access-Control-Allow-Origin": "*"}
        )

@app.post("/api/remove-bg-base64")
async def proxy_remove_bg_base64(request: Request):
    """代理Base64抠图请求"""
    try:
        # 获取请求数据
        data = await request.json()
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{LOCAL_API_URL}/api/remove-bg-base64",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            result = response.json()
            return JSONResponse(
                content=result,
                status_code=response.status_code,
                headers={"Access-Control-Allow-Origin": "*"}
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "代理请求失败", "message": str(e)},
            headers={"Access-Control-Allow-Origin": "*"}
        )

def create_self_signed_cert():
    """创建自签名证书"""
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
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Local"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Bolt.new Proxy"),
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
            x509.IPAddress("127.0.0.1"),
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

if __name__ == "__main__":
    port = int(os.environ.get("PROXY_PORT", 8443))
    
    print("🔐 HTTPS代理服务器启动中...")
    
    # 检查证书文件
    if not (os.path.exists("cert.pem") and os.path.exists("key.pem")):
        print("📄 创建自签名证书...")
        try:
            create_self_signed_cert()
            print("✅ 证书创建成功")
        except ImportError:
            print("❌ 缺少cryptography库，使用HTTP模式")
            print("💡 运行: pip install cryptography")
            # HTTP模式
            print(f"🌐 HTTP代理服务器: http://localhost:{port}")
            uvicorn.run(app, host="0.0.0.0", port=port)
            exit()
    
    # 配置SSL上下文
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain("cert.pem", "key.pem")
    
    print(f"🔐 HTTPS代理服务器: https://localhost:{port}")
    print(f"🔗 代理目标: {LOCAL_API_URL}")
    print("⚠️  浏览器会显示安全警告，点击'高级'→'继续访问'即可")
    print("💡 主要接口:")
    print(f"   - POST https://localhost:{port}/api/remove-bg")
    print(f"   - POST https://localhost:{port}/api/remove-bg-base64")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        ssl_context=ssl_context
    ) 