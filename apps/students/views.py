"""
CyberTech Academy - Student Views (Admission Gate — hardened)
"""
import uuid, requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, get_backends
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie

from .forms import StudentRegistrationForm
from .models import StudentProfile, AdmissionPayment, Enrollment, LessonProgress
from apps.courses.models import Course, Lesson
from apps.zoom_sessions.models import ZoomSession
from apps.core.email_utils import (
    send_registration_confirmation,
    send_admission_fee_confirmed,
)

ADMISSION_FEE = AdmissionPayment.ADMISSION_FEE


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def _get_fresh_profile(user):
    """Always fetch profile fresh from DB — never use cached ORM."""
    try:
        return StudentProfile.objects.select_related('user').get(user=user)
    except StudentProfile.DoesNotExist:
        return None


def _self_heal(user, profile):
    """
    If a successful payment exists but the profile isn't updated yet,
    fix it automatically instead of blocking the student.
    Returns the healed profile.
    """
    if profile.can_login:
        return profile  # already fine

    payment = AdmissionPayment.objects.filter(
        student=user, payment_status='success'
    ).first()

    if payment:
        # Payment succeeded but profile wasn't updated — fix it now
        StudentProfile.objects.filter(user=user).update(
            admission_status=StudentProfile.AdmissionStatus.ADMITTED,
            admitted_at=payment.paid_at or timezone.now(),
            admission_fee_paid=True,
            admission_fee_paid_at=payment.paid_at or timezone.now(),
        )
        from apps.accounts.models import User as UserModel
        UserModel.objects.filter(pk=user.pk).update(is_active=True)
        # Return fresh profile
        return StudentProfile.objects.get(user=user)

    return profile


def _check_admitted(user):
    """
    Returns True if student is fully admitted and fee paid.
    Instructors and superadmins always pass.
    Always reads fresh from DB.
    """
    if not user.is_authenticated:
        return False
    if hasattr(user, 'role') and user.role in ('instructor', 'superadmin'):
        return True
    profile = _get_fresh_profile(user)
    if profile is None:
        return False
    # Auto-heal if payment succeeded but profile not updated
    profile = _self_heal(user, profile)
    return profile.can_login


# ─────────────────────────────────────────────────────────────
# REGISTRATION
# ─────────────────────────────────────────────────────────────
def register(request):
    if request.user.is_authenticated:
        return redirect('students:dashboard')

    form = StudentRegistrationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        try:
            course = form.cleaned_data.get('course_interest')
            mode   = form.cleaned_data.get('learning_mode', 'both')
            send_registration_confirmation(
                user, course.title if course else 'N/A', mode
            )
        except Exception:
            pass
        return redirect('students:admission_pending')

    return render(request, 'students/register.html', {'form': form})


# ─────────────────────────────────────────────────────────────
# ADMISSION PENDING
# ─────────────────────────────────────────────────────────────
def admission_pending(request):
    return render(request, 'students/admission_pending.html')


