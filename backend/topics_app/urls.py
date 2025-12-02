from django.urls import path
from .views import TopicsPageView

urlpatterns = [
    path('', TopicsPageView.as_view(), name='topics-content'),
]
