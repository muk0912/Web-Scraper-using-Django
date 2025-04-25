from django.apps import AppConfig


class ScraperAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scraper_app'
    
    def ready(self):
        import scraper_app.signals  # noqa