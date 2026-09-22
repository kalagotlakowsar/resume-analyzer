import os
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator

from .models import Resume, JobRole, AnalysisReport, Skill, SkillCategory, Feedback
from .forms import ResumeUploadForm
from .nlp import extract_text_from_file, parse_resume_full
from .scoring import calculate_ats_score
from .recommender import generate_recommendations

def index(request):
    """Landing homepage presenting the AI Resume Analyzer solution."""
    total_roles = JobRole.objects.count()
    total_skills = Skill.objects.count()
    total_analyses = AnalysisReport.objects.count()
    recent_roles = JobRole.objects.all()[:8]
    
    context = {
        'total_roles': total_roles,
        'total_skills': total_skills,
        'total_analyses': total_analyses,
        'recent_roles': recent_roles,
    }
    return render(request, 'analyzer/index.html', context)


@login_required
def upload_resume(request):
    """Handles resume upload, text extraction, NLP parsing, ATS scoring and report creation."""
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume_file = request.FILES['file']
            target_role = form.cleaned_data.get('job_role')
            custom_role_title = form.cleaned_data.get('custom_role_title')
            custom_jd_text = form.cleaned_data.get('custom_job_description')

            # 1. Extract Text & Metadata
            meta = extract_text_from_file(resume_file, resume_file.name)
            
            if not meta['text'].strip():
                messages.error(request, "Could not extract readable text from this file. Please ensure it is not an image-only/scanned PDF.")
                return render(request, 'analyzer/upload.html', {'form': form, 'roles': JobRole.objects.all()})

            # 2. Save Resume Record
            resume = Resume.objects.create(
                user=request.user,
                title=form.cleaned_data.get('title') or os.path.splitext(resume_file.name)[0],
                file=resume_file,
                file_name=resume_file.name,
                file_type=meta['file_type'],
                file_size_kb=round(resume_file.size / 1024, 2),
                page_count=meta['page_count'],
                word_count=meta['word_count'],
                extracted_text=meta['text']
            )

            # 3. NLP Parsing Engine
            parsed_data = parse_resume_full(meta['text'])

            # 4. ATS Scoring & Skill Gap Engine
            scoring_res = calculate_ats_score(
                parsed_data=parsed_data,
                resume_meta=meta,
                target_role=target_role,
                custom_jd_text=custom_jd_text
            )

            # 5. AI Recommendations
            recommendations = generate_recommendations(
                parsed_data=parsed_data,
                scoring_data=scoring_res,
                target_role=target_role,
                custom_role_title=custom_role_title
            )

            # 6. Save Analysis Report
            report = AnalysisReport.objects.create(
                resume=resume,
                job_role=target_role,
                custom_role_title=custom_role_title,
                custom_job_description=custom_jd_text,
                ats_score=scoring_res['ats_score'],
                keyword_match_score=scoring_res['subscores']['keyword_match_score'],
                skills_score=scoring_res['subscores']['skills_score'],
                experience_score=scoring_res['subscores']['experience_score'],
                education_score=scoring_res['subscores']['education_score'],
                completeness_score=scoring_res['subscores']['completeness_score'],
                formatting_score=scoring_res['subscores']['formatting_score'],
                parsed_data=parsed_data,
                matched_skills=scoring_res['skill_gap']['matched_skills'],
                missing_skills=scoring_res['skill_gap']['missing_skills'],
                recommended_skills=scoring_res['skill_gap']['recommended_skills'],
                category_breakdown=parsed_data.get('categorized_skills', {}),
                ai_recommendations=recommendations,
                section_analysis=parsed_data.get('flags', {})
            )

            messages.success(request, f"Resume successfully analyzed! Overall ATS Compatibility Score: {report.ats_score}%")
            return redirect('view_report', report_id=report.id)
        else:
            messages.error(request, "Please fix the errors indicated in the upload form.")
    else:
        form = ResumeUploadForm()

    roles = JobRole.objects.all()
    return render(request, 'analyzer/upload.html', {'form': form, 'roles': roles})


