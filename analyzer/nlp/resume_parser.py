import re
from .skill_extractor import extract_skills_from_text, categorize_skills

# Regex patterns for contact information
EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
PHONE_REGEX = r'(?:(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?)|(?:\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9})'
LINKEDIN_REGEX = r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|profile)\/([a-zA-Z0-9_-]+)'
GITHUB_REGEX = r'(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_-]+)'
PORTFOLIO_REGEX = r'(?:https?:\/\/)?(?:www\.)?([a-zA-Z0-9-]+\.(?:dev|io|me|portfolio|tech|app|com))(?:\/[a-zA-Z0-9_\-\.]+)?'

# Action verbs list commonly analyzed by ATS systems
ACTION_VERBS = [
    'accelerated', 'achieved', 'administered', 'advised', 'analyzed', 'architected', 
    'automated', 'built', 'calculated', 'centralized', 'championed', 'collaborated', 
    'composed', 'conceptualized', 'conducted', 'configured', 'constructed', 'coordinated', 
    'created', 'customized', 'debugged', 'decreased', 'delivered', 'demonstrated', 
    'deployed', 'designed', 'developed', 'devised', 'diagnosed', 'directed', 'documented', 
    'doubled', 'drafted', 'drove', 'engineered', 'enhanced', 'established', 'evaluated', 
    'executed', 'expanded', 'expedited', 'facilitated', 'formulated', 'founded', 'generated', 
    'guided', 'headed', 'identified', 'implemented', 'improved', 'increased', 'initiated', 
    'innovated', 'inspected', 'installed', 'instituted', 'integrated', 'invented', 'launched', 
    'led', 'managed', 'maximized', 'mentored', 'migrated', 'minimized', 'modernized', 
    'negotiated', 'optimized', 'orchestrated', 'organized', 'overhauled', 'oversaw', 
    'pioneered', 'planned', 'prepared', 'presented', 'prioritized', 'produced', 'programmed', 
    'published', 'rebuilt', 'reduced', 'refactored', 'resolved', 'restructured', 'revamped', 
    'saved', 'scaled', 'scheduled', 'secured', 'simplified', 'spearheaded', 'standardized', 
    'streamlined', 'strengthened', 'structured', 'supervised', 'surpassed', 'synthesized', 
    'systematized', 'tested', 'tracked', 'trained', 'transformed', 'troubleshot', 'upgraded', 
    'validated', 'visualized', 'won', 'yielded'
]

# Section headers standard keywords
SECTION_KEYWORDS = {
    'summary': ['summary', 'professional summary', 'executive summary', 'career summary', 'about me', 'profile', 'objective', 'career objective'],
    'experience': ['experience', 'work experience', 'professional experience', 'employment history', 'internships', 'work history', 'career history'],
    'education': ['education', 'academic background', 'academics', 'qualifications', 'degrees', 'educational background'],
    'skills': ['skills', 'technical skills', 'core competencies', 'technologies', 'tools & technologies', 'expertise', 'skills & abilities', 'proficiencies'],
    'projects': ['projects', 'academic projects', 'personal projects', 'key projects', 'technical projects', 'featured projects', 'open source'],
    'certifications': ['certifications', 'licenses', 'certificates', 'courses', 'professional certifications', 'accreditations'],
    'achievements': ['achievements', 'awards', 'honors', 'accomplishments', 'recognition', 'publications', 'extracurricular activities']
}

# Recognized Degrees list
DEGREES_PATTERNS = [
    r'\b(?:B\.?Tech|B\.?E\.?|Bachelor of Technology|Bachelor of Engineering)\b',
    r'\b(?:B\.?S\.?|B\.?Sc\.?|Bachelor of Science)\b',
    r'\b(?:M\.?Tech|M\.?E\.?|Master of Technology|Master of Engineering)\b',
    r'\b(?:M\.?S\.?|M\.?Sc\.?|Master of Science)\b',
    r'\b(?:B\.?C\.?A\.?|Bachelor of Computer Applications)\b',
    r'\b(?:M\.?C\.?A\.?|Master of Computer Applications)\b',
    r'\b(?:B\.?B\.?A\.?|M\.?B\.?A\.?|Master of Business Administration)\b',
    r'\b(?:Ph\.?D|Doctor of Philosophy|Doctorate)\b',
    r'\b(?:Diploma|Associate Degree|Higher Secondary|HSC|CBSE|ICSE)\b'
]


def extract_contact_info(text):
    """Extract email, phone, linkedin, github, portfolio, and location from text."""
    contacts = {
        'email': None,
        'phone': None,
        'linkedin': None,
        'github': None,
        'portfolio': None,
        'location': None,
        'name': None,
    }
    
    # 1. Email
    email_match = re.search(EMAIL_REGEX, text)
    if email_match:
        contacts['email'] = email_match.group(0)
        
    # 2. Phone
    phone_match = re.search(PHONE_REGEX, text)
    if phone_match:
        # Clean matched phone number
        phone_str = phone_match.group(0).strip()
        if len(re.sub(r'\D', '', phone_str)) >= 7:
            contacts['phone'] = phone_str
            
    # 3. LinkedIn
    li_match = re.search(LINKEDIN_REGEX, text, re.IGNORECASE)
    if li_match:
        contacts['linkedin'] = f"linkedin.com/in/{li_match.group(1)}"
        
    # 4. GitHub
    gh_match = re.search(GITHUB_REGEX, text, re.IGNORECASE)
    if gh_match:
        contacts['github'] = f"github.com/{gh_match.group(1)}"
        
    # 5. Portfolio
    port_match = re.search(PORTFOLIO_REGEX, text, re.IGNORECASE)
    if port_match:
        url = port_match.group(0)
        if not any(k in url.lower() for k in ['linkedin', 'github', 'gmail', 'yahoo', 'outlook']):
            contacts['portfolio'] = url

    # 6. Candidate Name Heuristic (usually appears in top 3-4 non-empty lines)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    for line in lines[:4]:
        # Filter out lines containing email, phone, URLs or standard headings
        if '@' in line or 'http' in line or 'www' in line or '+' in line:
            continue
        words = line.split()
        if 1 <= len(words) <= 4:
            # Check if words look like a person's name (letters only, capitalized)
            if all(re.match(r'^[A-Za-z.\'-]+$', w) for w in words):
                contacts['name'] = line
                break

    return contacts


