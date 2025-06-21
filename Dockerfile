FROM python:3.10-slim

WORKDIR /rembg

RUN pip install --upgrade pip

RUN apt-get update && apt-get install -y curl && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

RUN python -m pip install ".[cpu,cli]"
RUN rembg d u2net

# 安装 API 依赖
RUN pip install fastapi uvicorn[standard] python-multipart pillow

# 暴露端口 (Render 会自动设置 PORT 环境变量)
EXPOSE $PORT

# 启动 API 服务器 (使用 shell 形式确保环境变量正确传递)
CMD python api_server.py
