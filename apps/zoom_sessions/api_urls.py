from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.ZoomSessionListView.as_view(), name='api-sessions-list'),
]