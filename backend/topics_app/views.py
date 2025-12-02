from rest_framework import viewsets
from .models import Topic
from .serializers import TopicSerializer

class TopicsPageView(viewsets.ReadOnlyModelViewSet):
    queryset = Topic.objects.filter(is_active=True).order_by('level', 'title')
    serializer_class = TopicSerializer

