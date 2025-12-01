from django.contrib import admin
from django.db import models
from django.forms import Textarea, TextInput
from .models import StartHerePage

@admin.register(StartHerePage)
class StartHerePageAdmin(admin.ModelAdmin):
    list_display = ['title', 'updated_at']
    
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 28, 'style': 'width: 80%;'})},
        models.CharField: {'widget': TextInput(attrs={'style': 'width: 70%;'})},
    }
    
    class Media:
        css = {
            'all': ('starthere_app/css/admin_overrides.css',)
        }
    
    def has_add_permission(self, request):
        # Disable add permission if an instance already exists
        if StartHerePage.objects.exists():
            return False
        return super().has_add_permission(request)

