from django.contrib import admin
from .models import Quote, QuoteContent

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_active', 'last_synced', 'neo4j_id']
    search_fields = ['title', 'author', 'source', 'neo4j_id']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['neo4j_id', 'last_synced', 'created_at', 'updated_at']
    list_filter = ['is_active', 'last_synced']

@admin.register(QuoteContent)
class QuoteContentAdmin(admin.ModelAdmin):
    list_display = ['neo4j_id', 'quote', 'short_content', 'created_at']
    search_fields = ['neo4j_id', 'content', 'quote__title']
    list_filter = ['created_at']
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content'
