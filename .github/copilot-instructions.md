# AI Agent Instructions - YouTube Downloader

## Project Overview
A Flask-based web application for downloading YouTube videos and playlists. Frontend (HTML/CSS/JS) communicates with Python backend via REST API.

### Tech Stack
- **Backend**: Flask (Python), yt-dlp (video downloader), CORS-enabled
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Deployment**: Gunicorn + Heroku (Procfile present)
- **Dependencies**: See [requirements.txt](requirements.txt)

## Architecture

### Two-Endpoint Design
- `POST /download-video`: Downloads single video to `downloads/` directory with format `{title} - {id}.mp4`
- `POST /download-playlist`: Downloads playlist to `downloads/{playlist_name}/` with numbered structure

**Key Pattern**: Both endpoints accept JSON `{"url": "..."}`, return consistent JSON responses with `{"status": "success"/"error", "msg": "..."}`.

### Data Flow
1. Frontend captures URL → calls Flask API
2. Flask uses yt-dlp to extract metadata and download
3. Files saved locally to `downloads/` hierarchy
4. Frontend receives status response (not file path)

### YouTube Restrictions Handling
- **Design philosophy**: Graceful degradation. When YouTube blocks formats/videos, don't error - return partial success
- Response type is always HTTP 200 (not error codes) with status field in JSON
- Playlist downloads report count of successfully downloaded videos: `f"Downloaded {downloaded} videos (others blocked)"`
- Single video shows message: `"Video downloaded successfully (if allowed by YouTube)"`

## Developer Workflows

### Local Setup
```bash
pip install -r requirements.txt
python app.py  # Runs on localhost:5000
```

### Testing Frontend
- Open `index.html` in browser (or serve via Flask's static route)
- Paste YouTube URL into form
- Check `downloads/` folder for output files

### Deployment
- Procfile specifies command: `gunicorn main:app` (note: expects `main.py`, not `app.py` - might be outdated config)
- Deployed to Heroku (based on Procfile presence)

## Critical Conventions & Gotchas

### yt-dlp Configuration
```python
ydl_opts = {
    "format": "best/bestvideo+bestaudio",  # Prefer merged format
    "merge_output_format": "mp4",           # Always output MP4
    "ignoreerrors": True,                   # Don't crash on individual video failures
    "quiet": False,                         # Log operations
}
```
**Pattern**: These options are duplicated in both endpoints - **maintain consistency across both**. Changes to one should reflect in the other.

### File Paths & Templates
- Single video: `downloads/%(title)s - %(id)s.%(ext)s`
- Playlist: `downloads/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s`

Filenames derived from YouTube metadata. Invalid characters handled by yt-dlp internally.

### Error Handling Specifics
- `logging.exception()` used to log full tracebacks before returning generic error responses
- No exception propagation to user (caught and logged)
- Broad Exception catching (not specific) - intentional for catching YouTube API errors, network issues, etc.

## Integration Points

### Frontend-Backend Communication
- API base URL used in JavaScript (check `index.html` for fetch calls) - likely `localhost:5000` or environment-dependent
- CORS enabled globally via `CORS(app)` - any origin allowed
- JSON request/response format mandatory

### External Dependency: yt-dlp
- Community-maintained fork of youtube-dl
- Requires periodic updates as YouTube changes (not version-pinned in requirements.txt)
- May fail silently if outdated - update yt-dlp first when debugging download failures

## Important Files
- [app.py](app.py): All backend logic (two routes)
- [index.html](index.html): Full frontend (HTML/CSS/JS mixed)
- [requirements.txt](requirements.txt): Dependencies
- [Procfile](Procfile): Deployment config
- `downloads/`: Output directory (created on first run)

## Common Maintenance Scenarios

**Adding new download format?**
- Modify `ydl_opts["format"]` in both endpoints
- Test with single video first, then playlist

**Changing file naming?**
- Update `outtmpl` in both endpoints simultaneously
- Test file path generation with special characters

**Debugging YouTube restrictions?**
- Check recent yt-dlp issues (may require version bump)
- Add custom headers/cookies in yt-dlp config if needed
- `cookies.txt` present in repo - consider implementing cookie-based auth if needed

---

**Last Updated**: December 2025 | **Project Maturity**: Early-stage/learner project (GFG.java suggests educational context)
