from flask import Flask, request, jsonify
import os
import yt_dlp
from pytubefix import Playlist, YouTube
from pytubefix.cli import on_progress

# Create downloads folder if not exists
os.makedirs("downloads", exist_ok=True)

app = Flask(__name__)

# ----------- Single Video Download -----------------
@app.route("/download-video", methods=["POST"])
def download_video():
    url = request.json.get("url")
    if not url:
        return jsonify({"status": "error", "msg": "No URL provided"}), 400

    ydl_opts = {
        "format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "merge_output_format": "mp4",
        "outtmpl": "downloads/final_1080p.%(ext)s",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return jsonify({"status": "success", "msg": "Video downloaded!"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500


# ----------- Playlist Download -----------------
@app.route("/download-playlist", methods=["POST"])
def download_playlist():
    url = request.json.get("url")
    if not url:
        return jsonify({"status": "error", "msg": "No URL provided"}), 400

    try:
        playlist = Playlist(url)
        for vid in playlist.video_urls:
            yt = YouTube(vid, on_progress_callback=on_progress)
            yt.streams.get_highest_resolution().download("downloads/")
        return jsonify({"status": "success", "msg": "Playlist downloaded!"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500


@app.route("/", methods=["GET"])
def home():
    return "✅ YouTube Downloader Backend Running!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
