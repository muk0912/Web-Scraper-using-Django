from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ScrapingTask
from .tasks import scrape_url

@receiver(post_save, sender=ScrapingTask)
def task_post_save(sender, instance, created, **kwargs):
    """
    Signal handler to trigger scraping when a new task is created
    """
    # Only trigger on creation, not on updates
    if created:
        # Schedule the task to run immediately
        scrape_url.delay(instance.id)