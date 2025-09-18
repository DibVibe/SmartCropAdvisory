#!/usr/bin/env bash

set -o errexit

# Ensure we're using Python 3.11
python --version

# Upgrade pip, setuptools, and wheel first
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

# Install gunicorn separately if needed
pip install gunicorn

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --noinput

echo "Build completed successfully!"
