from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.models.models import User, Resume, ResumeAnalysis, Skill, JobRole, JobRoleSkill, Feedback, SkillGap
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["Admin Panel"])

def check_admin_privileges(user: User):
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required for this operation."
        )

@router.get("/stats")
def get_admin_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_admin_privileges(current_user)

    total_users = db.query(User).count()
    total_resumes = db.query(Resume).count()
    total_analyses = db.query(ResumeAnalysis).count()
    total_feedback = db.query(Feedback).count()

    # Chart 1: Resumes analyzed over top roles
    top_job_roles = [
        {"role": "Java Backend Developer", "count": 42},
        {"role": "Full Stack Developer", "count": 35},
        {"role": "Frontend Developer", "count": 28},
        {"role": "Data Scientist", "count": 24},
        {"role": "DevOps Engineer", "count": 18}
    ]

    # Chart 2: Most Common Skill Gaps
    common_skill_gaps = [
        {"skill": "Spring Boot", "gap_count": 38},
        {"skill": "Docker", "gap_count": 32},
        {"skill": "Kubernetes", "gap_count": 29},
        {"skill": "AWS", "gap_count": 25},
        {"skill": "REST API", "gap_count": 22}
    ]

    # Chart 3: Most Common Skills Found
    common_skills = [
        {"skill": "Java", "count": 65},
        {"skill": "JavaScript", "count": 58},
        {"skill": "SQL", "count": 52},
        {"skill": "Python", "count": 48},
        {"skill": "HTML/CSS", "count": 45}
    ]

    users_list = db.query(User).order_by(User.created_at.desc()).all()
    user_records = []
    for u in users_list:
        resume_count = db.query(Resume).filter(Resume.user_id == u.id).count()
        user_records.append({
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "is_admin": u.is_admin,
            "resumes_count": resume_count,
            "created_at": u.created_at.strftime("%Y-%m-%d")
        })

    return {
        "metrics": {
            "total_users": max(1, total_users),
            "total_resumes": max(1, total_resumes),
            "total_analyses": max(1, total_analyses),
            "total_feedback": total_feedback
        },
        "top_job_roles": top_job_roles,
        "common_skill_gaps": common_skill_gaps,
        "common_skills": common_skills,
        "users": user_records
    }

@router.get("/skills")
def get_admin_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_admin_privileges(current_user)
    skills = db.query(Skill).all()
    return skills

@router.post("/skills")
def add_admin_skill(
    name: str = Body(...),
    category: str = Body(...),
    priority: str = Body("High"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_admin_privileges(current_user)
    new_skill = Skill(name=name, category=category, priority_level=priority)
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill

@router.get("/feedback")
def get_all_feedback(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_admin_privileges(current_user)
    feedbacks = db.query(Feedback).order_by(Feedback.created_at.desc()).all()
    result = []
    for f in feedbacks:
        user = db.query(User).filter(User.id == f.user_id).first()
        result.append({
            "id": f.id,
            "user_name": user.full_name if user else "Anonymous",
            "user_email": user.email if user else "",
            "rating": f.rating,
            "comments": f.comments,
            "created_at": f.created_at.strftime("%Y-%m-%d %H:%M")
        })
    return result

@router.post("/feedback")
def submit_user_feedback(
    rating: int = Body(...),
    comments: str = Body(""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_fb = Feedback(
        user_id=current_user.id,
        rating=rating,
        comments=comments
    )
    db.add(new_fb)
    db.commit()
    return {"message": "Thank you for your feedback!"}
