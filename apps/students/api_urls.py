from django.urls import path
from . import api_views

urlpatterns = [
    path('enrollments/', api_views.MyEnrollmentsView.as_view(), name='api-my-enrollments'),
    path('profile/',     api_views.MyProfileView.as_view(),     name='api-student-profile'),
]