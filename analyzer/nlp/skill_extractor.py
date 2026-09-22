import re

# Comprehensive Built-in Taxonomy of Skills categorized for instant high-speed matching
BUILTIN_SKILLS_TAXONOMY = {
    'Programming Languages': [
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'C', 'Ruby', 'Go', 'Golang', 
        'Rust', 'PHP', 'Swift', 'Kotlin', 'R', 'Scala', 'Dart', 'SQL', 'PL/SQL', 'HTML', 'HTML5', 
        'CSS', 'CSS3', 'Sass', 'SCSS', 'Bash', 'Shell', 'PowerShell', 'Perl', 'Lua', 'Haskell', 'MATLAB'
    ],
    'Frameworks & Libraries': [
        'Django', 'Flask', 'FastAPI', 'React', 'React.js', 'Angular', 'Vue.js', 'Vue', 'Next.js', 
        'Nuxt.js', 'Node.js', 'Express.js', 'Express', 'Spring Boot', 'Spring', 'ASP.NET', '.NET Core', 
        'Laravel', 'Ruby on Rails', 'Redux', 'Tailwind CSS', 'Bootstrap', 'jQuery', 'TensorFlow', 
        'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'SciPy', 'Keras', 'OpenCV', 'HuggingFace', 
        'NLTK', 'SpaCy', 'GraphQL', 'REST API', 'WebSockets', 'Hibernate', 'Prisma', 'Sequelize'
    ],
    'Databases': [
        'PostgreSQL', 'MySQL', 'SQLite', 'MongoDB', 'Redis', 'Oracle', 'Microsoft SQL Server', 
        'MS SQL', 'Cassandra', 'DynamoDB', 'Elasticsearch', 'Firebase', 'Supabase', 'MariaDB', 
        'CouchDB', 'Neo4j', 'Snowflake', 'BigQuery', 'Amazon Redshift'
    ],
    'Cloud & DevOps': [
        'AWS', 'Amazon Web Services', 'Azure', 'Google Cloud', 'GCP', 'Docker', 'Kubernetes', 'K8s', 
        'CI/CD', 'Jenkins', 'GitHub Actions', 'GitLab CI', 'Terraform', 'Ansible', 'Linux', 'Ubuntu', 
        'CentOS', 'Nginx', 'Apache', 'Serverless', 'Microservices', 'Prometheus', 'Grafana', 'ELK Stack', 
        'Helm', 'CloudFormation', 'IAM', 'EC2', 'S3', 'Lambda', 'Docker Compose'
    ],
    'Tools & Methodologies': [
        'Git', 'GitHub', 'GitLab', 'Bitbucket', 'Jira', 'Confluence', 'Trello', 'Postman', 'Swagger', 
        'Agile', 'Scrum', 'Kanban', 'TDD', 'BDD', 'Unit Testing', 'PyTest', 'Jest', 'Mocha', 'Selenium', 
        'VS Code', 'IntelliJ', 'PyCharm', 'Figma', 'Adobe XD', 'Webpack', 'Vite', 'Babel', 'Maven', 'Gradle'
    ],
    'AI & Data Science': [
        'Machine Learning', 'Deep Learning', 'Natural Language Processing', 'NLP', 'Computer Vision', 
        'Artificial Intelligence', 'Data Analysis', 'Data Visualization', 'Data Mining', 'Big Data', 
        'Hadoop', 'Spark', 'Kafka', 'Tableau', 'Power BI', 'ETL', 'LLM', 'Generative AI', 'Transformers', 
        'Reinforcement Learning', 'Feature Engineering', 'Statistical Analysis', 'A/B Testing'
    ],
    'Soft Skills': [
        'Communication', 'Leadership', 'Problem Solving', 'Critical Thinking', 'Team Collaboration', 
        'Time Management', 'Adaptability', 'Mentorship', 'Project Management', 'Presentation', 
        'Analytical Skills', 'Decision Making', 'Conflict Resolution', 'Creativity', 'Attention to Detail'
    ]
}

