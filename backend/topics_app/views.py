from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Topic
from .serializers import TopicSerializer

class TopicsPageView(APIView):
    def get(self, request):
        topics = Topic.objects.filter(is_active=True).order_by('level', 'title')
        serializer = TopicSerializer(topics, many=True)
        return Response(serializer.data)
