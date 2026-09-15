from typing import Dict, Any, List

def calculate_ats_score(parsed_data: Dict[str, Any], target_role: str = "Software Engineer") -> Dict[str, Any]:
    all_skills = parsed_data.get("all_skills", [])
    sections = parsed_data.get("sections", {})
    personal_info = parsed_data.get("personal_info", {})
    raw_text = parsed_data.get("raw_text", "")

    # 1. Section Completeness (Max 25 pts)
    completeness_pts = 0
    if personal_info.get("name") and personal_info.get("email"): completeness_pts += 5
    if personal_info.get("phone") or personal_info.get("linkedin"): completeness_pts += 5
    if sections.get("summary"): completeness_pts += 5
    if sections.get("experience"): completeness_pts += 5
    if sections.get("education"): completeness_pts += 5

    section_completeness_pct = min(100, int((completeness_pts / 25) * 100))

    # 2. Skills Match Score (Max 25 pts)
    skill_count = len(all_skills)
    skills_pct = min(100, int((skill_count / 10) * 100)) if skill_count > 0 else 40

    # 3. Keyword Match (Max 20 pts)
    tech_keywords = ["git", "api", "database", "agile", "development", "architecture", "system", "testing", "ci/cd", "cloud"]
    found_keywords = [kw for kw in tech_keywords if kw in raw_text.lower()]
    keyword_pct = min(100, int((len(found_keywords) / len(tech_keywords)) * 100))

    # 4. Formatting Quality (Max 15 pts)
    # Check length, structural markers
    formatting_pts = 15
    if len(raw_text) < 200: formatting_pts -= 5
    if not sections.get("education"): formatting_pts -= 3
    if not sections.get("experience"): formatting_pts -= 4
    formatting_pct = int((formatting_pts / 15) * 100)

    # 5. Experience Relevance (Max 15 pts)
    exp_count = len(sections.get("experience", []))
    exp_pct = min(100, max(50, exp_count * 25))

    # Overall Weighted Score (0 - 100)
    total_ats_score = round(
        (section_completeness_pct * 0.25) +
        (skills_pct * 0.25) +
        (keyword_pct * 0.20) +
        (formatting_pct * 0.15) +
        (exp_pct * 0.15)
    )
    total_ats_score = max(35, min(98, total_ats_score))

    # Actionable ATS Improvement Suggestions
    suggestions = []
    if "spring boot" not in [s.lower() for s in all_skills] and "java" in [s.lower() for s in all_skills]:
        suggestions.append("Add Spring Boot to your technical skills to improve backend matching.")
    if "git" not in [s.lower() for s in all_skills]:
        suggestions.append("Include Git/GitHub experience explicitly in your technical skills.")
    if not any(char.isdigit() for char in raw_text):
        suggestions.append("Include measurable metrics and numeric achievements in your projects (e.g. 'Improved speed by 35%').")
    if not personal_info.get("linkedin"):
        suggestions.append("Add your LinkedIn profile URL to the header contact section.")
    if len(all_skills) < 8:
        suggestions.append("List more industry standard frameworks and libraries in your skills section.")
    suggestions.append("Use stronger action verbs (e.g., Developed, Engineered, Optimized, Spearheaded) at the start of bullet points.")
    suggestions.append("Tailor keywords specifically to match the target job description.")

    return {
        "ats_score": total_ats_score,
        "keyword_score": keyword_pct,
        "skills_score": skills_pct,
        "formatting_score": formatting_pct,
        "experience_score": exp_pct,
        "section_completeness_score": section_completeness_pct,
        "suggestions": suggestions
    }
