from rest_framework import generics, permissions
from django.utils import timezone
from .models import ZoomSession
from .serializers import ZoomSessionSerializer


class ZoomSessionListView(generics.ListAPIView):
    serializer_class   = ZoomSessionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return ZoomSession.objects.filter(
            is_active=True, scheduled_at__gte=timezone.now()
        ).select_related('instructor').order_by('scheduled_at')
