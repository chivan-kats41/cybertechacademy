"""
CyberTech Academy - Courses Models
"""
import uuid
from django.db import models
from django.conf import settings


class Category(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name        = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(unique=True)
    icon        = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Course(models.Model):
    class Difficulty(models.TextChoices):
        BEGINNER     = 'beginner',     'Beginner'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        ADVANCED     = 'advanced',     'Advanced'

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title          = models.CharField(max_length=200)
    slug           = models.SlugField(unique=True)
    description    = models.TextField()
    category       = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    instructor     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                       null=True, related_name='courses_teaching',
                                       limit_choices_to={'role': 'instructor'})
    thumbnail      = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    price          = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_free        = models.BooleanField(default=False)
    difficulty     = models.CharField(max_length=20, choices=Difficulty.choices, default=Difficulty.BEGINNER)
    duration_hours = models.PositiveIntegerField(default=0)
    is_published   = models.BooleanField(default=False)
    is_featured    = models.BooleanField(default=False)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def total_lessons(self):
        return Lesson.objects.filter(module__course=self).count()

    @property
    def total_enrollments(self):
        return self.enrollments.count()


class Module(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course      = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order       = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class Lesson(models.Model):
    class ContentType(models.TextChoices):
        VIDEO = 'video', 'Video'
        AUDIO = 'audio', 'Audio'
        PDF   = 'pdf',   'PDF Document'
        TEXT  = 'text',  'Text / Article'
        QUIZ  = 'quiz',  'Quiz'

    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module           = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title            = models.CharField(max_length=200)
    content_type     = models.CharField(max_length=10, choices=ContentType.choices, default=ContentType.VIDEO)

    # Video — YouTube embed URL, Vimeo, or direct .mp4 link
    video_url        = models.URLField(blank=True, help_text="YouTube embed URL or direct .mp4 link")

    # File upload — PDF, audio file, or video file
    file_upload      = models.FileField(upload_to='lesson_files/', blank=True, null=True,
                                        help_text="Upload PDF, audio (.mp3/.wav), or video file")

    # Text/article content
    text_content     = models.TextField(blank=True)

    order            = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=0)
    is_preview       = models.BooleanField(default=False, help_text="Free preview — no enrollment needed")
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.module.title} — {self.title}"

    def get_embed_url(self):
        """Convert YouTube watch URL → embed URL if needed."""
        url = self.video_url or ''
        if 'youtube.com/watch?v=' in url:
            vid = url.split('v=')[1].split('&')[0]
            return f"https://www.youtube.com/embed/{vid}?rel=0&modestbranding=1"
        if 'youtu.be/' in url:
            vid = url.split('youtu.be/')[1].split('?')[0]
            return f"https://www.youtube.com/embed/{vid}?rel=0&modestbranding=1"
        if 'vimeo.com/' in url and 'player.vimeo.com' not in url:
            vid = url.rstrip('/').split('/')[-1]
            return f"https://player.vimeo.com/video/{vid}"
        return url  # already embed URL or direct link