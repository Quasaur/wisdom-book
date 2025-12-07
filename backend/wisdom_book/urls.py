from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/neo4j/", include("neo4j_app.urls")),
    path("api/start-here/", include("starthere_app.urls")),
    path("api/topics/", include("topics_app.urls")),
    path("api/thoughts/", include("thoughts_app.urls")),
    path("api/quotes/", include("quotes_app.urls")),
    path("api/passages/", include("passages_app.urls")),
    path('api/tags/', include('tags_app.urls')),
    path("graph/", include("graphview_app.urls")),
    re_path(r"^.*$", TemplateView.as_view(template_name="index.html")),
]
