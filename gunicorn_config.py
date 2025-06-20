import os

# 绑定地址和端口
bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"

# 工作进程数
workers = 1  # 由于 AI 模型内存占用大，建议使用单个 worker

# 工作进程类
worker_class = "uvicorn.workers.UvicornWorker"

# 超时设置
timeout = 120  # 2分钟超时，因为图像处理可能需要时间

# 日志设置
accesslog = "-"
errorlog = "-"
loglevel = "info"

# 应用模块
module = "api_server:app" 