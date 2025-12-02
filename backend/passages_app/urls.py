from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PassagesPageView

router = DefaultRouter()
router.register(r'', PassagesPageView, basename='passages')

urlpatterns = [
    path('', include(router.urls)),
]
