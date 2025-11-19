# Import MongoDB views if available, fallback to Django ORM
try:
    from .views_mongo import (
        student_dashboard_stats, 
        student_analytics, 
        student_list, 
        student_detail
    )
    MONGODB_VIEWS = True
    print("✅ Using MongoDB views")
except ImportError:
    MONGODB_VIEWS = False
    print("❌ MongoDB views not available, using Django ORM fallback")

# Keep original imports for other views
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from .models import Student, Department, Batch, StudentBacklog, StudentMentor, StudentNote
from .serializers import (
    StudentSerializer, StudentListSerializer, DepartmentSerializer,
    BatchSerializer, StudentBacklogSerializer, StudentMentorSerializer,
    StudentNoteSerializer
)


class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class DepartmentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class BatchListCreateView(generics.ListCreateAPIView):
    queryset = Batch.objects.select_related('department').all()
    serializer_class = BatchSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department', 'year']


class BatchRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Batch.objects.select_related('department').all()
    serializer_class = BatchSerializer


class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.select_related('batch').all()
    serializer_class = StudentListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['risk_category', 'current_semester', 'is_active', 'batch__department']
    search_fields = ['first_name', 'last_name', 'student_id', 'email']
    ordering_fields = ['current_risk_score', 'cgpa', 'attendance_percentage']
    ordering = ['-current_risk_score']


class StudentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.select_related('batch').all()
    serializer_class = StudentSerializer


class StudentBacklogListCreateView(generics.ListCreateAPIView):
    queryset = StudentBacklog.objects.select_related('student').all()
    serializer_class = StudentBacklogSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'status', 'semester']


class StudentMentorListCreateView(generics.ListCreateAPIView):
    queryset = StudentMentor.objects.select_related('student').all()
    serializer_class = StudentMentorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'is_active', 'mentor_type']


class StudentNoteListCreateView(generics.ListCreateAPIView):
    queryset = StudentNote.objects.select_related('student').all()
    serializer_class = StudentNoteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'note_type', 'is_important']


# Django ORM fallback functions (only used if MongoDB views are not available)
if not MONGODB_VIEWS:
    @api_view(['GET'])
    def student_dashboard_stats(request):
        """Get dashboard statistics - Django ORM Fallback"""
        return Response({
            'error': 'MongoDB not configured properly. Please check MongoDB connection.',
            'total_students': 0,
            'database_type': 'SQLite (Fallback)'
        })

    @api_view(['GET'])
    def student_analytics(request):
        """Get analytics data - Django ORM Fallback"""
        return Response({
            'error': 'MongoDB not configured properly. Please check MongoDB connection.',
            'database_type': 'SQLite (Fallback)'
        })