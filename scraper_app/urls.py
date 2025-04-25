from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('task/new/', views.TaskCreateView.as_view(), name='task_create'),
    path('task/advanced/new/', views.AdvancedTaskCreateView.as_view(), name='advanced_task_create'),
    path('task/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('result/<int:pk>/', views.ResultDetailView.as_view(), name='result_detail'),
    path('task/<int:pk>/run/', views.run_scraper_now, name='run_task'),
    path('task/<int:pk>/delete/', views.delete_task, name='delete_task'),
    path('task/<int:pk>/status/', views.task_status, name='task_status'),
    path('test/', views.test_view, name='test'),
]