from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from django.utils import timezone
import json

try:
    from .models_mongo import Department, Batch, Student, StudentBacklog, StudentMentor, StudentNote, Attendance
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    from .models import Department, Batch, Student, StudentBacklog, StudentMentor, StudentNote


@api_view(['GET'])
def admin_dashboard_stats(request):
    """Get comprehensive admin dashboard statistics"""
    try:
        if MONGODB_AVAILABLE:
            # MongoDB queries
            stats = {
                'database_info': {
                    'type': 'MongoDB',
                    'connection': 'Active',
                    'host': 'localhost:27017',
                    'database': 'dropout_prediction_db'
                },
                'student_stats': {
                    'total_students': Student.objects.count(),
                    'active_students': Student.objects.filter(is_active=True).count(),
                    'inactive_students': Student.objects.filter(is_active=False).count(),
                    'high_risk_students': Student.objects.filter(risk_category='high').count(),
                    'medium_risk_students': Student.objects.filter(risk_category='medium').count(),
                    'low_risk_students': Student.objects.filter(risk_category='low').count(),
                },
                'academic_stats': {
                    'total_departments': Department.objects.count(),
                    'total_batches': Batch.objects.count(),
                    'total_backlogs': StudentBacklog.objects.filter(status='pending').count(),
                    'cleared_backlogs': StudentBacklog.objects.filter(status='cleared').count(),
                },
                'support_stats': {
                    'active_mentorships': StudentMentor.objects.filter(is_active=True).count(),
                    'total_notes': StudentNote.objects.count(),
                    'important_notes': StudentNote.objects.filter(is_important=True).count(),
                    'attendance_records': Attendance.objects.count(),
                },
                'recent_activities': get_recent_activities(),
                'risk_trend': get_risk_trend(),
                'department_breakdown': get_department_breakdown()
            }
        else:
            # Django ORM fallback
            stats = {
                'database_info': {
                    'type': 'SQLite',
                    'connection': 'Active',
                    'message': 'Using SQLite fallback'
                },
                'student_stats': {
                    'total_students': 0,
                    'message': 'MongoDB not available'
                }
            }
        
        return Response({
            'success': True,
            'data': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return Response({
            'error': f'Error fetching admin stats: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def admin_student_management(request):
    """Get student management data with filtering and pagination"""
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        search = request.GET.get('search', '')
        risk_filter = request.GET.get('risk_category', '')
        department_filter = request.GET.get('department', '')
        semester_filter = request.GET.get('semester', '')
        active_filter = request.GET.get('is_active', '')
        
        if MONGODB_AVAILABLE:
            # Build query
            query = {}
            
            if risk_filter:
                query['risk_category'] = risk_filter
            if semester_filter:
                query['current_semester'] = int(semester_filter)
            if active_filter:
                query['is_active'] = active_filter.lower() == 'true'
            
            students = Student.objects.filter(**query)
            
            # Department filter
            if department_filter:
                dept = Department.objects.filter(code=department_filter).first()
                if dept:
                    batches = Batch.objects.filter(department=dept)
                    students = students.filter(batch__in=batches)
            
            # Search filter
            if search:
                # MongoDB text search (simplified)
                search_students = []
                for student in students:
                    if (search.lower() in student.first_name.lower() or 
                        search.lower() in student.last_name.lower() or 
                        search.lower() in student.student_id.lower() or
                        search.lower() in student.email.lower()):
                        search_students.append(student)
                students = search_students
            
            # Pagination
            total_count = len(students) if isinstance(students, list) else students.count()
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            
            if isinstance(students, list):
                paginated_students = students[start_index:end_index]
            else:
                paginated_students = list(students[start_index:end_index])
            
            # Format student data
            student_list = []
            for student in paginated_students:
                student_data = {
                    'id': str(student.id),
                    'student_id': student.student_id,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'phone': student.phone,
                    'current_semester': student.current_semester,
                    'cgpa': student.cgpa,
                    'attendance_percentage': student.attendance_percentage,
                    'risk_category': student.risk_category,
                    'current_risk_score': student.current_risk_score,
                    'batch_name': student.batch.name,
                    'department_name': student.batch.department.name,
                    'department_code': student.batch.department.code,
                    'is_active': student.is_active,
                    'enrollment_date': student.enrollment_date.isoformat() if student.enrollment_date else None,
                    'family_income': student.family_income,
                    'is_hosteler': student.is_hosteler,
                    'created_at': student.created_at.isoformat() if student.created_at else None
                }
                student_list.append(student_data)
            
            return Response({
                'success': True,
                'data': {
                    'students': student_list,
                    'pagination': {
                        'current_page': page,
                        'page_size': page_size,
                        'total_count': total_count,
                        'total_pages': (total_count + page_size - 1) // page_size,
                        'has_next': end_index < total_count,
                        'has_previous': page > 1
                    },
                    'filters': {
                        'search': search,
                        'risk_category': risk_filter,
                        'department': department_filter,
                        'semester': semester_filter,
                        'is_active': active_filter
                    }
                }
            })
        
        else:
            return Response({
                'success': False,
                'error': 'MongoDB not available'
            })
    
    except Exception as e:
        return Response({
            'error': f'Error fetching student management data: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def admin_update_student(request, student_id):
    """Update student information"""
    try:
        if not MONGODB_AVAILABLE:
            return Response({
                'error': 'MongoDB not available'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            student = Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            return Response({
                'error': 'Student not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Update fields from request data
        data = request.data
        updateable_fields = [
            'first_name', 'last_name', 'email', 'phone', 'current_semester',
            'cgpa', 'attendance_percentage', 'family_income', 'distance_from_home',
            'is_hosteler', 'is_active'
        ]
        
        updated_fields = []
        for field in updateable_fields:
            if field in data:
                setattr(student, field, data[field])
                updated_fields.append(field)
        
        # Recalculate risk score
        if any(field in data for field in ['cgpa', 'attendance_percentage', 'family_income', 'distance_from_home']):
            from .file_upload_views import calculate_risk_score, get_risk_category
            
            student_data = {
                'cgpa': student.cgpa,
                'attendance_percentage': student.attendance_percentage,
                'family_income': student.family_income,
                'distance_from_home': student.distance_from_home,
                'current_semester': student.current_semester
            }
            
            new_risk_score = calculate_risk_score(student_data)
            new_risk_category = get_risk_category(new_risk_score)
            
            student.current_risk_score = new_risk_score
            student.risk_category = new_risk_category
            updated_fields.extend(['current_risk_score', 'risk_category'])
        
        student.save()
        
        return Response({
            'success': True,
            'message': f'Student {student_id} updated successfully',
            'updated_fields': updated_fields,
            'student': {
                'student_id': student.student_id,
                'name': f"{student.first_name} {student.last_name}",
                'risk_category': student.risk_category,
                'current_risk_score': student.current_risk_score
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'Error updating student: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def admin_delete_student(request, student_id):
    """Delete student record"""
    try:
        if not MONGODB_AVAILABLE:
            return Response({
                'error': 'MongoDB not available'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            student = Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            return Response({
                'error': 'Student not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        student_name = f"{student.first_name} {student.last_name}"
        student.delete()
        
        return Response({
            'success': True,
            'message': f'Student {student_name} ({student_id}) deleted successfully'
        })
        
    except Exception as e:
        return Response({
            'error': f'Error deleting student: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def admin_system_health(request):
    """Get system health information"""
    try:
        health_info = {
            'timestamp': datetime.now().isoformat(),
            'system_status': 'Healthy',
            'database': {
                'mongodb': {
                    'status': 'Connected' if MONGODB_AVAILABLE else 'Not Available',
                    'host': 'localhost:27017',
                    'database': 'dropout_prediction_db'
                }
            },
            'collections': {},
            'performance': {
                'response_time': 'Good',
                'memory_usage': 'Normal',
                'last_backup': 'Not configured'
            }
        }
        
        if MONGODB_AVAILABLE:
            # Get collection stats
            health_info['collections'] = {
                'students': Student.objects.count(),
                'departments': Department.objects.count(),
                'batches': Batch.objects.count(),
                'attendance': Attendance.objects.count(),
                'backlogs': StudentBacklog.objects.count(),
                'mentors': StudentMentor.objects.count(),
                'notes': StudentNote.objects.count()
            }
        
        return Response({
            'success': True,
            'data': health_info
        })
        
    except Exception as e:
        return Response({
            'error': f'Error fetching system health: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_recent_activities():
    """Get recent system activities"""
    try:
        if not MONGODB_AVAILABLE:
            return []
        
        activities = []
        
        # Recent student enrollments (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_students = Student.objects.filter(created_at__gte=week_ago).order_by('-created_at')[:5]
        
        for student in recent_students:
            activities.append({
                'type': 'enrollment',
                'message': f"New student enrolled: {student.first_name} {student.last_name}",
                'timestamp': student.created_at.isoformat() if student.created_at else None,
                'risk_level': student.risk_category
            })
        
        # Recent high-risk students
        high_risk_students = Student.objects.filter(risk_category='high').order_by('-current_risk_score')[:3]
        
        for student in high_risk_students:
            activities.append({
                'type': 'alert',
                'message': f"High-risk student: {student.first_name} {student.last_name} (Score: {student.current_risk_score})",
                'timestamp': student.last_risk_update.isoformat() if student.last_risk_update else None,
                'risk_level': 'high'
            })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x['timestamp'] or '', reverse=True)
        return activities[:10]
        
    except Exception:
        return []


def get_risk_trend():
    """Get risk trend data for the last 30 days"""
    try:
        if not MONGODB_AVAILABLE:
            return {}
        
        # For now, return current distribution
        # In a real implementation, you'd track historical data
        return {
            'high_risk': Student.objects.filter(risk_category='high').count(),
            'medium_risk': Student.objects.filter(risk_category='medium').count(),
            'low_risk': Student.objects.filter(risk_category='low').count(),
            'trend': 'stable'  # This would be calculated from historical data
        }
        
    except Exception:
        return {}


def get_department_breakdown():
    """Get breakdown by department"""
    try:
        if not MONGODB_AVAILABLE:
            return []
        
        departments = Department.objects.all()
        breakdown = []
        
        for dept in departments:
            batches = Batch.objects.filter(department=dept)
            total_students = 0
            high_risk = 0
            
            for batch in batches:
                batch_students = Student.objects.filter(batch=batch)
                total_students += batch_students.count()
                high_risk += batch_students.filter(risk_category='high').count()
            
            breakdown.append({
                'department_code': dept.code,
                'department_name': dept.name,
                'total_students': total_students,
                'high_risk_students': high_risk,
                'risk_percentage': round((high_risk / total_students * 100) if total_students > 0 else 0, 1)
            })
        
        return breakdown
        
    except Exception:
        return []