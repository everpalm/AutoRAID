FROM arm32v7/python:3

# 安装必要的 Python 库
RUN pip3 install RPi.GPIO

# 复制您的腳本 代码到容器中
COPY . /script
WORKDIR /script

# 安装必要的 Python 库，包括本地包
RUN pip install -e .
RUN pip install -r requirements.txt

# 设置 PYTHONPATH
ENV PYTHONPATH="/script:${PYTHONPATH}"

# 暴露 API 端口
EXPOSE 80

# 运行 API
CMD ["pytest"]