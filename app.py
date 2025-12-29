from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import yt_dlp
import os
import logging
import traceback

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Create downloads folder
os.makedirs("downloads", exist_ok=True)


# ---------------- SINGLE VIDEO ----------------
@app.route("/download-video", methods=["POST"])
def download_video():
    try:
        data = request.get_json() or {}
        url = data.get("url")

        if not url:
            return jsonify({"status": "error", "msg": "No URL provided"}), 400

        logger.info(f"Download request received for video: {url}")

        ydl_opts = {
            "format": "best[height<=720]/best/bestvideo+bestaudio",
            "merge_output_format": "mp4",
            "outtmpl": "downloads/%(title)s - %(id)s.%(ext)s",
            "noplaylist": True,
            "ignoreerrors": True,
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "socket_timeout": 30,
            "retries": 3,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # First extract info without downloading to check if video is accessible
                logger.info("Extracting video information...")
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    logger.warning("No video information extracted")
                    return jsonify({
                        "status": "error",
                        "msg": "Could not access video. It may be private, deleted, or restricted."
                    }), 200

                # Check if video has formats
                formats = info.get("formats", [])
                if not formats:
                    logger.warning("Video has no available formats")
                    return jsonify({
                        "status": "error",
                        "msg": "This video cannot be downloaded due to YouTube restrictions"
                    }), 200

                # Now download the video
                logger.info("Starting video download...")
                ydl.download([url])
                logger.info("Video download completed")

                return jsonify({
                    "status": "success",
                    "msg": "Video downloaded successfully!"
                }), 200

        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            logger.error(f"yt-dlp download error: {error_msg}")
            
            if "Private video" in error_msg or "private" in error_msg.lower():
                return jsonify({
                    "status": "error",
                    "msg": "This video is private and cannot be downloaded."
                }), 200
            elif "Video unavailable" in error_msg or "unavailable" in error_msg.lower():
                return jsonify({
                    "status": "error",
                    "msg": "Video is unavailable. It may have been deleted or restricted."
                }), 200
            elif "Sign in to confirm your age" in error_msg or "age" in error_msg.lower():
                return jsonify({
                    "status": "error",
                    "msg": "This video requires age verification and cannot be downloaded."
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "msg": f"Download failed: {error_msg[:100]}"
                }), 200

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Unexpected error during video download: {error_msg}")
            logger.error(traceback.format_exc())
            
            # Check for timeout
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                return jsonify({
                    "status": "error",
                    "msg": "Request timed out. The video may be too large or the server is slow. Please try again."
                }), 200
            
            return jsonify({
                "status": "error",
                "msg": "An error occurred while downloading. Please check the URL and try again."
            }), 200

    except Exception as e:
        logger.error(f"Fatal error in download_video endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "msg": "Server error. Please try again later."
        }), 500


# ---------------- PLAYLIST ----------------
@app.route("/download-playlist", methods=["POST"])
def download_playlist():
    try:
        data = request.get_json() or {}
        url = data.get("url")

        if not url:
            return jsonify({"status": "error", "msg": "No URL provided"}), 400

        logger.info(f"Download request received for playlist: {url}")

        ydl_opts = {
            "format": "best[height<=720]/best/bestvideo+bestaudio",
            "merge_output_format": "mp4",
            "outtmpl": "downloads/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s",
            "ignoreerrors": True,
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "socket_timeout": 30,
            "retries": 3,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info("Extracting playlist information...")
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    logger.warning("No playlist information extracted")
                    return jsonify({
                        "status": "error",
                        "msg": "Could not access playlist. It may be private or unavailable."
                    }), 200

                entries = info.get("entries", [])
                total = len(entries)
                logger.info(f"Playlist has {total} videos")

                if total == 0:
                    return jsonify({
                        "status": "error",
                        "msg": "Playlist is empty or cannot be accessed."
                    }), 200

                # Download the entire playlist (yt-dlp handles it efficiently)
                logger.info("Starting playlist download...")
                ydl.download([url])
                logger.info("Playlist download process completed")
                
                # Note: With ignoreerrors=True, yt-dlp will skip failed videos automatically
                # We return success if the process completed without crashing
                return jsonify({
                    "status": "success",
                    "msg": f"Playlist download completed. Some videos may have been skipped due to restrictions."
                }), 200

        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            logger.error(f"yt-dlp playlist error: {error_msg}")
            
            if "Private" in error_msg or "private" in error_msg.lower():
                return jsonify({
                    "status": "error",
                    "msg": "This playlist is private and cannot be downloaded."
                }), 200
            elif "unavailable" in error_msg.lower():
                return jsonify({
                    "status": "error",
                    "msg": "Playlist is unavailable or cannot be accessed."
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "msg": f"Playlist download failed: {error_msg[:100]}"
                }), 200

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Unexpected error during playlist download: {error_msg}")
            logger.error(traceback.format_exc())
            
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                return jsonify({
                    "status": "error",
                    "msg": "Request timed out. The playlist may be too large. Please try downloading individual videos."
                }), 200
            
            return jsonify({
                "status": "error",
                "msg": "An error occurred while downloading the playlist. Please check the URL and try again."
            }), 200

    except Exception as e:
        logger.error(f"Fatal error in download_playlist endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "msg": "Server error. Please try again later."
        }), 500


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint for Render"""
    return jsonify({
        "status": "healthy",
        "service": "YouTube Downloader"
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
