# 使用更稳定的 Python 版本
FROM arm32v7/python:3.10-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3-dev \
    build-essential \
    libffi-dev \
    libssl-dev \
    curl \
    pkg-config \
    iproute2 \
    && apt-get clean

# 安装 Rust 工具链，用于构建 cryptography
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y \
    && /root/.cargo/bin/rustup install 1.65.0 \
    && /root/.cargo/bin/rustup default 1.65.0 \
    && echo 'export PATH=$HOME/.cargo/bin:$PATH' >> /etc/profile

# 确保 PATH 包含 Cargo（Rust 工具链）
ENV PATH="/root/.cargo/bin:${PATH}"

# 升级 pip、setuptools 和 wheel
RUN pip install --upgrade pip setuptools wheel

# 安装兼容版本的 Python 包
RUN pip install --no-cache-dir \
    cffi==1.15.1 \
    cryptography==38.0.4 \
    paramiko

# 设置工作目录
WORKDIR /script

# 复制依赖文件和代码
COPY requirements.txt /script/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /script

# 创建日志目录
RUN mkdir -p /script/logs && touch /script/logs/uart.log

# 设置环境变量
ENV PYTHONPATH="/script"

# 暴露端口
EXPOSE 80

# 运行默认命令
CMD ["pytest"]
