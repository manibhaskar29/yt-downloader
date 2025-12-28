# YouTube Downloader

A simple YouTube video and playlist downloader with a modern web interface.

## Setup Instructions

### 1. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
# Create virtual environment (if not already created)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 2. Install Dependencies

Once the virtual environment is activated, install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Run the Application

**Option 1: Run Backend Only (Frontend served by Flask)**
```bash
python app.py
```

The application will be available at:
- **Frontend:** http://localhost:8080
- **Backend API:** http://localhost:8080/download-video and http://localhost:8080/download-playlist

**Option 2: Run Backend and Frontend Separately**

If you want to run them separately (for development):

1. **Terminal 1 - Backend:**
   ```bash
   python app.py
   ```

2. **Terminal 2 - Frontend (Simple HTTP Server):**
   ```bash
   # Python 3
   python -m http.server 3000
   
   # Or using Python 2
   python -m SimpleHTTPServer 3000
   ```
   
   Then open http://localhost:3000 in your browser.

   **Note:** If running separately, you may need to update the API endpoints in `templates/index.html` to match your backend URL.

## Project Structure

```
yt-downloader/
├── app.py                 # Flask backend server
├── requirements.txt       # Python dependencies
├── Procfile              # Render deployment config
├── runtime.txt           # Python version for Render
├── .gitignore           # Git ignore rules
├── templates/           # HTML templates
│   └── index.html       # Frontend web interface
├── downloads/           # Downloaded videos (gitignored)
├── run.bat              # Windows batch script
├── run.ps1              # PowerShell script
├── README.md            # This file
└── DEPLOYMENT.md        # Deployment guide
```

## Features

- ✅ Download single YouTube videos
- ✅ Download entire playlists
- ✅ Modern, responsive web interface
- ✅ CORS enabled for cross-origin requests

## Dependencies

- Flask - Web framework
- flask-cors - CORS support
- yt-dlp - YouTube downloader
- pytubefix - Alternative YouTube downloader
- gunicorn - Production WSGI server (optional)

## Troubleshooting

### Virtual Environment Issues

If you get an error about scripts not being executable:
- **Windows:** Make sure you're using PowerShell or Command Prompt
- **Linux/Mac:** Run `chmod +x venv/bin/activate`

### Port Already in Use

If port 8080 is already in use, you can change it in `app.py`:
```python
app.run(host="0.0.0.0", port=8080)  # Change 8080 to another port
```

### Dependencies Not Installing

Make sure your virtual environment is activated before running `pip install -r requirements.txt`.

## Usage

1. Start the server: `python app.py`
2. Open your browser and go to: http://localhost:8080
3. Paste a YouTube video or playlist URL
4. Click download
5. Videos will be saved in the `downloads/` folder

## 🚀 Deployment

### Deploy to Render

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

**Quick Steps:**
1. Push your code to GitHub
2. Connect repository to Render
3. Render will automatically detect and deploy your Flask app
4. Your app will be live at `https://your-app.onrender.com`

### Deploy to GitHub

1. Initialize git: `git init`
2. Add files: `git add .`
3. Commit: `git commit -m "Initial commit"`
4. Push to GitHub: `git push origin main`

**Note:** Make sure to exclude `venv/` and `downloads/` folders (already in `.gitignore`)

