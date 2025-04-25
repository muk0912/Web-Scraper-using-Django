from django.contrib import admin
from .models import ScrapingTask, ScrapedData, ScrapedDataElement

class ScrapedDataElementInline(admin.TabularInline):
    model = ScrapedDataElement
    extra = 0
    readonly_fields = ['element_type', 'content', 'attributes', 'order']
    can_delete = False
    max_num = 0

class ScrapedDataInline(admin.TabularInline):
    model = ScrapedData
    extra = 0
    readonly_fields = ['title', 'content', 'meta_description', 'scraped_at']
    can_delete = False
    max_num = 0
    show_change_link = True

@admin.register(ScrapingTask)
class ScrapingTaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'created_by', 'status', 'last_run', 'is_recurring', 'run_frequency']
    list_filter = ['status', 'is_recurring', 'created_at']
    search_fields = ['name', 'url', 'description']
    readonly_fields = ['created_at', 'updated_at', 'last_run']
    inlines = [ScrapedDataInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)

@admin.register(ScrapedData)
class ScrapedDataAdmin(admin.ModelAdmin):
    list_display = ['task', 'title', 'scraped_at']
    list_filter = ['scraped_at']
    search_fields = ['title', 'content', 'meta_description']
    readonly_fields = ['task', 'title', 'content', 'html_content', 'meta_description', 'page_links', 'images', 'scraped_at']
    inlines = [ScrapedDataElementInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(task__created_by=request.user)

@admin.register(ScrapedDataElement)
class ScrapedDataElementAdmin(admin.ModelAdmin):
    list_display = ['id', 'element_type', 'content_preview', 'scraped_data', 'order']
    list_filter = ['element_type']
    search_fields = ['content']
    readonly_fields = ['scraped_data', 'element_type', 'content', 'attributes', 'order']
    
    def content_preview(self, obj):
        if len(obj.content) > 50:
            return f"{obj.content[:50]}..."
        return obj.content
    content_preview.short_description = 'Content Preview'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(scraped_data__task__created_by=request.user)