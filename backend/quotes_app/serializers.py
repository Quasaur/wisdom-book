from rest_framework import serializers
from .models import Quote, QuoteContent

class QuoteContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteContent
        fields = [
            'en_title', 'en_content',
            'es_title', 'es_content',
            'fr_title', 'fr_content',
            'hi_title', 'hi_content',
            'zh_title', 'zh_content'
        ]

class QuoteSerializer(serializers.ModelSerializer):
    contents = QuoteContentSerializer(many=True, read_only=True)
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Quote
        fields = ['id', 'title', 'author', 'source', 'book_link', 'slug', 'is_active', 'neo4j_id', 'contents', 'tags']

    def get_tags(self, obj):
        return [t.tag for t in obj.quote_tags.all()]
