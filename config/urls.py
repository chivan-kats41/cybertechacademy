from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/',      admin.site.urls),
    path('accounts/',   include('allauth.urls')),

    # Core pages
    path('', include('apps.core.urls', namespace='core')),

    # Courses
    path('courses/', include('apps.courses.urls', namespace='courses')),

    # Students — includes /register/, /dashboard/, /admission/*, /learn/*
    path('', include('apps.students.urls', namespace='students')),

    # Zoom Sessions
    path('sessions/', include('apps.zoom_sessions.urls', namespace='zoom_sessions')),

    # Payments
    path('payments/', include('apps.payments.urls', namespace='payments')),

    # REST API v1
    path('api/v1/', include([
        path('accounts/', include('apps.accounts.api_urls')),
        path('courses/',  include('apps.courses.api_urls')),
        path('students/', include('apps.students.api_urls')),
        path('sessions/', include('apps.zoom_sessions.api_urls')),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'apps.core.views.error_404'
handler500 = 'apps.core.views.error_500'