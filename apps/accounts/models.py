import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User Model extending AbstractUser.
    Supports three roles: Superadmin, Instructor, Student.
    """
    class Role(models.TextChoices):
        SUPERADMIN = 'superadmin', 'Superadmin'
        INSTRUCTOR = 'instructor', 'Instructor'
        STUDENT    = 'student',    'Student'

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email        = models.EmailField(unique=True)
    role         = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    phone        = models.CharField(max_length=20, blank=True)
    country      = models.CharField(max_length=100, blank=True)
    avatar       = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio          = models.TextField(blank=True)
    is_verified  = models.BooleanField(default=False)
    date_joined  = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name        = 'User'
        verbose_name_plural = 'Users'
        ordering            = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}>"

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_instructor(self):
        return self.role == self.Role.INSTRUCTOR

    @property
    def is_superadmin(self):
        return self.role == self.Role.SUPERADMIN