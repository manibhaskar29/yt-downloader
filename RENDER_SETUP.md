# Render Deployment Setup Guide

## Issue: Repository Not Showing in Render

If your `yt-downloader` repository is not showing in Render's repository list, follow these steps:

### Option 1: Use Public Git Repository (Recommended)

1. In Render dashboard, click **"New Web Service"**
2. Select **"Public Git Repository"** (instead of connecting via Git Provider)
3. Enter your repository URL:
   ```
   https://github.com/manibhaskar29/yt-downloader
   ```
4. Click **"Continue"**
5. Fill in the deployment settings (see below)

### Option 2: Make Repository Public

1. Go to: https://github.com/manibhaskar29/yt-downloader/settings
2. Scroll down to **"Danger Zone"**
3. Click **"Change repository visibility"**
4. Select **"Make public"**
5. Confirm the change
6. Go back to Render and refresh - your repo should appear

### Option 3: Reconnect GitHub Account

1. In Render dashboard, go to **Account Settings**
2. Click **"Connected Accounts"** or **"Git Providers"**
3. Disconnect and reconnect your GitHub account
4. Make sure to grant access to all repositories
5. Refresh the page

---

## Render Deployment Settings

Once your repository is connected, use these settings:

### Basic Settings:
- **Name**: `yt-downloader` (or any name you prefer)
- **Region**: `Oregon (US West)` (or your preferred region)
- **Branch**: `main`
- **Root Directory**: (leave empty)

### Build & Start Commands:
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```
  
- **Start Command**: 
  ```bash
  gunicorn app:app
  ```

### Instance Type:
- **Free**: For testing (spins down after 15 min inactivity)
- **Starter ($7/month)**: For always-on service

### Environment Variables:
No environment variables needed for basic setup.

### Advanced Settings:
- **Auto-Deploy**: `Yes` (automatically deploys on git push)
- **Health Check Path**: `/` (optional)

---

## After Deployment

1. Wait for build to complete (2-5 minutes)
2. Your app will be available at: `https://yt-downloader.onrender.com`
3. Test the endpoints:
   - Frontend: `https://yt-downloader.onrender.com/`
   - API: `https://yt-downloader.onrender.com/download-video`

---

## Troubleshooting

### Build Fails:
- Check that `requirements.txt` has all dependencies
- Verify Python version in `runtime.txt` is supported
- Check Render build logs for specific errors

### App Crashes:
- Verify `Procfile` has correct command: `gunicorn app:app`
- Check Render logs for error messages
- Ensure all imports in `app.py` are available

### Repository Still Not Showing:
- Make sure repository is public (for free tier)
- Try using "Public Git Repository" option with direct URL
- Check GitHub account permissions in Render settings

---

## Quick Checklist

- [ ] Repository is public (or using Public Git Repository option)
- [ ] Repository URL is correct: `https://github.com/manibhaskar29/yt-downloader`
- [ ] Branch is set to `main`
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `gunicorn app:app`
- [ ] `Procfile` exists in repository
- [ ] `requirements.txt` has all dependencies
- [ ] `runtime.txt` specifies Python version

---

**Need Help?** Check Render documentation or create an issue on GitHub!




