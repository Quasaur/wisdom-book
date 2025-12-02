from rest_framework import viewsets
from .models import Quote
from .serializers import QuoteSerializer

class QuotesPageView(viewsets.ReadOnlyModelViewSet):
    queryset = Quote.objects.filter(is_active=True).order_by('title')
    serializer_class = QuoteSerializer

