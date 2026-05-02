#!/bin/bash

# Setup script for C.C. Autonomous AI Model Organization

echo "Setting up C.C. Autonomous AI Model Organization..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories if not exist
mkdir -p logs data

# Copy example config
cp config/.env.example config/.env 2>/dev/null || echo "No .env.example found, please create config/.env manually"

echo "Setup complete. Please configure your API keys in config/.env"
echo "Run example: python example.py"
echo "Run server: python -m uvicorn src.main:app --reload"