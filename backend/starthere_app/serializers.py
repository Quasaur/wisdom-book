from rest_framework import serializers
from .models import StartHerePage

class StartHerePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StartHerePage
        fields = ['title', 'subtitle', 'hero_image_url', 'content', 'updated_at']
