from django.urls import path
from .views import DreamCreateView, DreamListView

urlpatterns = [
    path('new/', DreamCreateView.as_view(), name='new_dream'),
    path('', DreamListView.as_view(), name='my_dreams'),

]
