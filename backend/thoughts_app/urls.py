from django.urls import path
from .views import ThoughtsPageView

urlpatterns = [
    path('', ThoughtsPageView.as_view(), name='thoughts-content'),
]
