from django.urls import path
from . import views
app_name = 'payments'
urlpatterns = [
    path('zoom/<uuid:session_pk>/',     views.zoom_checkout,   name='zoom_checkout'),
    path('zoom/verify/<str:ref>/',       views.zoom_verify,     name='zoom_verify'),
    path('course/<slug:course_slug>/',   views.course_checkout, name='course_checkout'),
    path('course/verify/<str:ref>/',     views.course_verify,   name='course_verify'),
]
