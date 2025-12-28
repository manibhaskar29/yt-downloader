# YouTube Downloader - PowerShell Run Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  YouTube Downloader - Starting..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host ""
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Check if requirements are installed
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$flaskInstalled = pip show flask 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host ""
} else {
    Write-Host "Dependencies already installed." -ForegroundColor Green
    Write-Host ""
}

# Run the application
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Flask server..." -ForegroundColor Cyan
Write-Host "  Open http://localhost:8080 in your browser" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

python app.py

