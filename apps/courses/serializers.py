from rest_framework import serializers
from .models import Category, Course, Module, Lesson


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ['id', 'name', 'slug', 'icon', 'description']


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Lesson
        fields = ['id', 'title', 'content_type', 'video_url',
                  'order', 'duration_minutes', 'is_preview']


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model  = Module
        fields = ['id', 'title', 'description', 'order', 'lessons']


class CourseListSerializer(serializers.ModelSerializer):
    category         = CategorySerializer(read_only=True)
    instructor_name  = serializers.SerializerMethodField()
    total_lessons    = serializers.IntegerField(read_only=True)
    total_enrollments = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Course
        fields = ['id', 'title', 'slug', 'description', 'category', 'instructor_name',
                  'thumbnail', 'price', 'is_free', 'difficulty', 'duration_hours',
                  'is_featured', 'total_lessons', 'total_enrollments', 'created_at']

    def get_instructor_name(self, obj):
        return obj.instructor.get_full_name() if obj.instructor else None


class CourseDetailSerializer(CourseListSerializer):
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + ['modules']