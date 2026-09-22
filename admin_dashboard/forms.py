from django import forms
from analyzer.models import JobRole, Skill, SkillCategory

class JobRoleAdminForm(forms.ModelForm):
    class Meta:
        model = JobRole
        fields = ['title', 'category', 'min_experience_years', 'average_salary_range', 'description', 'required_skills', 'preferred_skills']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Role Title'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Software Engineering, AI & Data'}),
            'min_experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'average_salary_range': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '$80,000 - $120,000'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed job description for ATS matching...'}),
            'required_skills': forms.SelectMultiple(attrs={'class': 'form-select select2', 'size': '8'}),
            'preferred_skills': forms.SelectMultiple(attrs={'class': 'form-select select2', 'size': '8'}),
        }


class SkillAdminForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'category', 'synonyms', 'is_trending']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Skill Name (e.g. FastAPI)'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'synonyms': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comma-separated aliases (e.g. fastapi, fast-api)'}),
            'is_trending': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
