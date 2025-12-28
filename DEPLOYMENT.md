# Deployment Guide

This guide explains how to deploy the YouTube Downloader to GitHub and Render.

## 📋 Prerequisites

- GitHub account
- Render account (free tier available)
- Git installed on your machine

---

## 🚀 Deployment to Render

### Step 1: Push to GitHub

1. **Initialize Git repository** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - YouTube Downloader"
   ```

2. **Create a new repository on GitHub**:
   - Go to https://github.com/new
   - Create a new repository (e.g., `yt-downloader`)
   - Don't initialize with README (we already have one)

3. **Push your code**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/yt-downloader.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy on Render

1. **Go to Render Dashboard**:
   - Visit https://render.com
   - Sign up/Login with GitHub

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your `yt-downloader` repository

3. **Configure Settings**:
   - **Name**: `yt-downloader` (or any name you prefer)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (or choose paid for better performance)

4. **Environment Variables** (Optional):
   - You can add environment variables if needed
   - For now, no variables are required

5. **Deploy**:
   - Click "Create Web Service"
   - Render will automatically build and deploy your app
   - Wait for deployment to complete (usually 2-5 minutes)

6. **Access Your App**:
   - Once deployed, you'll get a URL like: `https://yt-downloader.onrender.com`
   - Your app is now live! 🎉

### Render Configuration Files

The project includes:
- **Procfile**: Tells Render how to run your app
- **requirements.txt**: Lists all Python dependencies
- **runtime.txt**: Specifies Python version

---

## 📦 Project Structure

```
yt-downloader/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── Procfile              # Render deployment config
├── runtime.txt           # Python version for Render
├── .gitignore           # Git ignore rules
├── templates/           # HTML templates
│   └── index.html       # Frontend interface
├── downloads/           # Downloaded videos (gitignored)
├── run.bat              # Windows batch script
├── run.ps1              # PowerShell script
├── README.md            # Project documentation
└── DEPLOYMENT.md        # This file
```

---

## 🔧 Render Deployment Notes

### Important Points:

1. **Free Tier Limitations**:
   - Apps on free tier spin down after 15 minutes of inactivity
   - First request after spin-down may take 30-60 seconds
   - Consider upgrading to paid tier for always-on service

2. **Build Time**:
   - First deployment: 5-10 minutes
   - Subsequent deployments: 2-5 minutes

3. **File Storage**:
   - Downloads are stored in the `downloads/` folder
   - Files are ephemeral on free tier (may be deleted)
   - For persistent storage, consider using cloud storage (S3, etc.)

4. **Port Configuration**:
   - Render automatically sets the `PORT` environment variable
   - The app uses `os.environ.get("PORT", 8080)` to handle this

---

## 🐛 Troubleshooting

### Build Fails

- Check that `requirements.txt` has all dependencies
- Verify Python version in `runtime.txt` is supported
- Check Render build logs for specific errors

### App Crashes on Start

- Verify `Procfile` has correct command: `gunicorn app:app`
- Check that all imports in `app.py` are available
- Review Render logs for error messages

### Downloads Not Working

- Check Render logs for yt-dlp errors
- Verify YouTube URL format
- Some videos may be blocked by YouTube

---

## 🔄 Updating Your Deployment

1. **Make changes locally**
2. **Commit and push to GitHub**:
   ```bash
   git add .
   git commit -m "Your update message"
   git push
   ```
3. **Render automatically detects changes** and redeploys
4. **Wait for deployment to complete** (check Render dashboard)

---

## 📝 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/latest/deploying/)
- [Gunicorn Documentation](https://gunicorn.org/)

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Repository is public (for free Render tier) or connected via GitHub
- [ ] `Procfile` exists and is correct
- [ ] `requirements.txt` has all dependencies
- [ ] `runtime.txt` specifies Python version
- [ ] `.gitignore` excludes `venv/` and `downloads/`
- [ ] App builds successfully on Render
- [ ] App starts without errors
- [ ] Frontend loads correctly
- [ ] API endpoints respond correctly

---

**Need Help?** Check Render logs or create an issue on GitHub!

