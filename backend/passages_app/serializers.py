from rest_framework import serializers
from .models import Passage, PassageContent

class PassageContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassageContent
        fields = [
            'en_title', 'en_content',
            'es_title', 'es_content',
            'fr_title', 'fr_content',
            'hi_title', 'hi_content',
            'zh_title', 'zh_content'
        ]

class PassageSerializer(serializers.ModelSerializer):
    contents = PassageContentSerializer(many=True, read_only=True)
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Passage
        fields = ['id', 'title', 'book', 'chapter', 'verse', 'source', 'slug', 'is_active', 'neo4j_id', 'contents', 'tags']

    def get_tags(self, obj):
        return [t.tag for t in obj.passage_tags.all()]
