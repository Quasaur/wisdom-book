from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TopicsPageView

router = DefaultRouter()
router.register(r'', TopicsPageView, basename='topics')

urlpatterns = [
    path('', include(router.urls)),
]
