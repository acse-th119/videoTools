# 使用官方 Python 镜像
FROM python:3.12-slim
# FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.12.9-slim-linuxarm64

RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# 设置工作目录
WORKDIR /app

# 拷贝代码
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 7860

# 启动应用
CMD ["python", "mainui.py"]
