from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import datetime

from .models import (
    UserProfile, Resume, Education, Experience, Skill, 
    Project, Certification, Language
)
from .serializers import (
    UserProfileSerializer, ResumeSerializer, EducationSerializer,
    ExperienceSerializer, SkillSerializer, ProjectSerializer,
    CertificationSerializer, LanguageSerializer
)


# Public Views
def home(request):
    """Public home page"""
    return render(request, 'resume_builder_app/home.html')


def signup(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})


# Web Views
@login_required
def dashboard(request):
    """Main dashboard view"""
    resumes = Resume.objects.filter(user=request.user).order_by('-updated_at')
    context = {
        'resumes': resumes,
    }
    return render(request, 'resume_builder_app/dashboard.html', context)


@login_required
def resume_builder(request, resume_id=None):
    """Resume builder interface"""
    resume = None
    if resume_id:
        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    if request.method == 'POST':
        # Debug: Print form data
        print("Form data received:")
        for key, value in request.POST.items():
            print(f"  {key}: {value}")
        
        # Handle form submission
        try:
            if resume_id:
                # Update existing resume
                resume.title = request.POST.get('title', f"{request.POST.get('first_name', '')} {request.POST.get('last_name', '')} - Resume")
                resume.template = request.POST.get('template', 'modern')
                resume.summary = request.POST.get('summary', '')
                resume.save()
            else:
                # Create new resume
                resume = Resume.objects.create(
                    user=request.user,
                    title=request.POST.get('title', f"{request.POST.get('first_name', '')} {request.POST.get('last_name', '')} - Resume"),
                    template=request.POST.get('template', 'modern'),
                    summary=request.POST.get('summary', '')
                )
            
            # Update user profile if provided
            if request.POST.get('first_name') or request.POST.get('last_name'):
                user = request.user
                user.first_name = request.POST.get('first_name', user.first_name)
                user.last_name = request.POST.get('last_name', user.last_name)
                user.email = request.POST.get('email', user.email)
                user.save()
            
            # Create or update user profile
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.phone = request.POST.get('phone', profile.phone)
            profile.address = request.POST.get('address', profile.address)
            profile.linkedin_url = request.POST.get('linkedin_url', profile.linkedin_url)
            profile.github_url = request.POST.get('github_url', profile.github_url)
            profile.save()
            
            # Process form data for related objects
            _process_experiences(request, resume)
            _process_education(request, resume)
            _process_skills(request, resume)
            _process_projects(request, resume)
            _process_certifications(request, resume)
            
            messages.success(request, 'Resume saved successfully!')
            return redirect('preview_resume', resume_id=resume.id)
            
        except Exception as e:
            messages.error(request, f'Error saving resume: {str(e)}')
    
    # Get user profile
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None
    
    context = {
        'resume': resume,
        'user_profile': user_profile,
        'templates': Resume.RESUME_TEMPLATES,
        'experiences': resume.experiences.all() if resume else [],
        'educations': resume.educations.all() if resume else [],
        'skills': resume.skills.all() if resume else [],
        'projects': resume.projects.all() if resume else [],
        'certifications': resume.certifications.all() if resume else [],
    }
    return render(request, 'resume_builder_app/resume_builder.html', context)



@login_required
def preview_resume(request, resume_id):
    """Preview resume in different templates"""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    template = request.GET.get('template', resume.template)
    
    # Get user profile
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None
    
    # Debug: Print resume data to console
    print(f"Resume ID: {resume.id}")
    print(f"Resume Title: {resume.title}")
    print(f"Resume Summary: {resume.summary}")
    print(f"Resume Template: {resume.template}")
    print(f"User: {request.user.first_name} {request.user.last_name}")
    print(f"User Profile: {user_profile}")
    print(f"Experiences: {resume.experiences.count()}")
    print(f"Education: {resume.educations.count()}")
    print(f"Skills: {resume.skills.count()}")
    print(f"Projects: {resume.projects.count()}")
    print(f"Certifications: {resume.certifications.count()}")
    
    context = {
        'resume': resume,
        'template': template,
        'user_profile': user_profile,
    }
    return render(request, f'resume_builder_app/preview_{template}.html', context)


@login_required
def debug_preview(request, resume_id):
    """Debug preview to show resume data"""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    # Get user profile
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None
    
    context = {
        'resume': resume,
        'user_profile': user_profile,
    }
    return render(request, 'resume_builder_app/debug_preview.html', context)


