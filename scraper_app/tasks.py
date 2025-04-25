import requests
from bs4 import BeautifulSoup
from celery import shared_task
from django.utils import timezone
from requests.exceptions import RequestException
import logging

from .models import ScrapingTask, ScrapedData, ScrapedDataElement

logger = logging.getLogger(__name__)

@shared_task
def scrape_url(task_id, options=None):
    """
    Task to scrape a URL and store the results
    
    Args:
        task_id: ID of the ScrapingTask to process
        options: Dictionary of scraping options (optional)
    """
    # Default options
    default_options = {
        'css_selector': None,
        'extract_images': True,
        'extract_links': True,
        'max_depth': 0,
    }
    
    # Merge with provided options
    if options:
        default_options.update(options)
    options = default_options
    
    try:
        # Get the task
        task = ScrapingTask.objects.get(id=task_id)
        task.update_status('in_progress')
        
        # Make the request with a reasonable timeout
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(task.url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Create the scraped data record
        scraped_data = ScrapedData.objects.create(
            task=task,
            title=soup.title.string if soup.title else None,
            html_content=response.text,
            meta_description=get_meta_description(soup),
            page_links=extract_links(soup) if options['extract_links'] else None,
            images=extract_images(soup) if options['extract_images'] else None,
        )
        
        # Extract content based on CSS selector if provided
        if options['css_selector']:
            content_elements = soup.select(options['css_selector'])
            content = '\n'.join([elem.get_text(strip=True) for elem in content_elements])
        else:
            # Default to extract main content (basic algorithm, can be improved)
            content = extract_main_content(soup)
        
        scraped_data.content = content
        scraped_data.save()
        
        # Process individual elements
        process_elements(soup, scraped_data, options)
        
        # Update task status
        task.update_status('completed')
        
        # Schedule next run if recurring
        if task.is_recurring and task.run_frequency > 0:
            next_run = timezone.now() + timezone.timedelta(hours=task.run_frequency)
            schedule_next_scrape.apply_async(args=[task_id], eta=next_run)
        
        return f"Successfully scraped {task.url}"
        
    except ScrapingTask.DoesNotExist:
        logger.error(f"Task with ID {task_id} does not exist")
        return f"Task with ID {task_id} does not exist"
    
    except RequestException as e:
        logger.error(f"Request error for task {task_id}: {str(e)}")
        if 'task' in locals():
            task.update_status('failed')
        return f"Request error: {str(e)}"
    
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {str(e)}")
        if 'task' in locals():
            task.update_status('failed')
        return f"Error: {str(e)}"

@shared_task
def schedule_next_scrape(task_id):
    """Schedule the next scrape for a recurring task"""
    try:
        task = ScrapingTask.objects.get(id=task_id)
        if task.is_recurring:
            scrape_url.delay(task_id)
    except ScrapingTask.DoesNotExist:
        logger.error(f"Cannot schedule next scrape - Task with ID {task_id} does not exist")

def get_meta_description(soup):
    """Extract meta description from soup"""
    meta = soup.find('meta', attrs={'name': 'description'})
    if meta and 'content' in meta.attrs:
        return meta['content']
    return None

def extract_links(soup):
    """Extract links from soup"""
    links = []
    for a in soup.find_all('a', href=True):
        links.append({
            'text': a.get_text(strip=True),
            'href': a['href']
        })
    return links

def extract_images(soup):
    """Extract images from soup"""
    images = []
    for img in soup.find_all('img', src=True):
        images.append({
            'src': img['src'],
            'alt': img.get('alt', ''),
            'title': img.get('title', '')
        })
    return images

def extract_main_content(soup):
    """
    Basic algorithm to extract main content
    This is a simplified approach - production systems would use more sophisticated
    content extraction algorithms
    """
    # Try common content containers
    content_candidates = [
        soup.find('article'),
        soup.find('main'),
        soup.find(id='content'),
        soup.find(id='main'),
        soup.find(class_='content'),
        soup.find(class_='main')
    ]
    
    # Use the first valid candidate
    for candidate in content_candidates:
        if candidate:
            return candidate.get_text(strip=True)
    
    # Fallback to body content
    body = soup.find('body')
    if body:
        # Remove navigation, header, footer, sidebar elements
        for elem in body.select('nav, header, footer, aside'):
            elem.decompose()
        return body.get_text(strip=True)
    
    # Last resort
    return soup.get_text(strip=True)

def process_elements(soup, scraped_data, options):
    """Process and store individual page elements"""
    order = 0
    
    # Define the container to look in
    container = soup
    if options['css_selector']:
        selected = soup.select(options['css_selector'])
        if selected:
            # Create a new soup with just these elements
            container = BeautifulSoup('<div></div>', 'lxml')
            div = container.div
            for elem in selected:
                div.append(elem)
    
    # Process headings
    for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        for heading in container.find_all(tag):
            ScrapedDataElement.objects.create(
                scraped_data=scraped_data,
                element_type='heading',
                content=heading.get_text(strip=True),
                attributes={'level': tag},
                order=order
            )
            order += 1
    
    # Process paragraphs
    for p in container.find_all('p'):
        if p.get_text(strip=True):  # Only if there's actual text
            ScrapedDataElement.objects.create(
                scraped_data=scraped_data,
                element_type='paragraph',
                content=p.get_text(strip=True),
                order=order
            )
            order += 1
    
    # Process links if requested
    if options['extract_links']:
        for a in container.find_all('a', href=True):
            if a.get_text(strip=True):
                ScrapedDataElement.objects.create(
                    scraped_data=scraped_data,
                    element_type='link',
                    content=a.get_text(strip=True),
                    attributes={'href': a['href']},
                    order=order
                )
                order += 1
    
    # Process images if requested
    if options['extract_images']:
        for img in container.find_all('img', src=True):
            ScrapedDataElement.objects.create(
                scraped_data=scraped_data,
                element_type='image',
                content=img.get('alt', ''),
                attributes={
                    'src': img['src'],
                    'alt': img.get('alt', ''),
                    'title': img.get('title', '')
                },
                order=order
            )
            order += 1
    
    # Process lists
    for list_tag in container.find_all(['ul', 'ol']):
        items = [li.get_text(strip=True) for li in list_tag.find_all('li')]
        if items:
            ScrapedDataElement.objects.create(
                scraped_data=scraped_data,
                element_type='list',
                content='\n'.join(items),
                attributes={
                    'type': list_tag.name,
                    'items': items
                },
                order=order
            )
            order += 1
    
    # Process tables
    for table in container.find_all('table'):
        # Simple table processing - could be enhanced
        rows = []
        for tr in table.find_all('tr'):
            cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
            if cells:
                rows.append(cells)
        
        if rows:
            ScrapedDataElement.objects.create(
                scraped_data=scraped_data,
                element_type='table',
                content=str(rows),  # Simple representation
                attributes={
                    'rows': rows
                },
                order=order
            )
            order += 1