from django.urls import path
from .views import QuotesPageView

urlpatterns = [
    path('', QuotesPageView.as_view(), name='quotes-list'),
]
