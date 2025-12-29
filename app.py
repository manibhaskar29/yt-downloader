from flask import Flask, request, jsonify, render_template, send_file, Response
from flask_cors import CORS
import yt_dlp
import os
import logging
import traceback
import glob
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Create downloads folder
os.makedirs("downloads", exist_ok=True)

# Check if cookies file exists
COOKIES_FILE = "cookies.txt"
HAS_COOKIES = os.path.exists(COOKIES_FILE) and os.path.getsize(COOKIES_FILE) > 0
if HAS_COOKIES:
    logger.info(f"Cookies file found: {COOKIES_FILE}")
else:
    logger.warning(f"Cookies file not found. YouTube may block downloads. See README for instructions.")


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
        
        # Add cookies if available
        if HAS_COOKIES:
            ydl_opts["cookiefile"] = COOKIES_FILE
            logger.info("Using cookies file for authentication")

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

                # Get video title and ID for filename
                video_title = info.get("title", "video")
                video_id = info.get("id", "unknown")
                
                # Now download the video
                logger.info("Starting video download...")
                ydl.download([url])
                logger.info("Video download completed")

                # Find the downloaded file
                downloaded_file = None
                pattern = f"downloads/*{video_id}*"
                files = glob.glob(pattern)
                if files:
                    downloaded_file = files[0]
                    filename = os.path.basename(downloaded_file)
                    download_url = f"/download-file/{filename}"
                    logger.info(f"Video saved as: {filename}")
                    
                    return jsonify({
                        "status": "success",
                        "msg": "Video downloaded successfully!",
                        "download_url": download_url,
                        "filename": filename
                    }), 200
                else:
                    logger.warning("Downloaded file not found")
                    return jsonify({
                        "status": "error",
                        "msg": "Video download completed but file not found."
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
            elif "Sign in to confirm you're not a bot" in error_msg or "bot" in error_msg.lower():
                return jsonify({
                    "status": "error",
                    "msg": "YouTube is blocking the download. Please add cookies.txt file to bypass bot detection. See README for instructions."
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
        
        # Add cookies if available
        if HAS_COOKIES:
            ydl_opts["cookiefile"] = COOKIES_FILE
            logger.info("Using cookies file for authentication")

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

                # Get playlist name
                playlist_name = info.get("title", "playlist")
                
                # Download the entire playlist (yt-dlp handles it efficiently)
                logger.info("Starting playlist download...")
                ydl.download([url])
                logger.info("Playlist download process completed")
                
                # Find downloaded files
                playlist_dir = os.path.join("downloads", playlist_name)
                downloaded_files = []
                if os.path.exists(playlist_dir):
                    files = glob.glob(os.path.join(playlist_dir, "*"))
                    downloaded_files = [os.path.basename(f) for f in files if os.path.isfile(f)]
                
                # Note: With ignoreerrors=True, yt-dlp will skip failed videos automatically
                if downloaded_files:
                    return jsonify({
                        "status": "success",
                        "msg": f"Playlist download completed! {len(downloaded_files)} videos downloaded.",
                        "playlist_name": playlist_name,
                        "download_count": len(downloaded_files),
                        "download_url": f"/download-playlist-files/{playlist_name}"
                    }), 200
                else:
                    return jsonify({
                        "status": "error",
                        "msg": "No videos were downloaded. They may have been blocked by YouTube."
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
            elif "Sign in to confirm you're not a bot" in error_msg or "bot" in error_msg.lower():
                return jsonify({
                    "status": "error",
                    "msg": "YouTube is blocking the download. Please add cookies.txt file to bypass bot detection. See README for instructions."
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


@app.route("/download-file/<path:filename>", methods=["GET"])
def download_file(filename):
    """Serve downloaded video files"""
    try:
        # Security: prevent directory traversal
        safe_filename = os.path.basename(filename)
        # Try to find the file in downloads directory (could be in subdirectory for playlists)
        file_path = None
        
        # First try direct path
        direct_path = os.path.join("downloads", safe_filename)
        if os.path.exists(direct_path):
            file_path = direct_path
        else:
            # Search in subdirectories
            for root, dirs, files in os.walk("downloads"):
                if safe_filename in files:
                    file_path = os.path.join(root, safe_filename)
                    break
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({"status": "error", "msg": "File not found"}), 404
        
        # Determine MIME type based on extension
        ext = os.path.splitext(safe_filename)[1].lower()
        mime_types = {
            '.mp4': 'video/mp4',
            '.webm': 'video/webm',
            '.mkv': 'video/x-matroska',
            '.mp3': 'audio/mpeg',
            '.m4a': 'audio/mp4',
        }
        mime_type = mime_types.get(ext, 'application/octet-stream')
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=safe_filename,
            mimetype=mime_type
        )
    except Exception as e:
        logger.error(f"Error serving file: {str(e)}")
        return jsonify({"status": "error", "msg": "Error serving file"}), 500


@app.route("/list-files", methods=["GET"])
def list_files():
    """List all downloaded files"""
    try:
        files = []
        for file_path in glob.glob("downloads/**/*", recursive=True):
            if os.path.isfile(file_path):
                rel_path = os.path.relpath(file_path, "downloads")
                files.append({
                    "filename": os.path.basename(file_path),
                    "path": rel_path,
                    "size": os.path.getsize(file_path),
                    "download_url": f"/download-file/{os.path.basename(file_path)}"
                })
        return jsonify({
            "status": "success",
            "files": files,
            "count": len(files)
        }), 200
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({"status": "error", "msg": "Error listing files"}), 500


@app.route("/download-playlist-files/<playlist_name>", methods=["GET"])
def download_playlist_files(playlist_name):
    """List files in a playlist directory"""
    try:
        # Security: prevent directory traversal
        safe_playlist_name = os.path.basename(playlist_name)
        playlist_dir = os.path.join("downloads", safe_playlist_name)
        
        if not os.path.exists(playlist_dir):
            return jsonify({"status": "error", "msg": "Playlist directory not found"}), 404
        
        files = []
        for file_path in glob.glob(os.path.join(playlist_dir, "*")):
            if os.path.isfile(file_path):
                filename = os.path.basename(file_path)
                files.append({
                    "filename": filename,
                    "size": os.path.getsize(file_path),
                    "download_url": f"/download-file/{filename}"
                })
        
        return jsonify({
            "status": "success",
            "playlist_name": safe_playlist_name,
            "files": files,
            "count": len(files)
        }), 200
    except Exception as e:
        logger.error(f"Error listing playlist files: {str(e)}")
        return jsonify({"status": "error", "msg": "Error listing playlist files"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
