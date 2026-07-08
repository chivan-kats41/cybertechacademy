from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ('email', 'get_full_name', 'role', 'country', 'is_verified', 'is_active', 'date_joined')
    list_filter   = ('role', 'is_verified', 'is_active', 'country')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering      = ('-date_joined',)

    fieldsets = (
        (None,            {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'country', 'avatar', 'bio')}),
        ('Role & Status', {'fields': ('role', 'is_verified', 'is_active', 'is_staff', 'is_superuser')}),
        ('Permissions',   {'fields': ('groups', 'user_permissions')}),
        ('Dates',         {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('email', 'username', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )