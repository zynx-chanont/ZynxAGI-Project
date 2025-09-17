#!/bin/bash

# --- Exit on error ---
set -o errexit

echo "Building ZynxAGI Monorepo..."

# --- 1. Build The Lovable.dev Frontend ---
echo "Building Lovable.dev frontend..."
cd lovable.dev
if [ -f "package.json" ]; then
    npm install
    npm run build
else
    echo "package.json not found in lovable.dev, skipping frontend build"
fi
cd ..

# --- 2. Build The Legacy React Frontend ---
echo "Building legacy React frontend..."
cd frontend
if [ -f "package.json" ]; then
    npm install
    npm run build
else
    echo "package.json not found in frontend, skipping legacy build"
fi
cd ..

# --- 3. Install Python Dependencies ---
echo "Installing Python backend dependencies..."
pip install -r requirements.txt

echo "Monorepo build finished!"  