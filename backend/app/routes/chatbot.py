from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from pydantic import BaseModel
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.models import User, Resume
from app.ai.chatbot import chat_with_astra, normalize_resume_context

router = APIRouter(prefix="/api/chatbot", tags=["Astra AI Career Assistant"])

class ChatRequest(BaseModel):
    message: str
    target_role: Optional[str] = "Software Engineer"

@router.post("/chat")
def chat_with_assistant(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    latest_resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()

    candidate_context = {
        "name": current_user.full_name,
        "summary": "Software Engineering Candidate",
        "skills": ["Python", "Java", "REST API", "SQL", "React"],
        "target_role": req.target_role or "Software Engineer",
        "missing_skills": ["Spring Boot", "Docker", "AWS", "System Design"],
        "ats_score": 78,
    }

    if latest_resume and latest_resume.parsed_json:
        parsed_resume = latest_resume.parsed_json
        normalized_resume = normalize_resume_context(parsed_resume, req.target_role or "Software Engineer")
        candidate_context.update(normalized_resume)

    reply = chat_with_astra(
        user_message=req.message,
        candidate_context=candidate_context
    )

    return {
        "reply": reply,
        "sender": "Astra AI",
        "timestamp": "Just now"
    }
