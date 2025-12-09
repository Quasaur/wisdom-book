from rest_framework import viewsets
from .models import Thought
from .serializers import ThoughtSerializer

class ThoughtsPageView(viewsets.ReadOnlyModelViewSet):
    queryset = Thought.objects.filter(is_active=True).order_by('level', 'title')
    serializer_class = ThoughtSerializer

