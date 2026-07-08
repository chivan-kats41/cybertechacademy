"""
CyberTech Academy - Students Models
Registration, Admission, Enrollment, Progress tracking
"""
import uuid
from django.db import models
from django.conf import settings
from apps.courses.models import Course, Lesson


class StudentProfile(models.Model):

    class LearningMode(models.TextChoices):
        ONLINE = 'online', 'Online Lessons'
        ZOOM   = 'zoom',   'Zoom Sessions'
        BOTH   = 'both',   'Both'

    class AdmissionStatus(models.TextChoices):
        PENDING  = 'pending',  'Pending Review'
        ADMITTED = 'admitted', 'Admitted'
        REJECTED = 'rejected', 'Rejected'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user            = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                           related_name='student_profile')
    course_interest = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='interested_students')
    learning_mode   = models.CharField(max_length=10, choices=LearningMode.choices, default=LearningMode.BOTH)
    date_registered = models.DateTimeField(auto_now_add=True)
    is_active       = models.BooleanField(default=True)
    terms_accepted  = models.BooleanField(default=False)

    # ── Admission fields ──────────────────────────────────────
    admission_status     = models.CharField(
        max_length=10,
        choices=AdmissionStatus.choices,
        default=AdmissionStatus.PENDING
    )
    admitted_at          = models.DateTimeField(null=True, blank=True)
    admission_fee_paid   = models.BooleanField(default=False)
    admission_fee_paid_at = models.DateTimeField(null=True, blank=True)
    admission_notes      = models.TextField(blank=True, help_text="Internal admin notes")

    class Meta:
        verbose_name        = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
        ordering            = ['-date_registered']

    def __str__(self):
        return f"{self.user.get_full_name()} [{self.get_admission_status_display()}]"

    @property
    def can_login(self):
        """Student can only access platform after admission AND fee payment."""
        return (
            self.admission_status == self.AdmissionStatus.ADMITTED
            and self.admission_fee_paid
        )

    @property
    def enrolled_courses_count(self):
        return self.user.enrollments.count()

    @property
    def completed_courses_count(self):
        return self.user.enrollments.filter(completed=True).count()


class AdmissionPayment(models.Model):
    """Tracks the mandatory UGX 20,000 admission fee payment."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED  = 'failed',  'Failed'

    ADMISSION_FEE = 20000  # UGX

    id                  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student             = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                               related_name='admission_payment')
    amount              = models.DecimalField(max_digits=10, decimal_places=2, default=ADMISSION_FEE)
    currency            = models.CharField(max_length=10, default='UGX')
    payment_reference   = models.CharField(max_length=200, unique=True)
    flutterwave_tx_id   = models.CharField(max_length=200, blank=True)
    payment_status      = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    paid_at             = models.DateTimeField(null=True, blank=True)
    created_at          = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.get_full_name()} | Admission Fee | {self.payment_status.upper()}"


class Enrollment(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                    related_name='enrollments')
    course      = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed   = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['student', 'course']
        ordering        = ['-enrolled_at']

    def __str__(self):
        return f"{self.student.get_full_name()} → {self.course.title}"

    @property
    def progress_percent(self):
        total = self.course.total_lessons
        if total == 0:
            return 0
        done = LessonProgress.objects.filter(
            student=self.student,
            lesson__module__course=self.course,
            completed=True
        ).count()
        return int((done / total) * 100)


class LessonProgress(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='lesson_progress')
    lesson     = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress_records')
    completed  = models.BooleanField(default=False)
    watched_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'lesson']

    def __str__(self):
        return f"{'✅' if self.completed else '⏳'} {self.student.get_full_name()} — {self.lesson.title}"