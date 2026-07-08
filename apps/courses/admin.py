from django.contrib import admin
from .models import Category, Course, Module, Lesson


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display        = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}
    search_fields       = ('name',)


class LessonInline(admin.TabularInline):
    model  = Lesson
    extra  = 1
    fields = ('title', 'content_type', 'order', 'duration_minutes', 'is_preview')


class ModuleInline(admin.TabularInline):
    model  = Module
    extra  = 1
    fields = ('title', 'order', 'description')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display   = ('title', 'instructor', 'category', 'difficulty',
                      'price', 'is_free', 'is_published', 'is_featured')
    list_filter    = ('is_published', 'is_free', 'is_featured', 'difficulty', 'category')
    list_editable  = ('is_published', 'is_featured')
    search_fields  = ('title', 'description', 'instructor__email')
    prepopulated_fields = {'slug': ('title',)}
    inlines        = [ModuleInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter  = ('course',)
    inlines      = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'content_type', 'order', 'duration_minutes', 'is_preview')
    list_filter  = ('content_type', 'is_preview', 'module__course')
    search_fields = ('title',)