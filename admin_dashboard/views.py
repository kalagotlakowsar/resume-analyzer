import csv
import json
from collections import Counter
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from django.utils.text import slugify
from django.db.models import Avg, Count

from analyzer.models import Resume, JobRole, Skill, SkillCategory, AnalysisReport
from .forms import JobRoleAdminForm, SkillAdminForm

def is_staff_or_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'admin'))


@login_required
@user_passes_test(is_staff_or_admin, login_url='index')
def dashboard_overview(request):
    """Platform-wide analytics and performance dashboard."""
    total_users = User.objects.count()
    total_resumes = Resume.objects.count()
    total_reports = AnalysisReport.objects.count()
    
    avg_ats = AnalysisReport.objects.aggregate(Avg('ats_score'))['ats_score__avg'] or 0.0
    avg_ats = round(avg_ats, 1)

    # Score distribution brackets
    excellent_count = AnalysisReport.objects.filter(ats_score__gte=85).count()
    good_count = AnalysisReport.objects.filter(ats_score__gte=70, ats_score__lt=85).count()
    fair_count = AnalysisReport.objects.filter(ats_score__gte=50, ats_score__lt=70).count()
    poor_count = AnalysisReport.objects.filter(ats_score__lt=50).count()

    # Top targeted job roles
    top_roles = JobRole.objects.annotate(report_count=Count('reports')).order_by('-report_count')[:6]

    # Calculate Top Missing Skills across platform
    all_missing_skills = []
    for r in AnalysisReport.objects.only('missing_skills'):
        if isinstance(r.missing_skills, list):
            all_missing_skills.extend(r.missing_skills)
    missing_counter = Counter(all_missing_skills).most_common(10)

    # Calculate Top Matched Skills
    all_matched_skills = []
    for r in AnalysisReport.objects.only('matched_skills'):
        if isinstance(r.matched_skills, list):
            all_matched_skills.extend(r.matched_skills)
    matched_counter = Counter(all_matched_skills).most_common(10)

    recent_reports = AnalysisReport.objects.select_related('resume', 'resume__user', 'job_role').order_by('-created_at')[:10]

    # Score Distribution JSON for Chart.js
    score_dist_json = json.dumps({
        'labels': ['Needs Work (<50%)', 'Fair (50-69%)', 'Good (70-84%)', 'High Match (85%+)'],
        'values': [poor_count, fair_count, good_count, excellent_count]
    })

    # Missing Skills JSON for Chart.js
    missing_skills_json = json.dumps({
        'labels': [item[0] for item in missing_counter[:6]],
        'values': [item[1] for item in missing_counter[:6]]
    })

    context = {
        'total_users': total_users,
        'total_resumes': total_resumes,
        'total_reports': total_reports,
        'avg_ats': avg_ats,
        'excellent_count': excellent_count,
        'good_count': good_count,
        'fair_count': fair_count,
        'poor_count': poor_count,
        'top_roles': top_roles,
        'missing_counter': missing_counter,
        'matched_counter': matched_counter,
        'recent_reports': recent_reports,
        'score_dist_json': score_dist_json,
        'missing_skills_json': missing_skills_json,
    }
    return render(request, 'admin_dashboard/dashboard.html', context)


@login_required
@user_passes_test(is_staff_or_admin, login_url='index')
def manage_users(request):
    """User accounts manager."""
    users = User.objects.annotate(resume_count=Count('resumes')).order_by('-date_joined')
    return render(request, 'admin_dashboard/manage_users.html', {'users': users})


@login_required
@user_passes_test(is_staff_or_admin, login_url='index')
def toggle_user_status(request, user_id):
    """Toggle user active status."""
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "You cannot deactivate your own account.")
    else:
        target_user.is_active = not target_user.is_active
        target_user.save()
        status_str = "activated" if target_user.is_active else "deactivated"
        messages.success(request, f"User {target_user.username} has been {status_str}.")
    return redirect('manage_users')


@login_required
@user_passes_test(is_staff_or_admin, login_url='index')
def manage_roles(request):
    """Job Roles CRUD list."""
    roles = JobRole.objects.annotate(reports_count=Count('reports')).order_by('title')
    return render(request, 'admin_dashboard/manage_roles.html', {'roles': roles})


