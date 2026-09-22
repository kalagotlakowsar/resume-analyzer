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
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('job_seeker', 'Student / Job Seeker'), ('counselor', 'Career Counselor / Recruiter'), ('admin', 'Platform Administrator')], default='job_seeker', max_length=20)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('target_job_title', models.CharField(blank=True, default='Full Stack Developer', max_length=100)),
                ('experience_level', models.CharField(choices=[('entry', 'Fresher / Entry-Level (0 - 1 year)'), ('junior', 'Junior Professional (1 - 3 years)'), ('mid', 'Mid-Level Specialist (3 - 6 years)'), ('senior', 'Senior / Lead Specialist (6+ years)')], default='entry', max_length=20)),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'accounts_profile',
            },
        ),
    ]
