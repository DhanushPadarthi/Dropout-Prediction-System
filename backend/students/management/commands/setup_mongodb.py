from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, date, timedelta
import random
import mongoengine

class Command(BaseCommand):
    help = 'Test MongoDB connection and create sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--students',
            type=int,
            default=50,
            help='Number of students to create (default: 50)'
        )
        parser.add_argument(
            '--test-connection',
            action='store_true',
            help='Just test MongoDB connection'
        )

    def handle(self, *args, **options):
        self.stdout.write("🔍 Testing MongoDB connection...")
        
        try:
            # Test connection
            from pymongo import MongoClient
            client = MongoClient('mongodb://localhost:27017/')
            
            # Test if MongoDB is running
            client.admin.command('ping')
            self.stdout.write(self.style.SUCCESS("✅ MongoDB is running!"))
            
            # List databases
            db_list = client.list_database_names()
            self.stdout.write(f"📊 Available databases: {db_list}")
            
            if options['test_connection']:
                self.stdout.write("🔍 Connection test completed!")
                return
            
            # Import MongoEngine models
            try:
                from students.models_mongo import Department, Batch, Student, Attendance
                self.stdout.write("✅ MongoEngine models imported successfully")
            except ImportError as e:
                self.stdout.write(self.style.ERROR(f"❌ Failed to import models: {e}"))
                return
            
            # Create sample data
            self.create_sample_data(options['students'])
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ MongoDB connection failed: {e}"))
            self.stdout.write("Make sure MongoDB is running on localhost:27017")
            self.stdout.write("You can start MongoDB service or check MongoDB Compass")

    def create_sample_data(self, num_students):
        """Create sample data in MongoDB"""
        from students.models_mongo import Department, Batch, Student, Attendance
        
        self.stdout.write(f"📝 Creating sample data with {num_students} students...")
        
        # Create Departments
        departments_data = [
            {'name': 'Computer Science Engineering', 'code': 'CSE'},
            {'name': 'Information Technology', 'code': 'IT'},
            {'name': 'Electronics and Communication', 'code': 'ECE'},
            {'name': 'Mechanical Engineering', 'code': 'ME'},
        ]

        departments = []
        for dept_data in departments_data:
            try:
                dept = Department.objects.get(code=dept_data['code'])
                self.stdout.write(f"📋 Department {dept.code} already exists")
            except Department.DoesNotExist:
                dept = Department(
                    name=dept_data['name'],
                    code=dept_data['code']
                )
                dept.save()
                self.stdout.write(f"✅ Created department: {dept.name}")
            departments.append(dept)

        # Create Batches
        current_year = timezone.now().year
        batches = []
        for year in range(current_year - 2, current_year + 1):
            for dept in departments:
                batch_name = f'{dept.code}-{year}'
                try:
                    batch = Batch.objects.get(name=batch_name)
                    self.stdout.write(f"📋 Batch {batch.name} already exists")
                except Batch.DoesNotExist:
                    batch = Batch(
                        name=batch_name,
                        year=year,
                        department=dept
                    )
                    batch.save()
                    self.stdout.write(f"✅ Created batch: {batch.name}")
                batches.append(batch)

        # Sample names
        first_names = ['Aarav', 'Vivaan', 'Aditya', 'Ananya', 'Diya', 'Priya', 'Rohan', 'Aryan', 'Kiran', 'Neha']
        last_names = ['Sharma', 'Verma', 'Singh', 'Kumar', 'Gupta', 'Patel', 'Shah', 'Reddy', 'Rao', 'Nair']

        # Create Students
        for i in range(num_students):
            batch = random.choice(batches)
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            student_id = f"{batch.year % 100:02d}{batch.department.code}{i+1:03d}"
            email = f"{first_name.lower()}.{last_name.lower()}{i+1}@college.edu"
            
            # Check if student already exists
            try:
                existing_student = Student.objects.get(student_id=student_id)
                continue  # Skip if already exists
            except Student.DoesNotExist:
                pass
            
            # Generate academic data
            attendance_percentage = random.uniform(60, 95)
            cgpa = random.uniform(5.5, 9.5)
            
            # Calculate risk score
            risk_score = 0
            if attendance_percentage < 75:
                risk_score += 30
            if cgpa < 6.5:
                risk_score += 25
            risk_score += random.randint(0, 20)
            
            # Determine risk category
            if risk_score >= 60:
                risk_category = 'high'
            elif risk_score >= 30:
                risk_category = 'medium'
            else:
                risk_category = 'low'
            
            # Create student
            student = Student(
                student_id=student_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=f"9{random.randint(100000000, 999999999)}",
                date_of_birth=date(2002, random.randint(1, 12), random.randint(1, 28)),
                gender=random.choice(['M', 'F']),
                batch=batch,
                current_semester=random.randint(1, 8),
                cgpa=round(cgpa, 2),
                attendance_percentage=round(attendance_percentage, 2),
                current_risk_score=round(risk_score, 2),
                risk_category=risk_category,
                family_income=random.randint(300000, 1500000),
                distance_from_home=random.randint(10, 200),
                is_hosteler=random.choice([True, False]),
                is_active=True,
                enrollment_date=date(batch.year, 7, random.randint(1, 15)),
            )
            student.save()
            
            if i % 10 == 0:
                self.stdout.write(f"📝 Created {i+1} students...")

        # Final counts
        total_departments = Department.objects.count()
        total_batches = Batch.objects.count()
        total_students = Student.objects.count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"🎉 Sample data created successfully!\n"
                f"📊 Departments: {total_departments}\n"
                f"📊 Batches: {total_batches}\n"
                f"📊 Students: {total_students}\n"
                f"🔍 View in MongoDB Compass: mongodb://localhost:27017\n"
                f"📊 Database: dropout_prediction_db"
            )
        )