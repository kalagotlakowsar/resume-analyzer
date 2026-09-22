from django.contrib import admin
from .models import SkillCategory, Skill, JobRole, Resume, AnalysisReport, Feedback

@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_trending')
    list_filter = ('category', 'is_trending')
    search_fields = ('name', 'synonyms')


@admin.register(JobRole)
class JobRoleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'min_experience_years', 'created_at')
    list_filter = ('category',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('required_skills', 'preferred_skills')


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'file_name', 'file_type', 'file_size_kb', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('title', 'file_name', 'user__username', 'extracted_text')


@admin.register(AnalysisReport)
class AnalysisReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'resume', 'job_role', 'ats_score', 'keyword_match_score', 'skills_score', 'created_at')
    list_filter = ('ats_score', 'created_at')
    search_fields = ('resume__file_name', 'job_role__title')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('report', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