def segment_sections(text):
    """
    Segments resume into standard sections: summary, experience, education, skills, projects, certifications, achievements.
    """
    sections = {
        'summary': '',
        'experience': '',
        'education': '',
        'skills': '',
        'projects': '',
        'certifications': '',
        'achievements': '',
        'other': ''
    }
    
    lines = text.split('\n')
    current_section = 'summary'  # default start
    
    # Pre-build section lookup
    header_map = {}
    for sec_key, kw_list in SECTION_KEYWORDS.items():
        for kw in kw_list:
            header_map[kw] = sec_key
            
    buffer = {k: [] for k in sections.keys()}
    
    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
            
        lower_line = cleaned_line.lower().strip(': -#*')
        
        # Check if line is a section header (short line matching known keywords)
        is_header = False
        if len(cleaned_line.split()) <= 4:
            for kw, sec_key in header_map.items():
                if lower_line == kw or lower_line == kw + 's' or lower_line.startswith(kw + ':'):
                    current_section = sec_key
                    is_header = True
                    break
                    
        if not is_header:
            buffer[current_section].append(cleaned_line)
            
    for sec, line_list in buffer.items():
        sections[sec] = "\n".join(line_list).strip()
        
    return sections


def extract_education_details(education_text, full_text):
    """Extracts degree names, GPAs, graduation years, and college names."""
    combined_text = f"{education_text}\n{full_text}"
    degrees_found = []
    
    for pat in DEGREES_PATTERNS:
        matches = re.findall(pat, combined_text, re.IGNORECASE)
        for m in matches:
            clean_m = m.strip()
            if clean_m and clean_m.lower() not in [d.lower() for d in degrees_found]:
                degrees_found.append(clean_m)
                
    # Extract GPA / CGPA / Percentages
    gpa_matches = re.findall(r'(?:CGPA|GPA|Score|Percentage|Marks)[\s:]*([0-9]+(?:\.[0-9]+)?(?:\s*\/\s*[0-9]+(?:\.[0-9]+)?)?%?)', combined_text, re.IGNORECASE)
    # Extract Graduation Years (e.g. 2018 - 2022, 2024, Class of 2023)
    year_matches = re.findall(r'\b(?:19|20)\d{2}(?:\s*[-–—to]+\s*(?:(?:19|20)\d{2}|Present|Current))?\b', education_text)
    
    return {
        'degrees': degrees_found,
        'gpa_scores': gpa_matches[:3],
        'years': year_matches[:3],
        'has_education_section': bool(degrees_found or education_text)
    }


def analyze_action_verbs_and_metrics(text):
    """Finds strong action verbs and quantified impact metrics in the text."""
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    found_verbs = set()
    for w in words:
        if w in ACTION_VERBS:
            found_verbs.add(w)
            
    # Quantifiable metrics: numbers with %, $, k, ms, x, or numbers >= 2
    metric_matches = re.findall(r'(?:\$\s*\d+[\d,.]*(?:k|m|b)?|\d+[\d,.]*%\s*|\b\d+x\b|\b\d+\s*(?:ms|sec|hours|days|users|clients|teams|projects|engineers|students|leads)\b)', text, re.IGNORECASE)
    
    return {
        'action_verbs_count': len(found_verbs),
        'action_verbs_list': sorted(list(found_verbs)),
        'metrics_count': len(metric_matches),
        'metrics_samples': list(set(metric_matches))[:8]
    }


def parse_resume_full(raw_text):
    """
    Master parser orchestrating contact extraction, section segmentation,
    skill extraction, education details, and impact metrics.
    """
    contacts = extract_contact_info(raw_text)
    sections = segment_sections(raw_text)
    education_info = extract_education_details(sections.get('education', ''), raw_text)
    skills = extract_skills_from_text(raw_text)
    categorized_skills = categorize_skills(skills)
    impact_data = analyze_action_verbs_and_metrics(sections.get('experience', '') or raw_text)
    
    # Experience presence indicators
    exp_text = sections.get('experience', '')
    has_experience = bool(exp_text and len(exp_text.split()) > 20)
    
    # Project presence indicators
    proj_text = sections.get('projects', '')
    has_projects = bool(proj_text and len(proj_text.split()) > 15)
    
    # Certifications presence
    cert_text = sections.get('certifications', '')
    has_certifications = bool(cert_text and len(cert_text.split()) > 8)

    return {
        'contacts': contacts,
        'sections': sections,
        'education': education_info,
        'skills': skills,
        'categorized_skills': categorized_skills,
        'impact': impact_data,
        'flags': {
            'has_summary': bool(sections.get('summary', '').strip()),
            'has_experience': has_experience,
            'has_education': education_info['has_education_section'],
            'has_projects': has_projects,
            'has_certifications': has_certifications,
            'has_skills_section': bool(sections.get('skills', '').strip() or len(skills) >= 4)
        }
    }