@login_required
def view_report(request, report_id):
    """Detailed visual analysis report dashboard."""
    report = get_object_or_404(AnalysisReport, id=report_id)
    
    # Restrict to owner or admin
    if report.resume.user != request.user and not request.user.is_staff:
        messages.error(request, "You do not have permission to view this report.")
        return redirect('index')

    parsed = report.parsed_data
    contacts = parsed.get('contacts', {})
    education = parsed.get('education', {})
    impact = parsed.get('impact', {})
    sections = parsed.get('sections', {})

    # Categorized skill badges data
    matched_skills = report.matched_skills or []
    missing_skills = report.missing_skills or []
    recommended_skills = report.recommended_skills or []

    # Chart data in JSON for JavaScript / Chart.js
    chart_subscores = {
        'labels': ['Keywords', 'Skills Match', 'Experience', 'Education', 'Completeness', 'Formatting'],
        'values': [
            report.keyword_match_score,
            report.skills_score,
            report.experience_score,
            report.education_score,
            report.completeness_score,
            report.formatting_score,
        ]
    }

    chart_skills_dist = {
        'labels': ['Matched Skills', 'Missing Skills', 'Recommended Boosts'],
        'values': [len(matched_skills), len(missing_skills), len(recommended_skills)]
    }

    context = {
        'report': report,
        'parsed': parsed,
        'contacts': contacts,
        'education': education,
        'impact': impact,
        'sections': sections,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'recommended_skills': recommended_skills,
        'chart_subscores_json': json.dumps(chart_subscores),
        'chart_skills_dist_json': json.dumps(chart_skills_dist),
    }
    return render(request, 'analyzer/report.html', context)


@login_required
def download_report_pdf(request, report_id):
    """Generates printable PDF report view."""
    report = get_object_or_404(AnalysisReport, id=report_id)
    if report.resume.user != request.user and not request.user.is_staff:
        messages.error(request, "Permission denied.")
        return redirect('index')

    parsed = report.parsed_data
    contacts = parsed.get('contacts', {})
    education = parsed.get('education', {})
    impact = parsed.get('impact', {})

    context = {
        'report': report,
        'parsed': parsed,
        'contacts': contacts,
        'education': education,
        'impact': impact,
        'is_printable': True,
    }
    return render(request, 'analyzer/report_pdf.html', context)


@login_required
def resume_history(request):
    """List of all past analyzed resumes for the current user."""
    resumes_list = Resume.objects.filter(user=request.user).prefetch_related('reports')
    paginator = Paginator(resumes_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'analyzer/history.html', {'page_obj': page_obj})


@login_required
def compare_resumes(request):
    """Side-by-side comparison of 2 or more reports to track candidate improvements."""
    reports_qs = AnalysisReport.objects.filter(resume__user=request.user)
    
    report_id1 = request.GET.get('r1')
    report_id2 = request.GET.get('r2')
    
    r1 = None
    r2 = None
    
    if report_id1:
        r1 = reports_qs.filter(id=report_id1).first()
    if report_id2:
        r2 = reports_qs.filter(id=report_id2).first()
        
    if not r1 and reports_qs.count() >= 1:
        r1 = reports_qs[0]
    if not r2 and reports_qs.count() >= 2:
        r2 = reports_qs[1]

    context = {
        'all_reports': reports_qs,
        'r1': r1,
        'r2': r2,
    }
    return render(request, 'analyzer/compare.html', context)


@login_required
def delete_resume(request, resume_id):
    """Deletes a resume and all associated analysis reports."""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    if request.method == 'POST':
        resume.delete()
        messages.success(request, "Resume deleted successfully.")
        return redirect('resume_history')
    return redirect('resume_history')


def ajax_skills_for_role(request, role_id):
    """AJAX API endpoint returning required and preferred skills for a selected JobRole."""
    try:
        role = JobRole.objects.get(id=role_id)
        req = list(role.required_skills.values('id', 'name', 'category__name'))
        pref = list(role.preferred_skills.values('id', 'name', 'category__name'))
        return JsonResponse({
            'success': True,
            'title': role.title,
            'description': role.description,
            'required_skills': req,
            'preferred_skills': pref,
            'min_experience_years': role.min_experience_years
        })
    except JobRole.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Role not found'}, status=404)
