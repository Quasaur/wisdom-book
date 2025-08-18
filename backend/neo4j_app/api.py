from typing import Any, Dict
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from .neo4j_service import neo4j_service
from django.utils.text import slugify

def envelope(data, *, total=None, skip=0, limit=25, extra_meta: Dict[str, Any] | None = None):
    meta = {"count": len(data), "skip": skip, "limit": limit}
    if total is not None:
        meta["total"] = total
    if extra_meta:
        meta.update(extra_meta)
    return {"data": data, "meta": meta}

def error_response(code: str, message: str, http_status: int):
    return JsonResponse(
        {"error": {"code": code, "message": message}},
        status=http_status,
    )

def parse_pagination(request):
    def _int(name, default):
        try:
            v = int(request.GET.get(name, default))
            return max(v, 0)
        except ValueError:
            return default
    skip = _int("skip", 0)
    limit = _int("limit", 25)
    if limit > 100:
        limit = 100
    return skip, limit

class HealthView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, _request):
        ok = neo4j_service.health()
        if not ok:
            return error_response("NEO4J_UNAVAILABLE", "Database not reachable", status.HTTP_503_SERVICE_UNAVAILABLE)
        return JsonResponse(envelope([], extra_meta={"ok": True}))

class TopicsView(APIView):
    def get(self, request):
        skip, limit = parse_pagination(request)
        try:
            topics, total = neo4j_service.get_all_topics(skip=skip, limit=limit)
            return JsonResponse(envelope(topics, total=total, skip=skip, limit=limit))
        except Exception as e:
            return error_response("NEO4J_ERROR", f"Failed to fetch topics: {e}", status.HTTP_500_INTERNAL_SERVER_ERROR)

class SearchView(APIView):
    def get(self, request):
        q = request.GET.get("q", "").strip()
        if not q:
            return error_response("BAD_REQUEST", "Missing required query param 'q'", status.HTTP_400_BAD_REQUEST)
        skip, limit = parse_pagination(request)
        try:
            results, total = neo4j_service.search_content(q, skip=skip, limit=limit)
            return JsonResponse(envelope(results, total=total, skip=skip, limit=limit))
        except Exception as e:
            return error_response("NEO4J_ERROR", f"Search failed: {e}", status.HTTP_500_INTERNAL_SERVER_ERROR)

class ItemDetailView(APIView):
    """
    Retrieve a single node by label (item_type) using case-insensitive
    exact match on name or alias. Returns 404 if not found.
    """
    def get(self, request, item_type: str, item_id: str):
        label = item_type.upper()
        if label not in {"TOPIC", "THOUGHT", "QUOTE", "PASSAGE"}:
            return error_response("BAD_TYPE", f"Unsupported item_type '{item_type}'", status.HTTP_400_BAD_REQUEST)
        cypher = f"""
        MATCH (n:{label})
        WHERE (exists(n.name) AND toLower(n.name) = toLower($id))
           OR (exists(n.alias) AND toLower(n.alias) = toLower($id))
        RETURN n, labels(n) AS labels
        LIMIT 2
        """
        rows = neo4j_service.run_query(cypher, {"id": item_id})
        if not rows:
            return error_response("NOT_FOUND", f"{label} '{item_id}' not found", status.HTTP_404_NOT_FOUND)
        if len(rows) > 1:
            return JsonResponse(envelope(
                [{"labels": rows[0]["labels"], "properties": rows[0]["n"]}],
                extra_meta={"warning": "AMBIGUOUS_MATCH"}))
        return JsonResponse(envelope(
            [{"labels": rows[0]["labels"], "properties": rows[0]["n"]}]))
        data = rows[0]["n"]
        return JsonResponse(envelope([{"labels": rows[0]["labels"], "properties": data}]))
