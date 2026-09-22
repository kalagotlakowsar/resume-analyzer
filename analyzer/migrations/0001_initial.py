from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SkillCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('icon', models.CharField(default='bi-code-slash', max_length=50)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'Skill Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('synonyms', models.TextField(blank=True, help_text='Comma-separated list of synonyms / aliases (e.g. JS, JavaScript, Vanilla JS)')),
                ('is_trending', models.BooleanField(default=False)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='skills', to='analyzer.skillcategory')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='JobRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150, unique=True)),
                ('slug', models.SlugField(max_length=150, unique=True)),
                ('category', models.CharField(default='Engineering', max_length=100)),
                ('description', models.TextField(help_text='Detailed job description used for NLP keyword matching')),
                ('min_experience_years', models.IntegerField(default=0)),
                ('average_salary_range', models.CharField(blank=True, default='$70,000 - $120,000', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('preferred_skills', models.ManyToManyField(blank=True, related_name='preferred_for_roles', to='analyzer.skill')),
                ('required_skills', models.ManyToManyField(blank=True, related_name='required_for_roles', to='analyzer.skill')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Resume',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='My Resume', max_length=200)),
                ('file', models.FileField(upload_to='resumes/')),
                ('file_name', models.CharField(max_length=255)),
                ('file_type', models.CharField(max_length=20)),
                ('file_size_kb', models.FloatField(default=0.0)),
                ('page_count', models.IntegerField(default=1)),
                ('word_count', models.IntegerField(default=0)),
                ('extracted_text', models.TextField(blank=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='resumes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.CreateModel(
            name='AnalysisReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('custom_role_title', models.CharField(blank=True, max_length=150, null=True)),
                ('custom_job_description', models.TextField(blank=True, null=True)),
                ('ats_score', models.FloatField(default=0.0)),
                ('keyword_match_score', models.FloatField(default=0.0)),
                ('skills_score', models.FloatField(default=0.0)),
                ('experience_score', models.FloatField(default=0.0)),
                ('education_score', models.FloatField(default=0.0)),
                ('completeness_score', models.FloatField(default=0.0)),
                ('formatting_score', models.FloatField(default=0.0)),
                ('parsed_data', models.JSONField(blank=True, default=dict)),
                ('matched_skills', models.JSONField(blank=True, default=list)),
                ('missing_skills', models.JSONField(blank=True, default=list)),
                ('recommended_skills', models.JSONField(blank=True, default=list)),
                ('category_breakdown', models.JSONField(blank=True, default=dict)),
                ('ai_recommendations', models.JSONField(blank=True, default=list)),
                ('section_analysis', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('job_role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reports', to='analyzer.jobrole')),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='analyzer.resume')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])),
                ('comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='analyzer.analysisreport')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
