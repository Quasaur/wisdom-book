from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Thought, Content

@admin.register(Thought)
class ThoughtAdmin(admin.ModelAdmin):
    list_display = ['title', 'parent_id', 'is_active', 'last_synced', 'neo4j_id']
    search_fields = ['title', 'description', 'neo4j_id']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['neo4j_id', 'last_synced', 'created_at', 'updated_at']
    list_filter = ['is_active', 'last_synced']
    
    actions = ['sync_from_neo4j']
    
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('sync-all/', self.sync_all_view, name='thoughts_app_thought_sync_all'),
        ]
        return my_urls + urls

    def sync_all_view(self, request):
        from .services import thoughts_service
        success, message, count = thoughts_service.sync_thoughts_from_neo4j()
        
        if success:
            self.message_user(request, message, level=messages.SUCCESS)
        else:
            self.message_user(request, f"Sync failed: {message}", level=messages.ERROR)
            
        return HttpResponseRedirect("../")
    
    def sync_from_neo4j(self, request, queryset):
        """Admin action to sync selected thoughts from Neo4j"""
        from .services import thoughts_service
        
        success_count = 0
        for thought in queryset:
            # For now, we just trigger a full sync as we don't have single-fetch optimized yet
            # or we could implement single fetch in service.
            # Let's just do a full sync for simplicity or log that we are skipping optimization
            pass
            
        # Actually, let's just run the full sync for now as it's safer
        success, message, count = thoughts_service.sync_thoughts_from_neo4j()
        self.message_user(request, message)
    sync_from_neo4j.short_description = "Sync thoughts from Neo4j"

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['neo4j_id', 'thought', 'short_content', 'created_at']
    search_fields = ['neo4j_id', 'content', 'thought__title']
    list_filter = ['created_at']
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content'
