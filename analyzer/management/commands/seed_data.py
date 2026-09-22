from django.core.management.base import BaseCommand
from django.utils.text import slugify
from analyzer.models import SkillCategory, Skill, JobRole
from analyzer.nlp.skill_extractor import BUILTIN_SKILLS_TAXONOMY

CATEGORY_ICONS = {
    'Programming Languages': 'bi-code-slash',
    'Frameworks & Libraries': 'bi-box-seam',
    'Databases': 'bi-database',
    'Cloud & DevOps': 'bi-cloud-check',
    'Tools & Methodologies': 'bi-tools',
    'AI & Data Science': 'bi-cpu',
    'Soft Skills': 'bi-people',
}

ROLE_TEMPLATES = [
    {
        'title': 'Full Stack Developer',
        'category': 'Software Engineering',
        'min_exp': 1,
        'salary': '$85,000 - $135,000',
        'description': 'Responsible for developing and maintaining robust web applications from frontend user interfaces to backend microservices and databases. Strong command of modern web frameworks, REST APIs, asynchronous task processing, database optimization, and deployment pipelines.',
        'required': ['Python', 'JavaScript', 'Django', 'React', 'HTML', 'CSS', 'PostgreSQL', 'Git', 'REST API'],
        'preferred': ['Docker', 'AWS', 'Redis', 'TypeScript', 'Tailwind CSS', 'CI/CD', 'Unit Testing']
    },
    {
        'title': 'Python Developer',
        'category': 'Backend Engineering',
        'min_exp': 1,
        'salary': '$80,000 - $130,000',
        'description': 'Develop scalable backend architectures, high-performance APIs, data processing pipelines, and microservices in Python. Write clean, maintainable code using Django, Flask, or FastAPI with SQL database modeling and unit testing.',
        'required': ['Python', 'Django', 'FastAPI', 'PostgreSQL', 'Git', 'REST API', 'SQL'],
        'preferred': ['Docker', 'Redis', 'Celery', 'AWS', 'PyTest', 'Linux', 'Microservices']
    },
    {
        'title': 'Data Scientist',
        'category': 'Data & AI',
        'min_exp': 2,
        'salary': '$95,000 - $150,000',
        'description': 'Apply statistical modeling, machine learning, and predictive analytics to solve complex business problems. Extract insights from structured and unstructured data, build predictive pipelines, and deploy machine learning models.',
        'required': ['Python', 'Machine Learning', 'Pandas', 'NumPy', 'Scikit-learn', 'SQL', 'Data Analysis'],
        'preferred': ['Deep Learning', 'TensorFlow', 'PyTorch', 'Data Visualization', 'Tableau', 'NLP', 'Big Data']
    },
    {
        'title': 'Machine Learning Engineer',
        'category': 'Data & AI',
        'min_exp': 2,
        'salary': '$105,000 - $165,000',
        'description': 'Design, train, optimize, and deploy production-grade machine learning and deep learning models. Work with large-scale datasets, MLOps deployment pipelines, GPU acceleration, and RESTful model inference endpoints.',
        'required': ['Python', 'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Git'],
        'preferred': ['Docker', 'Kubernetes', 'AWS', 'NLP', 'Computer Vision', 'LLM', 'FastAPI', 'MLOps']
    },
    {
        'title': 'DevOps & Cloud Engineer',
        'category': 'Infrastructure & Cloud',
        'min_exp': 2,
        'salary': '$100,000 - $155,000',
        'description': 'Automate infrastructure provisioning, maintain CI/CD deployment pipelines, manage containerized clusters, and ensure high availability, scalability, and security of cloud infrastructure across AWS, Azure, or GCP.',
        'required': ['Linux', 'Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Git', 'Terraform', 'Bash'],
        'preferred': ['Ansible', 'Jenkins', 'GitHub Actions', 'Prometheus', 'Grafana', 'Python', 'Nginx']
    },
    {
        'title': 'Frontend React Developer',
        'category': 'Frontend Engineering',
        'min_exp': 1,
        'salary': '$75,000 - $125,000',
        'description': 'Build responsive, accessible, high-performance web applications using modern JavaScript/TypeScript and React ecosystem. Integrate backend REST/GraphQL APIs, manage application state, and deliver pixel-perfect user experiences.',
        'required': ['JavaScript', 'TypeScript', 'React', 'HTML', 'CSS', 'Git', 'REST API'],
        'preferred': ['Next.js', 'Redux', 'Tailwind CSS', 'Bootstrap', 'Jest', 'Figma', 'Webpack']
    },
    {
        'title': 'Backend Java Software Engineer',
        'category': 'Software Engineering',
        'min_exp': 2,
        'salary': '$90,000 - $140,000',
        'description': 'Design and implement enterprise backend distributed systems, RESTful microservices, and transaction-safe database architectures using Java and Spring Boot.',
        'required': ['Java', 'Spring Boot', 'SQL', 'PostgreSQL', 'Git', 'REST API', 'Hibernate'],
        'preferred': ['Docker', 'Microservices', 'AWS', 'Kafka', 'Redis', 'Unit Testing', 'Maven']
    },
    {
        'title': 'Cybersecurity Analyst',
        'category': 'Security',
        'min_exp': 2,
        'salary': '$85,000 - $135,000',
        'description': 'Monitor networks and systems for security breaches, conduct vulnerability assessments, implement threat mitigation controls, and ensure compliance with security standards.',
        'required': ['Linux', 'Network Security', 'Python', 'Bash', 'Vulnerability Assessment'],
        'preferred': ['AWS', 'IAM', 'SIEM', 'Penetration Testing', 'Cryptography', 'Wireshark']
    },
    {
        'title': 'Mobile App Developer (Flutter/React Native/iOS)',
        'category': 'Mobile Engineering',
        'min_exp': 1,
        'salary': '$80,000 - $130,000',
        'description': 'Design and develop cross-platform or native mobile applications for iOS and Android platforms with smooth UI interactions, local caching, push notifications, and REST API sync.',
        'required': ['JavaScript', 'React', 'Git', 'REST API', 'Mobile Development'],
        'preferred': ['Dart', 'TypeScript', 'Firebase', 'Redux', 'Swift', 'Kotlin', 'App Store']
    },
    {
        'title': 'Product Manager (Tech)',
        'category': 'Product Management',
        'min_exp': 3,
        'salary': '$110,000 - $170,000',
        'description': 'Lead product strategy, define feature roadmaps, work closely with engineering and design teams, conduct user research, and drive data-driven product launches.',
        'required': ['Product Management', 'Agile', 'Scrum', 'Data Analysis', 'Communication', 'Leadership', 'Project Management'],
        'preferred': ['SQL', 'Jira', 'Figma', 'A/B Testing', 'Tableau', 'Strategic Planning']
    }
]

