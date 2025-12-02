from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Quote
from .serializers import QuoteSerializer

class QuotesPageView(APIView):
    def get(self, request):
        quotes = Quote.objects.filter(is_active=True).order_by('title')
        serializer = QuoteSerializer(quotes, many=True)
        return Response(serializer.data)
