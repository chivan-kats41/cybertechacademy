from django.shortcuts import render, redirect
from django.contrib import messages
from apps.courses.models import Course, Category
from apps.zoom_sessions.models import ZoomSession
from django.utils import timezone


def home(request):
    featured_courses  = Course.objects.filter(is_published=True, is_featured=True)[:6]
    upcoming_sessions = ZoomSession.objects.filter(is_active=True, scheduled_at__gte=timezone.now()).order_by('scheduled_at')[:3]
    categories        = Category.objects.all()[:6]
    return render(request, 'core/home.html', {
        'featured_courses':  featured_courses,
        'upcoming_sessions': upcoming_sessions,
        'categories':        categories,
    })


def contact(request):
    if request.method == 'POST':
        messages.success(request, "Thanks for reaching out! We'll get back to you within 24 hours.")
        return redirect('core:contact')
    return render(request, 'core/contact.html')


def error_404(request, exception):
    return render(request, 'core/404.html', status=404)


def error_500(request):
    return render(request, 'core/500.html', status=500)