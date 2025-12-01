from django.urls import path
from .views import StartHerePageView

urlpatterns = [
    path('', StartHerePageView.as_view(), name='start-here-content'),
]
