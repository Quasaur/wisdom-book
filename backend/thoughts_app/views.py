from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Thought
from .serializers import ThoughtSerializer

class ThoughtsPageView(APIView):
    def get(self, request):
        thoughts = Thought.objects.filter(is_active=True).order_by('title')
        serializer = ThoughtSerializer(thoughts, many=True)
        return Response(serializer.data)
