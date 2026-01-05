# 使用官方 Python 運行時作為父映像
FROM python:3.10-slim

# 設定工作目錄為 /app
WORKDIR /app

# moviepy 需要 ffmpeg 進行轉檔
RUN apt-get update \
  && apt-get install -y --no-install-recommends ffmpeg \
  && rm -rf /var/lib/apt/lists/*

# 將當前目錄內容複製到容器中的 /app
COPY . /app

# 安裝 pyproject.toml 中指定的依賴
RUN pip install --trusted-host pypi.python.org --no-cache-dir .

# 讓端口 80 可供此容器外的環境使用
EXPOSE 80

# 定義環境變量
ENV NAME World

# 運行 app.py 當容器啟動
CMD ["python", "app.py"]
