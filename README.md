# yt_download（CI/CD 學習範例）

這個 repo 用一個簡單的 Flask 服務示範 CI/CD：

- CI：跑 `ruff` + `pytest`
- CD：build/push Docker image，並用 SSH 在伺服器更新容器
- 下載/轉檔：用 `yt-dlp` + `ffmpeg` 抽取音訊輸出 mp3

## Dev / Prod 怎麼切換（Docker Compose profiles）

本機開發（dev，會掛載原始碼，port 在 `8080`）：

```bash
docker compose --profile dev up --build
curl http://localhost:8080/healthz
```

正式執行（prod，使用 gunicorn，port 在 `80`，拉遠端 image）：

```bash
IMAGE_TAG=latest docker compose -f compose.prod.yml up -d
curl http://localhost/healthz
```

部署時（GitHub Actions）會用 `compose.prod.yml`，並設定 `IMAGE_TAG=sha-<commit>` 來拉取對應版本的 image（不依賴 `latest`）。如果 server 沒有 `docker compose`（v2 plugin），也會自動改用 `docker-compose`（v1）。

停止：

```bash
docker compose down
```

## 用 uv 管依賴（lock + sync）

更新 lock（依賴有變動時）：

```bash
uv lock
```

安裝（開發含測試工具）：

```bash
uv sync --extra dev
```

模擬 CI（不允許動 lock）：

```bash
uv sync --frozen --extra dev
```
