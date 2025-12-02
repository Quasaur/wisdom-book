from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuotesPageView

router = DefaultRouter()
router.register(r'', QuotesPageView, basename='quotes')

urlpatterns = [
    path('', include(router.urls)),
]
