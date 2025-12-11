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
            'all': (
                'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.css',
                'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/theme/monokai.min.css',
                'starthere_app/css/admin_overrides.css',
            )
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/xml/xml.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/javascript/javascript.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/css/css.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/htmlmixed/htmlmixed.min.js',
            'starthere_app/js/enable_codemirror.js',
        )
    
    def has_add_permission(self, request):
        # Disable add permission if an instance already exists
        if StartHerePage.objects.exists():
            return False
        return super().has_add_permission(request)

