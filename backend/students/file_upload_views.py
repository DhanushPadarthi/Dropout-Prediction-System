from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
import io
from datetime import datetime, date
import re
from django.core.files.storage import default_storage
import logging

# Configure logging
logger = logging.getLogger(__name__)

try:
    from .models_mongo import Department, Batch, Student
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    from .models import Department, Batch, Student


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_students_file(request):
    """
    Upload and process Excel/CSV file with student data
    
    Expected columns:
    - student_id (required)
    - first_name (required)
    - last_name (required)
    - email (required)
    - phone
    - date_of_birth (YYYY-MM-DD or DD/MM/YYYY)
    - gender (M/F)
    - batch_name (required)
    - department_code (required)
    - current_semester
    - cgpa
    - attendance_percentage
    - family_income
    - distance_from_home
    - is_hosteler (True/False/1/0/Yes/No)
    """
    
    if 'file' not in request.FILES:
        return Response({
            'error': 'No file provided',
            'message': 'Please upload an Excel or CSV file'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    uploaded_file = request.FILES['file']
    
    # Validate file type
    allowed_extensions = ['.xlsx', '.xls', '.csv']
    file_extension = None
    for ext in allowed_extensions:
        if uploaded_file.name.lower().endswith(ext):
            file_extension = ext
            break
    
    if not file_extension:
        return Response({
            'error': 'Invalid file type',
            'message': f'Please upload a file with one of these extensions: {", ".join(allowed_extensions)}',
            'allowed_extensions': allowed_extensions
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Read the file
        if file_extension == '.csv':
            df = pd.read_csv(io.StringIO(uploaded_file.read().decode('utf-8')))
        else:
            df = pd.read_excel(uploaded_file)
        
        # Validate required columns
        required_columns = ['student_id', 'first_name', 'last_name', 'email', 'batch_name', 'department_code']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return Response({
                'error': 'Missing required columns',
                'missing_columns': missing_columns,
                'required_columns': required_columns,
                'found_columns': list(df.columns)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Process the data
        results = process_student_data(df)
        
        return Response({
            'message': 'File processed successfully',
            'results': results,
            'database_type': 'MongoDB' if MONGODB_AVAILABLE else 'SQLite'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return Response({
            'error': 'Error processing file',
            'details': str(e),
            'message': 'Please check the file format and data validity'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def process_student_data(df):
    """Process the pandas DataFrame and create/update student records"""
    results = {
        'total_rows': len(df),
        'successful_imports': 0,
        'skipped_records': 0,
        'errors': [],
        'created_departments': [],
        'created_batches': [],
        'student_summery': []
    }
    
    # Clean the data
    df = df.fillna('')  # Replace NaN with empty strings
    
    # Track created departments and batches
    departments_cache = {}
    batches_cache = {}
    
    for index, row in df.iterrows():
        try:
            # Validate and process each row
            student_data = validate_and_clean_row(row, index + 2)  # +2 for Excel row number (header + 0-index)
            
            if student_data['errors']:
                results['errors'].extend(student_data['errors'])
                results['skipped_records'] += 1
                continue
            
            # Get or create department
            dept_code = student_data['department_code'].upper()
            if dept_code not in departments_cache:
                if MONGODB_AVAILABLE:
                    try:
                        dept = Department.objects.get(code=dept_code)
                    except Department.DoesNotExist:
                        # Create new department with default name
                        dept = Department(
                            code=dept_code,
                            name=f"{dept_code} Department"
                        )
                        dept.save()
                        results['created_departments'].append(dept_code)
                else:
                    dept, created = Department.objects.get_or_create(
                        code=dept_code,
                        defaults={'name': f"{dept_code} Department"}
                    )
                    if created:
                        results['created_departments'].append(dept_code)
                
                departments_cache[dept_code] = dept
            else:
                dept = departments_cache[dept_code]
            
            # Get or create batch
            batch_name = student_data['batch_name']
            batch_key = f"{dept_code}_{batch_name}"
            
            if batch_key not in batches_cache:
                # Extract year from batch name (assuming format like "CSE-2024" or "2024-CSE")
                year_match = re.search(r'20\d{2}', batch_name)
                batch_year = int(year_match.group()) if year_match else datetime.now().year
                
                if MONGODB_AVAILABLE:
                    try:
                        batch = Batch.objects.get(name=batch_name, department=dept)
                    except Batch.DoesNotExist:
                        batch = Batch(
                            name=batch_name,
                            year=batch_year,
                            department=dept
                        )
                        batch.save()
                        results['created_batches'].append(batch_name)
                else:
                    batch, created = Batch.objects.get_or_create(
                        name=batch_name,
                        department=dept,
                        defaults={'year': batch_year}
                    )
                    if created:
                        results['created_batches'].append(batch_name)
                
                batches_cache[batch_key] = batch
            else:
                batch = batches_cache[batch_key]
            
            # Check if student already exists
            student_id = student_data['student_id']
            
            if MONGODB_AVAILABLE:
                try:
                    existing_student = Student.objects.get(student_id=student_id)
                    results['errors'].append(f"Row {index + 2}: Student {student_id} already exists")
                    results['skipped_records'] += 1
                    continue
                except Student.DoesNotExist:
                    pass
            else:
                if Student.objects.filter(student_id=student_id).exists():
                    results['errors'].append(f"Row {index + 2}: Student {student_id} already exists")
                    results['skipped_records'] += 1
                    continue
            
            # Calculate risk score
            risk_score = calculate_risk_score(student_data)
            risk_category = get_risk_category(risk_score)
            
            # Create student record
            student = Student(
                student_id=student_id,
                first_name=student_data['first_name'],
                last_name=student_data['last_name'],
                email=student_data['email'],
                phone=student_data.get('phone', ''),
                date_of_birth=student_data.get('date_of_birth'),
                gender=student_data.get('gender', 'M'),
                batch=batch,
                current_semester=student_data.get('current_semester', 1),
                cgpa=student_data.get('cgpa', 0.0),
                attendance_percentage=student_data.get('attendance_percentage', 0.0),
                current_risk_score=risk_score,
                risk_category=risk_category,
                family_income=student_data.get('family_income'),
                distance_from_home=student_data.get('distance_from_home'),
                is_hosteler=student_data.get('is_hosteler', False),
                is_active=True,
                enrollment_date=student_data.get('enrollment_date', date.today()),
            )
            student.save()
            
            results['successful_imports'] += 1
            results['student_summery'].append({
                'student_id': student_id,
                'name': f"{student_data['first_name']} {student_data['last_name']}",
                'risk_category': risk_category,
                'batch': batch_name
            })
            
        except Exception as e:
            error_msg = f"Row {index + 2}: Error processing record - {str(e)}"
            results['errors'].append(error_msg)
            results['skipped_records'] += 1
            logger.error(error_msg)
    
    return results


def validate_and_clean_row(row, row_number):
    """Validate and clean individual row data"""
    cleaned_data = {}
    errors = []
    
    # Required fields
    required_fields = {
        'student_id': str,
        'first_name': str,
        'last_name': str,
        'email': str,
        'batch_name': str,
        'department_code': str
    }
    
    for field, field_type in required_fields.items():
        value = str(row.get(field, '')).strip()
        if not value:
            errors.append(f"Row {row_number}: Missing required field '{field}'")
        else:
            cleaned_data[field] = value
    
    # Email validation
    if 'email' in cleaned_data:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, cleaned_data['email']):
            errors.append(f"Row {row_number}: Invalid email format")
    
    # Optional fields with validation
    optional_fields = {
        'phone': {'type': str, 'pattern': r'^\d{10}$'},
        'gender': {'type': str, 'choices': ['M', 'F', 'Male', 'Female']},
        'current_semester': {'type': int, 'min': 1, 'max': 8},
        'cgpa': {'type': float, 'min': 0.0, 'max': 10.0},
        'attendance_percentage': {'type': float, 'min': 0.0, 'max': 100.0},
        'family_income': {'type': int, 'min': 0},
        'distance_from_home': {'type': int, 'min': 0},
    }
    
    for field, validation in optional_fields.items():
        value = row.get(field, '')
        if value and str(value).strip():
            try:
                if validation['type'] == int:
                    cleaned_value = int(float(str(value)))  # Handle "1.0" -> 1
                elif validation['type'] == float:
                    cleaned_value = float(value)
                else:
                    cleaned_value = str(value).strip()
                
                # Additional validations
                if 'min' in validation and cleaned_value < validation['min']:
                    errors.append(f"Row {row_number}: {field} must be >= {validation['min']}")
                elif 'max' in validation and cleaned_value > validation['max']:
                    errors.append(f"Row {row_number}: {field} must be <= {validation['max']}")
                elif 'choices' in validation and cleaned_value not in validation['choices']:
                    errors.append(f"Row {row_number}: {field} must be one of {validation['choices']}")
                elif 'pattern' in validation and not re.match(validation['pattern'], str(cleaned_value)):
                    errors.append(f"Row {row_number}: {field} format is invalid")
                else:
                    cleaned_data[field] = cleaned_value
                    
            except (ValueError, TypeError):
                errors.append(f"Row {row_number}: Invalid {field} format")
    
    # Date of birth processing
    dob_value = row.get('date_of_birth', '')
    if dob_value and str(dob_value).strip():
        try:
            # Try multiple date formats
            dob_str = str(dob_value).strip()
            date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']
            
            parsed_date = None
            for date_format in date_formats:
                try:
                    parsed_date = datetime.strptime(dob_str, date_format).date()
                    break
                except ValueError:
                    continue
            
            if parsed_date:
                cleaned_data['date_of_birth'] = parsed_date
            else:
                errors.append(f"Row {row_number}: Invalid date_of_birth format. Use YYYY-MM-DD or DD/MM/YYYY")
                
        except Exception:
            errors.append(f"Row {row_number}: Error parsing date_of_birth")
    
    # Boolean field processing
    hosteler_value = row.get('is_hosteler', '')
    if hosteler_value and str(hosteler_value).strip():
        hosteler_str = str(hosteler_value).strip().lower()
        if hosteler_str in ['true', '1', 'yes', 'y']:
            cleaned_data['is_hosteler'] = True
        elif hosteler_str in ['false', '0', 'no', 'n']:
            cleaned_data['is_hosteler'] = False
        else:
            errors.append(f"Row {row_number}: is_hosteler must be True/False, 1/0, or Yes/No")
    
    # Gender normalization
    if 'gender' in cleaned_data:
        gender = cleaned_data['gender'].lower()
        if gender in ['male', 'm']:
            cleaned_data['gender'] = 'M'
        elif gender in ['female', 'f']:
            cleaned_data['gender'] = 'F'
    
    cleaned_data['errors'] = errors
    return cleaned_data


def calculate_risk_score(student_data):
    """Calculate risk score based on student data"""
    risk_score = 0
    
    # Attendance risk (0-30 points)
    attendance = student_data.get('attendance_percentage', 100)
    if attendance < 60:
        risk_score += 30
    elif attendance < 75:
        risk_score += 15
    elif attendance < 85:
        risk_score += 5
    
    # CGPA risk (0-25 points)
    cgpa = student_data.get('cgpa', 10.0)
    if cgpa < 5.0:
        risk_score += 25
    elif cgpa < 6.5:
        risk_score += 15
    elif cgpa < 7.5:
        risk_score += 8
    
    # Financial risk (0-20 points)
    family_income = student_data.get('family_income', 1000000)
    if family_income < 200000:
        risk_score += 20
    elif family_income < 500000:
        risk_score += 10
    
    # Distance risk (0-15 points)
    distance = student_data.get('distance_from_home', 0)
    if distance > 500:
        risk_score += 15
    elif distance > 200:
        risk_score += 8
    elif distance > 100:
        risk_score += 5
    
    # Semester risk (0-10 points)
    semester = student_data.get('current_semester', 1)
    if semester > 6:
        risk_score += 10
    elif semester > 4:
        risk_score += 5
    
    return min(100, risk_score)


def get_risk_category(risk_score):
    """Determine risk category based on score"""
    if risk_score >= 70:
        return 'high'
    elif risk_score >= 40:
        return 'medium'
    else:
        return 'low'


@api_view(['GET'])
def download_sample_template(request):
    """Download a sample Excel template for student data upload"""
    
    try:
        # Create sample data
        sample_data = {
            'student_id': ['21CSE001', '21CSE002', '21IT001'],
            'first_name': ['Aarav', 'Diya', 'Rohan'],
            'last_name': ['Sharma', 'Patel', 'Kumar'],
            'email': ['aarav.sharma@college.edu', 'diya.patel@college.edu', 'rohan.kumar@college.edu'],
            'phone': ['9876543210', '9876543211', '9876543212'],
            'date_of_birth': ['2003-05-15', '2003-07-22', '2003-03-10'],
            'gender': ['M', 'F', 'M'],
            'batch_name': ['CSE-2021', 'CSE-2021', 'IT-2021'],
            'department_code': ['CSE', 'CSE', 'IT'],
            'current_semester': [6, 6, 6],
            'cgpa': [8.5, 9.2, 7.8],
            'attendance_percentage': [85.5, 92.0, 78.5],
            'family_income': [500000, 800000, 350000],
            'distance_from_home': [50, 25, 150],
            'is_hosteler': ['Yes', 'No', 'Yes']
        }
        
        # Create DataFrame
        df = pd.DataFrame(sample_data)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Students', index=False)
            
            # Add instructions sheet
            instructions = pd.DataFrame({
                'Field': [
                    'student_id', 'first_name', 'last_name', 'email', 'phone', 
                    'date_of_birth', 'gender', 'batch_name', 'department_code',
                    'current_semester', 'cgpa', 'attendance_percentage', 
                    'family_income', 'distance_from_home', 'is_hosteler'
                ],
                'Required': [
                    'Yes', 'Yes', 'Yes', 'Yes', 'No', 'No', 'No', 'Yes', 'Yes',
                    'No', 'No', 'No', 'No', 'No', 'No'
                ],
                'Format/Rules': [
                    'Unique identifier (e.g., 21CSE001)',
                    'First name of student',
                    'Last name of student', 
                    'Valid email address',
                    '10-digit phone number',
                    'YYYY-MM-DD or DD/MM/YYYY format',
                    'M/F or Male/Female',
                    'Batch name (e.g., CSE-2021)',
                    'Department code (e.g., CSE, IT, ECE)',
                    'Current semester (1-8)',
                    'CGPA (0.0-10.0)',
                    'Attendance percentage (0-100)',
                    'Family income in rupees',
                    'Distance from home in kilometers',
                    'Yes/No or True/False or 1/0'
                ]
            })
            instructions.to_excel(writer, sheet_name='Instructions', index=False)
        
        output.seek(0)
        
        # Return file response
        from django.http import HttpResponse
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="student_upload_template.xlsx"'
        return response
        
    except Exception as e:
        return Response({
            'error': 'Error generating template',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)