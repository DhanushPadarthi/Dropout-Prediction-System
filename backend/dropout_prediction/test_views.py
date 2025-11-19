from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def test_endpoint(request):
    """Simple test endpoint to verify API is working"""
    return Response({
        'status': 'success',
        'message': 'Django API is working!',
        'timestamp': 'now'
    })