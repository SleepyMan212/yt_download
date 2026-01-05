# 使用官方 Python 運行時作為父映像
FROM python:3.10-slim

# 設定工作目錄為 /app
WORKDIR /app

# yt-dlp 需要 ffmpeg 進行音訊抽取/轉檔
RUN apt-get update \
  && apt-get install -y --no-install-recommends ffmpeg \
  && rm -rf /var/lib/apt/lists/*

# 將當前目錄內容複製到容器中的 /app
COPY . /app

# 安裝 pyproject.toml 中指定的依賴
RUN pip install --trusted-host pypi.python.org --no-cache-dir .

# 讓端口 80 可供此容器外的環境使用
EXPOSE 80

# Production: 用 gunicorn 跑 Flask app（不要用 Flask 內建開發伺服器）
ENV PORT=80
CMD ["sh", "-c", "exec gunicorn -b 0.0.0.0:${PORT} app:app"]
