from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.models import User, Resume
from app.ai.interview_generator import generate_interview_questions, evaluate_interview_answer

router = APIRouter(prefix="/api/interview", tags=["AI Interview Prep"])

class QuestionGenRequest(BaseModel):
    target_role: Optional[str] = "Software Engineer"

class AnswerEvalRequest(BaseModel):
    question: str
    answer: str

@router.post("/generate")
def get_interview_questions(
    req: QuestionGenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    latest_resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()

    resume_summary = "Software Developer"
    skills = ["Java", "Python", "REST API", "SQL"]
    target_role = req.target_role or "Software Engineer"

    if latest_resume:
        data = latest_resume.parsed_json or latest_resume.parsed_data or {}
        if isinstance(data, dict):
            raw_skills = data.get("all_skills") or data.get("skills") or []
            if isinstance(raw_skills, list) and raw_skills:
                skills = [str(skill).strip() for skill in raw_skills if str(skill).strip()]

            sections = data.get("sections") or {}
            summary = sections.get("summary") or sections.get("profile") or sections.get("about")
            if summary:
                resume_summary = str(summary)

            role_hint = data.get("target_role") or data.get("job_target_role")
            if role_hint:
                target_role = str(role_hint)

    questions = generate_interview_questions(
        resume_summary=resume_summary,
        skills=skills,
        target_role=target_role
    )
    return questions

@router.post("/evaluate")
def evaluate_candidate_answer(
    req: AnswerEvalRequest,
    current_user: User = Depends(get_current_user)
):
    if not req.answer or len(req.answer.strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a complete answer for evaluation."
        )

    evaluation = evaluate_interview_answer(question=req.question, answer=req.answer)
    return evaluation
