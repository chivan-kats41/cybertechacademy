from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Registration & Admission flow
    path('register/',                  views.register,          name='register'),
    path('admission/pending/',         views.admission_pending, name='admission_pending'),
    path('admission/pay/',             views.admission_pay,     name='admission_pay'),
    path('admission/verify/<str:ref>/', views.admission_verify, name='admission_verify'),
    path('admission/success/',         views.admission_success, name='admission_success'),

    # Gated student area
    path('dashboard/',                                            views.dashboard,     name='dashboard'),
    path('profile/',                                              views.profile,       name='profile'),
    path('enroll/<slug:course_slug>/',                            views.enroll_course, name='enroll'),
    path('learn/<slug:course_slug>/',                             views.learn,         name='learn'),
    path('learn/<slug:course_slug>/lesson/<uuid:lesson_id>/',     views.lesson_detail, name='lesson'),
]