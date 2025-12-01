from rest_framework.views import APIView
from rest_framework.response import Response
from .models import StartHerePage
from .serializers import StartHerePageSerializer

class StartHerePageView(APIView):
    """
    Retrieve the Start Here page content.
    """
    def get(self, request, format=None):
        # Get the singleton instance, or create a default one if it doesn't exist
        page, created = StartHerePage.objects.get_or_create(pk=1)
        serializer = StartHerePageSerializer(page)
        return Response(serializer.data)

