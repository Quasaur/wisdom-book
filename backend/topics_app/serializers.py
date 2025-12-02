from rest_framework import serializers
from .models import Topic

class TopicSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='tag',
        source='topic_tags'
    )

    class Meta:
        model = Topic
        fields = ['id', 'level', 'title', 'description', 'slug', 'is_active', 'neo4j_id', 'tags']
