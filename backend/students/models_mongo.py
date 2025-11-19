from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime, date
from enum import Enum


class GenderChoices(Enum):
    MALE = 'M'
    FEMALE = 'F'


class RiskCategoryChoices(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'


class FeeStatusChoices(Enum):
    PAID = 'paid'
    PENDING = 'pending'
    OVERDUE = 'overdue'
    PARTIAL = 'partial'


class BacklogStatusChoices(Enum):
    PENDING = 'pending'
    CLEARED = 'cleared'
    ATTEMPTING = 'attempting'


class MentorTypeChoices(Enum):
    ACADEMIC = 'academic'
    PERSONAL = 'personal'
    CAREER = 'career'


class NoteTypeChoices(Enum):
    ACADEMIC = 'academic'
    BEHAVIORAL = 'behavioral'
    PERSONAL = 'personal'
    FINANCIAL = 'financial'
    ATTENDANCE = 'attendance'
    OTHER = 'other'


class Department(Document):
    """Department model for organizing students"""
    name = fields.StringField(max_length=100, required=True, unique=True)
    code = fields.StringField(max_length=10, required=True, unique=True)
    created_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'departments',
        'indexes': ['code', 'name']
    }
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Batch(Document):
    """Batch model for organizing students by year"""
    name = fields.StringField(max_length=50, required=True)
    year = fields.IntField(required=True)
    department = fields.ReferenceField(Department, required=True)
    created_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'batches',
        'indexes': [
            ('year', 'department'),
            'year',
            'department'
        ]
    }
    
    def __str__(self):
        return self.name


class Student(Document):
    """Main Student model with comprehensive student information"""
    
    # Personal Information
    student_id = fields.StringField(max_length=20, required=True, unique=True)
    first_name = fields.StringField(max_length=50, required=True)
    last_name = fields.StringField(max_length=50, required=True)
    email = fields.EmailField(required=True, unique=True)
    phone = fields.StringField(max_length=15)
    date_of_birth = fields.DateField(required=True)
    gender = fields.StringField(max_length=1, choices=[choice.value for choice in GenderChoices], required=True)
    
    # Academic Information
    batch = fields.ReferenceField(Batch, required=True)
    current_semester = fields.IntField(min_value=1, max_value=8, required=True)
    cgpa = fields.FloatField(min_value=0.0, max_value=10.0, required=True)
    attendance_percentage = fields.FloatField(min_value=0.0, max_value=100.0, required=True)
    
    # Contact Information
    emergency_contact = fields.StringField(max_length=15)
    address = fields.StringField()
    
    # Guardian Information
    guardian_name = fields.StringField(max_length=100)
    guardian_phone = fields.StringField(max_length=15)
    guardian_email = fields.EmailField()
    guardian_relation = fields.StringField(max_length=50)
    
    # Academic Status
    is_active = fields.BooleanField(default=True)
    enrollment_date = fields.DateField(required=True)
    expected_graduation = fields.DateField()
    
    # Social and Financial Information
    family_income = fields.IntField()
    distance_from_home = fields.IntField()  # in km
    is_hosteler = fields.BooleanField(default=False)
    
    # Financial Information
    fee_status = fields.StringField(
        max_length=20,
        choices=[choice.value for choice in FeeStatusChoices],
        default=FeeStatusChoices.PENDING.value
    )
    total_fee_amount = fields.FloatField(default=0.0)
    paid_amount = fields.FloatField(default=0.0)
    last_payment_date = fields.DateField()
    
    # Risk Assessment Fields
    current_risk_score = fields.FloatField(min_value=0.0, max_value=100.0, default=0.0)
    risk_category = fields.StringField(
        max_length=10,
        choices=[choice.value for choice in RiskCategoryChoices],
        default=RiskCategoryChoices.LOW.value
    )
    last_risk_update = fields.DateTimeField(default=datetime.utcnow)
    
    # Additional Fields
    profile_picture = fields.StringField()  # Store file path or URL
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'students',
        'indexes': [
            'student_id',
            'email',
            'risk_category',
            'current_risk_score',
            'batch',
            ('batch', 'current_semester'),
            'is_active'
        ]
    }
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
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
    
    def __str__(self):
        return f"{self.student_id} - {self.full_name}"


class Attendance(Document):
    """Model to track monthly attendance for students"""
    student = fields.ReferenceField(Student, required=True)
    month = fields.IntField(min_value=1, max_value=12, required=True)
    year = fields.IntField(required=True)
    classes_held = fields.IntField(default=0)
    classes_attended = fields.IntField(default=0)
    
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'attendance',
        'indexes': [
            ('student', 'month', 'year'),
            'student',
            ('year', 'month')
        ]
    }
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    @property
    def attendance_percentage(self):
        if self.classes_held == 0:
            return 0
        return (self.classes_attended / self.classes_held) * 100
    
    def __str__(self):
        return f"{self.student.student_id} - {self.month}/{self.year} ({self.attendance_percentage:.1f}%)"


class StudentBacklog(Document):
    """Model to track student backlogs/failed subjects"""
    student = fields.ReferenceField(Student, required=True)
    subject_name = fields.StringField(max_length=100, required=True)
    subject_code = fields.StringField(max_length=20)
    semester = fields.IntField(required=True)
    academic_year = fields.StringField(max_length=10)  # e.g., "2023-24"
    
    # Status tracking
    status = fields.StringField(
        max_length=20,
        choices=[choice.value for choice in BacklogStatusChoices],
        default=BacklogStatusChoices.PENDING.value
    )
    
    # Dates
    failed_date = fields.DateField()
    cleared_date = fields.DateField()
    
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'student_backlogs',
        'indexes': [
            'student',
            'status',
            ('student', 'semester'),
            'semester'
        ]
    }
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.student_id} - {self.subject_name} ({self.status})"


class StudentMentor(Document):
    """Model to assign mentors to students"""
    student = fields.ReferenceField(Student, required=True)
    mentor_name = fields.StringField(max_length=100, required=True)
    mentor_email = fields.EmailField(required=True)
    
    # Assignment details
    assigned_date = fields.DateField(required=True)
    is_active = fields.BooleanField(default=True)
    
    # Mentor type
    mentor_type = fields.StringField(
        max_length=20,
        choices=[choice.value for choice in MentorTypeChoices],
        default=MentorTypeChoices.ACADEMIC.value
    )
    
    created_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'student_mentors',
        'indexes': [
            'student',
            'mentor_email',
            ('student', 'mentor_type'),
            'is_active'
        ]
    }
    
    def __str__(self):
        return f"{self.student.student_id} -> {self.mentor_name} ({self.mentor_type})"


class StudentNote(Document):
    """Model for mentor notes about students"""
    student = fields.ReferenceField(Student, required=True)
    created_by = fields.StringField(max_length=100, required=True)
    
    note_text = fields.StringField(required=True)
    title = fields.StringField(max_length=200)
    
    # Note categorization
    note_type = fields.StringField(
        max_length=20,
        choices=[choice.value for choice in NoteTypeChoices],
        default=NoteTypeChoices.OTHER.value
    )
    
    # Privacy and access
    is_private = fields.BooleanField(default=False)
    is_important = fields.BooleanField(default=False)
    
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'student_notes',
        'indexes': [
            'student',
            'note_type',
            'created_by',
            'is_important',
            '-created_at'
        ]
    }
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Note for {self.student.student_id} by {self.created_by}"