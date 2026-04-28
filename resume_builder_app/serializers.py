from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, Resume, Education, Experience, Skill, 
    Project, Certification, Language, ResumeGeneration
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = '__all__'


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = '__all__'


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'


class ResumeSerializer(serializers.ModelSerializer):
    educations = EducationSerializer(many=True, read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Resume
        fields = '__all__'


class ResumeGenerationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ResumeGeneration
        fields = '__all__'


class AIResumeRequestSerializer(serializers.Serializer):
    job_title = serializers.CharField(max_length=200)
    years_of_experience = serializers.IntegerField(min_value=0, max_value=50)
    skills = serializers.ListField(child=serializers.CharField(), required=False)
    education_level = serializers.CharField(max_length=100, required=False)
    industry = serializers.CharField(max_length=100, required=False)
    additional_info = serializers.CharField(required=False) 