from rest_framework import serializers
from .models import TagSource

class TagSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagSource
        fields = ['id', 'name', 'source_type', 'source_id', 'tags', 'created_at', 'updated_at']
