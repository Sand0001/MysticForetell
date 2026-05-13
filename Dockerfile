# 使用官方的轻量级 Python 镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量，防止 python 缓存和输出缓冲
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 将当前目录的所有文件复制到容器的 /app 目录下
COPY . .

# 暴露 FastAPI 运行的端口
EXPOSE 80

# 启动命令
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80"]
