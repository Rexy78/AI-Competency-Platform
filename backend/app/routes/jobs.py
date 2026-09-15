from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.models.models import User, Resume
from app.utils.auth import get_current_user
from app.ai.job_matcher import recommend_job_roles
from app.ai.jd_analyzer import analyze_job_description
from app.schemas.schemas import JDAnalysisRequest

router = APIRouter(prefix="/api/jobs", tags=["Job Recommendations & Description Analysis"])

@router.get("/recommendations")
def get_job_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    latest_resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
    user_skills = []
    if latest_resume and latest_resume.parsed_json:
        user_skills = latest_resume.parsed_json.get("all_skills", [])
    else:
        user_skills = ["Java", "SQL", "Git", "Python", "HTML", "CSS", "JavaScript"]

    recommendations = recommend_job_roles(user_skills)
    return recommendations

@router.post("/jd-match")
def match_job_description(
    payload: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    jd_text = payload.get("job_description", "")
    if not jd_text.strip():
        raise HTTPException(status_code=400, detail="Job description text is required.")

    latest_resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
    user_skills = []
    if latest_resume and latest_resume.parsed_json:
        user_skills = latest_resume.parsed_json.get("all_skills", [])
    else:
        user_skills = ["Java", "SQL", "Git", "Python", "HTML", "CSS", "JavaScript"]

    res = analyze_job_description(jd_text, user_skills)

    # Normalize keys for frontend compatibility
    return {
        "jd_match_score": res.get("job_match_score", 82),
        "total_jd_keywords": len(res.get("extracted_jd_skills", [])),
        "extracted_jd_skills": res.get("extracted_jd_skills", []),
        "present_skills": res.get("matching_skills", []),
        "missing_skills": res.get("missing_skills", []),
        "experience_requirement": res.get("experience_requirement", "2+ Years Required"),
        "education_requirement": res.get("education_requirement", "Bachelor's Degree in CS or related field"),
        "tailoring_suggestions": res.get("tailoring_suggestions", [
            "Incorporate missing core keywords into your skills section.",
            "Align terminology in work experience bullet points with action verbs in this job posting.",
            "Add a targeted Professional Summary highlighting relevant role experience."
        ])
    }

@router.post("/analyze")
def analyze_job_posting(
    payload: JDAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return match_job_description({"job_description": payload.job_description}, current_user, db)
