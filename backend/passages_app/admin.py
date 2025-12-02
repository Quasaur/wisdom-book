from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Passage, PassageContent

@admin.register(Passage)
class PassageAdmin(admin.ModelAdmin):
    list_display = ('title', 'book', 'chapter', 'verse', 'neo4j_id', 'is_active', 'last_synced')
    search_fields = ('title', 'book', 'neo4j_id')
    list_filter = ('is_active', 'book')
    readonly_fields = ('last_synced', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    
    actions = ['sync_from_neo4j']
    
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('sync-all/', self.sync_all_view, name='passages_app_passage_sync_all'),
        ]
        return my_urls + urls

    def sync_all_view(self, request):
        from .services import passages_service
        success, message, count = passages_service.sync_passages_from_neo4j()
        
        if success:
            self.message_user(request, message, level=messages.SUCCESS)
        else:
            self.message_user(request, f"Sync failed: {message}", level=messages.ERROR)
            
        return HttpResponseRedirect("../")
    
    def sync_from_neo4j(self, request, queryset):
        """Admin action to sync selected passages from Neo4j"""
        from .services import passages_service
        
        # Trigger full sync for simplicity
        success, message, count = passages_service.sync_passages_from_neo4j()
        self.message_user(request, message)
    sync_from_neo4j.short_description = "Sync passages from Neo4j"

@admin.register(PassageContent)
class PassageContentAdmin(admin.ModelAdmin):
    list_display = ('passage', 'neo4j_id', 'en_title', 'created_at')
    search_fields = ('passage__title', 'neo4j_id', 'en_title', 'en_content')
    list_filter = ('created_at',)
