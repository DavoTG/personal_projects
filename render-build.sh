#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Install gunicorn if not in requirements (it should be, but just in case)
pip install gunicorn

# Build frontend
echo "Building frontend..."
cd "Gym scheduling/frontend"
npm install
npm run build
cd ../..
