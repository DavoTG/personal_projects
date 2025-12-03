#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Install gunicorn if not in requirements (it should be, but just in case)
pip install gunicorn

# Build frontend
echo "Checking Node.js version..."
node -v
npm -v

echo "Building frontend..."
cd "Gym scheduling/frontend"
echo "Current directory: $(pwd)"
npm install
npm run build
echo "Frontend build complete. Listing dist directory:"
ls -la dist
cd ../..
