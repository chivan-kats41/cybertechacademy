from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import api_views

urlpatterns = [
    path('me/',       api_views.MeView.as_view(),       name='api-me'),
    path('login/',    obtain_auth_token,                 name='api-login'),
    path('register/', api_views.RegisterView.as_view(),  name='api-register'),
]