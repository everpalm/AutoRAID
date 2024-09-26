FROM arm32v7/python:3

# 更新並安裝必要的系統工具和依賴
RUN apt-get update && apt-get install -y \
    python3-dev \
    build-essential \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    pkg-config \
    bash

# 安装 rustup 并设置环境变量
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y \
    && /root/.cargo/bin/rustup install 1.65.0 \
    && /root/.cargo/bin/rustup default 1.65.0 \
    && echo 'export PATH=$HOME/.cargo/bin:$PATH' >> /etc/profile

# 确保 PATH 包含 Cargo
ENV PATH="/root/.cargo/bin:${PATH}"

# 升级 pip、setuptools 和 wheel
RUN pip install --upgrade pip setuptools wheel

# 安装 Python 依赖
RUN pip install bcrypt==3.1.7 cryptography

# 設定工作目錄，並將腳本代碼複製進容器
WORKDIR /script
COPY requirements.txt /script/
RUN pip install --no-cache-dir -r requirements.txt

# Prior to execution
COPY . /script
RUN touch /script/logs/uart.log
# ENV PYTHONPATH="/script:${PYTHONPATH}"
ENV PYTHONPATH="/script"
EXPOSE 80
CMD ["pytest"]
