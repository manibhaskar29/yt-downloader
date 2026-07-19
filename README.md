# YouTube Downloader

A full-stack web application that enables users to download YouTube videos and playlists in the highest available quality (up to 4K). Built with a Flask backend API and vanilla JavaScript frontend, featuring automatic video-audio stream merging and a responsive UI.

## 🚀 Live Demo

Visit the application and start downloading videos instantly!

## 📌 Project Overview

This YouTube downloader application provides a simple, user-friendly interface for downloading YouTube content while ensuring the highest possible video quality. The backend leverages **yt-dlp** (a modern YouTube downloader library) with FFmpeg integration to merge the best available video and audio streams into a single MP4 file.

### Key Features

- ✅ **High-Quality Downloads** - Downloads videos in the highest available quality (4K/1080p/720p)
- ✅ **Playlist Support** - Download entire playlists with a single click
- ✅ **Smart Stream Merging** - Automatically combines best video + audio using FFmpeg
- ✅ **RESTful API** - Clean Flask API with proper error handling and CORS support
- ✅ **Responsive UI** - Modern, mobile-friendly interface
- ✅ **Download Progress** - Real-time feedback and error messages

## 🛠️ Tech Stack

**Backend:**
- Python 3.7+
- Flask (Web Framework)
- yt-dlp (YouTube Downloader)
- Flask-CORS (Cross-Origin Resource Sharing)
- FFmpeg (Media Processing)

**Frontend:**
- HTML5
- CSS3
- Vanilla JavaScript (Fetch API)

## 📂 Project Structure

```
yt-downloader/
├── app.py              # Flask backend API
├── index.html          # Frontend interface
├── requirements.txt    # Python dependencies
├── Procfile           # Deployment configuration
├── run.bat            # Windows batch script
├── run.ps1            # PowerShell script
└── downloads/         # Downloaded videos (auto-created)
```

## ⚙️ Installation & Setup

### Prerequisites

1. **Python 3.7+** - [Download here](https://www.python.org/downloads/)
2. **FFmpeg** - Required for high-quality downloads
   - Windows: `winget install ffmpeg` or [download manually](https://ffmpeg.org/download.html)
   - Mac: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd yt-downloader-working
   ```

2. **Create & activate virtual environment**
   
   Windows (PowerShell):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   
   macOS/Linux:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the app**
   
   Open your browser and navigate to:
   ```
   http://localhost:8080
   ```

## 🎯 Usage

1. Open the application in your browser
2. Paste a YouTube video or playlist URL into the input field
3. Click **"Download Video"** or **"Download Playlist"**
4. Wait for the download to complete
5. Find your videos in the `downloads/` folder

## 🔧 API Endpoints

### POST `/download-video`
Downloads a single YouTube video in highest quality.

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Response:**
```json
{
  "status": "success",
  "msg": "Video downloaded successfully"
}
```

### POST `/download-playlist`
Downloads all videos from a YouTube playlist.

**Request Body:**
```json
{
  "url": "https://www.youtube.com/playlist?list=PLAYLIST_ID"
}
```

**Response:**
```json
{
  "status": "success",
  "msg": "Downloaded 12 videos"
}
```

## 💡 How It Works

1. **Frontend** sends a POST request with the YouTube URL to the Flask API
2. **Backend** uses yt-dlp to fetch video metadata and available formats
3. **Format Selection** prioritizes `bestvideo+bestaudio` for maximum quality
4. **FFmpeg** merges the separate video and audio streams into a single MP4 file
5. **Download** saves the final video to the `downloads/` folder
6. **Response** returns success/error status to the frontend

## 🎨 Features Breakdown

### Smart Format Selection
The application uses the format string `bestvideo+bestaudio/best`:
- Downloads the highest quality video stream (up to 8K if available)
- Downloads the highest quality audio stream separately
- Merges them using FFmpeg into a single file
- Falls back to best single-file format if needed

### Error Handling
- Invalid URLs
- Age-restricted content
- Region-locked videos
- Network failures
- FFmpeg merge errors


## 📝 License

This project is for educational purposes. Please respect YouTube's Terms of Service and copyright laws.

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your Profile](https://linkedin.com/in/yourprofile)

---

**Note:** This project demonstrates full-stack development skills including REST API design, asynchronous operations, external library integration, and responsive web design.
