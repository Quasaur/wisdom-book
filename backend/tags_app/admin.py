from django.contrib import admin
from .models import TagSource

@admin.register(TagSource)
class TagSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type', 'source_id', 'created_at')
    list_filter = ('source_type',)
    search_fields = ('name', 'tags')
    readonly_fields = ('created_at', 'updated_at')
