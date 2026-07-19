# .\venv\Scripts\Activate.ps1
# python app.py
# http://localhost:8080
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp
import os
import logging

# Path to the cookies.txt file exported from your browser
COOKIES_FILE = os.path.join(os.path.dirname(__file__), "cookies.txt")

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
        # Use android client to bypass JS challenge solving requirement
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": "downloads/%(title)s - %(id)s.%(ext)s",
        "noplaylist": True,
        "ignoreerrors": True,
        "quiet": False,
        "no_warnings": False,
        # Use exported cookies.txt to bypass YouTube bot detection
        **({"cookiefile": COOKIES_FILE} if os.path.exists(COOKIES_FILE) else {}),
        # Add delays between requests to avoid rate limiting
        "sleep_interval": 2,
        "max_sleep_interval": 5,
        # Ensure proper merging of video and audio
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4",
        }],
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


# ---------------- FETCH PLAYLIST INFO (no download) ----------------
@app.route("/fetch-playlist", methods=["POST"])
def fetch_playlist():
    """Returns the list of videos in a playlist without downloading them."""
    data = request.get_json() or {}
    url = data.get("url")

    if not url:
        return jsonify({"status": "error", "msg": "No URL provided"}), 400

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,          # Only fetch metadata, no download
        "ignoreerrors": True,
        **({"cookiefile": COOKIES_FILE} if os.path.exists(COOKIES_FILE) else {}),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            entries = info.get("entries", []) if info else []

            videos = []
            for i, entry in enumerate(entries):
                if not entry:
                    continue
                video_id = entry.get("id", "")
                videos.append({
                    "index": i + 1,
                    "title": entry.get("title", f"Video {i + 1}"),
                    "url": entry.get("url") or f"https://www.youtube.com/watch?v={video_id}",
                    "thumbnail": f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg" if video_id else "",
                    "duration": entry.get("duration_string") or str(entry.get("duration") or ""),
                })

        return jsonify({
            "status": "success",
            "playlist_title": info.get("title", "Playlist") if info else "Playlist",
            "videos": videos
        }), 200

    except Exception:
        logging.exception("Playlist fetch failed")
        return jsonify({
            "status": "error",
            "msg": "Could not fetch playlist. Check the URL or cookies."
        }), 200


# ---------------- DOWNLOAD SELECTED PLAYLIST VIDEOS ----------------
@app.route("/download-playlist", methods=["POST"])
def download_playlist():
    data = request.get_json() or {}
    video_urls = data.get("video_urls", [])   # list of selected video URLs
    playlist_name = data.get("playlist_name", "Playlist")

    if not video_urls:
        return jsonify({"status": "error", "msg": "No videos selected"}), 400

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": f"downloads/{playlist_name}/%(title)s.%(ext)s",
        "noplaylist": True,
        "ignoreerrors": True,
        "quiet": False,
        "no_warnings": False,
        **({"cookiefile": COOKIES_FILE} if os.path.exists(COOKIES_FILE) else {}),
        "sleep_interval": 2,
        "max_sleep_interval": 5,
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4",
        }],
    }

    downloaded = 0
    failed = 0

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for video_url in video_urls:
                try:
                    info = ydl.extract_info(video_url, download=True)
                    if info and info.get("formats"):
                        downloaded += 1
                    else:
                        failed += 1
                except Exception:
                    logging.exception(f"Failed to download: {video_url}")
                    failed += 1

        return jsonify({
            "status": "success",
            "msg": f"Downloaded {downloaded} video(s). {failed} failed/blocked."
        }), 200

    except Exception:
        logging.exception("Playlist download failed")
        return jsonify({
            "status": "error",
            "msg": "Download failed. Please try again."
        }), 200


@app.route("/", methods=["GET"])
def home():
    return send_from_directory(".", "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
