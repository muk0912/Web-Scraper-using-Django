from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ScrapingTask(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    url = models.URLField(max_length=500)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scraping_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_run = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_recurring = models.BooleanField(default=False)
    run_frequency = models.PositiveIntegerField(default=0, help_text="Frequency in hours (0 for one-time)")
    
    def __str__(self):
        return f"{self.name} - {self.url}"
    
    def update_status(self, status):
        self.status = status
        if status == 'completed' or status == 'failed':
            self.last_run = timezone.now()
        self.save()

class ScrapedData(models.Model):
    task = models.ForeignKey(ScrapingTask, on_delete=models.CASCADE, related_name='scraped_data')
    title = models.CharField(max_length=500, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    html_content = models.TextField(blank=True, null=True)
    scraped_at = models.DateTimeField(auto_now_add=True)
    
    # Extracted metadata
    meta_description = models.TextField(blank=True, null=True)
    page_links = models.JSONField(blank=True, null=True)
    images = models.JSONField(blank=True, null=True)
    
    def __str__(self):
        return f"Data for {self.task.name} - {self.scraped_at}"

class ScrapedDataElement(models.Model):
    ELEMENT_TYPE_CHOICES = (
        ('heading', 'Heading'),
        ('paragraph', 'Paragraph'),
        ('link', 'Link'),
        ('image', 'Image'),
        ('list', 'List'),
        ('table', 'Table'),
        ('other', 'Other'),
    )
    
    scraped_data = models.ForeignKey(ScrapedData, on_delete=models.CASCADE, related_name='elements')
    element_type = models.CharField(max_length=20, choices=ELEMENT_TYPE_CHOICES)
    content = models.TextField()
    attributes = models.JSONField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.element_type} - {self.content[:50]}"