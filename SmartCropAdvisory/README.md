# 🌾 Smart Crop Advisory System (SIH25010)

[![Smart India Hackathon 2025](https://img.shields.io/badge/SIH-2025-blue)](https://www.sih.gov.in)
[![Django](https://img.shields.io/badge/Django-4.2-green)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 🚀 Live Demo

**[View Live Demo](https://your-deployment-url.herokuapp.com)**

## 📋 About

AI-powered crop recommendation system for 146 million small and marginal farmers in India. This system provides personalized crop suggestions based on soil type, weather patterns, and budget constraints.

## ✨ Features

- 🌱 Smart crop recommendations based on soil analysis
- 🌤️ Real-time weather integration
- 💰 Budget-optimized suggestions
- 📊 Yield prediction and profit analysis
- 🌍 Hyperlocal insights at village level
- 📱 Mobile-responsive Progressive Web App
- 🗣️ Multi-language support (Hindi + Regional)
- 📈 Market price tracking

## 🛠️ Tech Stack

- **Backend:** Django 4.2, Django REST Framework
- **Frontend:** HTML5, CSS3, JavaScript, Chart.js
- **Database:** PostgreSQL (Production), SQLite (Development)
- **Deployment:** Heroku/Render/PythonAnywhere
- **APIs:** OpenWeatherMap, Government Soil Database

## 🏃‍♂️ Quick Start

### Prerequisites

- Python 3.8+
- pip
- virtualenv

### Installation

1. Clone the repository

```bash
git clone https://github.com/yourusername/smart-crop-advisory.git
cd smart-crop-advisory
```

2. Create virtual environment

```bash
bashpython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies

```bash
bashpip install -r requirements.txt
```

4. Set up environment variables

```bash
bashcp .env.example .env
# Edit .env with your settings
```

5. Run migrations

```bash
bashpython manage.py migrate
```

6. Load sample data

```bash
bashpython manage.py loaddata fixtures/initial_data.json
```

7. Start development server

```bash
bashpython manage.py runserver
```

Visit http://localhost:8000 to see the application.
