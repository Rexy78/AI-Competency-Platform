from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.models import User, Resume, AIConversation, AIMessage
from app.ai.chatbot import chat_with_astra
from datetime import datetime

router = APIRouter(prefix="/api/chat", tags=["Astra Chat"])


class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str


@router.post("")
def chat(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # find or create conversation
    conv = None
    if req.conversation_id:
        conv = db.query(AIConversation).filter(AIConversation.id == req.conversation_id, AIConversation.user_id == current_user.id).first()
    if not conv:
        conv = AIConversation(user_id=current_user.id, title="Astra Chat", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # store user message
    user_msg = AIMessage(conversation_id=conv.id, role="user", message=req.message, created_at=datetime.utcnow())
    db.add(user_msg)
    db.commit()

    # load latest resume/profile
    latest_resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
    candidate_profile = {}
    if latest_resume and latest_resume.parsed_json:
        candidate_profile = latest_resume.parsed_json

    # load conversation history (last 50 messages)
    msgs = db.query(AIMessage).filter(AIMessage.conversation_id == conv.id).order_by(AIMessage.created_at.asc()).all()
    history = [{"role": m.role, "message": m.message} for m in msgs]

    # get assistant response
    reply = chat_with_astra(req.message, conversation_history=history, candidate_context=candidate_profile)

    assistant_msg = AIMessage(conversation_id=conv.id, role="assistant", message=reply, created_at=datetime.utcnow())
    db.add(assistant_msg)
    conv.updated_at = datetime.utcnow()
    db.commit()

    return {"conversation_id": conv.id, "reply": reply}


@router.get("/conversations")
def list_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    convs = db.query(AIConversation).filter(AIConversation.user_id == current_user.id).order_by(AIConversation.updated_at.desc()).all()
    return [{"id": c.id, "title": c.title or "Astra Chat", "created_at": c.created_at, "updated_at": c.updated_at} for c in convs]


@router.get("/history")
def get_history(conversation_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = db.query(AIConversation).filter(AIConversation.id == conversation_id, AIConversation.user_id == current_user.id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    msgs = db.query(AIMessage).filter(AIMessage.conversation_id == conv.id).order_by(AIMessage.created_at.asc()).all()
    return [{"role": m.role, "message": m.message, "created_at": m.created_at} for m in msgs]


@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = db.query(AIConversation).filter(AIConversation.id == conversation_id, AIConversation.user_id == current_user.id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    # delete messages
    db.query(AIMessage).filter(AIMessage.conversation_id == conv.id).delete()
    db.delete(conv)
    db.commit()
    return {"status": "deleted"}
