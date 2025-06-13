#!/bin/bash

# --- Exit on error ---
set -o errexit

# --- 1. Build The React Frontend ---
echo "Building React frontend..."
cd frontend
npm install
npm run build
cd ..

# --- 2. Install Python Dependencies ---
echo "Installing Python backend dependencies..."
pip install -r requirements.txt

echo "Build finished!" 