# Synonyms and alias normalization map
SYNONYM_MAP = {
    'js': 'JavaScript',
    'ts': 'TypeScript',
    'py': 'Python',
    'golang': 'Go',
    'k8s': 'Kubernetes',
    'postgres': 'PostgreSQL',
    'mssql': 'MS SQL',
    'reactjs': 'React',
    'react.js': 'React',
    'vuejs': 'Vue.js',
    'vue': 'Vue.js',
    'nodejs': 'Node.js',
    'node': 'Node.js',
    'expressjs': 'Express.js',
    'gcp': 'Google Cloud',
    'aws': 'AWS',
    'amazon web services': 'AWS',
    'ml': 'Machine Learning',
    'ai': 'Artificial Intelligence',
    'dl': 'Deep Learning',
    'nlp': 'Natural Language Processing',
    'ci/cd': 'CI/CD',
    'cicd': 'CI/CD',
    'restful api': 'REST API',
    'rest apis': 'REST API',
    'rest': 'REST API',
    'scikit learn': 'Scikit-learn',
    'sklearn': 'Scikit-learn',
    'tf': 'TensorFlow',
}


def normalize_skill_name(skill_str):
    """Normalize skill name using synonym mappings."""
    cleaned = skill_str.strip()
    lower = cleaned.lower()
    if lower in SYNONYM_MAP:
        return SYNONYM_MAP[lower]
    return cleaned


def extract_skills_from_text(raw_text, custom_skill_list=None):
    """
    Extracts skills present in raw_text using regex word-boundary pattern matching.
    Returns a deduplicated list of canonical skill names.
    """
    if not raw_text:
        return []
        
    text_lower = raw_text.lower()
    found_skills = set()
    
    # 1. Check against built-in taxonomy
    all_taxonomy_skills = []
    for cat, skills in BUILTIN_SKILLS_TAXONOMY.items():
        all_taxonomy_skills.extend(skills)
        
    # Also incorporate custom skill list from database if provided
    if custom_skill_list:
        all_taxonomy_skills.extend(custom_skill_list)
        
    for skill in all_taxonomy_skills:
        skill_clean = skill.strip()
        if not skill_clean:
            continue
            
        skill_lower = skill_clean.lower()
        
        # Exact boundary regex matching to avoid substring false positives (e.g., 'C' in 'CAT')
        # Escape special characters like ++, #, ., /
        escaped_pattern = re.escape(skill_lower)
        
        # For single-letter or short skills like C, R, Go, use strict word boundaries
        if len(skill_lower) <= 2:
            pattern = r'(?:\b|(?<=[^a-zA-Z0-9]))' + escaped_pattern + r'(?:\b|(?=[^a-zA-Z0-9]))'
        else:
            # For complex patterns like C++, C#, .NET, CI/CD, React.js
            pattern = r'(?:\b|(?<=[^a-zA-Z0-9]))' + escaped_pattern + r'(?:\b|(?=[^a-zA-Z0-9]))'
            
        if re.search(pattern, text_lower, re.IGNORECASE):
            canonical = normalize_skill_name(skill_clean)
            found_skills.add(canonical)
            
    # Check common synonyms explicitly
    for syn_key, canonical in SYNONYM_MAP.items():
        syn_pattern = r'(?:\b|(?<=[^a-zA-Z0-9]))' + re.escape(syn_key) + r'(?:\b|(?=[^a-zA-Z0-9]))'
        if re.search(syn_pattern, text_lower, re.IGNORECASE):
            found_skills.add(canonical)
            
    # Return sorted list
    return sorted(list(found_skills), key=lambda s: s.lower())


def categorize_skills(skills_list):
    """
    Categorizes a given list of skills into taxonomy categories.
    Returns: dict mapping category -> list of matched skill names.
    """
    categorized = {cat: [] for cat in BUILTIN_SKILLS_TAXONOMY.keys()}
    categorized['Other Technical'] = []
    
    # Inverted lookup map
    skill_to_cat = {}
    for cat, skills in BUILTIN_SKILLS_TAXONOMY.items():
        for s in skills:
            skill_to_cat[s.lower()] = cat
            
    for skill in skills_list:
        sk_lower = skill.lower()
        cat = skill_to_cat.get(sk_lower)
        if not cat:
            # Try synonym match
            normalized = normalize_skill_name(skill)
            cat = skill_to_cat.get(normalized.lower())
            
        if cat and cat in categorized:
            categorized[cat].append(skill)
        else:
            categorized['Other Technical'].append(skill)
            
    # Remove empty categories
    return {k: v for k, v in categorized.items() if v}
