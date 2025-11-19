from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def api_root(request):
    """
    API Root endpoint - provides information about available endpoints
    """
    return Response({
        'message': 'AI-Based Dropout Prediction & Counseling System API',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'students': {
                'departments': '/api/students/departments/',
                'batches': '/api/students/batches/',
                'students': '/api/students/students/',
                'backlogs': '/api/students/backlogs/',
                'mentors': '/api/students/mentors/',
                'notes': '/api/students/notes/',
                'analytics': '/api/students/analytics/',
                'dashboard_stats': '/api/students/dashboard-stats/',
            },
            'attendance': {
                'stats': '/api/attendance/stats/',
                'analytics': '/api/attendance/analytics/',
            }
        },
        'status': 'Running'
    })


@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint
    """
    return Response({
        'status': 'healthy',
        'service': 'AI Dropout Prediction API',
        'timestamp': request.META.get('HTTP_DATE', 'N/A')
    })