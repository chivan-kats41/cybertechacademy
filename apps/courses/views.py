"""
CyberTech Academy - Courses Views
Access control: preview = anyone, full = enrolled + admitted students
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404, HttpResponseForbidden
from django.db.models import Q
from .models import Course, Category, Lesson, Module
from apps.students.models import Enrollment, LessonProgress, StudentProfile


def _is_admitted(user):
    if not user.is_authenticated:
        return False
    try:
        return user.student_profile.can_login
    except StudentProfile.DoesNotExist:
        return False


def _has_access(user, lesson):
    """
    Returns True if the user may view this lesson's content.
    Rules:
      - is_preview=True  → anyone
      - enrolled + admitted → full access
      - instructor/superadmin → full access
    """
    if lesson.is_preview:
        return True
    if not user.is_authenticated:
        return False
    if user.role in ('instructor', 'superadmin'):
        return True
    if not _is_admitted(user):
        return False
    return Enrollment.objects.filter(
        student=user, course=lesson.module.course
    ).exists()


# ── Course List ───────────────────────────────────────────────
def course_list(request):
    courses    = Course.objects.filter(is_published=True).select_related('instructor', 'category')
    categories = Category.objects.all()

    cat_slug     = request.GET.get('cat', '')
    difficulty   = request.GET.get('difficulty', '')
    query        = request.GET.get('q', '')
    price_filter = request.GET.get('price', '')

    if cat_slug:
        courses = courses.filter(category__slug=cat_slug)
    if difficulty:
        courses = courses.filter(difficulty=difficulty)
    if query:
        courses = courses.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if price_filter == 'free':
        courses = courses.filter(is_free=True)
    elif price_filter == 'paid':
        courses = courses.filter(is_free=False)

    return render(request, 'courses/list.html', {
        'courses':      courses,
        'categories':   categories,
        'active_cat':   cat_slug,
        'active_diff':  difficulty,
        'active_price': price_filter,
        'search_query': query,
        'difficulties': Course.Difficulty.choices,
        'total_count':  courses.count(),
    })


# ── Course Detail ─────────────────────────────────────────────
def course_detail(request, slug):
    course  = get_object_or_404(Course, slug=slug, is_published=True)
    modules = course.modules.prefetch_related('lessons').all()

    is_enrolled   = False
    user_progress = 0
    is_admitted   = _is_admitted(request.user)

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            student=request.user, course=course
        ).exists()
        if is_enrolled:
            enr = Enrollment.objects.get(student=request.user, course=course)
            user_progress = enr.progress_percent

    related = Course.objects.filter(
        is_published=True, category=course.category
    ).exclude(pk=course.pk)[:3]

    return render(request, 'courses/detail.html', {
        'course':        course,
        'modules':       modules,
        'is_enrolled':   is_enrolled,
        'is_admitted':   is_admitted,
        'user_progress': user_progress,
        'related':       related,
        'total_lessons': course.total_lessons,
    })


# ── Lesson Viewer — the core access-controlled view ───────────
def lesson_view(request, course_slug, lesson_id):
    """
    Serves lesson content with full access control.
    - Preview lessons: open to all (no login required)
    - Full lessons: enrolled + admitted students only
    """
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)

    if not _has_access(request.user, lesson):
        # Not a preview & not enrolled/admitted
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next=/courses/{course_slug}/lesson/{lesson_id}/')
        if not _is_admitted(request.user):
            messages.warning(request, "Complete your admission to access this lesson.")
            return redirect('students:admission_pending')
        # Authenticated + admitted but not enrolled
        messages.warning(request, "Enroll in this course to access lessons.")
        return redirect('courses:detail', slug=course_slug)

    # Mark progress if enrolled
    if request.user.is_authenticated and _is_admitted(request.user):
        enrolled = Enrollment.objects.filter(
            student=request.user, course=course
        ).exists()
        if enrolled:
            LessonProgress.objects.get_or_create(
                student=request.user, lesson=lesson
            )

    # Sidebar: all modules + lessons for navigation
    modules = course.modules.prefetch_related('lessons').all()

    # Completed lesson IDs for sidebar tick marks
    completed_ids = set()
    if request.user.is_authenticated:
        completed_ids = set(
            LessonProgress.objects.filter(
                student=request.user,
                lesson__module__course=course,
                completed=True
            ).values_list('lesson_id', flat=True)
        )

    # Mark complete via POST
    if request.method == 'POST' and request.POST.get('action') == 'complete':
        if request.user.is_authenticated and _is_admitted(request.user):
            progress, _ = LessonProgress.objects.get_or_create(
                student=request.user, lesson=lesson
            )
            progress.completed = True
            progress.save()
            # Check course completion
            from apps.students.models import Enrollment as Enr
            try:
                enr   = Enr.objects.get(student=request.user, course=course)
                total = course.total_lessons
                done  = LessonProgress.objects.filter(
                    student=request.user,
                    lesson__module__course=course,
                    completed=True
                ).count()
                if total > 0 and done >= total:
                    from django.utils import timezone
                    enr.completed    = True
                    enr.completed_at = timezone.now()
                    enr.save()
                    messages.success(request, f"🎉 You completed '{course.title}'!")
            except Enr.DoesNotExist:
                pass
        return redirect('courses:lesson', course_slug=course_slug, lesson_id=lesson_id)

    # Prev / Next lesson navigation
    all_lessons = list(Lesson.objects.filter(
        module__course=course
    ).order_by('module__order', 'order'))
    current_idx = next((i for i, l in enumerate(all_lessons) if str(l.id) == str(lesson.id)), 0)
    prev_lesson = all_lessons[current_idx - 1] if current_idx > 0 else None
    next_lesson = all_lessons[current_idx + 1] if current_idx < len(all_lessons) - 1 else None

    try:
        enrollment  = Enrollment.objects.get(student=request.user, course=course) \
                      if request.user.is_authenticated else None
        progress_obj = LessonProgress.objects.filter(
            student=request.user, lesson=lesson
        ).first() if request.user.is_authenticated else None
    except Exception:
        enrollment   = None
        progress_obj = None

    return render(request, 'courses/lesson_player.html', {
        'course':        course,
        'lesson':        lesson,
        'modules':       modules,
        'completed_ids': completed_ids,
        'enrollment':    enrollment,
        'progress_obj':  progress_obj,
        'prev_lesson':   prev_lesson,
        'next_lesson':   next_lesson,
        'embed_url':     lesson.get_embed_url(),
        'has_full_access': _has_access(request.user, lesson),
    })