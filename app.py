from flask import Flask, request, jsonify
import yt_dlp
from flask_cors import CORS  # <-- add this

app = Flask(__name__)
CORS(app)  # <-- enable CORS for all routes

# --- Helper Function ---
def download_youtube(url, is_playlist=False):
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": "%(title)s.%(ext)s",
        "noplaylist": not is_playlist,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return {"status": "success", "title": info.get("title", "Unknown")}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- Routes ---
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "YouTube Downloader API is running 🚀"})

@app.route("/download-video", methods=["POST"])
def download_video():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400
    result = download_youtube(url, is_playlist=False)
    return jsonify(result)

@app.route("/download-playlist", methods=["POST"])
def download_playlist():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400
    result = download_youtube(url, is_playlist=True)
    return jsonify(result)

# --- Render needs this ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
