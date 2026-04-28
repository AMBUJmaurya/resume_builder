from django.contrib import admin
from django.utils.html import format_html
from .models import (
    UserProfile, Resume, Education, Experience, Skill, 
    Project, Certification, Language, ResumeGeneration
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'linkedin_url', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at']


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1
    fields = ['institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'current', 'gpa']


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 1
    fields = ['company', 'position', 'location', 'start_date', 'end_date', 'current', 'description']


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1
    fields = ['name', 'category']


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1
    fields = ['title', 'description', 'technologies', 'github_url', 'live_url']


class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 1
    fields = ['name', 'issuing_organization', 'issue_date', 'expiry_date', 'credential_id']


class LanguageInline(admin.TabularInline):
    model = Language
    extra = 1
    fields = ['name', 'level']


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'template', 'ai_generated', 'created_at', 'updated_at']
    list_filter = ['template', 'ai_generated', 'created_at', 'updated_at']
    search_fields = ['title', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [
        EducationInline,
        ExperienceInline,
        SkillInline,
        ProjectInline,
        CertificationInline,
        LanguageInline,
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['institution', 'degree', 'field_of_study', 'resume', 'start_date', 'end_date', 'current']
    list_filter = ['current', 'start_date', 'end_date']
    search_fields = ['institution', 'degree', 'field_of_study', 'resume__title']
    date_hierarchy = 'start_date'


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['position', 'company', 'resume', 'start_date', 'end_date', 'current']
    list_filter = ['current', 'start_date', 'end_date']
    search_fields = ['position', 'company', 'resume__title']
    date_hierarchy = 'start_date'


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'resume']
    list_filter = ['category']
    search_fields = ['name', 'category', 'resume__title']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'resume', 'start_date', 'end_date', 'current']
    list_filter = ['current', 'start_date', 'end_date']
    search_fields = ['title', 'description', 'resume__title']
    date_hierarchy = 'start_date'


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ['name', 'issuing_organization', 'resume', 'issue_date', 'expiry_date']
    list_filter = ['issue_date', 'expiry_date']
    search_fields = ['name', 'issuing_organization', 'resume__title']
    date_hierarchy = 'issue_date'


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'resume']
    list_filter = ['level']
    search_fields = ['name', 'resume__title']


@admin.register(ResumeGeneration)
class ResumeGenerationAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'created_at', 'prompt_preview']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__email', 'prompt']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def prompt_preview(self, obj):
        return obj.prompt[:100] + '...' if len(obj.prompt) > 100 else obj.prompt
    prompt_preview.short_description = 'Prompt Preview'
