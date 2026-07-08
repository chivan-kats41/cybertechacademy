from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('',                                   views.course_list,   name='list'),
    path('<slug:slug>/',                        views.course_detail, name='detail'),
    path('<slug:course_slug>/lesson/<uuid:lesson_id>/', views.lesson_view, name='lesson'),
]