@login_required
@user_passes_test(is_staff_or_admin, login_url='index')
def add_role(request):
    """Add a new target Job Role with required and preferred skills."""
    if request.method == 'POST':
        form = JobRoleAdminForm(request.POST)
        if form.is_valid():
            role = form.save(commit=False)
            role.slug = slugify(role.title)
            role.save()
            form.save_m2m()
            messages.success(request, f"Job Role '{role.title}' created successfully!")
            return redirect('manage_roles')
    else:
        form = JobRoleAdminForm()
    return render(request, 'admin_dashboard/role_form.html', {'form': form, 'title': 'Create New Job Role'})


@login_required
@user_passes_test(is_staff_or_admin, login_url='index')
def edit_role(request, role_id):
    """Edit an existing Job Role."""
    role = get_object_or_404(JobRole, id=role_id)
    if request.method == 'POST':
        form = JobRoleAdminForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, f"Job Role '{role.title}' updated successfully!")
            return redirect('manage_roles')
    else:
        form = JobRoleAdminForm(instance=role)
    return render(request, 'admin_dashboard/role_form.html', {'form': form, 'role': role, 'title': f'Edit Job Role: {role.title}'})


@login_required
@user_passes_test(is_staff_or_admin, login_url='index')
def delete_role(request, role_id):
    """Delete a Job Role."""
    role = get_object_or_404(JobRole, id=role_id)
    if request.method == 'POST':
        title = role.title
        role.delete()
        messages.success(request, f"Job Role '{title}' deleted.")
        return redirect('manage_roles')
    return redirect('manage_roles')


@login_required
@user_passes_test(is_staff_or_admin, login_url='index')
def manage_skills(request):
    """Skills taxonomy manager."""
    categories = SkillCategory.objects.prefetch_related('skills').all()
    if request.method == 'POST':
        form = SkillAdminForm(request.POST)
        if form.is_valid():
            skill = form.save()
            messages.success(request, f"Skill '{skill.name}' added successfully!")
            return redirect('manage_skills')
    else:
        form = SkillAdminForm()
        
    return render(request, 'admin_dashboard/manage_skills.html', {'categories': categories, 'form': form})


@login_required
@user_passes_test(is_staff_or_admin, login_url='index')
def delete_skill(request, skill_id):
    """Delete a skill from taxonomy."""
    skill = get_object_or_404(Skill, id=skill_id)
    if request.method == 'POST':
        name = skill.name
        skill.delete()
        messages.success(request, f"Skill '{name}' deleted.")
    return redirect('manage_skills')


@login_required
@user_passes_test(is_staff_or_admin, login_url='index')
def resume_logs(request):
    """Full repository view of analyzed resumes and scores."""
    reports = AnalysisReport.objects.select_related('resume', 'resume__user', 'job_role').order_by('-created_at')
    return render(request, 'admin_dashboard/resume_logs.html', {'reports': reports})


@login_required
@user_passes_test(is_staff_or_admin, login_url='index')
def export_resumes_csv(request):
    """Generates downloadable CSV export of all candidate analyses."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ai_resume_analyzer_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Report ID', 'Candidate Username', 'Candidate Email', 'Resume Title', 'File Name', 'Target Job Role', 'ATS Score', 'Keywords Score', 'Skills Score', 'Experience Score', 'Education Score', 'Matched Skills Count', 'Missing Skills Count', 'Date Analyzed'])

    reports = AnalysisReport.objects.select_related('resume', 'resume__user', 'job_role').order_by('-created_at')
    for r in reports:
        user_name = r.resume.user.username if r.resume.user else 'Guest'
        user_email = r.resume.user.email if r.resume.user else 'N/A'
        role_str = r.job_role.title if r.job_role else (r.custom_role_title or 'Custom Role')
        matched_cnt = len(r.matched_skills) if isinstance(r.matched_skills, list) else 0
        missing_cnt = len(r.missing_skills) if isinstance(r.missing_skills, list) else 0
        
        writer.writerow([
            r.id,
            user_name,
            user_email,
            r.resume.title,
            r.resume.file_name,
            role_str,
            r.ats_score,
            r.keyword_match_score,
            r.skills_score,
            r.experience_score,
            r.education_score,
            matched_cnt,
            missing_cnt,
            r.created_at.strftime('%Y-%m-%d %H:%M')
        ])

    return response
