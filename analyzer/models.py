from django.db import models
from django.contrib.auth.models import User
import json

class SkillCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default='bi-code-slash')
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Skill Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name='skills')
    synonyms = models.TextField(blank=True, help_text="Comma-separated list of synonyms / aliases (e.g. JS, JavaScript, Vanilla JS)")
    is_trending = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    def get_synonyms_list(self):
        if not self.synonyms:
            return [self.name.lower()]
        items = [s.strip().lower() for s in self.synonyms.split(',') if s.strip()]
        if self.name.lower() not in items:
            items.append(self.name.lower())
        return items


class JobRole(models.Model):
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True)
    category = models.CharField(max_length=100, default='Engineering')
    description = models.TextField(help_text="Detailed job description used for NLP keyword matching")
    required_skills = models.ManyToManyField(Skill, related_name='required_for_roles', blank=True)
    preferred_skills = models.ManyToManyField(Skill, related_name='preferred_for_roles', blank=True)
    min_experience_years = models.IntegerField(default=0)
    average_salary_range = models.CharField(max_length=100, blank=True, default="$70,000 - $120,000")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_all_required_skill_names(self):
        return list(self.required_skills.values_list('name', flat=True))

    def get_all_preferred_skill_names(self):
        return list(self.preferred_skills.values_list('name', flat=True))


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes', null=True, blank=True)
    title = models.CharField(max_length=200, default="My Resume")
    file = models.FileField(upload_to='resumes/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20)  # .pdf or .docx
    file_size_kb = models.FloatField(default=0.0)
    page_count = models.IntegerField(default=1)
    word_count = models.IntegerField(default=0)
    extracted_text = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} ({self.file_name}) - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"


class AnalysisReport(models.Model):
    SCORE_RATING_CHOICES = [
        ('poor', 'Needs Significant Work (Below 50%)'),
        ('average', 'Fair / Average ATS Match (50% - 69%)'),
        ('good', 'Good ATS Compatibility (70% - 84%)'),
        ('excellent', 'Excellent / High ATS Match (85% - 100%)'),
    ]

    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='reports')
    job_role = models.ForeignKey(JobRole, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports')
    custom_role_title = models.CharField(max_length=150, blank=True, null=True)
    custom_job_description = models.TextField(blank=True, null=True)

    # ATS Scoring breakdown (0 to 100)
    ats_score = models.FloatField(default=0.0)
    keyword_match_score = models.FloatField(default=0.0)
    skills_score = models.FloatField(default=0.0)
    experience_score = models.FloatField(default=0.0)
    education_score = models.FloatField(default=0.0)
    completeness_score = models.FloatField(default=0.0)
    formatting_score = models.FloatField(default=0.0)

    # Detailed structured JSON data
    parsed_data = models.JSONField(default=dict, blank=True)
    matched_skills = models.JSONField(default=list, blank=True)
    missing_skills = models.JSONField(default=list, blank=True)
    recommended_skills = models.JSONField(default=list, blank=True)
    category_breakdown = models.JSONField(default=dict, blank=True)
    ai_recommendations = models.JSONField(default=list, blank=True)
    section_analysis = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        role_label = self.job_role.title if self.job_role else (self.custom_role_title or "Custom Role")
        return f"Report: {self.resume.file_name} -> {role_label} ({self.ats_score}%)"

    @property
    def target_title(self):
        if self.job_role:
            return self.job_role.title
        return self.custom_role_title or "Custom Job Profile"

    @property
    def rating_badge_class(self):
        if self.ats_score >= 85:
            return "bg-success text-white"
        elif self.ats_score >= 70:
            return "bg-primary text-white"
        elif self.ats_score >= 50:
            return "bg-warning text-dark"
        return "bg-danger text-white"

    @property
    def rating_label(self):
        if self.ats_score >= 85:
            return "High ATS Compatibility (Top Tier)"
        elif self.ats_score >= 70:
            return "Good ATS Compatibility"
        elif self.ats_score >= 50:
            return "Moderate Match (Needs Optimization)"
        return "Low ATS Match (Requires Significant Improvement)"


class Feedback(models.Model):
    report = models.ForeignKey(AnalysisReport, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback {self.rating}* on Report {self.report.id}"
