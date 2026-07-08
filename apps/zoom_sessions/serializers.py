from rest_framework import serializers
from .models import ZoomSession


class ZoomSessionSerializer(serializers.ModelSerializer):
    instructor_name = serializers.SerializerMethodField()
    is_upcoming     = serializers.BooleanField(read_only=True)
    spots_remaining = serializers.IntegerField(read_only=True)

    class Meta:
        model  = ZoomSession
        fields = ['id', 'title', 'description', 'instructor_name', 'scheduled_at',
                  'duration_minutes', 'price', 'max_participants', 'is_upcoming',
                  'spots_remaining', 'is_active']

    def get_instructor_name(self, obj):
        return obj.instructor.get_full_name() if obj.instructor else None


