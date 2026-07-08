from rest_framework import generics, permissions, filters
from .models import Course, Category
from .serializers import CourseListSerializer, CourseDetailSerializer, CategorySerializer


class CategoryListView(generics.ListAPIView):
    queryset           = Category.objects.all()
    serializer_class   = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CourseListView(generics.ListAPIView):
    queryset           = Course.objects.filter(is_published=True).select_related('instructor', 'category')
    serializer_class   = CourseListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['title', 'description']
    ordering_fields    = ['price', 'created_at', 'title']


class CourseDetailView(generics.RetrieveAPIView):
    queryset           = Course.objects.filter(is_published=True)
    serializer_class   = CourseDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field       = 'slug'