# ─────────────────────────────────────────────────────────────
# ADMISSION FEE PAYMENT PAGE
# ─────────────────────────────────────────────────────────────
@ensure_csrf_cookie
def admission_pay(request):
    # If already logged in and already admitted — go straight to dashboard
    if request.user.is_authenticated and _check_admitted(request.user):
        return redirect('students:dashboard')

    email = request.GET.get('email', '')
    error = None

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        try:
            from apps.accounts.models import User
            user    = User.objects.get(email=email)
            profile = _get_fresh_profile(user)
        except Exception:
            error = "No admitted student found with that email. Please check and try again."
            return render(request, 'students/admission_pay.html', {
                'error': error, 'email': email, 'admission_fee': ADMISSION_FEE,
            })

        if profile is None:
            error = "Student profile not found. Please contact support."
            return render(request, 'students/admission_pay.html', {
                'error': error, 'email': email, 'admission_fee': ADMISSION_FEE,
            })

        # Self-heal first
        profile = _self_heal(user, profile)

        if profile.admission_fee_paid:
            messages.success(
                request,
                "Your admission fee is already paid! Please login to access your dashboard."
            )
            return redirect('/accounts/login/')

        if profile.admission_status != StudentProfile.AdmissionStatus.ADMITTED:
            error = "Your application has not been admitted yet. Please wait for our review."
            return render(request, 'students/admission_pay.html', {
                'error': error, 'email': email, 'admission_fee': ADMISSION_FEE,
            })

        # Get or create payment record
        payment, _ = AdmissionPayment.objects.get_or_create(
            student=user,
            defaults={
                'amount':            ADMISSION_FEE,
                'currency':          'UGX',
                'payment_reference': f"ADM-{uuid.uuid4().hex[:12].upper()}",
                'payment_status':    AdmissionPayment.Status.PENDING,
            }
        )

        # Reset failed payments
        if payment.payment_status == AdmissionPayment.Status.FAILED:
            payment.payment_reference = f"ADM-{uuid.uuid4().hex[:12].upper()}"
            payment.payment_status    = AdmissionPayment.Status.PENDING
            payment.save(update_fields=['payment_reference', 'payment_status'])

        # Initiate Flutterwave
        ref     = payment.payment_reference
        payload = {
            "tx_ref":       ref,
            "amount":       str(ADMISSION_FEE),
            "currency":     "UGX",
            "redirect_url": request.build_absolute_uri(f"/admission/verify/{ref}/"),
            "customer": {
                "email":       user.email,
                "name":        user.get_full_name(),
                "phonenumber": user.phone or "",
            },
            "customizations": {
                "title":       "CyberTech Academy",
                "description": "Admission Fee — UGX 20,000",
            },
        }
        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
            "Content-Type":  "application/json",
        }
        try:
            resp = requests.post(
                "https://api.flutterwave.com/v3/payments",
                json=payload, headers=headers, timeout=15
            )
            data = resp.json()
            if data.get("status") == "success":
                return redirect(data["data"]["link"])
            else:
                error = f"Payment gateway error: {data.get('message', 'Please try again.')}."
        except Exception:
            error = "Could not reach payment gateway. Please try again or contact support."

    return render(request, 'students/admission_pay.html', {
        'error': error, 'email': email, 'admission_fee': ADMISSION_FEE,
    })


# ─────────────────────────────────────────────────────────────
# ADMISSION FEE VERIFY — Flutterwave GET callback
# ─────────────────────────────────────────────────────────────
def admission_verify(request, ref):
    payment = get_object_or_404(AdmissionPayment, payment_reference=ref)
    tx_id   = request.GET.get('transaction_id', '')
    status  = request.GET.get('status', '')

    if status == 'successful' and tx_id:
        headers = {"Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"}
        try:
            resp = requests.get(
                f"https://api.flutterwave.com/v3/transactions/{tx_id}/verify",
                headers=headers, timeout=15
            )
            data = resp.json()
            if (data.get("status") == "success"
                    and data["data"]["status"] == "successful"
                    and int(data["data"]["amount"]) >= ADMISSION_FEE):

                # 1. Mark payment success
                payment.payment_status    = AdmissionPayment.Status.SUCCESS
                payment.flutterwave_tx_id = tx_id
                payment.paid_at           = timezone.now()
                payment.save()

                # 2. Update profile via queryset (bypasses ORM cache)
                StudentProfile.objects.filter(user=payment.student).update(
                    admission_status=StudentProfile.AdmissionStatus.ADMITTED,
                    admitted_at=timezone.now(),
                    admission_fee_paid=True,
                    admission_fee_paid_at=timezone.now(),
                )

                # 3. Activate user via queryset
                from apps.accounts.models import User as UserModel
                UserModel.objects.filter(pk=payment.student.pk).update(is_active=True)

                # 4. Re-fetch user completely fresh
                fresh_user = UserModel.objects.get(pk=payment.student.pk)

                # 5. Log student in automatically
                backend = get_backends()[0]
                fresh_user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
                login(request, fresh_user)

                # 6. Send confirmation email
                try:
                    send_admission_fee_confirmed(fresh_user)
                except Exception:
                    pass

                messages.success(
                    request,
                    f"🎉 Payment confirmed! Welcome to CyberTech Academy, {fresh_user.first_name}!"
                )
                return redirect('students:admission_success')

        except Exception:
            pass

    # Payment failed
    payment.payment_status = AdmissionPayment.Status.FAILED
    payment.save(update_fields=['payment_status'])
    messages.error(
        request,
        "Payment could not be verified. Please try again or call +256 705 221 604."
    )
    return redirect('students:admission_pay')


# ─────────────────────────────────────────────────────────────
# ADMISSION SUCCESS
# ─────────────────────────────────────────────────────────────
def admission_success(request):
    return render(request, 'students/admission_success.html')


