from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils import timezone

from .models import ScrapingTask, ScrapedData
from .forms import ScrapingTaskForm, AdvancedScrapeForm
from .tasks import scrape_url

class HomeView(ListView):
    model = ScrapingTask
    template_name = 'home.html'
    context_object_name = 'tasks'
    paginate_by = 10
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return ScrapingTask.objects.filter(created_by=self.request.user).order_by('-created_at')
        return ScrapingTask.objects.none()

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = ScrapingTask
    form_class = ScrapingTaskForm
    template_name = 'scrape_form.html'
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Trigger the scraping task
        scrape_url.delay(self.object.id)
        messages.success(self.request, f"Scraping task '{self.object.name}' created and queued!")
        
        return response

class AdvancedTaskCreateView(LoginRequiredMixin, CreateView):
    model = ScrapingTask
    form_class = AdvancedScrapeForm
    template_name = 'scrape_form.html'
    success_url = reverse_lazy('home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_advanced'] = True
        return context
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Store the advanced options in the task's metadata
        task = self.object
        task_options = {
            'css_selector': form.cleaned_data.get('custom_css_selector') or form.cleaned_data.get('css_selector'),
            'extract_images': form.cleaned_data.get('extract_images'),
            'extract_links': form.cleaned_data.get('extract_links'),
            'max_depth': form.cleaned_data.get('max_depth'),
        }
        
        # Trigger the scraping task with advanced options
        scrape_url.delay(task.id, task_options)
        messages.success(self.request, f"Advanced scraping task '{task.name}' created and queued!")
        
        return response

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = ScrapingTask
    template_name = 'scrape_detail.html'
    context_object_name = 'task'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_object()
        # Get the latest scraped data
        context['scraped_data'] = task.scraped_data.order_by('-scraped_at').first()
        # Get all historical scrapes
        context['historical_scrapes'] = task.scraped_data.order_by('-scraped_at')
        return context

class ResultDetailView(LoginRequiredMixin, DetailView):
    model = ScrapedData
    template_name = 'result_detail.html'
    context_object_name = 'result'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the elements sorted by order
        context['elements'] = self.object.elements.all().order_by('order')
        return context

@login_required
def run_scraper_now(request, pk):
    task = get_object_or_404(ScrapingTask, pk=pk, created_by=request.user)
    task.update_status('pending')
    scrape_url.delay(task.id)
    messages.success(request, f"Task '{task.name}' has been queued for scraping!")
    return redirect('task_detail', pk=task.pk)

@login_required
def delete_task(request, pk):
    task = get_object_or_404(ScrapingTask, pk=pk, created_by=request.user)
    if request.method == 'POST':
        task_name = task.name
        task.delete()
        messages.success(request, f"Task '{task_name}' has been deleted!")
        return redirect('home')
    return render(request, 'confirm_delete.html', {'task': task})

def task_status(request, pk):
    """AJAX endpoint to check task status"""
    task = get_object_or_404(ScrapingTask, pk=pk)
    return JsonResponse({
        'status': task.status,
        'last_run': task.last_run.isoformat() if task.last_run else None,
    })

def test_view(request):
    return render(request, 'test.html')