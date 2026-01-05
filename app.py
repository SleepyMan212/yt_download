from flask import Flask, request, send_from_directory, abort
import os
import subprocess
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'
app.config['DOWNLOAD_FOLDER'] = 'downloads' # 確保這個目錄存在且應用有讀寫權限
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

def ensure_download_folder():
    os.makedirs(app.config["DOWNLOAD_FOLDER"], exist_ok=True)

def normalize_youtube_url(url: str) -> str:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()

    video_id = None

    if host in {"youtu.be"}:
        candidate = parsed.path.lstrip("/").split("/", 1)[0]
        video_id = candidate or None
    elif host.endswith("youtube.com"):
        if parsed.path == "/watch":
            query = parse_qs(parsed.query)
            values = query.get("v") or []
            video_id = values[0] if values else None
        elif parsed.path.startswith("/shorts/"):
            candidate = parsed.path.split("/", 3)[2]
            video_id = candidate or None

    if not video_id:
        return url

    return f"https://www.youtube.com/watch?v={video_id}"

def download_video_as_mp3(youtube_url, destination_folder):
    youtube_url = normalize_youtube_url(youtube_url)
    destination = Path(destination_folder)
    destination.mkdir(parents=True, exist_ok=True)

    output_template = str(destination / "%(id)s.%(ext)s")

    cmd = [
        "yt-dlp",
        "--no-playlist",
        "-x",
        "--audio-format",
        "mp3",
        "-o",
        output_template,
        youtube_url,
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "yt-dlp failed")

    mp3_files = sorted(destination.glob("*.mp3"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not mp3_files:
        raise RuntimeError("yt-dlp succeeded but no mp3 produced")

    return mp3_files[0].name

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.route('/request_download', methods=['POST'])
def request_download():
    data = request.get_json(silent=True) or {}
    youtube_url = data.get("url")
    if not youtube_url:
        return abort(400)

    ensure_download_folder()
    try:
        mp3_filename = download_video_as_mp3(youtube_url, app.config["DOWNLOAD_FOLDER"])
    except Exception as exc:
        app.logger.exception("download failed")
        return {"error": "download failed", "detail": str(exc)}, 500

    token = serializer.dumps(mp3_filename, salt="file-download")
    return {"token": token}

@app.route('/download/<token>')
def download(token):
    try:
        filename = serializer.loads(token, salt='file-download', max_age=60*60) # 有效期1小時
        return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)
    except Exception:
        return abort(404)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", "80"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug,
    )
