from rest_framework import serializers
from .models import StudentProfile, Enrollment, LessonProgress
from apps.courses.serializers import CourseListSerializer


class EnrollmentSerializer(serializers.ModelSerializer):
    course          = CourseListSerializer(read_only=True)
    progress_percent = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Enrollment
        fields = ['id', 'course', 'enrolled_at', 'completed', 'completed_at', 'progress_percent']


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = StudentProfile
        fields = ['id', 'learning_mode', 'date_registered', 'is_active',
                  'enrolled_courses_count', 'completed_courses_count']
        read_only_fields = ['id', 'date_registered', 'enrolled_courses_count', 'completed_courses_count']


