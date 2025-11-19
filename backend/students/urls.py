from django.urls import path
from . import views
from . import ml_views
from . import debug_views
from . import simple_views

app_name = 'students'

urlpatterns = [
    # Department URLs - Using simple MongoDB views
    path('departments/', simple_views.department_list, name='department-list-create'),
    path('departments/<int:pk>/', views.DepartmentRetrieveUpdateDestroyView.as_view(), name='department-detail'),
    
    # Batch URLs - Using simple MongoDB views  
    path('batches/', simple_views.batch_list, name='batch-list-create'),
    path('batches/<int:pk>/', views.BatchRetrieveUpdateDestroyView.as_view(), name='batch-detail'),
    
    # Student URLs - Using simple MongoDB views
    path('students/', simple_views.student_list, name='student-list-create'),
    path('students/<int:pk>/', views.StudentRetrieveUpdateDestroyView.as_view(), name='student-detail'),
    
    # Student Backlog URLs
    path('backlogs/', views.StudentBacklogListCreateView.as_view(), name='backlog-list-create'),
    
    # Student Mentor URLs
    path('mentors/', views.StudentMentorListCreateView.as_view(), name='mentor-list-create'),
    
    # Student Note URLs
    path('notes/', views.StudentNoteListCreateView.as_view(), name='note-list-create'),
    
    # Analytics URLs - Using simple MongoDB views
    path('analytics/', simple_views.student_analytics, name='student-analytics'),
    path('dashboard-stats/', simple_views.student_dashboard_stats, name='dashboard-stats'),
    
    # File Upload URLs
    path('upload/', views.upload_students_file, name='upload-students'),
    path('download-template/', views.download_sample_template, name='download-template'),
    
    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard_stats, name='admin-dashboard'),
    path('admin/students/', views.admin_student_management, name='admin-students'),
    path('admin/students/<str:student_id>/update/', views.admin_update_student, name='admin-update-student'),
    path('admin/students/<str:student_id>/delete/', views.admin_delete_student, name='admin-delete-student'),
    path('admin/health/', views.admin_system_health, name='admin-health'),
    
    # Debug URLs
    path('debug/mongodb/', debug_views.test_mongodb_connection, name='debug-mongodb'),
    path('debug/departments/', debug_views.test_department_queries, name='debug-departments'),
    
    # Machine Learning URLs
    path('ml/train/', ml_views.train_ml_models, name='ml-train'),
    path('ml/predict/', ml_views.predict_student_risk, name='ml-predict'),
    path('ml/bulk-predict/', ml_views.bulk_predict_risk, name='ml-bulk-predict'),
    path('ml/model-info/', ml_views.ml_model_info, name='ml-model-info'),
    path('ml/analytics/', ml_views.analytics_dashboard, name='ml-analytics'),
    path('ml/feature-importance/', ml_views.feature_importance_analysis, name='ml-feature-importance'),
]