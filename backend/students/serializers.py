from rest_framework import serializers
from .models import Student, Department, Batch, StudentBacklog, StudentMentor, StudentNote


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class BatchSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Batch
        fields = '__all__'


class StudentBacklogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentBacklog
        fields = '__all__'


class StudentNoteSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = StudentNote
        fields = '__all__'


class StudentMentorSerializer(serializers.ModelSerializer):
    mentor_name = serializers.CharField(source='mentor.get_full_name', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    class Meta:
        model = StudentMentor
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    batch_name = serializers.CharField(source='batch.name', read_only=True)
    backlogs = StudentBacklogSerializer(many=True, read_only=True)
    notes = StudentNoteSerializer(many=True, read_only=True)
    mentors = StudentMentorSerializer(many=True, read_only=True)
    
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'current_risk_score', 'risk_category')


class StudentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    batch_name = serializers.CharField(source='batch.name', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'roll_number', 'full_name', 'email', 'phone',
            'department_name', 'batch_name', 'current_semester',
            'current_risk_score', 'risk_category', 'is_active', 'created_at'
        ]