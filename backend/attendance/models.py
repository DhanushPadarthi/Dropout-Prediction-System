from django.db import models
from students.models import Student
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date


class Subject(models.Model):
    """Subject model for tracking different courses"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    credits = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    department = models.ForeignKey('students.Department', on_delete=models.CASCADE)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        ordering = ['semester', 'code']


class AttendanceRecord(models.Model):
    """Individual attendance record for each student per class"""
    
    ATTENDANCE_STATUS = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused Absence'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    # Attendance details
    date = models.DateField(default=date.today)
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS, default='absent')
    
    # Class details
    class_type = models.CharField(
        max_length=20,
        choices=[
            ('lecture', 'Lecture'),
            ('practical', 'Practical'),
            ('tutorial', 'Tutorial'),
            ('seminar', 'Seminar'),
        ],
        default='lecture'
    )
    
    # Time tracking
    class_start_time = models.TimeField()
    class_end_time = models.TimeField()
    marked_at = models.DateTimeField(auto_now_add=True)
    
    # Additional information
    remarks = models.TextField(blank=True)
    marked_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='marked_attendance'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'subject', 'date', 'class_start_time')
        ordering = ['-date', '-class_start_time']
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['subject', 'date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student.student_id} - {self.subject.code} - {self.date} ({self.status})"


class AttendanceSummary(models.Model):
    """Summary model to cache attendance statistics for performance"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_summary')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    # Summary statistics
    total_classes = models.IntegerField(default=0)
    present_classes = models.IntegerField(default=0)
    absent_classes = models.IntegerField(default=0)
    late_classes = models.IntegerField(default=0)
    excused_classes = models.IntegerField(default=0)
    
    # Calculated fields
    attendance_percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    
    # Time period
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.IntegerField()
    
    # Status flags
    is_below_threshold = models.BooleanField(default=False)
    threshold_percentage = models.FloatField(default=75.0)  # Minimum required attendance
    
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'subject', 'month', 'year')
        ordering = ['-year', '-month']
        indexes = [
            models.Index(fields=['student', 'month', 'year']),
            models.Index(fields=['attendance_percentage']),
            models.Index(fields=['is_below_threshold']),
        ]
    
    def __str__(self):
        return f"{self.student.student_id} - {self.subject.code} - {self.month}/{self.year} ({self.attendance_percentage}%)"
    
    def update_summary(self):
        """Update attendance summary based on attendance records"""
        from django.db.models import Count, Q
        
        # Get attendance records for this student, subject, month, and year
        records = AttendanceRecord.objects.filter(
            student=self.student,
            subject=self.subject,
            date__month=self.month,
            date__year=self.year
        )
        
        # Calculate statistics
        self.total_classes = records.count()
        self.present_classes = records.filter(status='present').count()
        self.absent_classes = records.filter(status='absent').count()
        self.late_classes = records.filter(status='late').count()
        self.excused_classes = records.filter(status='excused').count()
        
        # Calculate attendance percentage
        if self.total_classes > 0:
            # Consider 'present' and 'late' as attendance, 'excused' as neutral
            attended_classes = self.present_classes + self.late_classes
            self.attendance_percentage = (attended_classes / self.total_classes) * 100
        else:
            self.attendance_percentage = 0.0
        
        # Check if below threshold
        self.is_below_threshold = self.attendance_percentage < self.threshold_percentage
        
        self.save()


class AttendanceAlert(models.Model):
    """Model to track attendance-based alerts"""
    
    ALERT_TYPES = [
        ('low_attendance', 'Low Attendance'),
        ('consecutive_absence', 'Consecutive Absences'),
        ('sudden_drop', 'Sudden Attendance Drop'),
        ('below_threshold', 'Below Required Threshold'),
    ]
    
    ALERT_SEVERITY = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_alerts')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=ALERT_SEVERITY, default='medium')
    
    # Alert details
    title = models.CharField(max_length=200)
    message = models.TextField()
    current_percentage = models.FloatField()
    threshold_percentage = models.FloatField(default=75.0)
    
    # Status tracking
    is_active = models.BooleanField(default=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Notification tracking
    notification_sent = models.BooleanField(default=False)
    notification_sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'is_active']),
            models.Index(fields=['alert_type', 'severity']),
            models.Index(fields=['is_resolved']),
        ]
    
    def __str__(self):
        return f"{self.student.student_id} - {self.get_alert_type_display()} ({self.severity})"


class AttendancePattern(models.Model):
    """Model to track attendance patterns and trends"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_patterns')
    
    # Pattern analysis
    pattern_type = models.CharField(
        max_length=20,
        choices=[
            ('improving', 'Improving'),
            ('declining', 'Declining'),
            ('stable', 'Stable'),
            ('irregular', 'Irregular'),
        ]
    )
    
    # Statistical data
    average_attendance = models.FloatField()
    trend_direction = models.CharField(
        max_length=10,
        choices=[
            ('up', 'Upward'),
            ('down', 'Downward'),
            ('stable', 'Stable'),
        ]
    )
    
    # Time period for analysis
    analysis_period_start = models.DateField()
    analysis_period_end = models.DateField()
    
    # Pattern confidence and reliability
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    # Additional insights
    insights = models.JSONField(default=dict, blank=True)  # Store pattern insights as JSON
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'pattern_type']),
            models.Index(fields=['trend_direction']),
        ]
    
    def __str__(self):
        return f"{self.student.student_id} - {self.pattern_type} pattern ({self.confidence_score:.2f})"