from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/neo4j/", include("neo4j_app.urls")),
]
