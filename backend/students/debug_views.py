from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def test_mongodb_connection(request):
    """Test MongoDB connection and basic queries"""
    try:
        from students.models_mongo import Student, Department, Batch
        
        # Test basic connections
        total_students = Student.objects.count()
        total_departments = Department.objects.count()
        total_batches = Batch.objects.count()
        
        # Test a simple student query
        students = list(Student.objects.all()[:5])
        student_sample = []
        
        for student in students:
            try:
                student_data = {
                    'student_id': student.student_id,
                    'name': f"{student.first_name} {student.last_name}",
                    'batch_name': student.batch.name if student.batch else 'N/A',
                    'department_name': student.batch.department.name if student.batch and student.batch.department else 'N/A',
                    'cgpa': student.cgpa,
                    'risk_category': student.risk_category
                }
                student_sample.append(student_data)
            except Exception as e:
                student_sample.append({
                    'student_id': student.student_id,
                    'error': str(e)
                })
        
        return JsonResponse({
            'success': True,
            'mongodb_connected': True,
            'stats': {
                'total_students': total_students,
                'total_departments': total_departments,
                'total_batches': total_batches
            },
            'student_sample': student_sample
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'mongodb_connected': False,
            'error': str(e),
            'error_type': type(e).__name__
        }, status=500)


@require_http_methods(["GET"])
def test_department_queries(request):
    """Test department-related queries"""
    try:
        from students.models_mongo import Student, Department, Batch
        
        departments = Department.objects.all()
        dept_info = []
        
        for dept in departments:
            try:
                # Get batches for this department
                batches = Batch.objects.filter(department=dept)
                batch_count = batches.count()
                
                # Get students in those batches
                students = Student.objects.filter(batch__in=batches)
                student_count = students.count()
                
                dept_info.append({
                    'department': dept.name,
                    'code': dept.code,
                    'batch_count': batch_count,
                    'student_count': student_count
                })
                
            except Exception as e:
                dept_info.append({
                    'department': dept.name,
                    'code': dept.code,
                    'error': str(e)
                })
        
        return JsonResponse({
            'success': True,
            'department_info': dept_info
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }, status=500)