class Command(BaseCommand):
    help = 'Seeds initial skill categories, skills, and comprehensive job roles into the database.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting database seeding..."))

        # 1. Seed Categories & Skills
        skill_obj_map = {}
        for cat_name, skill_list in BUILTIN_SKILLS_TAXONOMY.items():
            cat, _ = SkillCategory.objects.get_or_create(
                name=cat_name,
                defaults={
                    'slug': slugify(cat_name),
                    'icon': CATEGORY_ICONS.get(cat_name, 'bi-code-slash'),
                    'description': f'Key technical and domain proficiencies for {cat_name}.'
                }
            )
            for skill_name in skill_list:
                skill_obj, _ = Skill.objects.get_or_create(
                    name=skill_name,
                    category=cat,
                    defaults={
                        'synonyms': f"{skill_name.lower()}, {slugify(skill_name)}",
                        'is_trending': skill_name in ['FastAPI', 'Next.js', 'PyTorch', 'Kubernetes', 'Docker', 'Tailwind CSS', 'LLM']
                    }
                )
                skill_obj_map[skill_name.lower()] = skill_obj

        self.stdout.write(self.style.SUCCESS(f"Seeded {SkillCategory.objects.count()} categories and {Skill.objects.count()} skills."))

        # 2. Seed Job Roles
        for role_data in ROLE_TEMPLATES:
            role, created = JobRole.objects.get_or_create(
                title=role_data['title'],
                defaults={
                    'slug': slugify(role_data['title']),
                    'category': role_data['category'],
                    'min_experience_years': role_data['min_exp'],
                    'average_salary_range': role_data['salary'],
                    'description': role_data['description'],
                }
            )
            
            # Associate Required Skills
            for req_name in role_data['required']:
                sk = skill_obj_map.get(req_name.lower())
                if not sk:
                    # Create under Other / Tools if missing
                    default_cat = SkillCategory.objects.first()
                    sk, _ = Skill.objects.get_or_create(name=req_name, defaults={'category': default_cat})
                    skill_obj_map[req_name.lower()] = sk
                role.required_skills.add(sk)

            # Associate Preferred Skills
            for pref_name in role_data['preferred']:
                sk = skill_obj_map.get(pref_name.lower())
                if not sk:
                    default_cat = SkillCategory.objects.first()
                    sk, _ = Skill.objects.get_or_create(name=pref_name, defaults={'category': default_cat})
                    skill_obj_map[pref_name.lower()] = sk
                role.preferred_skills.add(sk)

            role.save()

        self.stdout.write(self.style.SUCCESS(f"Seeded {JobRole.objects.count()} Job Roles successfully!"))
