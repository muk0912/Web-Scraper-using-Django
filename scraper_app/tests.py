from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import ScrapingTask, ScrapedData

class ScraperModelTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create a test scraping task
        self.task = ScrapingTask.objects.create(
            name='Test Task',
            url='https://example.com',
            description='Test description',
            created_by=self.user
        )
    
    def test_task_creation(self):
        """Test that task creation works correctly"""
        self.assertEqual(self.task.name, 'Test Task')
        self.assertEqual(self.task.url, 'https://example.com')
        self.assertEqual(self.task.status, 'pending')
        self.assertEqual(self.task.created_by, self.user)
    
    def test_task_status_update(self):
        """Test that task status updates correctly"""
        self.task.update_status('in_progress')
        self.assertEqual(self.task.status, 'in_progress')
        
        self.task.update_status('completed')
        self.assertEqual(self.task.status, 'completed')
        self.assertIsNotNone(self.task.last_run)

class ScraperViewTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create a test scraping task
        self.task = ScrapingTask.objects.create(
            name='Test Task',
            url='https://example.com',
            description='Test description',
            created_by=self.user
        )
    
    def test_home_view_without_login(self):
        """Test that the home view works correctly without login"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome to Web Scraper')
    
    def test_home_view_with_login(self):
        """Test that the home view works correctly with login"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Scraping Tasks')
        self.assertContains(response, 'Test Task')
    
    def test_task_detail_view(self):
        """Test that the task detail view works correctly"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('task_detail', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')
        self.assertContains(response, 'https://example.com')
    
    def test_task_create_view(self):
        """Test that the task creation view requires login"""
        # Without login
        response = self.client.get(reverse('task_create'))
        self.assertNotEqual(response.status_code, 200)
        
        # With login
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('task_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New Scraping Task')