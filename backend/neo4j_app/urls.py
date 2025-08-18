from django.urls import path
from .api import HealthView, TopicsView, SearchView, ItemDetailView

app_name = "neo4j_app"

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("topics/", TopicsView.as_view(), name="topics"),
    path("search/", SearchView.as_view(), name="search"),
    path("items/<str:item_type>/<str:item_id>/", ItemDetailView.as_view(), name="item-detail"),
]
