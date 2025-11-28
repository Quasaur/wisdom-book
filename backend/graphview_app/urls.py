from django.urls import path
from . import views

app_name = 'graphview_app'

urlpatterns = [
    path('api/data/', views.graph_data_api, name='graph_data'),
]
