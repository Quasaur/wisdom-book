from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

class TopicsPageView(APIView):
    def get(self, request):
        data = {
            "title": "Topics",
            "subtitle": "Explore the Wisdom Book by Topic",
            "content": "<p>This is the Topics page content. It will eventually list all available topics.</p>"
        }
        return Response(data)
