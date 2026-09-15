from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.models.models import User, Resume, SkillGap, Recommendation
from app.utils.auth import get_current_user
from app.ai.taxonomy import SKILL_TAXONOMY, JOB_ROLE_REQUIREMENTS
from app.ai.skill_gap_engine import analyze_skill_gaps

router = APIRouter(prefix="/api/skills", tags=["Skills & Gap Analysis"])

@router.get("")
def get_all_skills():
    return SKILL_TAXONOMY

@router.get("/gaps")
def get_skill_gaps(
    target_role: str = "Java Backend Developer",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    latest_resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
    user_skills = []
    if latest_resume and latest_resume.parsed_json:
        user_skills = latest_resume.parsed_json.get("all_skills", [])
    else:
        # Default sample skills if user hasn't uploaded yet
        user_skills = ["Java", "SQL", "Git", "HTML", "CSS", "JavaScript"]

    gap_result = analyze_skill_gaps(user_skills, target_role)
    return gap_result
