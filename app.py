from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import yt_dlp
import os
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

# Create downloads folder
os.makedirs("downloads", exist_ok=True)


# ---------------- SINGLE VIDEO ----------------
@app.route("/download-video", methods=["POST"])
def download_video():
    data = request.get_json() or {}
    url = data.get("url")

    if not url:
        return jsonify({"status": "error", "msg": "No URL provided"}), 400

    ydl_opts = {
        "format": "best/bestvideo+bestaudio",
        "merge_output_format": "mp4",
        "outtmpl": "downloads/%(title)s - %(id)s.%(ext)s",
        "noplaylist": True,
        "ignoreerrors": True,
        "quiet": False,
        "no_warnings": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            # If YouTube blocks formats
            if not info or not info.get("formats"):
                return jsonify({
                    "status": "error",
                    "msg": "This video cannot be downloaded due to YouTube restrictions"
                }), 200

            return jsonify({
                "status": "success",
                "msg": "Video downloaded successfully (if allowed by YouTube)"
            }), 200

    except Exception as e:
        logging.exception("Video download failed")
        return jsonify({
            "status": "error",
            "msg": "YouTube blocked this video"
        }), 200


# ---------------- PLAYLIST ----------------
@app.route("/download-playlist", methods=["POST"])
def download_playlist():
    data = request.get_json() or {}
    url = data.get("url")

    if not url:
        return jsonify({"status": "error", "msg": "No URL provided"}), 400

    ydl_opts = {
        "format": "best/bestvideo+bestaudio",
        "merge_output_format": "mp4",
        "outtmpl": "downloads/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s",
        "ignoreerrors": True,
        "quiet": False,
        "no_warnings": False,
    }

    downloaded = 0

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            entries = info.get("entries", [])

            for e in entries:
                if e and e.get("formats"):
                    downloaded += 1

        return jsonify({
            "status": "success",
            "msg": f"Downloaded {downloaded} videos (others blocked by YouTube)"
        }), 200

    except Exception:
        logging.exception("Playlist download failed")
        return jsonify({
            "status": "error",
            "msg": "Playlist blocked by YouTube"
        }), 200


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
