from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import json
from datetime import datetime, timedelta

# Import MongoDB models directly
from .models_mongo import Student, Department, Batch, StudentBacklog, Attendance


@api_view(['GET'])
def student_dashboard_stats(request):
    """Get dashboard statistics for students"""
    try:
        # MongoDB queries
        total_students = Student.objects.count()
        high_risk_students = Student.objects.filter(risk_category='high').count()
        medium_risk_students = Student.objects.filter(risk_category='medium').count()
        low_risk_students = Student.objects.filter(risk_category='low').count()
        active_students = Student.objects.filter(is_active=True).count()
        
        # Get recent enrollments (if field exists)
        try:
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_enrollments = Student.objects.filter(
                enrollment_date__gte=thirty_days_ago
            ).count()
        except:
            recent_enrollments = 0
        
        # Average CGPA and attendance
        students = list(Student.objects.all())
        avg_cgpa = sum(s.cgpa for s in students) / len(students) if students else 0
        avg_attendance = sum(s.attendance_percentage for s in students) / len(students) if students else 0
        
        # Department statistics
        departments_stats = []
        departments = Department.objects.all()
        
        for dept in departments:
            dept_batches = Batch.objects.filter(department=dept)
            dept_students = Student.objects.filter(batch__in=dept_batches)
            dept_count = dept_students.count()
            
            if dept_count > 0:
                dept_high_risk = dept_students.filter(risk_category='high').count()
                departments_stats.append({
                    'name': dept.name,
                    'code': dept.code,
                    'total_students': dept_count,
                    'high_risk_students': dept_high_risk,
                    'risk_percentage': round((dept_high_risk / dept_count) * 100, 2)
                })
        
        # Sample students for quick access
        sample_students = []
        for student in Student.objects.all()[:10]:
            try:
                sample_students.append({
                    'student_id': student.student_id,
                    'name': f"{student.first_name} {student.last_name}",
                    'cgpa': student.cgpa,
                    'risk_category': student.risk_category,
                    'batch': student.batch.name if student.batch else 'N/A'
                })
            except:
                continue
        
        return Response({
            'success': True,
            'data': {
                'total_students': total_students,
                'high_risk_students': high_risk_students,
                'medium_risk_students': medium_risk_students,
                'low_risk_students': low_risk_students,
                'active_students': active_students,
                'recent_enrollments': recent_enrollments,
                'average_cgpa': round(avg_cgpa, 2),
                'average_attendance': round(avg_attendance, 2),
                'departments': departments_stats
            },
            'students': sample_students
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Error fetching dashboard statistics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def student_analytics(request):
    """Get analytics data for students"""
    try:
        # Risk distribution
        high_risk = Student.objects.filter(risk_category='high').count()
        medium_risk = Student.objects.filter(risk_category='medium').count()
        low_risk = Student.objects.filter(risk_category='low').count()
        
        # CGPA distribution
        students = list(Student.objects.all())
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
        
        # Semester distribution
        semester_distribution = {}
        for sem in range(1, 9):
            sem_students = Student.objects.filter(current_semester=sem)
            count = sem_students.count()
            if count > 0:
                high_risk_count = sem_students.filter(risk_category='high').count()
                semester_distribution[f'Semester {sem}'] = {
                    'total': count,
                    'high_risk': high_risk_count,
                    'percentage': round((high_risk_count / count) * 100, 2)
                }
        
        return Response({
            'success': True,
            'analytics': {
                'risk_distribution': {
                    'high': high_risk,
                    'medium': medium_risk,
                    'low': low_risk
                },
                'cgpa_distribution': cgpa_ranges,
                'attendance_distribution': attendance_ranges,
                'semester_distribution': semester_distribution
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Error fetching analytics data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def student_list(request):
    """Get list of all students"""
    try:
        students = []
        
        for student in Student.objects.all():
            try:
                student_data = {
                    'id': str(student.id),
                    'student_id': student.student_id,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'cgpa': student.cgpa,
                    'current_semester': student.current_semester,
                    'attendance_percentage': student.attendance_percentage,
                    'risk_category': student.risk_category,
                    'is_active': student.is_active,
                    'batch_name': student.batch.name if student.batch else 'N/A',
                    'department_name': student.batch.department.name if student.batch and student.batch.department else 'N/A'
                }
                students.append(student_data)
            except Exception as e:
                # Skip students with data issues
                continue
        
        return Response({
            'success': True,
            'students': students,
            'count': len(students)
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Error fetching student list'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def department_list(request):
    """Get list of all departments"""
    try:
        departments = []
        
        for dept in Department.objects.all():
            try:
                # Get batches for this department
                dept_batches = Batch.objects.filter(department=dept)
                batch_count = dept_batches.count()
                
                # Get students in those batches
                dept_students = Student.objects.filter(batch__in=dept_batches)
                student_count = dept_students.count()
                
                department_data = {
                    'id': str(dept.id),
                    'name': dept.name,
                    'code': dept.code,
                    'batch_count': batch_count,
                    'student_count': student_count,
                    'created_at': dept.created_at.isoformat() if dept.created_at else None
                }
                departments.append(department_data)
            except Exception as e:
                # Skip departments with data issues
                continue
        
        return Response({
            'success': True,
            'departments': departments,
            'count': len(departments)
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Error fetching department list'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def batch_list(request):
    """Get list of all batches"""
    try:
        batches = []
        
        for batch in Batch.objects.all():
            try:
                # Get students in this batch
                batch_students = Student.objects.filter(batch=batch)
                student_count = batch_students.count()
                
                batch_data = {
                    'id': str(batch.id),
                    'name': batch.name,
                    'year': batch.year,
                    'department_name': batch.department.name if batch.department else 'N/A',
                    'department_code': batch.department.code if batch.department else 'N/A',
                    'student_count': student_count,
                    'created_at': batch.created_at.isoformat() if batch.created_at else None
                }
                batches.append(batch_data)
            except Exception as e:
                # Skip batches with data issues
                continue
        
        return Response({
            'success': True,
            'batches': batches,
            'count': len(batches)
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Error fetching batch list'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)