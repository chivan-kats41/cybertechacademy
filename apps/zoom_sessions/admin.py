from django.contrib import admin
from .models import ZoomSession, ZoomRegistration


@admin.register(ZoomSession)
class ZoomSessionAdmin(admin.ModelAdmin):
    list_display  = ('title', 'instructor', 'scheduled_at', 'price', 'max_participants', 'is_active')
    list_filter   = ('is_active',)
    search_fields = ('title', 'instructor__email')
    ordering      = ('-scheduled_at',)


@admin.register(ZoomRegistration)
class ZoomRegistrationAdmin(admin.ModelAdmin):
    list_display  = ('student', 'session', 'registered_at')
    list_filter   = ('session',)
    search_fields = ('student__email', 'session__title')