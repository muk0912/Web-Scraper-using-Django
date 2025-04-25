#!/bin/bash

# Web Scraper Django Project Setup Script

echo "Setting up Web Scraper project..."

# Create a virtual environment
echo "Creating virtual environment..."
python -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Initialize Django
echo "Initializing Django..."
python manage.py migrate
python manage.py collectstatic --noinput

# Create a superuser
echo "Creating a superuser..."
echo "Please create a superuser account for accessing the admin panel and logging into the app:"
python manage.py createsuperuser

# Instructions for running Redis
echo ""
echo "------------------------"
echo "To run the application, you need to have Redis installed and running."
echo "If you haven't installed Redis yet, please follow these instructions:"
echo ""
echo "For Ubuntu/Debian:"
echo "  sudo apt update"
echo "  sudo apt install redis-server"
echo "  sudo systemctl start redis-server"
echo ""
echo "For macOS (using Homebrew):"
echo "  brew install redis"
echo "  brew services start redis"
echo ""
echo "For Windows:"
echo "  Please download Redis for Windows from https://github.com/microsoftarchive/redis/releases"
echo "  Or use Redis with WSL (Windows Subsystem for Linux)"
echo "------------------------"
echo ""

# Instructions for running the app
echo "Setup complete! To run the application:"
echo ""
echo "1. Start Redis (if not already running)"
echo "2. Start the Celery worker:"
echo "   celery -A web_scraper worker --loglevel=info"
echo "3. Start the Celery beat scheduler (for recurring tasks):"
echo "   celery -A web_scraper beat --loglevel=info"
echo "4. Start the Django development server:"
echo "   python manage.py runserver"
echo ""
echo "Then visit http://127.0.0.1:8000/ in your browser."
echo ""
echo "Happy scraping!"