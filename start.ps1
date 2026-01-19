# Quick Start Script for Timetide

Write-Host "🌊 Timetide - Travel Diary Application" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create .env if it doesn't exist
if (-Not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "⚠️  Please update .env with your configuration" -ForegroundColor Red
}

# Run the application
Write-Host ""
Write-Host "Starting Timetide application..." -ForegroundColor Green
Write-Host "Visit: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
python -m app.main
