#!/usr/bin/env bash

set -o errexit

# Upgrade pip
pip install --upgrade pip

# Install production dependencies
pip install -r requirements.txt

# Install Gunicorn if not in requirements.txt
pip install gunicorn

# Collect static files
python manage.py collectstatic --noinput

# Run migrations for Django's internal SQLite
python manage.py migrate --noinput
