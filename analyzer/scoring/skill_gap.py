from analyzer.nlp.skill_extractor import extract_skills_from_text, normalize_skill_name

def analyze_skill_gap(resume_skills, target_role=None, custom_jd_text=None):
    """
    Performs skill gap analysis:
    - Matched Skills: present in resume AND required/preferred in target role (or extracted from custom JD)
    - Missing Skills: required by target role / JD but missing in resume
    - Recommended Skills: trending/preferred skills for this role that candidate could add
    """
    resume_skills_set = {s.lower() for s in resume_skills}
    
    required_skills = []
    preferred_skills = []
    
    if target_role:
        required_skills = [s.name for s in target_role.required_skills.all()]
        preferred_skills = [s.name for s in target_role.preferred_skills.all()]
    elif custom_jd_text:
        # Extract skills from custom job description
        jd_skills = extract_skills_from_text(custom_jd_text)
        # Top 60% as required, remaining as preferred
        split_idx = max(1, int(len(jd_skills) * 0.65))
        required_skills = jd_skills[:split_idx]
        preferred_skills = jd_skills[split_idx:]
    else:
        # Fallback default general skills
        required_skills = ['Problem Solving', 'Communication', 'Git']
        preferred_skills = ['Agile', 'Team Collaboration']

    matched = []
    missing_required = []
    missing_preferred = []
    
    # Check Required Skills
    for r_skill in required_skills:
        if r_skill.lower() in resume_skills_set or normalize_skill_name(r_skill).lower() in resume_skills_set:
            matched.append({'name': r_skill, 'type': 'required', 'status': 'matched'})
        else:
            missing_required.append({'name': r_skill, 'type': 'required', 'status': 'missing'})
            
    # Check Preferred Skills
    for p_skill in preferred_skills:
        if p_skill.lower() in resume_skills_set or normalize_skill_name(p_skill).lower() in resume_skills_set:
            if not any(m['name'].lower() == p_skill.lower() for m in matched):
                matched.append({'name': p_skill, 'type': 'preferred', 'status': 'matched'})
        else:
            missing_preferred.append({'name': p_skill, 'type': 'preferred', 'status': 'recommended'})

    # Additional resume skills not in target requirements (Bonus/Additional skills)
    target_skill_names_lower = {s.lower() for s in required_skills + preferred_skills}
    additional_skills = [
        s for s in resume_skills 
        if s.lower() not in target_skill_names_lower
    ]

    total_required = len(required_skills) if required_skills else 1
    req_match_pct = round((len([m for m in matched if m['type'] == 'required']) / total_required) * 100, 1)

    return {
        'matched_skills': [m['name'] for m in matched],
        'matched_details': matched,
        'missing_skills': [m['name'] for m in missing_required],
        'missing_details': missing_required,
        'recommended_skills': [m['name'] for m in missing_preferred],
        'recommended_details': missing_preferred,
        'additional_skills': additional_skills,
        'required_count': len(required_skills),
        'preferred_count': len(preferred_skills),
        'match_percentage': min(100.0, req_match_pct)
    }
