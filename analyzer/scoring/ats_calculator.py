import math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .skill_gap import analyze_skill_gap

def calculate_cosine_similarity(text1, text2):
    """Computes TF-IDF cosine similarity between two text corpuses."""
    if not text1 or not text2:
        return 0.0
    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000
        )
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(sim)
    except Exception as e:
        print(f"Error calculating cosine similarity: {e}")
        return 0.0


def calculate_ats_score(parsed_data, resume_meta, target_role=None, custom_jd_text=None):
    """
    Computes a comprehensive ATS compatibility score (0 - 100) and sub-scores.
    
    Weights:
    - Keywords & Similarity: 30%
    - Skill Gap Matching: 25%
    - Experience & Impact: 15%
    - Education & Credentials: 10%
    - Section Completeness: 10%
    - Formatting & Readability: 10%
    """
    resume_text = resume_meta.get('text', '')
    resume_skills = parsed_data.get('skills', [])
    page_count = resume_meta.get('page_count', 1)
    word_count = resume_meta.get('word_count', 0)
    flags = parsed_data.get('flags', {})
    contacts = parsed_data.get('contacts', {})
    impact = parsed_data.get('impact', {})
    education = parsed_data.get('education', {})

    # Target text reference
    target_corpus = ""
    if target_role:
        target_corpus = f"{target_role.title} {target_role.description} " + " ".join(target_role.get_all_required_skill_names())
    elif custom_jd_text:
        target_corpus = custom_jd_text
    else:
        target_corpus = "software engineer developer programming python data cloud"

    # 1. Keyword Similarity Score (0 - 100)
    raw_sim = calculate_cosine_similarity(resume_text, target_corpus)
    # Cosine sim on raw text typically ranges from 0.15 to 0.65; scale logarithmically/linearly to 0-100
    keyword_match_score = min(100.0, max(20.0, raw_sim * 160.0))
    keyword_match_score = round(keyword_match_score, 1)

    # 2. Skills Match Score (0 - 100)
    gap_result = analyze_skill_gap(resume_skills, target_role, custom_jd_text)
    matched_req_count = len([m for m in gap_result['matched_details'] if m['type'] == 'required'])
    total_req_count = gap_result['required_count'] or 1
    req_ratio = matched_req_count / total_req_count
    
    # Bonus for preferred skills
    matched_pref_count = len([m for m in gap_result['matched_details'] if m['type'] == 'preferred'])
    total_pref_count = gap_result['preferred_count'] or 1
    pref_ratio = matched_pref_count / total_pref_count if total_pref_count > 0 else 0
    
    skills_score = round(min(100.0, (req_ratio * 80.0) + (pref_ratio * 20.0) + (min(len(resume_skills), 15) * 1.0)), 1)

    # 3. Experience & Impact Score (0 - 100)
    exp_score = 0.0
    if flags.get('has_experience', False):
        exp_score += 40.0
    if flags.get('has_projects', False):
        exp_score += 20.0
        
    action_verbs = impact.get('action_verbs_count', 0)
    if action_verbs >= 10:
        exp_score += 20.0
    elif action_verbs >= 5:
        exp_score += 12.0
    elif action_verbs >= 1:
        exp_score += 6.0
        
    metrics_count = impact.get('metrics_count', 0)
    if metrics_count >= 4:
        exp_score += 20.0
    elif metrics_count >= 2:
        exp_score += 12.0
    elif metrics_count >= 1:
        exp_score += 6.0
    experience_score = round(min(100.0, exp_score), 1)

    # 4. Education & Credentials Score (0 - 100)
    edu_score = 0.0
    if flags.get('has_education', False):
        edu_score += 50.0
    if len(education.get('degrees', [])) > 0:
        edu_score += 30.0
    if flags.get('has_certifications', False):
        edu_score += 20.0
    elif len(education.get('gpa_scores', [])) > 0:
        edu_score += 10.0
    education_score = round(min(100.0, edu_score), 1)

    # 5. Section Completeness Score (0 - 100)
    complete_points = 0.0
    # Contact items (Email + Phone + GitHub/LinkedIn) = 30 pts
    if contacts.get('email'): complete_points += 10.0
    if contacts.get('phone'): complete_points += 10.0
    if contacts.get('linkedin') or contacts.get('github'): complete_points += 10.0
    
    if flags.get('has_summary'): complete_points += 15.0
    if flags.get('has_skills_section'): complete_points += 15.0
    if flags.get('has_experience'): complete_points += 20.0
    if flags.get('has_education'): complete_points += 10.0
    if flags.get('has_projects'): complete_points += 10.0
    completeness_score = round(min(100.0, complete_points), 1)

    # 6. Formatting & Readability Score (0 - 100)
    format_points = 100.0
    # Page count check (Ideal 1-2 pages)
    if page_count > 3:
        format_points -= 25.0
    elif page_count == 3:
        format_points -= 10.0
        
    # Word count sanity check (300 to 1200 words is standard)
    if word_count < 150:
        format_points -= 30.0
    elif word_count > 1500:
        format_points -= 15.0
        
    # Bullet points / action verb presence is a proxy for readable structure
    if action_verbs < 3:
        format_points -= 10.0
    formatting_score = round(max(20.0, min(100.0, format_points)), 1)

    # Overall Weighted ATS Score
    overall_ats = (
        (0.30 * keyword_match_score) +
        (0.25 * skills_score) +
        (0.15 * experience_score) +
        (0.10 * education_score) +
        (0.10 * completeness_score) +
        (0.10 * formatting_score)
    )
    overall_ats = round(min(99.0, max(15.0, overall_ats)), 1)

    return {
        'ats_score': overall_ats,
        'subscores': {
            'keyword_match_score': keyword_match_score,
            'skills_score': skills_score,
            'experience_score': experience_score,
            'education_score': education_score,
            'completeness_score': completeness_score,
            'formatting_score': formatting_score,
        },
        'skill_gap': gap_result
    }
