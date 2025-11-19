from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('stats/', views.attendance_stats, name='attendance-stats'),
    path('analytics/', views.attendance_analytics, name='attendance-analytics'),
]