# ─────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────
@login_required
def dashboard(request):
    if not _check_admitted(request.user):
        profile = _get_fresh_profile(request.user)
        if profile is None:
            messages.error(request, "Student profile not found. Please contact support.")
            return redirect('/')
        if profile.admission_status == StudentProfile.AdmissionStatus.REJECTED:
            messages.error(request, "Your application was not accepted. Contact us for more info.")
            return redirect('/')
        if (profile.admission_status == StudentProfile.AdmissionStatus.ADMITTED
                and not profile.admission_fee_paid):
            messages.warning(
                request,
                "Please complete your admission fee payment to access your dashboard."
            )
            return redirect('students:admission_pay')
        return redirect('students:admission_pending')

    user        = request.user
    enrollments = Enrollment.objects.filter(student=user).select_related('course')
    upcoming    = ZoomSession.objects.filter(
        is_active=True,
        scheduled_at__gte=timezone.now(),
        registrations__student=user
    ).order_by('scheduled_at')[:5]

    return render(request, 'students/dashboard.html', {
        'enrollment_data': [
            {'enrollment': e, 'progress': e.progress_percent} for e in enrollments
        ],
        'upcoming_sessions': upcoming,
        'total_enrolled':    enrollments.count(),
        'total_completed':   enrollments.filter(completed=True).count(),
    })


# ─────────────────────────────────────────────────────────────
# ENROLL
# ─────────────────────────────────────────────────────────────
@login_required
def enroll_course(request, course_slug):
    if not _check_admitted(request.user):
        messages.warning(request, "Complete your admission before enrolling in courses.")
        return redirect('students:admission_pay')
    course  = get_object_or_404(Course, slug=course_slug, is_published=True)
    already = Enrollment.objects.filter(student=request.user, course=course).exists()
    if already:
        messages.info(request, "You are already enrolled in this course.")
        return redirect('courses:detail', slug=course_slug)
    if course.is_free:
        Enrollment.objects.create(student=request.user, course=course)
        messages.success(request, f"Enrolled in '{course.title}'! 🚀")
        return redirect('students:learn', course_slug=course_slug)
    return redirect('payments:course_checkout', course_slug=course_slug)


# ─────────────────────────────────────────────────────────────
# LEARN & LESSON
# ─────────────────────────────────────────────────────────────
@login_required
def learn(request, course_slug):
    if not _check_admitted(request.user):
        return redirect('students:admission_pay')
    course     = get_object_or_404(Course, slug=course_slug, is_published=True)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
    modules    = course.modules.prefetch_related('lessons').all()
    completed_ids = set(
        LessonProgress.objects.filter(
            student=request.user, lesson__module__course=course, completed=True
        ).values_list('lesson_id', flat=True)
    )
    return render(request, 'students/learn.html', {
        'course': course, 'enrollment': enrollment,
        'modules': modules, 'completed_ids': completed_ids,
        'progress': enrollment.progress_percent,
    })


@login_required
def lesson_detail(request, course_slug, lesson_id):
    if not _check_admitted(request.user):
        return redirect('students:admission_pay')
    course      = get_object_or_404(Course, slug=course_slug, is_published=True)
    lesson      = get_object_or_404(Lesson, id=lesson_id, module__course=course)
    enrollment  = get_object_or_404(Enrollment, student=request.user, course=course)
    progress, _ = LessonProgress.objects.get_or_create(student=request.user, lesson=lesson)

    if request.method == 'POST' and request.POST.get('action') == 'complete':
        progress.completed = True
        progress.save()
        total = course.total_lessons
        done  = LessonProgress.objects.filter(
            student=request.user, lesson__module__course=course, completed=True
        ).count()
        if total > 0 and done >= total:
            enrollment.completed    = True
            enrollment.completed_at = timezone.now()
            enrollment.save()
            messages.success(request, f"🎉 You completed '{course.title}'!")
        return redirect('students:lesson', course_slug=course_slug, lesson_id=lesson_id)

    modules = course.modules.prefetch_related('lessons').all()
    completed_ids = set(
        LessonProgress.objects.filter(
            student=request.user, lesson__module__course=course, completed=True
        ).values_list('lesson_id', flat=True)
    )
    return render(request, 'students/lesson_player.html', {
        'course': course, 'lesson': lesson, 'progress_obj': progress,
        'modules': modules, 'completed_ids': completed_ids, 'enrollment': enrollment,
    })


@login_required
def profile(request):
    try:
        student_profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        student_profile = None
    return render(request, 'students/profile.html', {'student_profile': student_profile})