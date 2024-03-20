from flask import Flask, request, send_from_directory, abort
import os
from itsdangerous import URLSafeTimedSerializer
from pytube import YouTube
from moviepy.editor import AudioFileClip

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'
app.config['DOWNLOAD_FOLDER'] = 'downloads' # 確保這個目錄存在且應用有讀寫權限
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

def download_video_as_mp3(youtube_url, destination_folder):
    video = YouTube(youtube_url)
    stream = video.streams.filter(only_audio=True).first()
    downloaded_file = stream.download(output_path=destination_folder)
    base, _ = os.path.splitext(downloaded_file)
    mp3_filename = os.path.basename(base) + ".mp3"
    mp3_filepath = os.path.join(destination_folder, mp3_filename)
    video_clip = AudioFileClip(downloaded_file)
    video_clip.write_audiofile(mp3_filepath)
    os.remove(downloaded_file) # 刪除原始下載的視頻檔案
    return mp3_filename

@app.route('/request_download', methods=['POST'])
def request_download():
    data = request.json
    youtube_url = data.get('url')
    if youtube_url:
        mp3_filename = download_video_as_mp3(youtube_url, app.config['DOWNLOAD_FOLDER'])
        token = serializer.dumps(mp3_filename, salt='file-download')
        return {'token': token}
    return abort(400)

@app.route('/download/<token>')
def download(token):
    try:
        filename = serializer.loads(token, salt='file-download', max_age=60*60) # 有效期1小時
        return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)
    except:
        return abort(404)

if __name__ == '__main__':
    app.run(debug=True, port=80)
