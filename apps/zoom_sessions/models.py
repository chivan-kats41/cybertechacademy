"""
CyberTech Academy - Zoom Sessions Models
Live paid sessions with payment gating
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class ZoomSession(models.Model):
    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title            = models.CharField(max_length=200)
    description      = models.TextField()
    instructor       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                         null=True, related_name='zoom_sessions_hosting',
                                         limit_choices_to={'role': 'instructor'})
    zoom_link        = models.URLField(help_text="Only revealed after successful payment")
    scheduled_at     = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    price            = models.DecimalField(max_digits=10, decimal_places=2)
    max_participants = models.PositiveIntegerField(default=50)
    thumbnail        = models.ImageField(upload_to='session_thumbnails/', blank=True, null=True)
    is_active        = models.BooleanField(default=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scheduled_at']

    def __str__(self):
        return f"{self.title} — {self.scheduled_at.strftime('%d %b %Y %H:%M')}"

    @property
    def is_upcoming(self):
        return self.scheduled_at > timezone.now()

    @property
    def spots_remaining(self):
        paid = self.payments.filter(payment_status='success').count()
        return max(0, self.max_participants - paid)

    @property
    def is_full(self):
        return self.spots_remaining == 0


class ZoomRegistration(models.Model):
    """Tracks which students are registered for a session (post payment)."""
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='zoom_registrations')
    session    = models.ForeignKey(ZoomSession, on_delete=models.CASCADE,
                                   related_name='registrations')
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'session']

    def __str__(self):
        return f"{self.student.get_full_name()} → {self.session.title}"