from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
from students.models import Department, Batch, Student, StudentBacklog, StudentMentor, StudentNote, Attendance

class Command(BaseCommand):
    help = 'Create comprehensive sample data for the dropout prediction system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--students',
            type=int,
            default=200,
            help='Number of students to create (default: 200)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Student.objects.all().delete()
            Department.objects.all().delete()
            Batch.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        # Create Departments
        departments_data = [
            {'name': 'Computer Science Engineering', 'code': 'CSE'},
            {'name': 'Information Technology', 'code': 'IT'},
            {'name': 'Electronics and Communication', 'code': 'ECE'},
            {'name': 'Mechanical Engineering', 'code': 'ME'},
            {'name': 'Civil Engineering', 'code': 'CE'},
            {'name': 'Electrical Engineering', 'code': 'EE'},
        ]

        departments = []
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                name=dept_data['name'],
                code=dept_data['code']
            )
            departments.append(dept)
            if created:
                self.stdout.write(f'Created department: {dept.name}')

        # Create Batches
        current_year = timezone.now().year
        batches = []
        for year in range(current_year - 4, current_year + 1):
            for dept in departments:
                batch, created = Batch.objects.get_or_create(
                    name=f'{dept.code}-{year}',
                    year=year,
                    department=dept
                )
                batches.append(batch)
                if created:
                    self.stdout.write(f'Created batch: {batch.name}')

        # Sample student names
        first_names = [
            'Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Reyansh', 'Ayaan', 'Krishna', 'Ishaan',
            'Ananya', 'Diya', 'Priya', 'Kavya', 'Aadhya', 'Sara', 'Myra', 'Aanya', 'Ira', 'Pihu',
            'Rohan', 'Aryan', 'Kiran', 'Neha', 'Rahul', 'Shreya', 'Amit', 'Pooja', 'Vikram', 'Divya'
        ]
        
        last_names = [
            'Sharma', 'Verma', 'Singh', 'Kumar', 'Gupta', 'Agarwal', 'Jain', 'Patel', 'Shah', 'Reddy',
            'Rao', 'Nair', 'Iyer', 'Menon', 'Chopra', 'Malhotra', 'Bansal', 'Srivastava', 'Tiwari', 'Pandey'
        ]

        # Create Students
        self.stdout.write(f'Creating {options["students"]} students...')
        
        for i in range(options['students']):
            batch = random.choice(batches)
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            # Generate realistic student ID
            student_id = f"{batch.year % 100:02d}{batch.department.code}{i+1:03d}"
            
            # Generate email
            email = f"{first_name.lower()}.{last_name.lower()}{i+1}@college.edu"
            
            # Calculate semester based on batch year
            years_since_start = current_year - batch.year
            current_semester = min(8, max(1, years_since_start * 2 + random.randint(0, 1)))
            
            # Generate realistic academic data
            attendance_percentage = random.uniform(45, 98)
            
            # Risk calculation based on multiple factors
            risk_factors = []
            
            # Attendance risk
            if attendance_percentage < 60:
                risk_factors.append(30)
            elif attendance_percentage < 75:
                risk_factors.append(15)
            else:
                risk_factors.append(5)
            
            # Academic performance risk
            cgpa = random.uniform(4.0, 9.5)
            if cgpa < 6.0:
                risk_factors.append(25)
            elif cgpa < 7.0:
                risk_factors.append(10)
            else:
                risk_factors.append(2)
            
            # Financial risk
            financial_risk = random.choice([0, 5, 15, 25])
            risk_factors.append(financial_risk)
            
            # Personal risk
            personal_risk = random.choice([0, 3, 8, 15])
            risk_factors.append(personal_risk)
            
            current_risk_score = min(100, sum(risk_factors) + random.randint(-10, 10))
            
            # Determine risk category
            if current_risk_score >= 70:
                risk_category = 'high'
            elif current_risk_score >= 40:
                risk_category = 'medium'
            else:
                risk_category = 'low'
            
            # Create student
            student = Student.objects.create(
                student_id=student_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=f"9{random.randint(100000000, 999999999)}",
                date_of_birth=datetime(
                    batch.year - random.randint(18, 22),
                    random.randint(1, 12),
                    random.randint(1, 28)
                ).date(),
                gender=random.choice(['M', 'F']),
                batch=batch,
                current_semester=current_semester,
                cgpa=round(cgpa, 2),
                attendance_percentage=round(attendance_percentage, 2),
                current_risk_score=round(current_risk_score, 2),
                risk_category=risk_category,
                family_income=random.randint(200000, 2000000),
                distance_from_home=random.randint(5, 500),
                is_hosteler=random.choice([True, False]),
                is_active=random.choice([True, True, True, False]),  # 75% active
                enrollment_date=datetime(batch.year, random.randint(6, 8), random.randint(1, 28)).date(),
            )
            
            # Create attendance records
            for month in range(1, 13):
                if month <= timezone.now().month or batch.year < current_year:
                    attendance = Attendance.objects.create(
                        student=student,
                        month=month,
                        year=current_year if batch.year == current_year else batch.year + random.randint(1, 3),
                        classes_held=random.randint(20, 25),
                        classes_attended=random.randint(
                            int(20 * (attendance_percentage - 10) / 100),
                            int(25 * (attendance_percentage + 5) / 100)
                        )
                    )
            
            # Create backlogs for some students
            if current_risk_score > 50 and random.random() < 0.4:
                num_backlogs = random.randint(1, min(4, current_semester))
                subjects = [
                    'Mathematics-I', 'Physics', 'Chemistry', 'Programming Fundamentals',
                    'Data Structures', 'Database Systems', 'Operating Systems', 'Computer Networks',
                    'Software Engineering', 'Web Technologies', 'Machine Learning', 'Algorithms'
                ]
                
                for _ in range(num_backlogs):
                    StudentBacklog.objects.create(
                        student=student,
                        subject_name=random.choice(subjects),
                        semester=random.randint(1, current_semester),
                        status=random.choice(['pending', 'cleared'])
                    )
            
            # Create mentor assignments
            if random.random() < 0.7:  # 70% students have mentors
                StudentMentor.objects.create(
                    student=student,
                    mentor_name=f"Prof. {random.choice(first_names)} {random.choice(last_names)}",
                    mentor_email=f"mentor{i+1}@college.edu",
                    assigned_date=student.enrollment_date + timedelta(days=random.randint(30, 365))
                )
            
            # Create notes for high-risk students
            if risk_category in ['high', 'medium'] and random.random() < 0.6:
                notes = [
                    "Student showing irregular attendance patterns",
                    "Academic performance declining in recent semester",
                    "Financial difficulties reported by student",
                    "Family issues affecting academic focus",
                    "Peer group influence concerns",
                    "Lack of interest in core subjects",
                    "Career guidance session recommended",
                    "Extra academic support provided"
                ]
                
                StudentNote.objects.create(
                    student=student,
                    note_text=random.choice(notes),
                    note_type=random.choice(['academic', 'personal', 'financial', 'other']),
                    created_by=f"Counselor {random.randint(1, 5)}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data:\n'
                f'- {Department.objects.count()} departments\n'
                f'- {Batch.objects.count()} batches\n'
                f'- {Student.objects.count()} students\n'
                f'- {StudentBacklog.objects.count()} backlogs\n'
                f'- {StudentMentor.objects.count()} mentor assignments\n'
                f'- {StudentNote.objects.count()} student notes\n'
                f'- {Attendance.objects.count()} attendance records'
            )
        )