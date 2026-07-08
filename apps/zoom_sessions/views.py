"""
CyberTech Academy - Zoom Sessions Views
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import ZoomSession, ZoomRegistration
from apps.payments.models import ZoomPayment


def session_list(request):
    upcoming = ZoomSession.objects.filter(
        is_active=True, scheduled_at__gte=timezone.now()
    ).select_related('instructor').order_by('scheduled_at')

    past = ZoomSession.objects.filter(
        is_active=True, scheduled_at__lt=timezone.now()
    ).select_related('instructor').order_by('-scheduled_at')[:6]

    # For each session, check if current user has paid
    paid_session_ids = set()
    if request.user.is_authenticated:
        paid_session_ids = set(
            ZoomPayment.objects.filter(
                student=request.user, payment_status='success'
            ).values_list('session_id', flat=True)
        )

    context = {
        'upcoming':         upcoming,
        'past':             past,
        'paid_session_ids': paid_session_ids,
    }
    return render(request, 'zoom_sessions/list.html', context)


def session_detail(request, pk):
    session = get_object_or_404(ZoomSession, pk=pk, is_active=True)

    has_access = False
    if request.user.is_authenticated:
        has_access = ZoomPayment.objects.filter(
            student=request.user, session=session, payment_status='success'
        ).exists()

    context = {
        'session':    session,
        'has_access': has_access,
    }
    return render(request, 'zoom_sessions/detail.html', context)