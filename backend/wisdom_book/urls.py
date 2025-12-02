from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/neo4j/", include("neo4j_app.urls")),
    path("api/start-here/", include("starthere_app.urls")),
    path("api/topics/", include("topics_app.urls")),
    path("api/thoughts/", include("thoughts_app.urls")),
    path("api/quotes/", include("quotes_app.urls")),
    path("api/passages/", include("passages_app.urls")),
    path("graph/", include("graphview_app.urls")),
]
