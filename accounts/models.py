from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ('job_seeker', 'Student / Job Seeker'),
        ('counselor', 'Career Counselor / Recruiter'),
        ('admin', 'Platform Administrator'),
    ]
    
    EXP_CHOICES = [
        ('entry', 'Fresher / Entry-Level (0 - 1 year)'),
        ('junior', 'Junior Professional (1 - 3 years)'),
        ('mid', 'Mid-Level Specialist (3 - 6 years)'),
        ('senior', 'Senior / Lead Specialist (6+ years)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='job_seeker')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    target_job_title = models.CharField(max_length=100, blank=True, default='Full Stack Developer')
    experience_level = models.CharField(max_length=20, choices=EXP_CHOICES, default='entry')
    bio = models.TextField(blank=True, max_length=500)
    profile_picture = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
