from django.shortcuts import render
from django.http import JsonResponse
from .services import PostgresGraphService

# Create your views here.

def graph_data_api(request):
    """API endpoint for graph data"""
    try:
        # PostgresGraphService.get_graph_data() returns a dict with nodes and relationships
        # Structure matches what frontend D3 expects
        graph_data = PostgresGraphService.get_graph_data()
        return JsonResponse(graph_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
