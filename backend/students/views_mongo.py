from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import json
from datetime import datetime, timedelta
from django.utils import timezone

try:
    from .models_mongo import Student, Department, Batch, StudentBacklog, Attendance
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    from .models import Student, Department, Batch, StudentBacklog, Attendance


@api_view(['GET'])
def student_dashboard_stats(request):
    """Get dashboard statistics for students"""
    try:
        if MONGODB_AVAILABLE:
            # MongoDB queries
            total_students = Student.objects.count()
            high_risk_students = Student.objects.filter(risk_category='high').count()
            medium_risk_students = Student.objects.filter(risk_category='medium').count()
            low_risk_students = Student.objects.filter(risk_category='low').count()
            active_students = Student.objects.filter(is_active=True).count()
            
            # Get recent enrollments (last 30 days)
            try:
                thirty_days_ago = datetime.now() - timedelta(days=30)
                recent_enrollments = Student.objects.filter(
                    enrollment_date__gte=thirty_days_ago
                ).count()
            except:
                # If enrollment_date field doesn't exist or has issues, default to 0
                recent_enrollments = 0
            
            # Average CGPA
            students = list(Student.objects.all())
            avg_cgpa = sum(s.cgpa for s in students) / len(students) if students else 0
            
            # Average attendance
            avg_attendance = sum(s.attendance_percentage for s in students) / len(students) if students else 0
            
        else:
            # Django ORM fallback
            total_students = Student.objects.count()
            high_risk_students = Student.objects.filter(risk_category='high').count()
            medium_risk_students = Student.objects.filter(risk_category='medium').count()
            low_risk_students = Student.objects.filter(risk_category='low').count()
            active_students = Student.objects.filter(is_active=True).count()
            
            thirty_days_ago = timezone.now().date() - timedelta(days=30)
            recent_enrollments = Student.objects.filter(
                enrollment_date__gte=thirty_days_ago
            ).count()
            
            from django.db.models import Avg
            avg_cgpa = Student.objects.aggregate(Avg('cgpa'))['cgpa__avg'] or 0
            avg_attendance = Student.objects.aggregate(Avg('attendance_percentage'))['attendance_percentage__avg'] or 0

        return Response({
            'total_students': total_students,
            'active_students': active_students,
            'high_risk_students': high_risk_students,
            'medium_risk_students': medium_risk_students,
            'low_risk_students': low_risk_students,
            'recent_enrollments': recent_enrollments,
            'avg_cgpa': round(avg_cgpa, 2),
            'avg_attendance': round(avg_attendance, 2),
            'database_type': 'MongoDB' if MONGODB_AVAILABLE else 'SQLite'
        })
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching dashboard stats: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def student_analytics(request):
    """Get analytics data for students"""
    try:
        if MONGODB_AVAILABLE:
            # MongoDB queries
            students = list(Student.objects.all())
            
            # Risk distribution
            risk_distribution = {
                'high': Student.objects.filter(risk_category='high').count(),
                'medium': Student.objects.filter(risk_category='medium').count(),
                'low': Student.objects.filter(risk_category='low').count()
            }
            
            # Department-wise distribution
            departments = list(Department.objects.all())
            dept_distribution = []
            for dept in departments:
                batches = list(Batch.objects.filter(department=dept))
                dept_count = 0
                for batch in batches:
                    dept_count += Student.objects.filter(batch=batch).count()
                dept_distribution.append({
                    'name': dept.name,
                    'code': dept.code,
                    'count': dept_count
                })
            
            # CGPA distribution
            cgpa_ranges = {
                '9.0-10.0': len([s for s in students if s.cgpa >= 9.0]),
                '8.0-8.9': len([s for s in students if 8.0 <= s.cgpa < 9.0]),
                '7.0-7.9': len([s for s in students if 7.0 <= s.cgpa < 8.0]),
                '6.0-6.9': len([s for s in students if 6.0 <= s.cgpa < 7.0]),
                'Below 6.0': len([s for s in students if s.cgpa < 6.0])
            }
            
            # Attendance distribution
            attendance_ranges = {
                '90-100%': len([s for s in students if s.attendance_percentage >= 90]),
                '80-89%': len([s for s in students if 80 <= s.attendance_percentage < 90]),
                '70-79%': len([s for s in students if 70 <= s.attendance_percentage < 80]),
                '60-69%': len([s for s in students if 60 <= s.attendance_percentage < 70]),
                'Below 60%': len([s for s in students if s.attendance_percentage < 60])
            }
            
        else:
            # Django ORM fallback
            risk_distribution = {
                'high': Student.objects.filter(risk_category='high').count(),
                'medium': Student.objects.filter(risk_category='medium').count(),
                'low': Student.objects.filter(risk_category='low').count()
            }
            
            dept_distribution = []
            for dept in Department.objects.all():
                dept_count = Student.objects.filter(batch__department=dept).count()
                dept_distribution.append({
                    'name': dept.name,
                    'code': dept.code,
                    'count': dept_count
                })
            
            # For simplicity, using raw queries for ranges in Django
            from django.db.models import Count, Q
            cgpa_ranges = {
                '9.0-10.0': Student.objects.filter(cgpa__gte=9.0).count(),
                '8.0-8.9': Student.objects.filter(cgpa__gte=8.0, cgpa__lt=9.0).count(),
                '7.0-7.9': Student.objects.filter(cgpa__gte=7.0, cgpa__lt=8.0).count(),
                '6.0-6.9': Student.objects.filter(cgpa__gte=6.0, cgpa__lt=7.0).count(),
                'Below 6.0': Student.objects.filter(cgpa__lt=6.0).count()
            }
            
            attendance_ranges = {
                '90-100%': Student.objects.filter(attendance_percentage__gte=90).count(),
                '80-89%': Student.objects.filter(attendance_percentage__gte=80, attendance_percentage__lt=90).count(),
                '70-79%': Student.objects.filter(attendance_percentage__gte=70, attendance_percentage__lt=80).count(),
                '60-69%': Student.objects.filter(attendance_percentage__gte=60, attendance_percentage__lt=70).count(),
                'Below 60%': Student.objects.filter(attendance_percentage__lt=60).count()
            }

        return Response({
            'risk_distribution': risk_distribution,
            'department_distribution': dept_distribution,
            'cgpa_distribution': cgpa_ranges,
            'attendance_distribution': attendance_ranges,
            'database_type': 'MongoDB' if MONGODB_AVAILABLE else 'SQLite'
        })
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching analytics: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def student_list(request):
    """Get list of students with filtering"""
    try:
        # Get query parameters
        risk_category = request.GET.get('risk_category', None)
        department = request.GET.get('department', None)
        semester = request.GET.get('semester', None)
        search = request.GET.get('search', None)
        
        if MONGODB_AVAILABLE:
            # MongoDB queries
            query = {}
            
            if risk_category:
                query['risk_category'] = risk_category
            if semester:
                query['current_semester'] = int(semester)
            
            students = Student.objects.filter(**query)
            
            if department:
                dept = Department.objects.filter(code=department).first()
                if dept:
                    batches = Batch.objects.filter(department=dept)
                    students = students.filter(batch__in=batches)
            
            if search:
                # MongoDB text search (simplified)
                students = students.filter(
                    first_name__icontains=search
                ) | students.filter(
                    last_name__icontains=search
                ) | students.filter(
                    student_id__icontains=search
                )
            
            # Convert to list for JSON serialization
            student_list = []
            for student in students[:50]:  # Limit to 50 results
                student_data = {
                    'student_id': student.student_id,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'current_semester': student.current_semester,
                    'cgpa': student.cgpa,
                    'attendance_percentage': student.attendance_percentage,
                    'risk_category': student.risk_category,
                    'current_risk_score': student.current_risk_score,
                    'batch_name': student.batch.name,
                    'department_name': student.batch.department.name,
                    'is_active': student.is_active
                }
                student_list.append(student_data)
            
        else:
            # Django ORM fallback
            students = Student.objects.all()
            
            if risk_category:
                students = students.filter(risk_category=risk_category)
            if department:
                students = students.filter(batch__department__code=department)
            if semester:
                students = students.filter(current_semester=int(semester))
            if search:
                from django.db.models import Q
                students = students.filter(
                    Q(first_name__icontains=search) |
                    Q(last_name__icontains=search) |
                    Q(student_id__icontains=search)
                )
            
            student_list = []
            for student in students[:50]:
                student_data = {
                    'student_id': student.student_id,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'current_semester': student.current_semester,
                    'cgpa': student.cgpa,
                    'attendance_percentage': student.attendance_percentage,
                    'risk_category': student.risk_category,
                    'current_risk_score': student.current_risk_score,
                    'batch_name': student.batch.name,
                    'department_name': student.batch.department.name,
                    'is_active': student.is_active
                }
                student_list.append(student_data)

        return Response({
            'students': student_list,
            'total_count': len(student_list),
            'database_type': 'MongoDB' if MONGODB_AVAILABLE else 'SQLite'
        })
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching student list: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def student_detail(request, student_id):
    """Get detailed information for a specific student"""
    try:
        if MONGODB_AVAILABLE:
            student = Student.objects.filter(student_id=student_id).first()
            if not student:
                return Response(
                    {'error': 'Student not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get related data
            backlogs = list(StudentBacklog.objects.filter(student=student))
            attendance_records = list(Attendance.objects.filter(student=student).order_by('-year', '-month'))
            
            student_data = {
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'phone': student.phone,
                'date_of_birth': student.date_of_birth.isoformat() if student.date_of_birth else None,
                'gender': student.gender,
                'current_semester': student.current_semester,
                'cgpa': student.cgpa,
                'attendance_percentage': student.attendance_percentage,
                'risk_category': student.risk_category,
                'current_risk_score': student.current_risk_score,
                'batch_name': student.batch.name,
                'department_name': student.batch.department.name,
                'family_income': student.family_income,
                'distance_from_home': student.distance_from_home,
                'is_hosteler': student.is_hosteler,
                'is_active': student.is_active,
                'enrollment_date': student.enrollment_date.isoformat() if student.enrollment_date else None,
                'backlogs': [
                    {
                        'subject_name': b.subject_name,
                        'semester': b.semester,
                        'status': b.status
                    } for b in backlogs
                ],
                'attendance_records': [
                    {
                        'month': a.month,
                        'year': a.year,
                        'classes_held': a.classes_held,
                        'classes_attended': a.classes_attended,
                        'percentage': a.attendance_percentage
                    } for a in attendance_records[:12]  # Last 12 months
                ]
            }
            
        else:
            # Django ORM fallback
            try:
                student = Student.objects.get(student_id=student_id)
            except Student.DoesNotExist:
                return Response(
                    {'error': 'Student not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            student_data = {
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'phone': student.phone,
                'date_of_birth': student.date_of_birth.isoformat() if student.date_of_birth else None,
                'gender': student.gender,
                'current_semester': student.current_semester,
                'cgpa': student.cgpa,
                'attendance_percentage': student.attendance_percentage,
                'risk_category': student.risk_category,
                'current_risk_score': student.current_risk_score,
                'batch_name': student.batch.name,
                'department_name': student.batch.department.name if hasattr(student.batch, 'department') else 'N/A',
                'family_income': student.family_income,
                'distance_from_home': student.distance_from_home,
                'is_hosteler': student.is_hosteler,
                'is_active': student.is_active,
                'enrollment_date': student.enrollment_date.isoformat() if student.enrollment_date else None,
                'backlogs': [],
                'attendance_records': []
            }

        return Response({
            'student': student_data,
            'database_type': 'MongoDB' if MONGODB_AVAILABLE else 'SQLite'
        })
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching student details: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )