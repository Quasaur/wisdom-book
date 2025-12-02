from rest_framework import serializers
from .models import Topic

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'level', 'title', 'description', 'slug', 'is_active', 'neo4j_id']
