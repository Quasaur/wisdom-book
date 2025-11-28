from django.shortcuts import render
from django.http import JsonResponse
from neo4j_app.neo4j_service import neo4j_service

# Create your views here.

def graph_data_api(request):
    """API endpoint for graph data"""
    try:
        # neo4j_service.get_graph_data() returns a dict with nodes and relationships
        graph_data = neo4j_service.get_graph_data()
        return JsonResponse(graph_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
