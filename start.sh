#!/bin/bash
# Quick Start Script for Timetide (Unix/Mac)

echo "🌊 Timetide - Travel Diary Application"
echo "====================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Run the application
echo ""
echo "Starting Timetide application..."
echo "Visit: http://localhost:8000"
echo ""
python -m app.main
