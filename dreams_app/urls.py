from django.urls import path
from .views import DreamCreateView, DreamListView, dream_detail


app_name = 'dreams_app'

urlpatterns = [
    path('new/', DreamCreateView.as_view(), name='new_dream'),
    path('', DreamListView.as_view(), name='my_dreams'),
    path('<int:pk>/', dream_detail, name='detail'),

]
