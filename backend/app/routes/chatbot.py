from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Literal, Optional, List
from pydantic import BaseModel, Field
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.models import User, Resume, ResumeAnalysis
from app.ai.chatbot import chat_with_astra, normalize_resume_context
from app.ai.skill_gap_engine import analyze_skill_gaps
from app.ai.taxonomy import JOB_ROLE_REQUIREMENTS

router = APIRouter(prefix="/api/chatbot", tags=["Astra AI Career Assistant"])

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=2000)


class ChatRequest(BaseModel):
    message: str
    target_role: Optional[str] = None
    history: List[ChatMessage] = Field(default_factory=list, max_length=12)


@router.get("/roles")
def get_chatbot_target_roles():
    return list(JOB_ROLE_REQUIREMENTS)


@router.post("/chat")
def chat_with_assistant(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    latest_resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
    latest_analysis = db.query(ResumeAnalysis).filter(
        ResumeAnalysis.user_id == current_user.id
    ).order_by(ResumeAnalysis.created_at.desc()).first()

    valid_roles = {role.casefold(): role for role in JOB_ROLE_REQUIREMENTS}
    requested_role = req.target_role or (latest_analysis.target_role if latest_analysis else None)
    target_role = valid_roles.get((requested_role or "").casefold())
    if req.target_role and not target_role:
        raise HTTPException(
            status_code=400,
            detail="Select a supported target role before requesting skill-gap analysis."
        )
    target_role = target_role or "Java Backend Developer"

    candidate_context = {
        "name": current_user.full_name,
        "summary": "",
        "skills": [],
        "target_role": target_role,
        "missing_skills": [],
        "ats_score": 0,
        "has_resume": bool(latest_resume),
        "skill_gap_status": "no_resume",
    }

    if latest_resume and latest_resume.parsed_json:
        parsed_resume = latest_resume.parsed_json
        normalized_resume = normalize_resume_context(parsed_resume, target_role)
        candidate_context.update(normalized_resume)
        candidate_context["target_role"] = target_role

        if candidate_context["skills"]:
            gap_result = analyze_skill_gaps(candidate_context["skills"], target_role)
            candidate_context.update({
                "skill_gap_status": "analyzed",
                "skill_match_percentage": gap_result["skill_match_percentage"],
                "gap_matrix": gap_result["gap_matrix"],
                "recommendations": gap_result["recommendations"],
                "matching_skills": [
                    gap["skill"] for gap in gap_result["gap_matrix"]
                    if gap["status"] == "Available"
                ],
                "missing_skills": [
                    gap["skill"] for gap in gap_result["gap_matrix"]
                    if gap["status"] == "Missing"
                ],
            })
        else:
            candidate_context["skill_gap_status"] = "no_detected_skills"
            candidate_context["missing_skills"] = []
            candidate_context["matching_skills"] = []
    elif latest_resume:
        candidate_context["skill_gap_status"] = "no_detected_skills"

    reply = chat_with_astra(
        user_message=req.message,
        conversation_history=[message.model_dump() for message in req.history],
        candidate_context=candidate_context
    )

    return {
        "reply": reply,
        "sender": "Astra AI",
        "timestamp": "Just now"
    }
