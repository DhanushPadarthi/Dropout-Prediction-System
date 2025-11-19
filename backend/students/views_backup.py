# Import MongoDB views if available, fallback to Django ORM
try:
    from .views_mongo import (
        student_dashboard_stats, 
        student_analytics, 
        student_list, 
        student_detail
    )
    MONGODB_VIEWS = True
except ImportError:
    MONGODB_VIEWS = False

# Keep original imports for fallback and other views
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
    filterset_fields = ['department', 'year', 'is_active']


class BatchRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Batch.objects.select_related('department').all()
    serializer_class = BatchSerializer


class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.select_related('department', 'batch').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'batch', 'current_semester', 'risk_category', 'is_active']
    search_fields = ['roll_number', 'full_name', 'email']
    ordering_fields = ['current_risk_score', 'created_at', 'full_name']
    ordering = ['-current_risk_score']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return StudentListSerializer
        return StudentSerializer


class StudentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.select_related('department', 'batch').prefetch_related(
        'backlogs', 'notes', 'mentors'
    ).all()
    serializer_class = StudentSerializer


class StudentBacklogListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentBacklogSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'subject_code', 'semester', 'status']
    
    def get_queryset(self):
        return StudentBacklog.objects.select_related('student').all()


class StudentMentorListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentMentorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'mentor', 'is_active']
    
    def get_queryset(self):
        return StudentMentor.objects.select_related('student', 'mentor').all()


class StudentNoteListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentNoteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'created_by', 'note_type']
    
    def get_queryset(self):
        return StudentNote.objects.select_related('student', 'created_by').all()


# MongoDB views are imported at the top, so this Django ORM version is only used as fallback
if not MONGODB_VIEWS:
    @api_view(['GET'])
    def student_analytics(request):
        """Get analytics data for students"""
        try:
        # Check if tables exist first
        from django.db import connection
        table_names = connection.introspection.table_names()
        
        if 'students_student' not in table_names:
            # Return mock data if tables don't exist
            data = {
                'total_students': 0,
                'high_risk_count': 0,
                'risk_distribution': [],
                'department_distribution': [],
                'department_risk_average': [],
                'message': 'Database tables not created yet. Please run migrations.'
            }
        else:
            # Get real data from database
            total_students = Student.objects.filter(is_active=True).count()
            
            # Risk level distribution
            risk_distribution = Student.objects.filter(is_active=True).values('risk_category').annotate(
                count=Count('id')
            ).order_by('risk_category')
            
            # Department-wise student count
            dept_distribution = Student.objects.filter(is_active=True).values(
                'department__name'
            ).annotate(count=Count('id')).order_by('-count')
            
            # Average risk score by department
            dept_risk_avg = Student.objects.filter(is_active=True).values(
                'department__name'
            ).annotate(avg_risk=Avg('current_risk_score')).order_by('-avg_risk')
            
        # High risk students count
        high_risk_count = Student.objects.filter(
            is_active=True, risk_category='HIGH'
        ).count()
        
        data = {
            'total_students': total_students,
            'high_risk_count': high_risk_count,
            'risk_distribution': list(risk_distribution),
            'department_distribution': list(dept_distribution),
            'department_risk_average': list(dept_risk_avg)
        }
        
        return Response(data)
    except Exception as e:
        return Response(
            {'error': str(e), 'details': 'Error in student_analytics view'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# MongoDB views are imported at the top, so this Django ORM version is only used as fallback
if not MONGODB_VIEWS:
    @api_view(['GET'])
    def student_dashboard_stats(request):
        """Get dashboard statistics - Django ORM Fallback"""
        try:
            # Check if tables exist first
            from django.db import connection
            table_names = connection.introspection.table_names()
            
            if 'students_student' not in table_names:
                # Return mock data if tables don't exist
                stats = {
                    'total_students': 0,
                    'high_risk_students': 0,
                    'medium_risk_students': 0,
                    'low_risk_students': 0,
                    'total_backlogs': 0,
                    'active_mentorships': 0,
                    'message': 'Database tables not created yet. Please run migrations.'
                }
            else:
                # Get real data from database
                stats = {
                    'total_students': Student.objects.filter(is_active=True).count(),
                    'high_risk_students': Student.objects.filter(
                        is_active=True, risk_category='HIGH'
                    ).count(),
                    'medium_risk_students': Student.objects.filter(
                        is_active=True, risk_category='MEDIUM'
                    ).count(),
                    'low_risk_students': Student.objects.filter(
                        is_active=True, risk_category='LOW'
                    ).count(),
                    'total_backlogs': StudentBacklog.objects.filter(
                        status='active'
                    ).count(),
                    'active_mentorships': StudentMentor.objects.filter(
                        is_active=True
                    ).count(),
                }
            
            return Response(stats)
        except Exception as e:
            return Response(
                {'error': str(e), 'details': 'Error in student_dashboard_stats view'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )