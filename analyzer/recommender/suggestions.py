def generate_recommendations(parsed_data, scoring_data, target_role=None, custom_role_title=None):
    """
    Generates intelligent, actionable, tailored suggestions based on:
    - Missing skills vs target role
    - Section completeness & contact details
    - Action verbs & quantified metrics density
    - Formatting & page count checks
    """
    recommendations = []
    
    contacts = parsed_data.get('contacts', {})
    flags = parsed_data.get('flags', {})
    impact = parsed_data.get('impact', {})
    skill_gap = scoring_data.get('skill_gap', {})
    subscores = scoring_data.get('subscores', {})
    role_name = target_role.title if target_role else (custom_role_title or "Target Job")
    
    missing_skills = skill_gap.get('missing_skills', [])
    recommended_skills = skill_gap.get('recommended_skills', [])

    # 1. High Priority: Missing Core Technical Skills
    if missing_skills:
        top_missing = missing_skills[:5]
        recommendations.append({
            'category': 'Keywords & Skills',
            'priority': 'High',
            'icon': 'bi-exclamation-triangle-fill',
            'badge_class': 'bg-danger text-white',
            'title': f'Incorporate Key Missing Skills for {role_name}',
            'description': f'Your resume is missing critical skills frequently screened by ATS algorithms for {role_name}: {", ".join(top_missing)}.',
            'action': f'If you have experience with {", ".join(top_missing)}, explicitly mention them in your Skills, Projects, and Work Experience bullet points.'
        })

    # 2. Recommended / Trending Skills Boost
    if recommended_skills:
        top_rec = recommended_skills[:4]
        recommendations.append({
            'category': 'Competitive Edge',
            'priority': 'Medium',
            'icon': 'bi-stars',
            'badge_class': 'bg-primary text-white',
            'title': 'Add In-Demand / Preferred Skill Keywords',
            'description': f'Candidates who also list {", ".join(top_rec)} stand out with higher recruiter shortlisting rates.',
            'action': 'Highlight any familiarity, coursework, or mini-projects incorporating these secondary technologies.'
        })

    # 3. Action Verbs & Google XYZ Formula
    action_verbs_count = impact.get('action_verbs_count', 0)
    metrics_count = impact.get('metrics_count', 0)
    
    if action_verbs_count < 8 or metrics_count < 3:
        recommendations.append({
            'category': 'Impact & Phrasing',
            'priority': 'High',
            'icon': 'bi-lightning-charge-fill',
            'badge_class': 'bg-danger text-white',
            'title': 'Adopt the Google "XYZ Formula" for Experience Bullets',
            'description': 'Replace passive duty statements with impactful accomplishment statements: "Accomplished [X] as measured by [Y], by doing [Z]".',
            'action': 'Example: Instead of "Worked on backend APIs", write: "Architected 12+ RESTful microservices using Python & FastAPI, reducing API response latency by 35% across 100k daily requests."'
        })

    # 4. Contact Information Completeness
    missing_contacts = []
    if not contacts.get('email'): missing_contacts.append('Email Address')
    if not contacts.get('phone'): missing_contacts.append('Phone Number')
    if not contacts.get('linkedin'): missing_contacts.append('LinkedIn Profile URL')
    if not contacts.get('github'): missing_contacts.append('GitHub / Portfolio URL')
    
    if missing_contacts:
        recommendations.append({
            'category': 'Contact Header',
            'priority': 'Medium',
            'icon': 'bi-person-badge',
            'badge_class': 'bg-warning text-dark',
            'title': 'Complete Your Header & Online Profiles',
            'description': f'ATS parsers look for standard contact information. Missing: {", ".join(missing_contacts)}.',
            'action': 'Ensure your full name, email, phone number with country code, and clickable LinkedIn/GitHub URLs are at the top.'
        })

    # 5. Professional Summary Check
    if not flags.get('has_summary'):
        recommendations.append({
            'category': 'Structure',
            'priority': 'Medium',
            'icon': 'bi-file-earmark-text',
            'badge_class': 'bg-warning text-dark',
            'title': 'Add a Tailored 2-3 Sentence Professional Summary',
            'description': 'A strong summary at the top anchors your primary skill set, years of experience, and value proposition for ATS scan and human recruiters.',
            'action': f'Craft an executive summary such as: "Results-driven Software Engineer with 2+ years developing scalable web applications in Python and Django..."'
        })

    # 6. Projects & Certifications Suggestions
    if missing_skills:
        primary_gap = missing_skills[0]
        recommendations.append({
            'category': 'Portfolio Growth',
            'priority': 'Low',
            'icon': 'bi-folder-check',
            'badge_class': 'bg-info text-dark',
            'title': f'Build a Showcase Project with {primary_gap}',
            'description': f'Demonstrate hands-on mastery of {primary_gap} by creating an end-to-end open-source project on GitHub with clear documentation and live demo link.',
            'action': f'Include technical architecture details and link the GitHub repository in your Projects section.'
        })

    # 7. Recommended Certifications
    cert_map = {
        'AWS': 'AWS Certified Solutions Architect / Cloud Practitioner',
        'Azure': 'Microsoft Certified: Azure Fundamentals (AZ-900 / AZ-204)',
        'Google Cloud': 'Google Cloud Associate Cloud Engineer',
        'Docker': 'Docker Certified Associate (DCA)',
        'Kubernetes': 'Certified Kubernetes Application Developer (CKAD)',
        'Python': 'PCEP / PCAP Certified Associate Python Programmer',
        'Java': 'Oracle Certified Professional: Java SE Programmer',
        'Machine Learning': 'TensorFlow Developer Certificate / DeepLearning.AI',
        'Scrum': 'Professional Scrum Master (PSM I)'
    }
    
    matched_cert_tips = []
    for sk in missing_skills + recommended_skills:
        if sk in cert_map:
            matched_cert_tips.append(f"{sk} -> {cert_map[sk]}")
            
    if matched_cert_tips:
        recommendations.append({
            'category': 'Certifications',
            'priority': 'Low',
            'icon': 'bi-award',
            'badge_class': 'bg-info text-dark',
            'title': 'Target High-Value Industry Certifications',
            'description': f'Certifications validate specialized knowledge: {"; ".join(matched_cert_tips[:3])}.',
            'action': 'Add valid certifications with issuing organization, date obtained, and verification credential ID.'
        })

    # 8. Formatting & ATS Readability
    formatting_score = subscores.get('formatting_score', 100)
    if formatting_score < 80:
        recommendations.append({
            'category': 'ATS Readability',
            'priority': 'Medium',
            'icon': 'bi-layout-text-window',
            'badge_class': 'bg-warning text-dark',
            'title': 'Optimize Resume Layout & Formatting',
            'description': 'Complex tables, images, multiple columns, and unusual fonts can break ATS parser reading order.',
            'action': 'Use clean single-column format, standard font (Arial, Calibri, Inter), standard section headers, and bullet points.'
        })

    return recommendations
