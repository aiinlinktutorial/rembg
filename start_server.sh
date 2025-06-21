#!/bin/bash

# 获取端口环境变量，默认为 10000
PORT=${PORT:-10000}

echo "🚀 Starting Rembg API server on port $PORT..."
echo "📝 API docs will be available at: /docs"
echo "🎯 Health check endpoint: /health"

# 使用 uvicorn 启动服务器
exec uvicorn api_server:app --host 0.0.0.0 --port $PORT --workers 1 