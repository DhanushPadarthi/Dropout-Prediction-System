from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Department(models.Model):
    """Department model for organizing students"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Batch(models.Model):
    """Batch model for organizing students by year"""
    name = models.CharField(max_length=50)
    year = models.IntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('year', 'department')
    
    def __str__(self):
        return self.name


class Student(models.Model):
    """Main Student model with comprehensive student information"""
    
    # Personal Information
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    student_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')])
    
    # Academic Information
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    current_semester = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)]
    )
    cgpa = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    attendance_percentage = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    
    # Contact Information
    emergency_contact = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    
    # Guardian Information
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_phone = models.CharField(max_length=15, blank=True)
    guardian_email = models.EmailField(blank=True)
    guardian_relation = models.CharField(max_length=50, blank=True)
    
    # Academic Status
    is_active = models.BooleanField(default=True)
    enrollment_date = models.DateField()
    expected_graduation = models.DateField(null=True, blank=True)
    
    # Social and Financial Information
    family_income = models.IntegerField(null=True, blank=True)
    distance_from_home = models.IntegerField(null=True, blank=True)  # in km
    is_hosteler = models.BooleanField(default=False)
    
    # Financial Information
    fee_status = models.CharField(
        max_length=20,
        choices=[
            ('paid', 'Paid'),
            ('pending', 'Pending'),
            ('overdue', 'Overdue'),
            ('partial', 'Partial'),
        ],
        default='pending'
    )
    total_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_payment_date = models.DateField(null=True, blank=True)
    
    # Risk Assessment Fields
    current_risk_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    risk_category = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low Risk'),
            ('medium', 'Medium Risk'),
            ('high', 'High Risk'),
        ],
        default='low'
    )
    last_risk_update = models.DateTimeField(auto_now=True)
    
    # Additional Fields
    profile_picture = models.ImageField(upload_to='students/profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['student_id']
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['risk_category']),
            models.Index(fields=['current_risk_score']),
            models.Index(fields=['batch']),
        ]
    
    def __str__(self):
        return f"{self.student_id} - {self.full_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def outstanding_fee(self):
        return self.total_fee_amount - self.paid_amount
    
    @property
    def fee_payment_percentage(self):
        if self.total_fee_amount == 0:
            return 100
        return (self.paid_amount / self.total_fee_amount) * 100


class StudentBacklog(models.Model):
    """Model to track student backlogs/failed subjects"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='backlogs')
    subject_name = models.CharField(max_length=100)
    subject_code = models.CharField(max_length=20, blank=True)
    semester = models.IntegerField()
    academic_year = models.CharField(max_length=10, blank=True)  # e.g., "2023-24"
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('cleared', 'Cleared'),
            ('attempting', 'Currently Attempting'),
        ],
        default='pending'
    )
    
    # Dates
    failed_date = models.DateField(null=True, blank=True)
    cleared_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.subject_name} ({self.status})"


class StudentMentor(models.Model):
    """Model to assign mentors to students"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='mentors')
    mentor_name = models.CharField(max_length=100)
    mentor_email = models.EmailField()
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentored_students', null=True, blank=True)
    
    # Assignment details
    assigned_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    # Mentor type
    mentor_type = models.CharField(
        max_length=20,
        choices=[
            ('academic', 'Academic Mentor'),
            ('personal', 'Personal Counselor'),
            ('career', 'Career Advisor'),
        ],
        default='academic'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.student_id} -> {self.mentor_name} ({self.mentor_type})"


class StudentNote(models.Model):
    """Model for mentor notes about students"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='notes')
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.CharField(max_length=100)
    
    note_text = models.TextField()
    title = models.CharField(max_length=200, blank=True)
    
    # Note categorization
    note_type = models.CharField(
        max_length=20,
        choices=[
            ('academic', 'Academic'),
            ('behavioral', 'Behavioral'),
            ('personal', 'Personal'),
            ('financial', 'Financial'),
            ('attendance', 'Attendance'),
            ('other', 'Other'),
        ],
        default='other'
    )
    
    # Privacy and access
    is_private = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note for {self.student.student_id} by {self.created_by}"


class Attendance(models.Model):
    """Model to track monthly attendance for students"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='monthly_attendance')
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.IntegerField()
    classes_held = models.IntegerField(default=0)
    classes_attended = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'month', 'year')
        ordering = ['-year', '-month']
    
    @property
    def attendance_percentage(self):
        if self.classes_held == 0:
            return 0
        return (self.classes_attended / self.classes_held) * 100
    
    def __str__(self):
        return f"{self.student.student_id} - {self.month}/{self.year} ({self.attendance_percentage:.1f}%)"