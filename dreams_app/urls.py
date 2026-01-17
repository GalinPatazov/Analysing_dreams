from django.urls import path
from .views import DreamCreateView, DreamListView, dream_detail, DreamUpdateView, DreamDeleteView, toggle_favorite, FavoriteListView


app_name = 'dreams_app'

urlpatterns = [
    path('new/', DreamCreateView.as_view(), name='new_dream'),
    path('', DreamListView.as_view(), name='my_dreams'),
    path('<int:pk>/', dream_detail, name='detail'),
    path('<int:pk>/edit/', DreamUpdateView.as_view(), name='edit_dream'),
    path('<int:pk>/delete/', DreamDeleteView.as_view(), name='delete_dream'),
    path('<int:pk>/favorite/', toggle_favorite, name='toggle_favorite'),
    path('favorites/', FavoriteListView.as_view(), name='favorites'),
]
