from rest_framework import serializers
from .models import Topic, TopicTag, Description

class DescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Description
        fields = [
            'en_title', 'en_content',
            'es_title', 'es_content',
            'fr_title', 'fr_content',
            'hi_title', 'hi_content',
            'zh_title', 'zh_content'
        ]

class TopicSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='tag',
        source='topic_tags'
    )
    descriptions = DescriptionSerializer(many=True, read_only=True)

    class Meta:
        model = Topic
        fields = ['id', 'level', 'title', 'description', 'slug', 'is_active', 'neo4j_id', 'tags', 'descriptions', 'parent_id']
