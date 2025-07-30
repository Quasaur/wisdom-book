from django.urls import path
from . import views

urlpatterns = [
    # List views
    path('thoughts/', views.ThoughtsListView.as_view(), name='thoughts-list'),
    path('topics/', views.TopicsListView.as_view(), name='topics-list'),
    path('quotes/', views.QuotesListView.as_view(), name='quotes-list'),
    path('passages/', views.PassagesListView.as_view(), name='passages-list'),
    
    # Detail view
    path('items/<str:item_type>/<str:item_id>/', views.ItemDetailView.as_view(), name='item-detail'),
    
    # Search
    path('search/', views.SearchView.as_view(), name='search'),
    
    # Graph data
    path('graph/', views.GraphDataView.as_view(), name='graph-data'),
    
    # Tags
    path('tags/', views.TagsView.as_view(), name='tags-list'),
    path('tags/<str:tag_name>/items/', views.TagItemsView.as_view(), name='tag-items'),
]
