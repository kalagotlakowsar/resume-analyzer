import os
import sys
import django

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User
from accounts.models import Profile
from analyzer.models import SkillCategory, Skill, JobRole, Resume, AnalysisReport
from analyzer.nlp.text_extractor import extract_text_from_file
from analyzer.nlp.resume_parser import parse_resume_full
from analyzer.scoring.ats_calculator import calculate_ats_score
from analyzer.recommender.suggestions import generate_recommendations

def test_full_pipeline():
    print("=" * 60)
    print("1. Running Database Migrations...")
    call_command('makemigrations', interactive=False)
    call_command('migrate', interactive=False)
    print("✓ Migrations applied successfully!")

    print("-" * 60)
    print("2. Seeding Initial Taxonomy & Job Roles...")
    call_command('seed_data')
    print(f"✓ Categories: {SkillCategory.objects.count()}, Skills: {Skill.objects.count()}, Roles: {JobRole.objects.count()}")

    print("-" * 60)
    print("3. Creating Default Demo Users...")
    admin_user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@resumeai.com', 'is_staff': True, 'is_superuser': True})
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        admin_user.profile.role = 'admin'
        admin_user.profile.save()
        print("✓ Created Superuser: admin / admin123")
    else:
        print("✓ Admin user already exists.")

    demo_user, created = User.objects.get_or_create(username='demo_user', defaults={'email': 'alex@example.com', 'first_name': 'Alex', 'last_name': 'Morgan'})
    if created:
        demo_user.set_password('demo123')
        demo_user.save()
        demo_user.profile.role = 'job_seeker'
        demo_user.profile.target_job_title = 'Full Stack Developer'
        demo_user.profile.save()
        print("✓ Created Demo User: demo_user / demo123")
    else:
        print("✓ Demo user already exists.")

    print("-" * 60)
    print("4. Testing NLP Parsing & ATS Scoring Pipeline...")
    
    sample_resume_text = """
    Alex Morgan
    Email: alex.morgan@example.com | Phone: +1-555-019-2834
    LinkedIn: linkedin.com/in/alex-morgan | GitHub: github.com/alexmorgan-dev
    New York, NY

    PROFESSIONAL SUMMARY
    Results-oriented Full Stack Developer with 3+ years of experience engineering scalable web applications. 
    Expertise in Python, Django, JavaScript, React.js, and PostgreSQL. Proven track record of improving system latency 
    and leading cross-functional engineering teams.

    SKILLS
    Languages: Python, JavaScript, TypeScript, SQL, HTML5, CSS3, Bash
    Frameworks & Libraries: Django, React.js, FastAPI, Bootstrap, Redux, Node.js
    Databases & Tools: PostgreSQL, MySQL, Redis, Git, GitHub, Docker, Postman
    Methodologies: Agile, Scrum, CI/CD, Unit Testing, REST API

    WORK EXPERIENCE
    Software Engineer | TechNova Solutions | 2023 - Present
    • Architected 15+ RESTful microservices using Python and Django, reducing API response latency by 35% across 200k daily users.
    • Engineered interactive frontend dashboards in React.js and TypeScript, increasing user engagement metrics by 28%.
    • Automated CI/CD deployment pipelines using Docker and GitHub Actions, expediting release cycles by 40%.
    • Mentored 4 junior software developers on clean code, TDD, and code review standards.

    Junior Developer | CodeCraft Studio | 2021 - 2023
    • Built database schemas and optimized SQL queries in PostgreSQL, improving data query speeds by 25%.
    • Developed responsive web pages using JavaScript, HTML5, CSS3, and Bootstrap.

    EDUCATION
    Bachelor of Technology (B.Tech) in Computer Science and Engineering
    State University of New York | CGPA: 3.8/4.0 | 2017 - 2021

    PROJECTS
    AI Task Orchestrator: Built a full-stack automated task management system with Django, Redis, and React.
    Cloud Analytics Dashboard: Developed real-time telemetry visualizer utilizing PostgreSQL and WebSockets.

    CERTIFICATIONS
    • AWS Certified Solutions Architect - Associate
    • PCEP Certified Associate Python Programmer
    """

    # Run parser
    parsed_res = parse_resume_full(sample_resume_text)
    print(f"✓ Parsed Name: {parsed_res['contacts']['name']}")
    print(f"✓ Parsed Email: {parsed_res['contacts']['email']}")
    print(f"✓ Parsed Phone: {parsed_res['contacts']['phone']}")
    print(f"✓ Extracted Skills ({len(parsed_res['skills'])}): {', '.join(parsed_res['skills'][:8])}...")
    print(f"✓ Action Verbs Count: {parsed_res['impact']['action_verbs_count']}")
    print(f"✓ Quantified Metrics Count: {parsed_res['impact']['metrics_count']}")

    # Run ATS Calculator against Full Stack Developer role
    role = JobRole.objects.filter(title__icontains='Full Stack').first()
    meta = {
        'text': sample_resume_text,
        'page_count': 1,
        'word_count': len(sample_resume_text.split()),
        'file_type': '.pdf',
        'file_name': 'alex_morgan_resume.pdf'
    }

    score_res = calculate_ats_score(parsed_res, meta, target_role=role)
    print(f"✓ Calculated ATS Compatibility Score: {score_res['ats_score']}%")
    print(f"  - Keywords Score: {score_res['subscores']['keyword_match_score']}%")
    print(f"  - Skills Score: {score_res['subscores']['skills_score']}%")
    print(f"  - Experience Score: {score_res['subscores']['experience_score']}%")
    print(f"  - Education Score: {score_res['subscores']['education_score']}%")
    print(f"  - Completeness Score: {score_res['subscores']['completeness_score']}%")
    print(f"  - Formatting Score: {score_res['subscores']['formatting_score']}%")

    print(f"✓ Matched Skills ({len(score_res['skill_gap']['matched_skills'])}): {score_res['skill_gap']['matched_skills']}")
    print(f"✓ Missing Skills ({len(score_res['skill_gap']['missing_skills'])}): {score_res['skill_gap']['missing_skills']}")

    # Generate Recommendations
    recs = generate_recommendations(parsed_res, score_res, target_role=role)
    print(f"✓ Generated {len(recs)} AI Recommendations.")
    for i, rec in enumerate(recs[:2], 1):
        print(f"  [{i}] [{rec['priority']}] {rec['title']}")

    # Create Sample Resume and Report
    test_resume, _ = Resume.objects.get_or_create(
        user=demo_user,
        title="Alex Morgan - Full Stack Developer",
        defaults={
            'file_name': 'alex_morgan_resume.pdf',
            'file_type': '.pdf',
            'file_size_kb': 145.2,
            'page_count': 1,
            'word_count': len(sample_resume_text.split()),
            'extracted_text': sample_resume_text
        }
    )

    test_report, _ = AnalysisReport.objects.get_or_create(
        resume=test_resume,
        job_role=role,
        defaults={
            'ats_score': score_res['ats_score'],
            'keyword_match_score': score_res['subscores']['keyword_match_score'],
            'skills_score': score_res['subscores']['skills_score'],
            'experience_score': score_res['subscores']['experience_score'],
            'education_score': score_res['subscores']['education_score'],
            'completeness_score': score_res['subscores']['completeness_score'],
            'formatting_score': score_res['subscores']['formatting_score'],
            'parsed_data': parsed_res,
            'matched_skills': score_res['skill_gap']['matched_skills'],
            'missing_skills': score_res['skill_gap']['missing_skills'],
            'recommended_skills': score_res['skill_gap']['recommended_skills'],
            'category_breakdown': parsed_res.get('categorized_skills', {}),
            'ai_recommendations': recs,
            'section_analysis': parsed_res.get('flags', {})
        }
    )

    print("-" * 60)
    print(f"✓ Successfully verified complete end-to-end system! Sample report ID: {test_report.id}")
    print("=" * 60)

if __name__ == '__main__':
    test_full_pipeline()
