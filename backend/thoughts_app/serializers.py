from rest_framework import serializers
from .models import Thought, Content

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = [
            'en_title', 'en_content',
            'es_title', 'es_content',
            'fr_title', 'fr_content',
            'hi_title', 'hi_content',
            'zh_title', 'zh_content'
        ]

class ThoughtSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True, read_only=True)

    class Meta:
        model = Thought
        fields = ['id', 'title', 'description', 'parent_id', 'slug', 'is_active', 'neo4j_id', 'contents']
