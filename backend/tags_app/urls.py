from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TagSourceViewSet

router = DefaultRouter()
router.register(r'tags', TagSourceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
