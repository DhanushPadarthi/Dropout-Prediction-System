from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from ml_models.dropout_prediction import ml_predictor
from datetime import datetime


@csrf_exempt
@require_http_methods(["POST"])
def train_ml_models(request):
    """Train the ML models with current student data"""
    try:
        print("🚀 Starting ML model training...")
        result = ml_predictor.train_models()
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'message': 'ML models trained successfully',
                'data': {
                    'performance_metrics': result['performance'],
                    'feature_importance': result['feature_importance'],
                    'training_data_size': result['training_data_size'],
                    'models_trained': list(result['performance'].keys())
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': result['message'],
                'error': result['error']
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error training ML models',
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def predict_student_risk(request):
    """Predict dropout risk for a specific student"""
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        model_name = data.get('model_name', 'random_forest')
        
        if not student_id:
            return JsonResponse({
                'success': False,
                'message': 'Student ID is required'
            }, status=400)
        
        # Get student data from MongoDB
        try:
            from students.models_mongo import Student
            student = Student.objects.get(student_id=student_id)
            
            # Prepare student data for prediction
            from datetime import date
            age = (date.today() - student.date_of_birth).days / 365.25 if student.date_of_birth else 20
            fee_payment_ratio = (student.paid_amount / student.total_fee_amount) if student.total_fee_amount > 0 else 1.0
            
            student_data = {
                'current_semester': student.current_semester,
                'cgpa': student.cgpa,
                'attendance_percentage': student.attendance_percentage,
                'family_income': student.family_income or 500000,
                'distance_from_home': student.distance_from_home or 50,
                'is_hosteler': student.is_hosteler,
                'gender': student.gender,
                'department': student.batch.department.code,
                'age': age,
                'fee_payment_ratio': fee_payment_ratio
            }
            
            # Get prediction
            prediction = ml_predictor.predict_dropout_risk(student_data, model_name)
            
            if 'error' in prediction:
                return JsonResponse({
                    'success': False,
                    'message': 'Error making prediction',
                    'error': prediction['error']
                }, status=500)
            
            return JsonResponse({
                'success': True,
                'student_id': student_id,
                'student_name': f"{student.first_name} {student.last_name}",
                'prediction': prediction,
                'timestamp': datetime.now().isoformat()
            })
            
        except Student.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': f'Student with ID {student_id} not found'
            }, status=404)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error predicting student risk',
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def bulk_predict_risk(request):
    """Predict dropout risk for multiple students"""
    try:
        data = json.loads(request.body)
        student_ids = data.get('student_ids', [])
        model_name = data.get('model_name', 'random_forest')
        limit = data.get('limit', 50)  # Default limit to prevent overload
        
        # If no specific student IDs provided, get all (with limit)
        if not student_ids:
            student_ids = None
            
        result = ml_predictor.bulk_predict(student_ids, model_name)
        
        if result['success']:
            # Sort by risk level (high risk first)
            predictions = result['predictions']
            predictions.sort(key=lambda x: x.get('probability_high_risk', 0), reverse=True)
            
            return JsonResponse({
                'success': True,
                'predictions': predictions[:limit],
                'total_analyzed': result['total_analyzed'],
                'model_used': model_name,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Error in bulk prediction',
                'error': result['error']
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error in bulk prediction',
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def ml_model_info(request):
    """Get information about trained ML models"""
    try:
        info = ml_predictor.get_model_info()
        
        return JsonResponse({
            'success': True,
            'model_info': info,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error getting model information',
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def analytics_dashboard(request):
    """Get advanced analytics data for dashboard"""
    try:
        from students.models_mongo import Student, Department
        
        # Basic statistics
        total_students = Student.objects.count()
        high_risk_students = Student.objects.filter(risk_category='high').count()
        medium_risk_students = Student.objects.filter(risk_category='medium').count()
        low_risk_students = Student.objects.filter(risk_category='low').count()
        
        # Department-wise analysis
        departments = Department.objects.all()
        dept_analysis = []
        
        for dept in departments:
            # Get all batches for this department - MongoDB approach
            from students.models_mongo import Batch
            dept_batches = Batch.objects.filter(department=dept)
            
            # Get students in those batches
            dept_students = Student.objects.filter(batch__in=dept_batches)
            dept_total = dept_students.count()
            
            if dept_total > 0:
                dept_high_risk = dept_students.filter(risk_category='high').count()
                dept_medium_risk = dept_students.filter(risk_category='medium').count()
                dept_low_risk = dept_students.filter(risk_category='low').count()
                
                # Calculate average metrics
                dept_students_list = list(dept_students)
                if dept_students_list:
                    avg_cgpa = sum(s.cgpa for s in dept_students_list) / len(dept_students_list)
                    avg_attendance = sum(s.attendance_percentage for s in dept_students_list) / len(dept_students_list)
                else:
                    avg_cgpa = 0
                    avg_attendance = 0
                
                dept_analysis.append({
                    'department': dept.name,
                    'code': dept.code,
                    'total_students': dept_total,
                    'high_risk': dept_high_risk,
                    'medium_risk': dept_medium_risk,
                    'low_risk': dept_low_risk,
                    'high_risk_percentage': round((dept_high_risk / dept_total) * 100, 2) if dept_total > 0 else 0,
                    'average_cgpa': round(avg_cgpa, 2),
                    'average_attendance': round(avg_attendance, 2)
                })
        
        # Semester-wise analysis
        semester_analysis = {}
        for semester in range(1, 9):
            sem_students = Student.objects.filter(current_semester=semester)
            sem_count = sem_students.count()
            
            if sem_count > 0:
                sem_high_risk = sem_students.filter(risk_category='high').count()
                semester_analysis[f'semester_{semester}'] = {
                    'total': sem_count,
                    'high_risk': sem_high_risk,
                    'risk_percentage': round((sem_high_risk / sem_count) * 100, 2)
                }
        
        # CGPA distribution
        cgpa_ranges = {
            '9.0-10.0': Student.objects.filter(cgpa__gte=9.0).count(),
            '8.0-8.9': Student.objects.filter(cgpa__gte=8.0, cgpa__lt=9.0).count(),
            '7.0-7.9': Student.objects.filter(cgpa__gte=7.0, cgpa__lt=8.0).count(),
            '6.0-6.9': Student.objects.filter(cgpa__gte=6.0, cgpa__lt=7.0).count(),
            'Below 6.0': Student.objects.filter(cgpa__lt=6.0).count()
        }
        
        # Attendance distribution
        attendance_ranges = {
            '90-100%': Student.objects.filter(attendance_percentage__gte=90).count(),
            '80-89%': Student.objects.filter(attendance_percentage__gte=80, attendance_percentage__lt=90).count(),
            '70-79%': Student.objects.filter(attendance_percentage__gte=70, attendance_percentage__lt=80).count(),
            '60-69%': Student.objects.filter(attendance_percentage__gte=60, attendance_percentage__lt=70).count(),
            'Below 60%': Student.objects.filter(attendance_percentage__lt=60).count()
        }
        
        return JsonResponse({
            'success': True,
            'analytics': {
                'overview': {
                    'total_students': total_students,
                    'high_risk_students': high_risk_students,
                    'medium_risk_students': medium_risk_students,
                    'low_risk_students': low_risk_students,
                    'high_risk_percentage': round((high_risk_students / total_students) * 100, 2) if total_students > 0 else 0
                },
                'department_analysis': dept_analysis,
                'semester_analysis': semester_analysis,
                'cgpa_distribution': cgpa_ranges,
                'attendance_distribution': attendance_ranges
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error getting analytics data',
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def feature_importance_analysis(request):
    """Get feature importance analysis from trained models"""
    try:
        info = ml_predictor.get_model_info()
        
        if not info['is_trained']:
            return JsonResponse({
                'success': False,
                'message': 'ML models are not trained yet. Please train models first.'
            }, status=400)
        
        # Prepare feature importance data for visualization
        feature_importance = info.get('feature_importance', {})
        
        # Combine feature importance from all models
        combined_importance = {}
        for model_name, importance_dict in feature_importance.items():
            for feature, importance in importance_dict.items():
                if feature not in combined_importance:
                    combined_importance[feature] = []
                combined_importance[feature].append({
                    'model': model_name,
                    'importance': round(importance, 4)
                })
        
        # Calculate average importance
        avg_importance = {}
        for feature, model_importances in combined_importance.items():
            avg_importance[feature] = round(
                sum(mi['importance'] for mi in model_importances) / len(model_importances), 4
            )
        
        # Sort by average importance
        sorted_features = sorted(avg_importance.items(), key=lambda x: x[1], reverse=True)
        
        return JsonResponse({
            'success': True,
            'feature_analysis': {
                'individual_model_importance': feature_importance,
                'combined_importance': combined_importance,
                'average_importance': dict(sorted_features),
                'top_features': sorted_features[:5]  # Top 5 most important features
            },
            'model_performance': info.get('performance_metrics', {}),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error getting feature importance analysis',
            'error': str(e)
        }, status=500)