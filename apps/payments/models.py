"""
CyberTech Academy - Payments Models
"""
import uuid
from django.db import models
from django.conf import settings
from apps.zoom_sessions.models import ZoomSession
from apps.courses.models import Course


class ZoomPayment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED  = 'failed',  'Failed'

    id                  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student             = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='zoom_payments')
    session             = models.ForeignKey(ZoomSession, on_delete=models.CASCADE, related_name='payments')
    amount_paid         = models.DecimalField(max_digits=10, decimal_places=2)
    currency            = models.CharField(max_length=10, default='UGX')
    payment_reference   = models.CharField(max_length=200, unique=True)
    flutterwave_tx_id   = models.CharField(max_length=200, blank=True)
    payment_status      = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    paid_at             = models.DateTimeField(null=True, blank=True)
    created_at          = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.get_full_name()} | {self.session.title} | {self.payment_status.upper()}"


class CoursePayment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED  = 'failed',  'Failed'

    id                  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student             = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_payments')
    course              = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments')
    amount_paid         = models.DecimalField(max_digits=10, decimal_places=2)
    currency            = models.CharField(max_length=10, default='UGX')
    payment_reference   = models.CharField(max_length=200, unique=True)
    flutterwave_tx_id   = models.CharField(max_length=200, blank=True)
    payment_status      = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    paid_at             = models.DateTimeField(null=True, blank=True)
    created_at          = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.get_full_name()} | {self.course.title} | {self.payment_status.upper()}"
