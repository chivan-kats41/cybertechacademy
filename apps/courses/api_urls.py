from django.urls import path
from . import api_views

urlpatterns = [
    path('',               api_views.CourseListView.as_view(),   name='api-course-list'),
    path('<slug:slug>/',   api_views.CourseDetailView.as_view(), name='api-course-detail'),
    path('categories/',    api_views.CategoryListView.as_view(), name='api-categories'),
]