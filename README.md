# Web Scraper Project

A Django-based web scraping application that allows users to scrape, analyze, and store content from websites.

## Features

- **User Authentication**: Secure login system to manage your scraping tasks
- **Simple & Advanced Scraping**: Basic URL scraping or targeted content extraction with CSS selectors
- **Content Analysis**: Extract structured elements like headings, paragraphs, links, and images
- **Scheduled Scraping**: Set up recurring scraping tasks at specified intervals
- **Data Visualization**: View scraped content in various formats including plain text, structured elements, and raw HTML
- **Historical Data**: Track changes to websites over time with a history of all scrapes

## Technical Stack

- **Backend**: Django 4.2
- **Task Queue**: Celery with Redis as broker
- **HTML Parsing**: Beautiful Soup 4
- **Frontend**: Bootstrap 5 with responsive design
- **Database**: SQLite (default, can be configured for PostgreSQL or other databases)

## Installation

### Prerequisites

- Python 3.8 or higher
- Redis (for Celery task queue)

### Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd web-scraper
   ```

2. Run the setup script (this will create a virtual environment, install dependencies, and set up the database):
   ```
   chmod +x setup.sh
   ./setup.sh
   ```

3. Alternatively, you can set up manually:
   ```
   # Create a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Initialize the database
   python manage.py migrate

   # Create a superuser
   python manage.py createsuperuser
   ```

## Running the Application

1. Start Redis (if not already running)

2. Start the Celery worker (for processing scraping tasks):
   ```
   celery -A web_scraper worker --loglevel=info
   ```

3. Start the Celery beat scheduler (for recurring tasks):
   ```
   celery -A web_scraper beat --loglevel=info
   ```

4. Run the Django development server:
   ```
   python manage.py runserver
   ```

5. Visit http://127.0.0.1:8000/ in your browser

## Usage

1. Create an account or log in
2. Create a new scraping task by entering a URL and task name
3. View the scraped content in various formats
4. Set up recurring scrapes to track changes over time
5. Export data for further analysis

## Advanced Features

### CSS Selectors

Use CSS selectors to target specific content on web pages. Some examples:

- `article` - Scrape the main article content
- `h1,h2,h3` - Scrape all headings
- `.content` - Scrape elements with the "content" class
- `#main-content` - Scrape the element with ID "main-content"

### Scheduling

Set up recurring scrapes at intervals specified in hours to:

- Track price changes on e-commerce sites
- Monitor news websites for updates
- Archive content that might change or disappear

## Security Considerations

- The application respects robots.txt rules
- Implements rate limiting to avoid overloading websites
- Only authenticated users can create and view scraping tasks

## Project Structure

```
web_scraper_project/
├── manage.py
├── requirements.txt
├── web_scraper/          # Project settings
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
├── scraper_app/          # Main application
│   ├── models.py         # Database models
│   ├── views.py          # View controllers
│   ├── tasks.py          # Celery tasks
│   ├── templates/        # HTML templates
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django - The web framework used
- Beautiful Soup - For HTML parsing
- Celery - For task queuing and scheduling
- Bootstrap - For frontend design