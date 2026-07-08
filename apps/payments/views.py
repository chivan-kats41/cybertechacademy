"""
CyberTech Academy - Payments Views (Flutterwave)
"""
import uuid, requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from .models import ZoomPayment, CoursePayment
from apps.zoom_sessions.models import ZoomSession, ZoomRegistration
from apps.courses.models import Course
from apps.students.models import Enrollment
from apps.core.email_utils import send_zoom_access_email


@login_required
def zoom_checkout(request, session_pk):
    session = get_object_or_404(ZoomSession, pk=session_pk, is_active=True)
    already = ZoomPayment.objects.filter(student=request.user, session=session, payment_status='success').exists()
    if already:
        messages.info(request, "You already have access to this session.")
        return redirect('zoom_sessions:detail', pk=session_pk)
    if request.method == 'POST':
        ref = f"ZS-{uuid.uuid4().hex[:12].upper()}"
        payment = ZoomPayment.objects.create(student=request.user, session=session, amount_paid=session.price, currency='UGX', payment_reference=ref, payment_status='pending')
        payload = {"tx_ref": ref, "amount": str(session.price), "currency": "UGX", "redirect_url": request.build_absolute_uri(f"/payments/zoom/verify/{ref}/"), "customer": {"email": request.user.email, "name": request.user.get_full_name(), "phonenumber": request.user.phone or ""}, "customizations": {"title": "CyberTech Academy", "description": f"Payment for: {session.title}"}}
        headers = {"Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}", "Content-Type": "application/json"}
        try:
            resp = requests.post("https://api.flutterwave.com/v3/payments", json=payload, headers=headers, timeout=15)
            data = resp.json()
            if data.get("status") == "success":
                return redirect(data["data"]["link"])
            else:
                messages.error(request, "Payment gateway error. Please try again.")
        except Exception:
            messages.error(request, "Could not connect to payment gateway.")
    return render(request, 'payments/zoom_checkout.html', {'session': session})


@login_required
def zoom_verify(request, ref):
    payment = get_object_or_404(ZoomPayment, payment_reference=ref, student=request.user)
    tx_id = request.GET.get('transaction_id', '')
    status = request.GET.get('status', '')
    if status == 'successful' and tx_id:
        headers = {"Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"}
        try:
            resp = requests.get(f"https://api.flutterwave.com/v3/transactions/{tx_id}/verify", headers=headers, timeout=15)
            data = resp.json()
            if data.get("status") == "success" and data["data"]["status"] == "successful":
                payment.payment_status = 'success'
                payment.flutterwave_tx_id = tx_id
                payment.paid_at = timezone.now()
                payment.save()
                ZoomRegistration.objects.get_or_create(student=request.user, session=payment.session)
                try:
                    send_zoom_access_email(request.user, payment.session)
                except Exception:
                    pass
                messages.success(request, "Payment successful! You now have access to the Zoom session.")
                return redirect('zoom_sessions:detail', pk=payment.session.pk)
        except Exception:
            pass
    payment.payment_status = 'failed'
    payment.save()
    messages.error(request, "Payment could not be verified. Please contact support.")
    return redirect('zoom_sessions:list')


@login_required
def course_checkout(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    already = Enrollment.objects.filter(student=request.user, course=course).exists()
    if already:
        messages.info(request, "You are already enrolled.")
        return redirect('students:learn', course_slug=course_slug)
    if course.is_free:
        Enrollment.objects.create(student=request.user, course=course)
        return redirect('students:learn', course_slug=course_slug)
    if request.method == 'POST':
        ref = f"CR-{uuid.uuid4().hex[:12].upper()}"
        CoursePayment.objects.create(student=request.user, course=course, amount_paid=course.price, currency='UGX', payment_reference=ref, payment_status='pending')
        payload = {"tx_ref": ref, "amount": str(course.price), "currency": "UGX", "redirect_url": request.build_absolute_uri(f"/payments/course/verify/{ref}/"), "customer": {"email": request.user.email, "name": request.user.get_full_name()}, "customizations": {"title": "CyberTech Academy", "description": f"Enrollment: {course.title}"}}
        headers = {"Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}", "Content-Type": "application/json"}
        try:
            resp = requests.post("https://api.flutterwave.com/v3/payments", json=payload, headers=headers, timeout=15)
            data = resp.json()
            if data.get("status") == "success":
                return redirect(data["data"]["link"])
            else:
                messages.error(request, "Payment gateway error. Please try again.")
        except Exception:
            messages.error(request, "Could not connect to payment gateway.")
    return render(request, 'payments/course_checkout.html', {'course': course})


@login_required
def course_verify(request, ref):
    payment = get_object_or_404(CoursePayment, payment_reference=ref, student=request.user)
    tx_id = request.GET.get('transaction_id', '')
    status = request.GET.get('status', '')
    if status == 'successful' and tx_id:
        headers = {"Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"}
        try:
            resp = requests.get(f"https://api.flutterwave.com/v3/transactions/{tx_id}/verify", headers=headers, timeout=15)
            data = resp.json()
            if data.get("status") == "success" and data["data"]["status"] == "successful":
                payment.payment_status = 'success'
                payment.flutterwave_tx_id = tx_id
                payment.paid_at = timezone.now()
                payment.save()
                Enrollment.objects.get_or_create(student=request.user, course=payment.course)
                messages.success(request, f"Enrolled in '{payment.course.title}'! Start learning now.")
                return redirect('students:learn', course_slug=payment.course.slug)
        except Exception:
            pass
    payment.payment_status = 'failed'
    payment.save()
    messages.error(request, "Payment verification failed. Contact support.")
    return redirect('courses:list')