@login_required
def download_resume_pdf(request, resume_id):
    """Download resume as PDF"""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    # Get user profile
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None

    # Render the template
    template = get_template(f'resume_builder_app/preview_{resume.template}.html')
    context = {
        'resume': resume,
        'user_profile': user_profile,
        'user': request.user,  # Ensure user is available in template context
        'is_pdf': True
    }
    html = template.render(context)
    
    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="resume_{resume.id}.pdf"'
    
    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error generating PDF')
    
    return response


# API Views
class ResumeViewSet(viewsets.ModelViewSet):
    """API viewset for Resume model"""
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a resume"""
        resume = self.get_object()
        new_resume = Resume.objects.create(
            user=request.user,
            title=f"{resume.title} (Copy)",
            template=resume.template,
            summary=resume.summary,
            ai_generated=resume.ai_generated
        )
        
        # Duplicate related objects
        for education in resume.educations.all():
            Education.objects.create(
                resume=new_resume,
                institution=education.institution,
                degree=education.degree,
                field_of_study=education.field_of_study,
                start_date=education.start_date,
                end_date=education.end_date,
                current=education.current,
                gpa=education.gpa,
                description=education.description,
                order=education.order
            )
        
        for experience in resume.experiences.all():
            Experience.objects.create(
                resume=new_resume,
                company=experience.company,
                position=experience.position,
                location=experience.location,
                start_date=experience.start_date,
                end_date=experience.end_date,
                current=experience.current,
                description=experience.description,
                achievements=experience.achievements,
                order=experience.order
            )
        
        for skill in resume.skills.all():
            Skill.objects.create(
                resume=new_resume,
                name=skill.name,
                category=skill.category,
                order=skill.order
            )
        
        return Response({'id': new_resume.id, 'message': 'Resume duplicated successfully'})


class EducationViewSet(viewsets.ModelViewSet):
    """API viewset for Education model"""
    serializer_class = EducationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Education.objects.filter(resume__user=self.request.user)

    def perform_create(self, serializer):
        resume_id = self.request.data.get('resume')
        resume = get_object_or_404(Resume, id=resume_id, user=self.request.user)
        serializer.save(resume=resume)


class ExperienceViewSet(viewsets.ModelViewSet):
    """API viewset for Experience model"""
    serializer_class = ExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Experience.objects.filter(resume__user=self.request.user)

    def perform_create(self, serializer):
        resume_id = self.request.data.get('resume')
        resume = get_object_or_404(Resume, id=resume_id, user=self.request.user)
        serializer.save(resume=resume)


class SkillViewSet(viewsets.ModelViewSet):
    """API viewset for Skill model"""
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Skill.objects.filter(resume__user=self.request.user)

    def perform_create(self, serializer):
        resume_id = self.request.data.get('resume')
        resume = get_object_or_404(Resume, id=resume_id, user=self.request.user)
        serializer.save(resume=resume)


class ProjectViewSet(viewsets.ModelViewSet):
    """API viewset for Project model"""
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(resume__user=self.request.user)

    def perform_create(self, serializer):
        resume_id = self.request.data.get('resume')
        resume = get_object_or_404(Resume, id=resume_id, user=self.request.user)
        serializer.save(resume=resume)


class CertificationViewSet(viewsets.ModelViewSet):
    """API viewset for Certification model"""
    serializer_class = CertificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Certification.objects.filter(resume__user=self.request.user)

    def perform_create(self, serializer):
        resume_id = self.request.data.get('resume')
        resume = get_object_or_404(Resume, id=resume_id, user=self.request.user)
        serializer.save(resume=resume)


class LanguageViewSet(viewsets.ModelViewSet):
    """API viewset for Language model"""
    serializer_class = LanguageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Language.objects.filter(resume__user=self.request.user)

    def perform_create(self, serializer):
        resume_id = self.request.data.get('resume')
        resume = get_object_or_404(Resume, id=resume_id, user=self.request.user)
        serializer.save(resume=resume)



# Helper functions for processing form data
def _process_experiences(request, resume):
    """Process experience form data and create/update Experience objects"""
    companies = request.POST.getlist('company[]')
    positions = request.POST.getlist('position[]')
    start_dates = request.POST.getlist('start_date[]')
    end_dates = request.POST.getlist('end_date[]')
    descriptions = request.POST.getlist('description[]')
    
    print(f"Processing experiences: {len(companies)} entries")
    print(f"Companies: {companies}")
    print(f"Positions: {positions}")
    
    # Clear existing experiences for this resume
    resume.experiences.all().delete()
    
    # Create new experiences
    for i in range(len(companies)):
        if companies[i] and positions[i]:  # Only create if company and position are provided
            exp = Experience.objects.create(
                resume=resume,
                company=companies[i],
                position=positions[i],
                start_date=start_dates[i] if start_dates[i] else None,
                end_date=end_dates[i] if end_dates[i] else None,
                description=descriptions[i] if descriptions[i] else '',
                current=False  # Default to False, can be enhanced later
            )
            print(f"Created experience: {exp.company} - {exp.position}")


def _process_education(request, resume):
    """Process education form data and create/update Education objects"""
    institutions = request.POST.getlist('institution[]')
    degrees = request.POST.getlist('degree[]')
    fields_of_study = request.POST.getlist('field_of_study[]')
    gpas = request.POST.getlist('gpa[]')
    start_dates = request.POST.getlist('education_start_date[]')
    end_dates = request.POST.getlist('education_end_date[]')
    
    print(f"Processing education: {len(institutions)} entries")
    print(f"Institutions: {institutions}")
    print(f"Degrees: {degrees}")
    print(f"Start dates: {start_dates}")
    print(f"End dates: {end_dates}")
    
    # Clear existing education for this resume
    resume.educations.all().delete()
    
    # Create new education entries
    for i in range(len(institutions)):
        if institutions[i] and degrees[i]:  # Only create if institution and degree are provided
            edu = Education.objects.create(
                resume=resume,
                institution=institutions[i],
                degree=degrees[i],
                field_of_study=fields_of_study[i] if fields_of_study[i] else '',
                gpa=gpas[i] if gpas[i] else None,
                start_date=start_dates[i] if start_dates[i] else datetime.now().date(),
                end_date=end_dates[i] if end_dates[i] else None,
                current=False
            )
            print(f"Created education: {edu.institution} - {edu.degree}")


def _process_skills(request, resume):
    """Process skills form data and create/update Skill objects"""
    skill_names = request.POST.getlist('skill_name[]')
    
    print(f"Processing skills: {len(skill_names)} entries")
    print(f"Skill names: {skill_names}")
    
    # Clear existing skills for this resume
    resume.skills.all().delete()
    
    # Create new skills
    for i in range(len(skill_names)):
        if skill_names[i]:  # Only create if skill name is provided
            skill = Skill.objects.create(
                resume=resume,
                name=skill_names[i],
                category='Technical'  # Default category
            )
            print(f"Created skill: {skill.name}")


def _process_projects(request, resume):
    """Process project form data and create/update Project objects"""
    titles = request.POST.getlist('project_title[]')
    descriptions = request.POST.getlist('project_description[]')
    technologies = request.POST.getlist('project_technologies[]')

    print(f"Processing projects: {len(titles)} entries")
    print(f"Titles: {titles}")
    print(f"Descriptions: {descriptions}")
    print(f"Technologies: {technologies}")

    # Clear existing projects for this resume
    resume.projects.all().delete()

    # Create new projects
    for i in range(len(titles)):
        if titles[i]:
            tech_list = [t.strip() for t in technologies[i].split(',')] if technologies[i] else []
            project = Project.objects.create(
                resume=resume,
                title=titles[i],
                description=descriptions[i] if descriptions[i] else '',
                technologies=tech_list
            )
            print(f"Created project: {project.title}")


def _process_certifications(request, resume):
    """Process certification form data and create/update Certification objects"""
    names = request.POST.getlist('certification_name[]')
    organizations = request.POST.getlist('certification_organization[]')
    issue_dates = request.POST.getlist('certification_date[]')
    expiry_dates = request.POST.getlist('certification_expiry[]')

    print(f"Processing certifications: {len(names)} entries")
    print(f"Names: {names}")
    print(f"Organizations: {organizations}")

    # Clear existing certifications for this resume
    resume.certifications.all().delete()

    # Create new certifications
    for i in range(len(names)):
        if names[i]:  # Only create if name is provided
            certification = Certification.objects.create(
                resume=resume,
                name=names[i],
                issuing_organization=organizations[i] if organizations[i] else '',
                issue_date=issue_dates[i] if issue_dates[i] else datetime.now().date(),
                expiry_date=expiry_dates[i] if expiry_dates[i] else None
            )
            print(f"Created certification: {certification.name}")

