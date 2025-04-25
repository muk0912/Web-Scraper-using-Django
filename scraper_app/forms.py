from django import forms
from .models import ScrapingTask

class ScrapingTaskForm(forms.ModelForm):
    class Meta:
        model = ScrapingTask
        fields = ['url', 'name', 'description', 'is_recurring', 'run_frequency']
        widgets = {
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'My Scraping Task'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description of what you want to scrape', 'rows': 3}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'run_frequency': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '168'})
        }

    def clean_url(self):
        url = self.cleaned_data['url']
        # Basic validation for URL format - Django's URLField already does this
        # Add any additional validation here if needed
        return url

class AdvancedScrapeForm(ScrapingTaskForm):
    CSS_SELECTOR_CHOICES = [
        ('', 'No specific selector'),
        ('article', 'Article Content'),
        ('p', 'Paragraphs'),
        ('h1,h2,h3,h4,h5,h6', 'Headings'),
        ('table', 'Tables'),
        ('.content', 'Elements with "content" class'),
        ('#main', 'Element with ID "main"'),
    ]
    
    css_selector = forms.ChoiceField(
        choices=CSS_SELECTOR_CHOICES, 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    custom_css_selector = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Custom CSS selector'})
    )
    
    extract_images = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    extract_links = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    max_depth = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=3,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    class Meta(ScrapingTaskForm.Meta):
        fields = ScrapingTaskForm.Meta.fields + ['css_selector', 'custom_css_selector', 'extract_images', 'extract_links', 'max_depth']