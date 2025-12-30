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
            "format": "best/bestvideo+bestaudio",
            "merge_output_format": "mp4",
            "outtmpl": "downloads/%(title)s - %(id)s.%(ext)s",
            "noplaylist": True,
            "ignoreerrors": True,
            "quiet": False,
            "no_warnings": False,
        }
        
        # Add cookies if available
        if HAS_COOKIES:
            ydl_opts["cookiefile"] = COOKIES_FILE
            logger.info("Using cookies file for authentication")
        
        # Additional options to help bypass detection on cloud hosting
        # Note: These might help but can also interfere - test without if issues persist
        ydl_opts.update({
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Download directly (matching localhost behavior exactly)
                logger.info("Starting video download...")
                info = ydl.extract_info(url, download=True)

                # Check if download actually succeeded by looking for the file
                # This handles cases where info might not have formats but file was downloaded
                video_id = None
                if info:
                    video_id = info.get("id")
                
                # Try to find downloaded file by video ID
                downloaded_file = None
                if video_id:
                    pattern = f"downloads/*{video_id}*"
                    files = glob.glob(pattern)
                    if files:
                        downloaded_file = files[0]
                
                # If file exists, download succeeded regardless of info formats
                if downloaded_file:
                    filename = os.path.basename(downloaded_file)
                    download_url = f"/download-file/{filename}"
                    logger.info(f"Video saved as: {filename}")
                    
                    return jsonify({
                        "status": "success",
                        "msg": "Video downloaded successfully!",
                        "download_url": download_url,
                        "filename": filename
                    }), 200

                # If no file found, check if YouTube blocked formats
                if not info or not info.get("formats"):
                    return jsonify({
                        "status": "error",
                        "msg": "This video cannot be downloaded due to YouTube restrictions"
                    }), 200

                # Fallback - download might have succeeded but file not found yet
                return jsonify({
                    "status": "success",
                    "msg": "Video downloaded successfully (if allowed by YouTube)"
                }), 200

        except Exception as e:
            # Match localhost error handling exactly
            logger.exception("Video download failed")
            return jsonify({
                "status": "error",
                "msg": "YouTube blocked this video"
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
            "format": "best/bestvideo+bestaudio",
            "merge_output_format": "mp4",
            "outtmpl": "downloads/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s",
            "ignoreerrors": True,
            "quiet": False,
            "no_warnings": False,
        }
        
        # Add cookies if available
        if HAS_COOKIES:
            ydl_opts["cookiefile"] = COOKIES_FILE
            logger.info("Using cookies file for authentication")
        
        # Additional options to help bypass detection on cloud hosting
        ydl_opts.update({
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        })

        downloaded = 0

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Download directly (matching localhost behavior)
                logger.info("Starting playlist download...")
                info = ydl.extract_info(url, download=True)
                entries = info.get("entries", [])

                for e in entries:
                    if e and e.get("formats"):
                        downloaded += 1

                logger.info(f"Playlist download completed: {downloaded} videos")

                return jsonify({
                    "status": "success",
                    "msg": f"Downloaded {downloaded} videos (others blocked by YouTube)"
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


@app.route("/downloads", methods=["GET"])
def downloads_page():
    """Page to view all downloaded files"""
    try:
        files = []
        playlists = {}
        
        # Get all files
        for file_path in glob.glob("downloads/**/*", recursive=True):
            if os.path.isfile(file_path):
                rel_path = os.path.relpath(file_path, "downloads")
                file_info = {
                    "filename": os.path.basename(file_path),
                    "path": rel_path,
                    "size": os.path.getsize(file_path),
                    "size_mb": round(os.path.getsize(file_path) / (1024 * 1024), 2),
                    "download_url": f"/download-file/{os.path.basename(file_path)}"
                }
                
                # Check if it's in a playlist folder
                if os.path.sep in rel_path:
                    playlist_name = rel_path.split(os.path.sep)[0]
                    if playlist_name not in playlists:
                        playlists[playlist_name] = []
                    playlists[playlist_name].append(file_info)
                else:
                    files.append(file_info)
        
        # Render a simple HTML page
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Downloads - YouTube Downloader</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #ff0000; }}
                .file-item {{ padding: 10px; margin: 5px 0; background: #f5f5f5; border-radius: 5px; }}
                .download-btn {{ background: #ff0000; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; display: inline-block; margin-top: 5px; }}
                .download-btn:hover {{ background: #cc0000; }}
                .playlist-section {{ margin: 20px 0; }}
                .empty {{ color: #666; font-style: italic; }}
            </style>
        </head>
        <body>
            <h1>📥 Your Downloads</h1>
            <p><a href="/">← Back to Home</a></p>
            
            <h2>Single Videos ({len(files)})</h2>
            {"".join([f'<div class="file-item"><strong>{f["filename"]}</strong> ({f["size_mb"]} MB)<br><a href="{f["download_url"]}" class="download-btn">Download</a></div>' for f in files]) if files else '<p class="empty">No single videos downloaded yet.</p>'}
            
            {f'<h2>Playlists</h2>' + "".join([f'<div class="playlist-section"><h3>{name} ({len(pl_files)} files)</h3>' + "".join([f'<div class="file-item"><strong>{f["filename"]}</strong> ({f["size_mb"]} MB)<br><a href="{f["download_url"]}" class="download-btn">Download</a></div>' for f in pl_files]) + '</div>' for name, pl_files in playlists.items()]) if playlists else ''}
            
            {f'<p class="empty">No downloads found. Try downloading a video first!</p>' if not files and not playlists else ''}
        </body>
        </html>
        """
        return html, 200
    except Exception as e:
        logger.error(f"Error rendering downloads page: {str(e)}")
        return f"<h1>Error</h1><p>Error loading downloads: {str(e)}</p><a href='/'>Back to Home</a>", 500


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
