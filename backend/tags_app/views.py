from rest_framework import viewsets
from .models import TagSource
from .serializers import TagSourceSerializer

class TagSourceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ReadOnly ViewSet for TagSource.
    Allows filtering by source_type and searching by name.
    """
    queryset = TagSource.objects.all()
    serializer_class = TagSourceSerializer
    filterset_fields = ['source_type']
    search_fields = ['name', 'tags']
