from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'resumes', views.ResumeViewSet, basename='resume')
router.register(r'educations', views.EducationViewSet, basename='education')
router.register(r'experiences', views.ExperienceViewSet, basename='experience')
router.register(r'skills', views.SkillViewSet, basename='skill')
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'certifications', views.CertificationViewSet, basename='certification')
router.register(r'languages', views.LanguageViewSet, basename='language')

# Web URLs
urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    
    # Web views (require authentication)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('builder/', views.resume_builder, name='resume_builder'),
    path('builder/<int:resume_id>/', views.resume_builder, name='resume_builder_edit'),

    path('preview/<int:resume_id>/', views.preview_resume, name='preview_resume'),
    path('debug/<int:resume_id>/', views.debug_preview, name='debug_preview'),
    path('download/<int:resume_id>/', views.download_resume_pdf, name='download_resume_pdf'),
    
    # API endpoints
    path('api/', include(router.urls)),
] 