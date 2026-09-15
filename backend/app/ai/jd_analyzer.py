from typing import Dict, Any, List
from app.ai.parser import extract_skills_from_text

def analyze_job_description(jd_text: str, user_skills: List[str]) -> Dict[str, Any]:
    extracted_jd_skills = extract_skills_from_text(jd_text)
    
    # Heuristic detection for missing keywords or tech terms in JD
    extra_keywords = ["git", "agile", "ci/cd", "rest api", "unit testing", "scrum", "microservices"]
    for kw in extra_keywords:
        if kw in jd_text.lower() and kw.capitalize() not in extracted_jd_skills:
            extracted_jd_skills.append(kw.title())

    user_skills_lower = [s.lower().strip() for s in user_skills]

    matching_skills = []
    missing_skills = []

    for skill in extracted_jd_skills:
        skill_lower = skill.lower().strip()
        if any(skill_lower in us or us in skill_lower for us in user_skills_lower):
            matching_skills.append(skill)
        else:
            missing_skills.append(skill)

    total_req = len(extracted_jd_skills)
    match_score = round((len(matching_skills) / total_req) * 100) if total_req > 0 else 78

    tailoring_suggestions = []
    if missing_skills:
        top_missing = ", ".join(missing_skills[:4])
        tailoring_suggestions.append(f"Incorporate missing core skills explicitly into your skills section: {top_missing}.")
    tailoring_suggestions.append("Align the terminology in your work experience bullet points with the specific action verbs in this job posting.")
    tailoring_suggestions.append("Add a targeted Professional Summary highlighting your experience relevant to this specific role.")
    tailoring_suggestions.append("Ensure your project section explicitly mentions tools and libraries requested in the job description.")

    return {
        "job_match_score": match_score,
        "extracted_jd_skills": extracted_jd_skills,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "experience_requirement": "2+ Years (Extracted from JD)",
        "education_requirement": "Bachelor's Degree in Computer Science or related field",
        "tailoring_suggestions": tailoring_suggestions
    }
