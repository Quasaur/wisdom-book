from rest_framework import viewsets
from rest_framework.response import Response
from .models import Passage
from .serializers import PassageSerializer

class PassagesPageView(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for the Passages (Bible) page
    """
    queryset = Passage.objects.filter(is_active=True).prefetch_related('contents')
    serializer_class = PassageSerializer
    lookup_field = 'slug'

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
