import os
from flask import Flask, request, jsonify
import yt_dlp
from flask_cors import CORS

# --- Initialize Flask App ---
# Fix: Corrected the name to "_name_"
app = Flask(_name_)
CORS(app)

# --- Folder to save downloaded videos ---
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# --- Helper Function to download content ---
def download_youtube(url, is_playlist=False):
    # Fix: Securely retrieve credentials from environment variables
    youtube_username = os.environ.get('YOUTUBE_USERNAME')
    youtube_password = os.environ.get('YOUTUBE_PASSWORD')
    
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s"),
        "noplaylist": not is_playlist,
        'username': youtube_username,
        'password': youtube_password,
        'no_warnings': True,
        'ignoreerrors': True,
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
    
    # Fix: Added a check for invalid or missing JSON data
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid or missing JSON body"}), 400
        
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    result = download_youtube(url, is_playlist=False)
    return jsonify(result)

@app.route("/download-playlist", methods=["POST"])
def download_playlist():
    data = request.get_json()
    
    # Fix: Added a check for invalid or missing JSON data
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    url = data.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    result = download_youtube(url, is_playlist=True)
    return jsonify(result)

# --- Render needs this dynamic port ---
if _name_ == "_main_":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
